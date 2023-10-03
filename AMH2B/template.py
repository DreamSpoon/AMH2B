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

def get_searchable_object_name(object_name):
    if object_name.rfind(":") != -1:
        return object_name[object_name.rfind(":")+1 : len(object_name)]
    else:
        return object_name

def rename_mhx_object_to_searchable(selection_list):
    for obj in selection_list:
        if obj.type != 'MESH':
            continue
        obj.name = get_searchable_object_name(obj.name)

class AMH2B_OT_MakeObjectSearchable(bpy.types.Operator):
    """Rename selected objects, as needed, to make them searchable re:\nAutomatic search of file for vertex groups by object name and vertex group name prefix"""
    bl_idname = "amh2b.temp_make_tailor_object_searchable"
    bl_label = "Make Objects Searchable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rename_mhx_object_to_searchable(context.selected_objects)
        return {'FINISHED'}
