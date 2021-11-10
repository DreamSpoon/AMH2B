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

import re
import bpy
from bpy_extras.io_utils import ImportHelper

from .append_from_file_func import *
from .const import *
from .template import *
from .vgroup_func import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

def do_add_maskout_mod(act_ob):
    # add the Auto Mask vertex group if it does not exist
    add_ifnot_vertex_grp(act_ob, SC_VGRP_MASKOUT)
    v_grp = act_ob.vertex_groups.get(SC_VGRP_MASKOUT)

    # prevent duplicate masks: check for MaskOut in modifiers stack and quit if found
    for mod in act_ob.modifiers:
        if mod.type == 'MASK' and mod.vertex_group == SC_VGRP_MASKOUT:
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

class AMH2B_AddMaskOutMod(bpy.types.Operator):
    """Add Mask modifier to implement AutoMaskOut, adding AutoMaskOut vertex group to active object if needed"""
    bl_idname = "amh2b.vg_add_maskout_modifier"
    bl_label = "Add MaskOut Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        err_str = do_add_maskout_mod(act_ob)
        if err_str == None:
            return {'FINISHED'}

        self.report({'ERROR'}, err_str)
        return {'CANCELLED'}

def do_toggle_view_maskout_mod(act_ob):
    # find the MaskOut modifier in the stack
    for mod in act_ob.modifiers:
        if mod.type == 'MASK' and mod.vertex_group == SC_VGRP_MASKOUT:
            # toggle and ensure that viewport and render visibility are the same
            mod.show_viewport = not mod.show_viewport
            mod.show_render = mod.show_viewport
            return

class AMH2B_ToggleViewMaskoutMod(bpy.types.Operator):
    """Toggle the visibility of the Auto Mask modifier, in viewport and render"""
    bl_idname = "amh2b.vg_toggle_auto_maskout"
    bl_label = "Toggle AutoMaskOut"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        do_toggle_view_maskout_mod(act_ob)
        return {'FINISHED'}

def do_copy_vertex_groups_by_prefix(from_mesh_obj, sel_obj_list, vg_name_prefix):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # iterate over selected 'MESH' type objects that are not the active object
    for to_mesh_obj in (x for x in sel_obj_list if x.type == 'MESH' and x != from_mesh_obj):
        # skip destination mesh objects with different numbers of vertices
        dvc = len(to_mesh_obj.data.vertices)
        svc = len(from_mesh_obj.data.vertices)
        if dvc != svc:
            print("do_copy_vertex_groups_by_prefix(): Cannot copy vertex groups from source ("+from_mesh_obj.name+
                ") to dest ("+to_mesh_obj.name+"), source vertex count ("+str(svc)+
                ") doesn't equal destination vertex count ("+str(dvc)+").")
            continue
        copy_vgroups_by_name_prefix(from_mesh_obj, to_mesh_obj, vg_name_prefix)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_CopyVertexGroupsByPrefix(bpy.types.Operator):
    """Copy vertex groups by name prefix from active object (must be selected last) to all other selected mesh objects.\nObject name does not need to be 'searchable' """
    bl_idname = "amh2b.vg_copy_by_prefix"
    bl_label = "Copy Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        if len(context.selected_objects) < 2:
            self.report({'ERROR'}, "Less than two objects selected")
            return {'CANCELLED'}

        do_copy_vertex_groups_by_prefix(act_ob, context.selected_objects, context.scene.Amh2bPropVG_FunctionNamePrefix)
        return {'FINISHED'}

def delete_prefixed_vertex_groups(selection_list, delete_prefix):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # iterate over selected 'MESH' type objects
    for mesh_obj in (x for x in selection_list if x.type == 'MESH'):
        delete_vgroups_by_name_prefix(mesh_obj, delete_prefix)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_DeleteVertexGroupsByPrefix(bpy.types.Operator):
    """With all selected objects, delete vertex groups by prefix"""
    bl_idname = "amh2b.vg_delete_by_prefix"
    bl_label = "Delete Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        if scn.Amh2bPropVG_FunctionNamePrefix == '':
            self.report({'ERROR'}, "Vertex group name prefix is blank")
            return {'CANCELLED'}

        delete_prefixed_vertex_groups(context.selected_objects, scn.Amh2bPropVG_FunctionNamePrefix)
        return {'FINISHED'}

def do_make_tailor_vgroups(act_ob):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    add_ifnot_vertex_grp(act_ob, SC_VGRP_MASKOUT)
    add_ifnot_vertex_grp(act_ob, SC_VGRP_CLOTH_PIN)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_MakeTailorGroups(bpy.types.Operator):
    """Add AutoMaskOut and AutoClothPin vertex groups to the active object, if these groups don't already exist"""
    bl_idname = "amh2b.vg_make_auto_vgroups"
    bl_label = "Add Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        do_make_tailor_vgroups(act_ob)
        return {'FINISHED'}

def do_search_file_for_auto_vgroups(sel_obj_list, chosen_blend_file, name_prefix, swap_autoname_ext):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # copy list of selected objects, minus the active object
    other_obj_list = []
    for ob in sel_obj_list:
        if ob.type == 'MESH':
            other_obj_list.append(ob)
    bpy.ops.object.select_all(action='DESELECT')

    for sel in other_obj_list:
        search_name = get_searchable_object_name(sel.name)
        # if the desired VGroups mesh object name is already used then rename it before appending from file,
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

        # skip destination mesh objects with different numbers of vertices
        dvc = len(sel.data.vertices)
        svc = len(appended_obj.data.vertices)
        if dvc == svc:
            copy_vgroups_by_name_prefix(appended_obj, sel, name_prefix)
        else:
            print("do_search_file_for_auto_vgroups(): Cannot copy vertex groups from source ("+appended_obj.name+
                ") to dest ("+sel.name+"), source vertex count ("+str(svc)+
                ") doesn't equal destination vertex count ("+str(dvc)+").")

        # all objects were deselected before starting this loop,
        # and any objects currently selected could only have come from the append process,
        # so delete all selected objects
        bpy.ops.object.delete()

        # if an object was named in order to do appending then fix name
        if test_obj is not None:
            test_obj.name = search_name

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_SearchFileForAutoVGroups(AMH2B_SearchInFileInner, bpy.types.Operator, ImportHelper):
    """For each selected MESH object: Search another file automatically and try to copy vertex groups based on Prefix and object name.\nNote: Name of object from MHX import process is used to search for object in other selected file"""
    bl_idname = "amh2b.vg_copy_from_file"
    bl_label = "Copy from File"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        do_search_file_for_auto_vgroups(context.selected_objects, self.filepath,
            scn.Amh2bPropVG_FunctionNamePrefix, scn.Amh2bPropVG_SwapAutonameExt)
        return {'FINISHED'}
