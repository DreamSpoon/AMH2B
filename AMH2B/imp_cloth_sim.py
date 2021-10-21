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
#   Blender 2.xx Addon (tested and works with Blender 2.79b, 2.83, 2.93)
# A set of tools to automate the process of shading/texturing, and animating MakeHuman data imported in Blender.

import bpy
import os
import re
import mathutils
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper

from .imp_const import *
from .imp_object_func import *
from .imp_vgroup_func import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

def do_add_cuts_mask():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_add_cuts_mask() error: Active Object is not a MESH. Select a MESH object and try again.")
        return

    active_obj = bpy.context.active_object

    # add the AutoCuts vertex group if it does not exist
    add_ifnot_vertex_grp(active_obj, SC_VGRP_CUTS)
    v_grp = active_obj.vertex_groups.get(SC_VGRP_CUTS)

    # prevent duplicate masks: check for cuts mask in modifiers stack and quit if found
    for mod in active_obj.modifiers:
        if mod.type == 'MASK' and mod.vertex_group == SC_VGRP_CUTS:
            return

    # add mask modifier and set it
    mod = active_obj.modifiers.new("AutoCuts Mask", 'MASK')
    if mod is None:
        print("do_add_cuts_mask() error: Unable to add MASK modifier to object" + active_obj.name)
        return
    mod.vertex_group = v_grp.name
    mod.invert_vertex_group = True
    # move modifier to top of stack
    while active_obj.modifiers.find(mod.name) != 0:
        bpy.ops.object.modifier_move_up({"object": active_obj}, modifier=mod.name)

class AMH2B_AddCutsMask(bpy.types.Operator):
    """Add Mask modifier to implement AutoCuts, adding AutoCuts vertex group to active object if needed"""
    bl_idname = "amh2b.add_cuts_mask"
    bl_label = "Add Cuts Mask"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_add_cuts_mask()
        return {'FINISHED'}

def do_toggle_view_cuts_mask():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_toggle_view_cuts_mask() error: Active Object is not a MESH. Select a MESH object and try again.")
        return

    active_obj = bpy.context.active_object

    # find the cuts mask in the stack
    for mod in active_obj.modifiers:
        if mod.type == 'MASK' and mod.vertex_group == SC_VGRP_CUTS:
            # toggle and ensure that viewport and render visibility are the same
            mod.show_viewport = not mod.show_viewport
            mod.show_render = mod.show_viewport
            return

class AMH2B_ToggleViewCutsMask(bpy.types.Operator):
    """Toggle the visibility of the Cuts mask modifier, in viewport and render"""
    bl_idname = "amh2b.toggle_view_cuts_mask"
    bl_label = "Toggle View Cuts Mask"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_toggle_view_cuts_mask()
        return {'FINISHED'}

def do_copy_vertex_groups_by_prefix(vg_name_prefix):
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_copy_vertex_groups_by_prefix() error: active object was not a MESH. Select a MESH and try again.")
        return
    if len(bpy.context.selected_objects) < 2:
        print("do_copy_vertex_groups_by_prefix() error: less then 2 objects selected. Select another mesh and try again.")
        return

    from_mesh_obj = bpy.context.active_object
    selection_list = bpy.context.selected_objects
    # iterate over selected 'MESH' type objects that are not the active object
    for to_mesh_obj in (x for x in selection_list if x.type == 'MESH' and x != from_mesh_obj):
        copy_vgroups_by_name_prefix(from_mesh_obj, to_mesh_obj, vg_name_prefix)

class AMH2B_CopyVertexGroupsByPrefix(bpy.types.Operator):
    """Copy vertex groups by name prefix from the active object (must be selected last) to all other selected mesh objects.\nObject does not need to be 'searchable' """
    bl_idname = "amh2b.copy_vertex_groups_by_prefix"
    bl_label = "Copy VGroups by Prefix"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_copy_vertex_groups_by_prefix(bpy.context.scene.Amh2bPropVGCopyNamePrefix)
        return {'FINISHED'}

def do_make_tailor_vgroups():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_make_tailor_vgroups() error: active object was not a MESH. Select a MESH and try again.")
        return

    active_obj = bpy.context.active_object
    add_ifnot_vertex_grp(active_obj, SC_VGRP_CUTS)
    add_ifnot_vertex_grp(active_obj, SC_VGRP_PINS)

class AMH2B_MakeTailorGroups(bpy.types.Operator):
    """Add AutoCuts and AutoPins vertex groups to the active object, only if these groups don't already exist"""
    bl_idname = "amh2b.make_tailor_groups"
    bl_label = "Make Cut & Pin Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_make_tailor_vgroups()
        return {'FINISHED'}

def get_tailor_object_name(object_name):
    if object_name.rfind(":") != -1:
        return object_name[object_name.rfind(":")+1 : len(object_name)]
    else:
        return object_name

def do_rename_tailor_object_to_searchable():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_rename_tailor_object_to_searchable() error: Active Object is not MESH type. Select only one MESH object and try again.")
        return
    bpy.context.active_object.name = get_tailor_object_name(bpy.context.active_object.name)

class AMH2B_MakeTailorObjectSearchable(bpy.types.Operator):
    """Rename active object, if needed, to make it searchable re:\nAutomatic search of file for vertex groups by object name and vertex group name prefix"""
    bl_idname = "amh2b.make_tailor_object_searchable"
    bl_label = "Make Object Searchable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_rename_tailor_object_to_searchable()
        return {'FINISHED'}

# Returns True if material was successfully appended.
# Checks if the material already exists in this file, if it does exist then rename the
# current material, and then append the new material.
def append_object_from_blend_file(mat_filepath, obj_name):
    # path inside of file (i.e. like opening the "Append" window; see Action, Armature, Brush, Camera, ...)
    inner_path = "Object"

    try:
        bpy.ops.wm.append(
            filepath=os.path.join(mat_filepath, inner_path, obj_name),
            directory=os.path.join(mat_filepath, inner_path),
            filename=obj_name
            )
    except:
        return False

    if bpy.data.objects.get(obj_name) is None:
        return False

    return True

def do_search_file_for_auto_vgroups(chosen_blend_file, name_prefix):
    bpy.ops.object.mode_set(mode='OBJECT')

    # copy list of selected objects, minus the active object
    selection_list = []
    for ob in bpy.context.selected_objects:
        if ob.type == 'MESH':
            selection_list.append(bpy.data.objects[ob.name])
    bpy.ops.object.select_all(action='DESELECT')

    for sel in selection_list:
        search_name = get_tailor_object_name(sel.name)
        # if the desired VGroups mesh object name is already used then rename it before appending from file,
        # and rename later after the appended object is deleted
        test_obj = bpy.data.objects.get(search_name)
        if test_obj is not None:
            test_obj.name = "TempRenameName"

        # if cannot load mesh object from file...
        append_object_from_blend_file(chosen_blend_file, search_name)
        appended_obj = bpy.data.objects.get(search_name)
        if appended_obj is None:
            # if rename occurred, then undo rename
            if test_obj is not None:
                test_obj.name = search_name

            continue

        #do_inner_copy_sew_pattern(appended_obj, [sel])
        #do_inner_copy_tailor_vgroups(appended_obj, [sel])
        copy_vgroups_by_name_prefix(appended_obj, sel, name_prefix)

        # delete the following 2 commented lines:
        ## select only the appended object and delete it
        ##select_object(appended_obj)

        # all objects were deselected before starting this loop,
        # and any objects currently selected could only have come from the append process,
        # so delete all selected objects
        bpy.ops.object.delete()

        # if an object was named in order to do appending then fix name
        if test_obj is not None:
            test_obj.name = search_name

class AMH2B_SearchFileForAutoVGroups(AMH2B_SearchFileForAutoVGroupsInner, bpy.types.Operator, ImportHelper):
    """For each selected MESH object: Search another file automatically and try to copy vertex groups based on Prefix and object name.\nNote: Name of object from MHX import process is used to search for object in user selected file"""
    bl_idname = "amh2b.search_file_for_auto_vgroups"
    bl_label = "From File"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        do_search_file_for_auto_vgroups(self.filepath, bpy.context.scene.Amh2bPropVGCopyNamePrefix)
        return {'FINISHED'}

def do_add_cloth_sim():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_add_cloth_sim() error: Active Object must be a mesh.")
        return
    mesh_obj = bpy.context.active_object
    original_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    mod = mesh_obj.modifiers.new("Cloth", 'CLOTH')
    if mod is None:
        print("do_add_cloth_sim() error: Unable to add CLOTH modifier to object" + mesh_obj.name)
        return

    mod.settings.use_dynamic_mesh = True

    vert_grp = mesh_obj.vertex_groups.get(SC_VGRP_PINS)
    if vert_grp is not None:
        cloth_sim_use_pin_group(mod, vert_grp.name)

    vert_grp = mesh_obj.vertex_groups.get(SC_VGRP_TSEWN)
    if vert_grp is not None:
        cloth_sim_use_sew_group(mod, vert_grp.name)

    bpy.ops.object.mode_set(mode=original_mode)

class AMH2B_AddClothSim(bpy.types.Operator):
    """Add CLOTH modifer to active object with settings auto-filled for Pinning"""
    bl_idname = "amh2b.add_cloth_sim"
    bl_label = "Add Cloth Sim"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_add_cloth_sim()
        return {'FINISHED'}

def get_mod_verts_edges(obj):
    obj_mod_mesh = get_mesh_post_modifiers(obj)
    verts = [Vector([v.co.x, v.co.y, v.co.z]) for v in obj_mod_mesh.vertices]
    edges = obj_mod_mesh.edge_keys
    bpy.data.meshes.remove(obj_mod_mesh)
    return verts, edges

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

def check_create_basis_shape_key(obj):
    if obj.data.shape_keys is None:
        sk_basis = obj.shape_key_add(name='Basis')
        sk_basis.interpolation = 'KEY_LINEAR'

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

mod_names = ['ARMATURE', 'CAST', 'CURVE', 'DISPLACE', 'HOOK', 'LAPLACIANDEFORM', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP', 'SIMPLE_DEFORM', 'SMOOTH', 'CORRECTIVE_SMOOTH', 'LAPLACIANSMOOTH', 'SURFACE_DEFORM', 'WARP', 'WAVE', 'VOLUME_DISPLACE', 'CLOTH', 'EXPLODE', 'OCEAN', 'SOFT_BODY']

def is_deform_modifier(mod):
    if mod is not None and any(mod.name in mn for mn in mod_names):
        return True
    return False

def create_deform_shapekeys(obj, add_prefix, bind_frame_num, start_frame_num, end_frame_num, animate_keys):
    old_current_frame = bpy.context.scene.frame_current

    # before binding, temporarily mute visibility of the deform modifiers
    muted_deform_mods = []
    for mod in obj.modifiers:
        if is_deform_modifier(mod):
            # save the visiblity states of the modifier
            muted_deform_mods.append([mod, mod.show_viewport, mod.show_render])
            # mute the deform modifier
            mod.show_viewport = False
            mod.show_render = False

    # before binding, temporarily mute visibility of any active shape keys
    # if the object has shape keys, and more then a 'Basis' key ...
    muted_sk = []
    if obj.data.shape_keys is not None and len(obj.data.shape_keys.key_blocks) > 1:
        for sk in obj.data.shape_keys.key_blocks:
            # if Shape Key is not the Basis key and it is not muted then mute it and remember to restore
            if sk.name != 'Basis' and not sk.mute:
                muted_sk.append(sk)
                sk.mute = True

    # get "bind" vert matches in the bind frame
    bpy.context.scene.frame_set(bind_frame_num)
    vert_matches = get_vert_matches(obj)
    print("do_bake_deform_shape_keys(): Bind vertex count = " + str(len(vert_matches)))

    # after binding, restore the visibility muted shape keys
    for sk in muted_sk:
        sk.mute = False

    # after binding, restore the visibility muted deform modifiers
    for mod, show_v, show_r  in muted_deform_mods:
        mod.show_viewport = show_v
        mod.show_render = show_r

    # create shape keys in the "deform" frames
    for f in range(start_frame_num, end_frame_num+1):
        bpy.context.scene.frame_set(f)
        mod_verts = get_mod_verts(obj)
        sk = create_single_deform_shape_key(obj, add_prefix, vert_matches, mod_verts)
        if animate_keys:
            sk.value = 0
            sk.keyframe_insert(data_path='value', frame=f-1)
            sk.keyframe_insert(data_path='value', frame=f+1)
            sk.value = 1
            sk.keyframe_insert(data_path='value', frame=f)

    bpy.context.scene.frame_set(old_current_frame)

def do_bake_deform_shape_keys(add_prefix, bind_frame_num, start_frame_num, end_frame_num, animate_keys):
    if add_prefix == '':
        print("do_bake_deform_shape_keys() error: Shape key name prefix (add_prefix) is blank.")
        return
    if start_frame_num > end_frame_num:
        print("do_bake_deform_shape_keys() error: Start Frame number is higher than End Frame number.")
        return
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_bake_deform_shape_keys() error: Active Object must be a mesh.")
        return

    create_deform_shapekeys(bpy.context.active_object, add_prefix, bind_frame_num, start_frame_num, end_frame_num, animate_keys)

class AMH2B_BakeDeformShapeKeys(bpy.types.Operator):
    """Bake active object's mesh deformations to shape keys"""
    bl_idname = "amh2b.bake_deform_shape_keys"
    bl_label = "Bake Deform Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_bake_deform_shape_keys(bpy.context.scene.Amh2bPropDeformShapeKeyAddPrefix, bpy.context.scene.Amh2bPropDSK_BindFrame, bpy.context.scene.Amh2bPropDSK_StartFrame, bpy.context.scene.Amh2bPropDSK_EndFrame, bpy.context.scene.Amh2bPropDSK_AnimateSK)
        return {'FINISHED'}

def is_dsk_name(name, delete_prefix):
    if name == delete_prefix or re.match(delete_prefix + "\.\w*", name):
        return True
    else:
        return False

def delete_deform_shapekeys(obj, delete_prefix):
    if obj.data.shape_keys is None or obj.data.shape_keys.key_blocks is None:
        return
    for sk in obj.data.shape_keys.key_blocks:
        if is_dsk_name(sk.name, delete_prefix):
            obj.shape_key_remove(sk)

def do_delete_deform_shape_keys(delete_prefix):
    if delete_prefix == '':
        print("do_delete_deform_shape_keys() error: Shape key name prefix (delete_prefix) is blank.")
        return
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_delete_deform_shape_keys() error: Active Object must be a mesh.")
        return

    delete_deform_shapekeys(bpy.context.active_object, delete_prefix)

class AMH2B_DeleteDeformShapeKeys(bpy.types.Operator):
    """Delete mesh deformations shape keys from active object"""
    bl_idname = "amh2b.delete_deform_shape_keys"
    bl_label = "Delete Deform Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_delete_deform_shape_keys(bpy.context.scene.Amh2bPropDeformShapeKeyDeletePrefix)
        return {'FINISHED'}

def do_deform_sk_view_toggle():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_toggle_view_cuts_mask() error: Active Object is not a MESH. Select a MESH object and try again.")
        return

    active_obj = bpy.context.active_object

    # save original sk_view_active state by checking all modifiers for an armature with
    # AutoCuts vertex group; if any found then the view state is "on";
    # also the view state is "on" if any cloth or soft body sims have their viewport view set to visible
    sk_view_active = False
    for mod in active_obj.modifiers:
        if mod.type == 'ARMATURE' and mod.vertex_group == SC_VGRP_CUTS:
            sk_view_active = True
        elif (mod.type == 'CLOTH' or mod.type == 'SOFT_BODY') and mod.show_viewport == False:
            sk_view_active = True

    if active_obj.vertex_groups.get(SC_VGRP_CUTS) is None:
        obj_has_cuts_grp = False
    else:
        obj_has_cuts_grp = True

    # based on original view state, do toggle
    for mod in active_obj.modifiers:
        if mod.type == 'ARMATURE' and (mod.vertex_group == SC_VGRP_CUTS or mod.vertex_group == ""):
            if sk_view_active:
                mod.vertex_group = ""
            else:
                mod.vertex_group = SC_VGRP_CUTS
                mod.invert_vertex_group = False
        elif mod.type == 'CLOTH' or mod.type == 'SOFT_BODY':
            mod.show_viewport = sk_view_active
            mod.show_render = sk_view_active

class AMH2B_DeformSK_ViewToggle(bpy.types.Operator):
    """Toggle visibility between shape keys and cloth/soft body sims on active object"""
    bl_idname = "amh2b.deform_sk_view_toggle"
    bl_label = "Deform SK View Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_deform_sk_view_toggle()
        return {'FINISHED'}
