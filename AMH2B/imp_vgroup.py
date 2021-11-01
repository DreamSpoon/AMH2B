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
from bpy_extras.io_utils import ImportHelper

from .imp_const import *
from .imp_vgroup_func import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

def do_add_cuts_mask(act_ob):
    # add the Auto Mask vertex group if it does not exist
    add_ifnot_vertex_grp(act_ob, SC_VGRP_CUTS)
    v_grp = act_ob.vertex_groups.get(SC_VGRP_CUTS)

    # prevent duplicate masks: check for cuts mask in modifiers stack and quit if found
    for mod in act_ob.modifiers:
        if mod.type == 'MASK' and mod.vertex_group == SC_VGRP_CUTS:
            return None

    # add mask modifier and set it
    mod = act_ob.modifiers.new("Auto Mask", 'MASK')
    if mod is None:
        return "Unable to add MASK modifier to object" + act_ob.name

    mod.vertex_group = v_grp.name
    mod.invert_vertex_group = True
    # move modifier to top of stack
    while act_ob.modifiers.find(mod.name) != 0:
        bpy.ops.object.modifier_move_up({"object": act_ob}, modifier=mod.name)

    return None

class AMH2B_AddCutsMask(bpy.types.Operator):
    """Add Mask modifier to implement AutoMaskOut, adding AutoMaskOut vertex group to active object if needed"""
    bl_idname = "amh2b.add_cuts_mask"
    bl_label = "Add MaskOut Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = bpy.context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        err_str = do_add_cuts_mask(act_ob)
        if err_str == None:
            return {'FINISHED'}

        self.report({'ERROR'}, err_str)
        return {'CANCELLED'}

def do_toggle_view_cuts_mask(act_ob):
    # find the cuts mask in the stack
    for mod in act_ob.modifiers:
        if mod.type == 'MASK' and mod.vertex_group == SC_VGRP_CUTS:
            # toggle and ensure that viewport and render visibility are the same
            mod.show_viewport = not mod.show_viewport
            mod.show_render = mod.show_viewport
            return

class AMH2B_ToggleViewCutsMask(bpy.types.Operator):
    """Toggle the visibility of the Auto Mask modifier, in viewport and render"""
    bl_idname = "amh2b.toggle_view_cuts_mask"
    bl_label = "Toggle AutoMaskOut"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = bpy.context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        do_toggle_view_cuts_mask(act_ob)
        return {'FINISHED'}

def do_copy_vertex_groups_by_prefix(from_mesh_obj, vg_name_prefix):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    selection_list = bpy.context.selected_objects
    # iterate over selected 'MESH' type objects that are not the active object
    for to_mesh_obj in (x for x in selection_list if x.type == 'MESH' and x != from_mesh_obj):
        copy_vgroups_by_name_prefix(from_mesh_obj, to_mesh_obj, vg_name_prefix)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_CopyVertexGroupsByPrefix(bpy.types.Operator):
    """Copy vertex groups by name prefix from active object (must be selected last) to all other selected mesh objects.\nObject name does not need to be 'searchable' """
    bl_idname = "amh2b.copy_vertex_groups_by_prefix"
    bl_label = "Copy Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = bpy.context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        if len(bpy.context.selected_objects) < 2:
            self.report({'ERROR'}, "Less than two objects selected")
            return {'CANCELLED'}

        do_copy_vertex_groups_by_prefix(act_ob, bpy.context.scene.Amh2bPropVGCopyNamePrefix)
        return {'FINISHED'}

def do_make_tailor_vgroups(act_ob):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    add_ifnot_vertex_grp(act_ob, SC_VGRP_CUTS)
    add_ifnot_vertex_grp(act_ob, SC_VGRP_PINS)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_MakeTailorGroups(bpy.types.Operator):
    """Add AutoMaskOut and AutoClothPin vertex groups to the active object, if these groups don't already exist"""
    bl_idname = "amh2b.make_tailor_groups"
    bl_label = "Add Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = bpy.context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        do_make_tailor_vgroups(act_ob)
        return {'FINISHED'}

def get_tailor_object_name(object_name):
    if object_name.rfind(":") != -1:
        return object_name[object_name.rfind(":")+1 : len(object_name)]
    else:
        return object_name

def do_rename_tailor_object_to_searchable(act_ob):
    act_ob.name = get_tailor_object_name(act_ob.name)

class AMH2B_MakeTailorObjectSearchable(bpy.types.Operator):
    """Rename active object, if needed, to make it searchable re:\nAutomatic search of file for vertex groups by object name and vertex group name prefix"""
    bl_idname = "amh2b.make_tailor_object_searchable"
    bl_label = "Make Object Searchable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = bpy.context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        do_rename_tailor_object_to_searchable(act_ob)
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
            selection_list.append(ob)
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
