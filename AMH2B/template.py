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

import bpy

from .material_func import rename_material

def get_mat_template_name(orig_name, delim, delim_count):
    pos = len(orig_name)
    c = 0
    while c < delim_count:
        pos = orig_name.rfind(delim[0], 0, pos)
        if pos < 0:
            break
        c = c + 1
    if pos < 0 or pos == len(orig_name):
        return orig_name
    else:
        return orig_name[pos+1:len(orig_name)]

#def is_mat_mhx_name(mat_name):
#    if mat_name.count(':') == 2:
#        return True
#    return False

#def is_mat_template_name(mat_name):
#    if mat_name.count(':') == 1:
#        return True
#    return False

def do_setup_mat_template(selection_list, active_slot_only, delimiter, delimiter_count):
    for obj in selection_list:
        # iterate over the material slots and check/rename the materials
        for mat_slot in (s for s in obj.material_slots if s.material is not None):
            # skip this slot if 'active slot only' is enabled and if this is not the active slot
            if active_slot_only and mat_slot != obj.material_slots[obj.active_material_index]:
                continue
            mat_name = mat_slot.material.name
            new_mat_name = get_mat_template_name(mat_name, delimiter, delimiter_count+1)
            rename_material(mat_name, new_mat_name)

class AMH2B_OT_SetupMatSwap(bpy.types.Operator):
    """Rename materials on all selected objects to make them searchable re: swap material from file"""
    bl_idname = "amh2b.temp_setup_mat_swap"
    bl_label = "Rename Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        do_setup_mat_template(context.selected_objects, scn.amh2b.temp_active_slot_only, scn.amh2b.temp_delimiter,
                              scn.amh2b.temp_delim_count)
        return {'FINISHED'}

def get_searchable_object_name(object_name):
    if object_name.rfind(":") != -1:
        return object_name[object_name.rfind(":")+1 : len(object_name)]
    else:
        return object_name

def do_rename_mhx_object_to_searchable(selection_list):
    for obj in selection_list:
        if obj.type != 'MESH':
            continue
        obj.name = get_searchable_object_name(obj.name)

class AMH2B_OT_MakeTailorObjectSearchable(bpy.types.Operator):
    """Rename selected objects, as needed, to make them searchable re:\nAutomatic search of file for vertex groups by object name and vertex group name prefix"""
    bl_idname = "amh2b.temp_make_tailor_object_searchable"
    bl_label = "Make Objects Searchable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_rename_mhx_object_to_searchable(context.selected_objects)
        return {'FINISHED'}
