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
from bpy.types import Operator

from .func import (ATTRIB_SHAPEKEY, SHAPEKEY_ATTRIB, shapekey_to_attribute, attribute_to_shapekey)

class AMH2B_OT_AttributeConvert(Operator):
    """Use Attribute with selected action, e.g. convert ShapeKey to Attribute"""
    bl_idname = "amh2b.attribute_convert"
    bl_label = "Convert"
    bl_options = {'REGISTER', 'UNDO'}

    # return False if no active object, or no ShapeKeys, or no ShapeKey chosen
    @classmethod
    def poll(cls, context):
        amh2b = context.scene.amh2b
        func = amh2b.attr_conv_function
        act_ob = context.active_object
        act_mesh = act_ob.data
        if act_ob is None or act_ob.type != 'MESH' or act_mesh is None:
            return False
        if func == ATTRIB_SHAPEKEY:
            attrib = act_mesh.attributes.get(amh2b.attr_conv_attribute)
            if attrib is None:
                return False
            return isinstance(attrib, bpy.types.FloatVectorAttribute)
        elif func == SHAPEKEY_ATTRIB:
            return act_mesh.shape_keys != None and act_mesh.shape_keys.key_blocks.get(amh2b.attr_conv_shapekey) != None

    def execute(self, context):
        amh2b = context.scene.amh2b
        func = amh2b.attr_conv_function
        if func == ATTRIB_SHAPEKEY:
            attribute_to_shapekey(context.active_object, amh2b.attr_conv_attribute)
        elif func == SHAPEKEY_ATTRIB:
            shapekey_to_attribute(context.active_object, amh2b.attr_conv_shapekey)
        return {'FINISHED'}
