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

from .func import (ATTRIB_SHAPEKEY, SHAPEKEY_ATTRIB)
from .operator import AMH2B_OT_AttributeConvert

def draw_panel_attributes(self, context, box):
    layout = self.layout
    scn = context.scene
    act_ob = context.active_object
    amh2b = scn.amh2b
    box.prop(amh2b, "attr_conv_function", text="")
    layout.separator()
    layout.operator(AMH2B_OT_AttributeConvert.bl_idname)
    if amh2b.attr_conv_function == SHAPEKEY_ATTRIB:
        if act_ob != None and act_ob.type == 'MESH' and act_ob.data.shape_keys != None:
            layout.prop_search(amh2b, "attr_conv_shapekey", act_ob.data.shape_keys, "key_blocks", text="")
        else:
            layout.prop(amh2b, "attr_conv_shapekey", text="")
    elif amh2b.attr_conv_function == ATTRIB_SHAPEKEY:
        if act_ob != None and act_ob.type == 'MESH' and act_ob.data.attributes != None:
            layout.prop_search(amh2b, "attr_conv_attribute", act_ob.data, "attributes", text="")
        else:
            layout.prop(amh2b, "attr_conv_attribute", text="")
