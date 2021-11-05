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

from .imp_material_func import *

def get_mat_template_name(mh_name):
    # if name is in MH format then return trimmed name
    if mh_name.count(':') == 2:
        return mh_name[ mh_name.find(":")+1 : len(mh_name) ]
    # otherwise return original name
    else:
        return mh_name

def is_mat_mhx_name(mat_name):
    if mat_name.count(':') == 2:
        return True
    return False

def is_mat_template_name(mat_name):
    if mat_name.count(':') == 1:
        return True
    return False

def do_setup_mat_template_single(selection_list):
    for obj in selection_list:
        if len(obj.material_slots) < 1 or obj.material_slots[obj.active_material_index] is None:
            continue

        active_mat_name = obj.material_slots[obj.active_material_index].name
        if is_mat_mhx_name(active_mat_name):
            new_mat_name = get_mat_template_name(active_mat_name)
            rename_material(active_mat_name, new_mat_name)

class AMH2B_SetupMatSwapSingle(bpy.types.Operator):
    """Rename active material slot of active object to make the material searchable re: swap material from file"""
    bl_idname = "amh2b.temp_setup_mat_swap_single"
    bl_label = "Active Material Only"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_setup_mat_template_single(context.selected_objects)
        return {'FINISHED'}

def do_setup_mat_template_multi(selection_list):
    for obj in selection_list:
        # iterate over the material slots and check/rename the materials
        for mat_slot in obj.material_slots:
            if mat_slot.material is None:
                continue
            mat_name = mat_slot.material.name
            if is_mat_mhx_name(mat_name):
                new_mat_name = get_mat_template_name(mat_name)
                rename_material(mat_name, new_mat_name)

class AMH2B_SetupMatSwapMulti(bpy.types.Operator):
    """Rename all materials on all selected objects to make them searchable re: swap material from file"""
    bl_idname = "amh2b.temp_setup_mat_swap_multi"
    bl_label = "All Material Slots"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_setup_mat_template_multi(context.selected_objects)
        return {'FINISHED'}

def get_searchable_object_name(object_name):
    if object_name.rfind(":") != -1:
        return object_name[object_name.rfind(":")+1 : len(object_name)]
    else:
        return object_name

def do_rename_mhx_object_to_searchable(act_ob):
    act_ob.name = get_searchable_object_name(act_ob.name)

class AMH2B_MakeTailorObjectSearchable(bpy.types.Operator):
    """Rename active object, if needed, to make it searchable re:\nAutomatic search of file for vertex groups by object name and vertex group name prefix"""
    bl_idname = "amh2b.temp_make_tailor_object_searchable"
    bl_label = "Make Object Searchable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        do_rename_mhx_object_to_searchable(act_ob)
        return {'FINISHED'}
