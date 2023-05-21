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

# duplicate selected objects, return active object afterwards
def dup_selected():
    bpy.ops.object.duplicate(linked=False)
    return bpy.context.active_object

def check_create_basis_shape_key(obj):
    if obj.data.shape_keys is None:
        sk_basis = obj.shape_key_add(name='Basis')
        sk_basis.interpolation = 'KEY_LINEAR'

def delete_all_objects_except(except_objects):
    # save a temp copy of list of all objects, because some objects will be deleted
    all_objs_current = [ ob for ob in bpy.data.objects ]
    bpy.ops.object.select_all(action='DESELECT')
    for delete_obj in (ob for ob in all_objs_current if ob not in except_objects):
        # un-hide
        delete_obj.hide_set(False)
        delete_obj.hide_select = False
        # select for deletion
        delete_obj.select_set(True)
    # delete all except the given "except objects"
    bpy.ops.object.delete()
