# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import re
import math
import mathutils
from mathutils import Vector
from numpy import subtract as np_subtract
from numpy import array as np_array

import bmesh
import bpy

from ..append_from_file_func import append_object_from_blend_file
from ..const import (FC_MATCH_DIST, SC_TEMP_SK_X, SC_TEMP_SK_Y, SC_TEMP_SK_Z)
from ..object_func import delete_all_objects_except, check_create_basis_shape_key
from ..template import get_searchable_object_name

SK_FUNC_APPLY_MOD = "SK_FUNC_APPLY_MOD"
SK_FUNC_BAKE = "SK_FUNC_BAKE"
SK_FUNC_COPY = "SK_FUNC_COPY"
SK_FUNC_DELETE = "SK_FUNC_DELETE"
SK_FUNC_ITEMS = [
    (SK_FUNC_APPLY_MOD, "Apply Modifier", "Apply Object Modifiers to mesh, with respect to ShapeKeys. Only " \
         "active Modifier(s) will be applied, and Modifier(s) will not be removed"),
    (SK_FUNC_BAKE, "Bake", "Bake mesh deform shapes to ShapeKeys"),
    (SK_FUNC_COPY, "Copy", ""),
    (SK_FUNC_DELETE, "Delete", ""),
]

def is_name_prefix_match(name, prefix):
    if name == prefix or re.match(prefix + "\w*", name):
        return True
    else:
        return False

def delete_shapekeys_by_prefix(obj, delete_prefix):
    for sk in obj.data.shape_keys.key_blocks:
        if sk.name != 'Basis' and is_name_prefix_match(sk.name, delete_prefix):
            # remove keyframes from shapekey, because Blender does'nt automatically remove them
            dp = sk.path_from_id('value')
            anim_data = obj.data.shape_keys.animation_data
            if anim_data is not None and anim_data.action is not None:
                fc = anim_data.action.fcurves.find(data_path=dp)
                if fc is not None:
                    anim_data.action.fcurves.remove(fc)
            # finally, remove the shapekey
            obj.shape_key_remove(sk)

def do_sk_func_delete(sel_obj_list, delete_prefix):
    # iterate over selected 'MESH' type objects that have shape keys; more than just Basis key
    for mesh_obj in (x for x in sel_obj_list
                     if x.type == 'MESH' and x.data.shape_keys is not None and
                     len(x.data.shape_keys.key_blocks) > 1):
        delete_shapekeys_by_prefix(mesh_obj, delete_prefix)

def v_distance(point1, point2) -> float:
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)

# returns [(vertex_index, vertex_scale), ...]
# src_obj and dest_obj must have the same topology
def get_vertex_difference_scales(src_obj, dst_obj):
    src_vert_edg_len_sum = [0] * len(src_obj.data.vertices)
    dst_vert_edg_len_sum = [0] * len(src_obj.data.vertices)
    # iterate over all edges, adding each edge length to both of its vertices
    for i in range(len(src_obj.data.edges)):
        ed = src_obj.data.edges[i]
        d = v_distance(src_obj.data.vertices[ed.vertices[0]].co, src_obj.data.vertices[ed.vertices[1]].co)
        src_vert_edg_len_sum[ed.vertices[0]] = src_vert_edg_len_sum[ed.vertices[0]] + d
        src_vert_edg_len_sum[ed.vertices[1]] = src_vert_edg_len_sum[ed.vertices[1]] + d

        ed = dst_obj.data.edges[i]
        d = v_distance(dst_obj.data.vertices[ed.vertices[0]].co, dst_obj.data.vertices[ed.vertices[1]].co)
        dst_vert_edg_len_sum[ed.vertices[0]] = dst_vert_edg_len_sum[ed.vertices[0]] + d
        dst_vert_edg_len_sum[ed.vertices[1]] = dst_vert_edg_len_sum[ed.vertices[1]] + d

    # get the difference in scales, per vertex
    output_list = []
    for i in range(len(src_vert_edg_len_sum)):
        # if scale is same then ignore this vert
        if src_vert_edg_len_sum[i] == dst_vert_edg_len_sum[i]:
            continue
        # prevent divide by zero
        if src_vert_edg_len_sum[i] == 0:
            continue
        # add to output list
        output_list.append((i, dst_vert_edg_len_sum[i] / src_vert_edg_len_sum[i]))

    return output_list

def copy_shapekeys_by_name_prefix(context, src_obj, dest_objects, copy_prefix, adapt_size):
    if src_obj.data.shape_keys is None:
        return

    # keep src_object selected throughout for loop, only switching dest_object select on and off
    src_obj.select_set(True)
    for dest_obj in dest_objects:
        # skip destination mesh objects with different numbers of vertices
        dvc = len(dest_obj.data.vertices)
        svc = len(src_obj.data.vertices)
        if dvc != svc:
            print("copy_shapekeys_by_name_prefix(): Cannot copy shapekeys from source ("+src_obj.name+
                ") to dest ("+dest_obj.name+"), source vertex count ("+str(svc)+
                ") doesn't equal destination vertex count ("+str(dvc)+").")
            continue

        # skip destination mesh objects with different numbers of edges
        dec = len(dest_obj.data.edges)
        sec = len(src_obj.data.edges)
        if dec != sec:
            print("copy_shapekeys_by_name_prefix(): Cannot copy shapekeys from source ("+src_obj.name+
                ") to dest ("+dest_obj.name+"), source edge count ("+str(sec)+
                ") doesn't equal destination edge count ("+str(dec)+").")
            continue

        # get the scaling needed, per vertex, to "fit" the shape key of the src_object to the dest_object
        vert_diff_scales = get_vertex_difference_scales(src_obj, dest_obj)

        show_temp = dest_obj.show_only_shape_key
        dest_obj.select_set(True)
        context.view_layer.objects.active = dest_obj
        check_create_basis_shape_key(dest_obj)
        for sk in src_obj.data.shape_keys.key_blocks:
            if sk.name == 'Basis':
                    continue
            if is_name_prefix_match(sk.name, copy_prefix):
                src_obj.active_shape_key_index = src_obj.data.shape_keys.key_blocks.find(sk.name)
                bpy.ops.object.shape_key_transfer()

            # if not adapt size then skip start next iteration
            if not adapt_size:
                continue

            # adjust for scale differences between source mesh and destination mesh, per vertex
            sk_index = len(dest_obj.data.shape_keys.key_blocks)-1
            for v_index, v_scale in vert_diff_scales:
                sk_loc = dest_obj.data.shape_keys.key_blocks[sk_index].data[v_index].co
                original_loc = dest_obj.data.shape_keys.key_blocks[0].data[v_index].co
                delta_loc = np_subtract(sk_loc, original_loc)
                dest_obj.data.shape_keys.key_blocks[sk_index].data[v_index].co = (v_scale * delta_loc[0] + original_loc[0],
                    v_scale * delta_loc[1] + original_loc[1], v_scale * delta_loc[2] + original_loc[2])

        dest_obj.select_set(False)
        # bpy.ops.object.shape_key_transfer will set show_only_shape_key to true, so reset to previous value
        dest_obj.show_only_shape_key = show_temp

    src_obj.select_set(False)

def do_copy_shape_keys(context, src_object, dest_objects, copy_prefix, adapt_size):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # de-select all objects because copying shape keys requires bpy.ops.object.shape_key_transfer,
    # and this requires exactly two specific objects be selected per shape key copy
    bpy.ops.object.select_all(action='DESELECT')

    copy_shapekeys_by_name_prefix(context, src_object, dest_objects, copy_prefix, adapt_size)
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def do_search_file_for_auto_sk(sel_obj_list, chosen_blend_file, name_prefix, adapt_size, swap_autoname_ext):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # copy list of selected objects, minus the active object
    selection_list = [ob for ob in sel_obj_list if ob.type == 'MESH']

    # keep a list of all objects in the Blend file, before objects are appended
    all_objects_list_before = [ ob for ob in bpy.data.objects ]

    bpy.ops.object.select_all(action='DESELECT')
    for sel in selection_list:
        search_name = get_searchable_object_name(sel.name)
        # if the desired ShapeKey mesh object name is already used then rename it before appending from file,
        # and rename later after the appended object is deleted
        test_obj = bpy.data.objects.get(search_name)
        if test_obj is not None:
            test_obj.name = "TempRenameName"

        # if cannot load mesh object from file...
        append_object_from_blend_file(chosen_blend_file, search_name)
        appended_obj = bpy.data.objects.get(search_name)
        if appended_obj is None:
            # if "swap autoname ext" is enabled then check object name, and if it follows the
            # '.001', '.002', etc. format, then try to swap again but with '.XYZ' extension removed
            if swap_autoname_ext and re.match(".*\.[0-9]{3}", search_name):
                no_ext_search_name = search_name[0:len(search_name)-4]
                append_object_from_blend_file(chosen_blend_file, no_ext_search_name)
                appended_obj = bpy.data.objects.get(no_ext_search_name)
            else:
                # if rename occurred, then undo rename
                if test_obj is not None:
                    test_obj.name = search_name
                continue

        # use bpy.context.selected_objects instead of sel_obj_list because bpy.context.selected_objects will change
        # as objects are selected/deselected
        appended_selection_list = [ob for ob in bpy.context.selected_objects]

        # de-select all objects because copying shape keys requires bpy.ops.object.shape_key_transfer,
        # and this requires exactly two specific objects be selected per shape key copy
        bpy.ops.object.select_all(action='DESELECT')
        copy_shapekeys_by_name_prefix(appended_obj, [sel], name_prefix, adapt_size)
        bpy.ops.object.select_all(action='DESELECT')

        # re-select the objects that were appended
        for ob in appended_selection_list:
            ob.select_set(True)

        # appended object may have pulled in other objects as dependencies, so delete all appended objects
        delete_all_objects_except(all_objects_list_before)

        # if an object was named in order to do appending then fix name
        if test_obj is not None:
            test_obj.name = search_name

    bpy.ops.object.mode_set(mode=old_3dview_mode)

def get_mod_verts(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    object_eval = obj.evaluated_get(depsgraph)
    obj_mod_mesh = bpy.data.meshes.new_from_object(object_eval)
    verts = [Vector([v.co.x, v.co.y, v.co.z]) for v in obj_mod_mesh.vertices]
    bpy.data.meshes.remove(obj_mod_mesh)
    return verts

# return list of (base_mesh_vert_index, modified_mesh_vert_index) tuples
def get_vert_matches(obj, mask_vgroup_name, mask_include):
    # create a KDTree of the base vertices, to efficiently search for overlapping verts
    base_verts = obj.data.vertices
    kd = mathutils.kdtree.KDTree(len(base_verts))
    for v in base_verts:
        kd.insert((v.co.x, v.co.y, v.co.z), v.index)
    kd.balance()
    # search the modified vertices for overlapping verts and build the "matches" list
    mod_verts = get_mod_verts(obj)
    matches = []
    i = -1
    for vco in mod_verts:
        i = i + 1
        found_list = kd.find_range(vco, FC_MATCH_DIST)
        # if none found within match distance then goto next iteration
        if len(found_list) < 1:
            continue
        found_vert_index = found_list[0][1]
        if mask_vgroup_name != "":
            mask_vgroup = obj.vertex_groups.get(mask_vgroup_name)
            if mask_vgroup is not None:
                vert_is_in_group = mask_vgroup.index in [i.group for i in obj.data.vertices[found_vert_index].groups]
                # check if vertex is needed re: mask include
                if mask_include and not vert_is_in_group:
                    continue
                # check if vertex is needed re: mask exclude
                if not mask_include and vert_is_in_group:
                    continue

        # append match tuple [base_mesh_vert_index, modified_mesh_vert_index]
        matches.append([found_vert_index, i])
    return matches

def create_single_deform_shape_key(obj, add_prefix, vert_matches, mod_verts):
    check_create_basis_shape_key(obj)
    # create a shape key
    sk = obj.shape_key_add(name=add_prefix)
    sk.interpolation = 'KEY_LINEAR'
    # modify shape key vertex positions to match modified (deformed) mesh
    for base_v_index, mod_v_index in vert_matches:
        sk.data[base_v_index].co.x = mod_verts[mod_v_index].x
        sk.data[base_v_index].co.y = mod_verts[mod_v_index].y
        sk.data[base_v_index].co.z = mod_verts[mod_v_index].z
    return sk

mod_names = ['ARMATURE', 'CAST', 'CURVE', 'DISPLACE', 'HOOK', 'LAPLACIANDEFORM', 'LATTICE', 'MESH_DEFORM',
    'SHRINKWRAP', 'SIMPLE_DEFORM', 'SMOOTH',
    'CORRECTIVE_SMOOTH', 'LAPLACIANSMOOTH', 'SURFACE_DEFORM', 'WARP', 'WAVE',
    'VOLUME_DISPLACE', 'CLOTH', 'EXPLODE', 'OCEAN', 'SOFT_BODY']

def is_deform_modifier(mod):
    if mod is not None and any(mod.type in mn for mn in mod_names):
        return True
    return False

def do_simple_bind(obj, add_prefix, start_frame_num, end_frame_num, animate_keys, append_frame_to_name,
    vert_matches):
    # create shape keys in the "deform" frames
    for frame in range(start_frame_num, end_frame_num+1):
        bpy.context.scene.frame_set(frame)
        mod_verts = get_mod_verts(obj)
        prefix = add_prefix
        if append_frame_to_name:
            prefix = prefix + str(frame).zfill(4)
        sk = create_single_deform_shape_key(obj, prefix, vert_matches, mod_verts)
        # if animating keys then add keyframes before and after the current frame with value = 0, and
        # add keyframe on current frame with value = 1
        if animate_keys:
            # switch the shapekey for it's key_blocks counter-part, so that keyframes will insert correctly
            sk = obj.data.shape_keys.key_blocks[sk.name]
            # set values and insert keyframes
            sk.value = 0
            sk.keyframe_insert(data_path='value', frame=frame-1)
            sk.keyframe_insert(data_path='value', frame=frame+1)
            sk.value = 1
            sk.keyframe_insert(data_path='value', frame=frame)

def do_dynamic_bind(obj, add_prefix, start_frame_num, end_frame_num, animate_keys, append_frame_to_name,
    vert_matches, extra_accuracy):
    # create a shape key for each axis, with offset of +1.0 along respective axis
    check_create_basis_shape_key(obj)
    sk_x = obj.shape_key_add(name=SC_TEMP_SK_X)
    sk_x.interpolation = 'KEY_LINEAR'
    for v in sk_x.data:
        v.co.x = v.co.x + 1.0

    sk_y = obj.shape_key_add(name=SC_TEMP_SK_Y)
    sk_y.interpolation = 'KEY_LINEAR'
    for v in sk_y.data:
        v.co.y = v.co.y + 1.0

    sk_z = obj.shape_key_add(name=SC_TEMP_SK_Z)
    sk_z.interpolation = 'KEY_LINEAR'
    for v in sk_z.data:
        v.co.z = v.co.z + 1.0

    obj.show_only_shape_key = False

    for frame in range(start_frame_num, end_frame_num+1):
        # go to current frame
        bpy.context.scene.frame_set(frame)

        # get target deformation points
        deformed_cos = get_mod_verts(obj)

        # temporarily mute visibility of the deform modifiers, except ARMATURE modifiers
        muted_deform_mods = []
        for mod in obj.modifiers:
            if mod.type != 'ARMATURE' and is_deform_modifier(mod):
                # save the visiblity states of the modifier
                muted_deform_mods.append([mod, mod.show_viewport, mod.show_render])
                # mute the deform modifier
                mod.show_viewport = False
                mod.show_render = False

        # temporarily mute visibility of any active shape keys if the object has shape keys,
        # and more then a 'Basis' key ...
        muted_sk = []
        if obj.data.shape_keys is not None and len(obj.data.shape_keys.key_blocks) > 1:
            for sk in obj.data.shape_keys.key_blocks:
                # if Shape Key is not the Basis key and it is not muted then mute it and remember to restore
                if sk.name != 'Basis' and not sk.mute and sk.name not in (sk_x.name, sk_y.name, sk_z.name):
                    muted_sk.append(sk)
                    sk.mute = True

        # get baseline vertice.co values after ARMATURE MODIFIERS, and before axis shape keys
        basis_cos = get_mod_verts(obj)

        # get x-offset vertice.co values
        sk_x.value = 1.0
        key_x_cos = get_mod_verts(obj)
        sk_x.value = 0.0
        # get y-offset vertice.co values
        sk_y.value = 1.0
        key_y_cos = get_mod_verts(obj)
        sk_y.value = 0.0
        # get z-offset vertice.co values
        sk_z.value = 1.0
        key_z_cos = get_mod_verts(obj)
        sk_z.value = 0.0

        deform_mats = [ np_array(
            [np_subtract(key_x_cos[i], basis_cos[i]),
            np_subtract(key_y_cos[i], basis_cos[i]),
            np_subtract(key_z_cos[i], basis_cos[i])])
            for i in range(len(basis_cos)) ]
        # release references and free memory
        key_x_cos = None
        key_y_cos = None
        key_z_cos = None

        prefix = add_prefix
        if append_frame_to_name:
            prefix = prefix + str(frame).zfill(4)
        sk_offsets = obj.shape_key_add(name=prefix)
        sk_offsets.interpolation = 'KEY_LINEAR'
        for base_v_index, mod_v_index in vert_matches:
            skv = sk_offsets.data[base_v_index]
            d_offset = np_subtract(deformed_cos[mod_v_index], basis_cos[mod_v_index])
            # apply change of basis matrix to deformed offset
            d_offset = deform_mats[mod_v_index].dot(d_offset)
            skv.co.x = skv.co.x + d_offset[0]
            skv.co.y = skv.co.y + d_offset[1]
            skv.co.z = skv.co.z + d_offset[2]

        for i in range(extra_accuracy):
            sk_offsets.value = 1.0
            key_test_cos = get_mod_verts(obj)
            sk_offsets.value = 0.0
            for base_v_index, mod_v_index in vert_matches:
                skv = sk_offsets.data[base_v_index]
                d_offset = np_subtract(deformed_cos[mod_v_index], key_test_cos[mod_v_index])
                d_offset = deform_mats[mod_v_index].dot(d_offset)
                skv.co.x = skv.co.x + d_offset[0]
                skv.co.y = skv.co.y + d_offset[1]
                skv.co.z = skv.co.z + d_offset[2]

        if animate_keys:
            # switch the shapekey for it's key_blocks counter-part, so that keyframes will insert correctly
            sk_offsets = obj.data.shape_keys.key_blocks[sk_offsets.name]
            # set values and insert keyframes
            sk_offsets.value = 0
            sk_offsets.keyframe_insert(data_path='value', frame=frame-1)
            sk_offsets.keyframe_insert(data_path='value', frame=frame+1)
            sk_offsets.value = 1
            sk_offsets.keyframe_insert(data_path='value', frame=frame)

        # restore the visibility muted shape keys
        for sk in muted_sk:
            sk.mute = False

        # restore the visibility muted deform modifiers
        for mod, show_v, show_r  in muted_deform_mods:
            mod.show_viewport = show_v
            mod.show_render = show_r

    obj.shape_key_remove(sk_x)
    obj.shape_key_remove(sk_y)
    obj.shape_key_remove(sk_z)

def do_bake_deform_shape_keys(context, obj, add_prefix, bind_frame_num, start_frame_num, end_frame_num, animate_keys,
    append_frame_to_name, is_dynamic, extra_accuracy, mask_vgroup_name, mask_include):
    old_current_frame = context.scene.frame_current

    # before binding, temporarily mute visibility of deform modifiers
    muted_deform_mods = []
    for mod in obj.modifiers:
        if is_deform_modifier(mod):
            # save visiblity states of modifier
            muted_deform_mods.append([mod, mod.show_viewport, mod.show_render])
            # mute deform modifier
            mod.show_viewport = False
            mod.show_render = False

    # before binding, temporarily mute visibility of any active shape keys
    # if object has shape keys, and more then a 'Basis' key ...
    muted_sk = []
    if obj.data.shape_keys is not None and len(obj.data.shape_keys.key_blocks) > 1:
        for sk in obj.data.shape_keys.key_blocks:
            # if Shape Key is not Basis key and it is not muted then mute it and remember to restore
            if sk.name != 'Basis' and not sk.mute:
                muted_sk.append(sk)
                sk.mute = True

    # get "bind" vert matches, by location, in bind frame
    context.scene.frame_set(bind_frame_num)
    vert_matches = get_vert_matches(obj, mask_vgroup_name, mask_include)
    print("do_bake_deform_shape_keys(): Bind vertex count = " + str(len(vert_matches)))

    # after binding, restore visibility of muted shape keys
    for sk in muted_sk:
        sk.mute = False

    # after binding, restore visibility of muted deform modifiers
    for mod, show_v, show_r  in muted_deform_mods:
        mod.show_viewport = show_v
        mod.show_render = show_r

    if is_dynamic:
        do_dynamic_bind(obj, add_prefix, start_frame_num, end_frame_num, animate_keys, append_frame_to_name,
            vert_matches, extra_accuracy)
    else:
        do_simple_bind(obj, add_prefix, start_frame_num, end_frame_num, animate_keys, append_frame_to_name,
            vert_matches)

    context.scene.frame_set(old_current_frame)

def copy_eval_bmesh_to_verts(context, from_ob, to_mesh):
    # get 'from_ob' vertice locations, with modifiers applied (local space)
    depsgraph = context.evaluated_depsgraph_get()
    bm = bmesh.new()
    bm.from_object(from_ob, depsgraph)
    bm.verts.ensure_lookup_table()
    # check if ShapeKeys are used, and select vertex data output
    active_sk_index = from_ob.active_shape_key_index
    vert_data = None
    if to_mesh.shape_keys != None and active_sk_index < len(to_mesh.shape_keys.key_blocks):
        vert_data = to_mesh.shape_keys.key_blocks[active_sk_index].data
    # use Mesh vertices if ShapeKey data output is not available
    if vert_data is None:
        vert_data = to_mesh.vertices
    # copy locations of bmesh vertices to output
    bm_vert_len = len(bm.verts)
    vert_data_len = len(vert_data)
    for i, v in enumerate(bm.verts):
        # exit loop if index out of range for original vertices
        if i >= vert_data_len:
            break
        vert_data[i].co = v.co
    bm.free()
    if i >= vert_data_len:
        return "Modified mesh vertex count greater than original mesh vertex count, (modified, original) = (%i, %i)" \
            % (bm_vert_len, vert_data_len)
    return None

def apply_modifier_sk(context, mesh_ob):
    original_mesh = mesh_ob.data
    # save state of original Object properties
    original_mesh_settings = {}
    if original_mesh.shape_keys != None:
        if original_mesh.shape_keys.use_relative:
            original_mesh_settings["shape_keys.use_relative"] = True
        original_mesh_settings["active_shape_key_index"] = mesh_ob.active_shape_key_index
        original_mesh_settings["add_rest_position_attribute"] = mesh_ob.add_rest_position_attribute
        original_mesh_settings["show_only_shape_key"] = mesh_ob.show_only_shape_key
    # save selected state of all Objects
    sel_ob_names = [ ob.name for ob in bpy.data.objects if ob.select_get() ]
    for ob in bpy.data.objects:
        ob.select_set(False)
    # create new Object with same mesh as original Object
    dup_mesh_ob = bpy.data.objects.new("TempObject", mesh_ob.data)
    context.scene.collection.objects.link(dup_mesh_ob)
    # select only 'dup_mesh_ob' and duplicate it, which will duplicate the Mesh as well
    dup_mesh_ob.select_set(True)
    # get old names list, duplicate object, and check new object names against old to get new object
    old_ob_names = [ ob.name for ob in bpy.data.objects ]
    bpy.ops.object.duplicate(linked=False)
    temp_mesh_ob = [ ob for ob in bpy.data.objects if ob.name not in old_ob_names ][0]
    # remove all animation data from duplicate Mesh, so ShapeKey properties can be modified easily (Drivers on
    # some properties could cause problems)
    dup_mesh = temp_mesh_ob.data
    if dup_mesh.shape_keys != None:
        dup_mesh.shape_keys.animation_data_clear()
    # move duplicated Mesh to original Object
    mesh_ob.data = dup_mesh
    # set ShapeKey to Basis, if any
    if original_mesh.shape_keys != None:
        original_mesh.shape_keys.use_relative = False
        dup_mesh.shape_keys.use_relative = False
        dup_mesh_ob.active_shape_key_index = 0
        dup_mesh_ob.add_rest_position_attribute = False
        dup_mesh_ob.show_only_shape_key = True
        mesh_ob.active_shape_key_index = 0
        mesh_ob.add_rest_position_attribute = False
        mesh_ob.show_only_shape_key = True
    # copy Basis
    ret_msg = copy_eval_bmesh_to_verts(context, mesh_ob, original_mesh)
    # copy other ShapeKeys, if any
    if mesh_ob.data.shape_keys != None:
        for index in range(len(mesh_ob.data.shape_keys.key_blocks) - 1):
            dup_mesh_ob.active_shape_key_index = index + 1
            mesh_ob.active_shape_key_index = index + 1
            msg = copy_eval_bmesh_to_verts(context, mesh_ob, original_mesh)
            if msg != None:
                ret_msg = msg
    # restore original Mesh to original Object
    mesh_ob.data = original_mesh
    # delete temp Object
    bpy.data.objects.remove(temp_mesh_ob)
    # delete dup mesh Object
    bpy.data.objects.remove(dup_mesh_ob)
    # restore selected state of all Objects
    for ob_name in sel_ob_names:
        ob = bpy.data.objects.get(ob_name)
        if ob != None:
            ob.select_set(True)
    # restore state of original Object properties
    if original_mesh.shape_keys != None:
        if original_mesh_settings.get("shape_keys.use_relative") == True:
            original_mesh.shape_keys.use_relative = True
        mesh_ob.active_shape_key_index = original_mesh_settings["active_shape_key_index"]
        mesh_ob.add_rest_position_attribute = original_mesh_settings["add_rest_position_attribute"]
        mesh_ob.show_only_shape_key = original_mesh_settings["show_only_shape_key"]
    # returns None if no error occurred, or string with error message
    return ret_msg
