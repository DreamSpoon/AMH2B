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
import os

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
