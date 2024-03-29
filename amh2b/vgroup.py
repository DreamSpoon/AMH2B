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
import bpy
from bpy_extras.io_utils import ImportHelper

from .append_from_file_func import append_object_from_blend_file
from .object_func import delete_all_objects_except
from .template import get_searchable_object_name
from .vgroup_func import (copy_vgroups_by_name_prefix, delete_vgroups_by_name_prefix)

def copy_vertex_groups_by_prefix(from_mesh_obj, sel_obj_list, vg_name_prefix, create_name_only):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # iterate over selected 'MESH' type objects that are not the active object
    for to_mesh_obj in (x for x in sel_obj_list if x.type == 'MESH' and x != from_mesh_obj):
        # skip destination mesh objects with different numbers of vertices
        dvc = len(to_mesh_obj.data.vertices)
        svc = len(from_mesh_obj.data.vertices)
        if dvc != svc and create_name_only == False:
            print("copy_vertex_groups_by_prefix(): Cannot copy vertex groups from source ("+from_mesh_obj.name+
                ") to dest ("+to_mesh_obj.name+"), source vertex count ("+str(svc)+
                ") doesn't equal destination vertex count ("+str(dvc)+").")
            continue
        copy_vgroups_by_name_prefix(from_mesh_obj, to_mesh_obj, vg_name_prefix, create_name_only)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_OT_CopyVertexGroupsByPrefix(bpy.types.Operator):
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

        scn = context.scene
        copy_vertex_groups_by_prefix(act_ob, context.selected_objects, scn.amh2b.vg_func_name_prefix, scn.amh2b.vg_create_name_only)
        return {'FINISHED'}

def delete_prefixed_vertex_groups(selection_list, delete_prefix):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # iterate over selected 'MESH' type objects
    for mesh_obj in (x for x in selection_list if x.type == 'MESH'):
        delete_vgroups_by_name_prefix(mesh_obj, delete_prefix)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_OT_DeleteVertexGroupsByPrefix(bpy.types.Operator):
    """With all selected objects, delete vertex groups by prefix"""
    bl_idname = "amh2b.vg_delete_by_prefix"
    bl_label = "Delete Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        if scn.amh2b.vg_func_name_prefix == '':
            self.report({'ERROR'}, "Vertex group name prefix is blank")
            return {'CANCELLED'}

        delete_prefixed_vertex_groups(context.selected_objects, scn.amh2b.vg_func_name_prefix)
        return {'FINISHED'}

def search_file_for_auto_vgroups(sel_obj_list, chosen_blend_file, name_prefix, swap_autoname_ext,
                                    create_name_only):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # copy list of selected objects, minus the active object
    other_obj_list = []
    for ob in sel_obj_list:
        if ob.type == 'MESH':
            other_obj_list.append(ob)
    bpy.ops.object.select_all(action='DESELECT')

    # keep a list of all objects in the Blend file, before objects are appended
    all_objects_list_before = [ ob for ob in bpy.data.objects ]

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

        # skip destination mesh objects with different numbers of vertices, unless create name only
        dvc = len(sel.data.vertices)
        svc = len(appended_obj.data.vertices)
        if dvc == svc or create_name_only == False:
            copy_vgroups_by_name_prefix(appended_obj, sel, name_prefix, create_name_only)
        else:
            print("search_file_for_auto_vgroups(): Cannot copy vertex groups from source ("+appended_obj.name+
                ") to dest ("+sel.name+"), source vertex count ("+str(svc)+
                ") doesn't equal destination vertex count ("+str(dvc)+").")

        # appended object may have pulled in other objects as dependencies, so delete all appended objects
        delete_all_objects_except(all_objects_list_before)

        # if an object was named in order to do appending then fix name
        if test_obj is not None:
            test_obj.name = search_name

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_OT_SearchFileForAutoVGroups(bpy.types.Operator, ImportHelper):
    """For each selected MESH object: Search another file automatically and try to copy vertex groups based on Prefix and object name.\nNote: Name of object from MHX import process is used to search for object in other selected file"""
    bl_idname = "amh2b.vg_copy_from_file"
    bl_label = "Copy from File"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob : bpy.props.StringProperty(default="*.blend", options={'HIDDEN'})

    def execute(self, context):
        scn = context.scene
        search_file_for_auto_vgroups(context.selected_objects, self.filepath,
            scn.amh2b.vg_func_name_prefix, scn.amh2b.vg_swap_autoname_ext, scn.amh2b.vg_create_name_only)
        return {'FINISHED'}
