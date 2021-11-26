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
#
# Automate MakeHuman 2 Blender (AMH2B)
#   Blender 2.79 - 2.93 Addon
# A set of tools to automate the process of shading/texturing, and animating MakeHuman data imported in Blender.

import bpy
from bpy_extras.io_utils import ImportHelper
import re
import mathutils
from mathutils import Vector
import numpy

from .append_from_file_func import *
from .const import *
from .object_func import *
from .template import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
else:
    from .imp_v28 import *

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


class AMH2B_SKFuncDelete(bpy.types.Operator):
    """With selected MESH type objects, delete shape keys by prefix"""
    bl_idname = "amh2b.sk_func_delete"
    bl_label = "Delete Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        delete_prefix = context.scene.Amh2bPropSK_FunctionPrefix
        do_sk_func_delete(context.selected_objects, delete_prefix)
        return {'FINISHED'}

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

def copy_shapekeys_by_name_prefix(src_obj, dest_objects, copy_prefix, adapt_size):
    if src_obj.data.shape_keys is None:
        return

    # keep src_object selected throughout for loop, only switching dest_object select on and off
    select_object(src_obj)
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
        select_object(dest_obj)
        set_active_object(dest_obj)
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
                delta_loc = numpy.subtract(sk_loc, original_loc)
                dest_obj.data.shape_keys.key_blocks[sk_index].data[v_index].co = (v_scale * delta_loc[0] + original_loc[0],
                    v_scale * delta_loc[1] + original_loc[1], v_scale * delta_loc[2] + original_loc[2])

        deselect_object(dest_obj)
        # bpy.ops.object.shape_key_transfer will set show_only_shape_key to true, so reset to previous value
        dest_obj.show_only_shape_key = show_temp

    deselect_object(src_obj)

def do_copy_shape_keys(src_object, dest_objects, copy_prefix, adapt_size):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # de-select all objects because copying shape keys requires bpy.ops.object.shape_key_transfer,
    # and this requires exactly two specific objects be selected per shape key copy
    bpy.ops.object.select_all(action='DESELECT')

    copy_shapekeys_by_name_prefix(src_object, dest_objects, copy_prefix, adapt_size)
    bpy.ops.object.mode_set(mode=old_3dview_mode)

# TODO copy animation keyframes too
class AMH2B_SKFuncCopy(bpy.types.Operator):
    """With active object, copy shape keys by prefix to all other selected objects"""
    bl_idname = "amh2b.sk_func_copy"
    bl_label = "Copy Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        copy_prefix = context.scene.Amh2bPropSK_FunctionPrefix
        ob_act = context.active_object
        if ob_act is None or ob_act.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        if ob_act.data.shape_keys is None or len(ob_act.data.shape_keys.key_blocks) < 2:
            self.report({'ERROR'}, "Active object does not have enough shape keys to be copied")
            return {'CANCELLED'}

        other_obj_list = [ob for ob in context.selected_editable_objects if ob.type == 'MESH' and ob != ob_act]
        if len(other_obj_list) < 1:
            self.report({'ERROR'}, "No meshes were selected to receive copied shape keys")
            return {'CANCELLED'}

        do_copy_shape_keys(ob_act, other_obj_list, copy_prefix, context.scene.Amh2bPropSK_AdaptSize)
        return {'FINISHED'}

def get_mod_verts(obj):
    obj_mod_mesh = get_mesh_post_modifiers(obj)
    verts = [Vector([v.co.x, v.co.y, v.co.z]) for v in obj_mod_mesh.vertices]
    bpy.data.meshes.remove(obj_mod_mesh)
    return verts

def get_vert_matches(obj):
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

        # append match tuple [base_mesh_vert_index, modified_mesh_vert_index]
        matches.append([found_list[0][1], i])

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
    # create a shape key for each axis, with offsets of +1.0 in for respective axis
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

        deform_mats = [ numpy.array(
            [numpy.subtract(key_x_cos[i], basis_cos[i]),
            numpy.subtract(key_y_cos[i], basis_cos[i]),
            numpy.subtract(key_z_cos[i], basis_cos[i])])
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
            d_offset = numpy.subtract(deformed_cos[mod_v_index], basis_cos[mod_v_index])
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
                d_offset = numpy.subtract(deformed_cos[mod_v_index], key_test_cos[mod_v_index])
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

def do_bake_deform_shape_keys(obj, add_prefix, bind_frame_num, start_frame_num, end_frame_num, animate_keys,
    append_frame_to_name, is_dynamic, extra_accuracy):
    old_current_frame = bpy.context.scene.frame_current

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
    bpy.context.scene.frame_set(bind_frame_num)
    vert_matches = get_vert_matches(obj)
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

    bpy.context.scene.frame_set(old_current_frame)

class AMH2B_BakeDeformShapeKeys(bpy.types.Operator):
    """Bake active object's mesh deformations to shape keys"""
    bl_idname = "amh2b.sk_bake_deform_shape_keys"
    bl_label = "Bake Deform Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        scn = context.scene
        if scn.Amh2bPropSK_DeformShapeKeyPrefix == '':
            self.report({'ERROR'}, "Shape key name prefix (add_prefix) is blank")
            return {'CANCELLED'}
        if scn.Amh2bPropSK_StartFrame > scn.Amh2bPropSK_EndFrame:
            self.report({'ERROR'}, "Start Frame number is higher than End Frame number")
            return {'CANCELLED'}

        do_bake_deform_shape_keys(act_ob, scn.Amh2bPropSK_DeformShapeKeyPrefix, scn.Amh2bPropSK_BindFrame,
            scn.Amh2bPropSK_StartFrame, scn.Amh2bPropSK_EndFrame, scn.Amh2bPropSK_Animate,
            scn.Amh2bPropSK_AddFrameToName, scn.Amh2bPropSK_Dynamic, scn.Amh2bPropSK_ExtraAccuracy)
        return {'FINISHED'}

def do_deform_sk_view_toggle(act_ob):
    # save original sk_view_active state by checking all modifiers for an armature with
    # AutoCuts vertex group; if any found then the view state is "on";
    # also the view state is "on" if any cloth or soft body sims have their viewport view set to visible
    sk_view_active = False
    for mod in act_ob.modifiers:
        if mod.type == 'ARMATURE' and mod.vertex_group == SC_VGRP_MASKOUT:
            sk_view_active = True
        elif (mod.type == 'CLOTH' or mod.type == 'SOFT_BODY') and mod.show_viewport == False:
            sk_view_active = True

    # based on original view state, do toggle
    for mod in act_ob.modifiers:
        if mod.type == 'ARMATURE' and (mod.vertex_group == SC_VGRP_MASKOUT or mod.vertex_group == ""):
            if sk_view_active:
                mod.vertex_group = ""
            else:
                mod.vertex_group = SC_VGRP_MASKOUT
                mod.invert_vertex_group = False
        elif mod.type == 'CLOTH' or mod.type == 'SOFT_BODY':
            mod.show_viewport = sk_view_active
            mod.show_render = sk_view_active

class AMH2B_DeformSK_ViewToggle(bpy.types.Operator):
    """Toggle visibility between shape keys and cloth/soft body sims on active object.\nIntended only for non-Dynamic deform shape keys"""
    bl_idname = "amh2b.sk_deform_sk_view_toggle"
    bl_label = "Deform SK View Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        do_deform_sk_view_toggle(act_ob)
        return {'FINISHED'}

def do_search_file_for_auto_sk(sel_obj_list, chosen_blend_file, name_prefix, adapt_size, swap_autoname_ext):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # copy list of selected objects, minus the active object
    selection_list = [ob for ob in sel_obj_list if ob.type == 'MESH']

    # keep a list of all objects in the Blend file, before objects are appended
    all_objects_list_before = get_all_objects_list()

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
            select_object(ob)

        # appended object may have pulled in other objects as dependencies, so delete all appended objects
        delete_all_objects_except(all_objects_list_before)

        # if an object was named in order to do appending then fix name
        if test_obj is not None:
            test_obj.name = search_name

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_SearchFileForAutoShapeKeys(AMH2B_SearchInFileInner, bpy.types.Operator, ImportHelper):
    """For each selected MESH object: Search another file automatically and try to copy shape keys based on Prefix and object name.\nNote: Name of object from MHX import process is used to search for object in other selected file"""
    bl_idname = "amh2b.sk_search_file_for_auto_sk"
    bl_label = "Copy from File"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        do_search_file_for_auto_sk(context.selected_objects, self.filepath, scn.Amh2bPropSK_FunctionPrefix,
            scn.Amh2bPropSK_AdaptSize, scn.Amh2bPropSK_SwapAutonameExt)
        return {'FINISHED'}
