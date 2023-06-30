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

SHAPEKEY_ATTRIB = "SHAPEKEY_ATTRIB"
ATTRIB_SHAPEKEY = "ATTRIB_SHAPEKEY"

ATTR_CONV_FUNC_ITEMS = [
    (SHAPEKEY_ATTRIB, "ShapeKey to Attribute", "Convert Mesh Object ShapeKey to Attribute (Float Vector type)"),
    (ATTRIB_SHAPEKEY, "Attribute to ShapeKey", "Convert Mesh Object Attribute (Float Vector type only) to ShapeKey"),
]

def shapekey_to_attribute(ob, sk_name):
    sk = ob.data.shape_keys.key_blocks.get(sk_name)
    new_attrib = ob.data.attributes.new(name=sk_name, type="FLOAT_VECTOR", domain="POINT")
    for i, sk_point in enumerate(sk.data):
        new_attrib.data[i].vector = sk_point.co

def attribute_to_shapekey(ob, attrib_name):
    attrib = ob.data.attributes.get(attrib_name)
    new_sk = ob.shape_key_add(name=attrib_name)
    for i, attr_point in enumerate(attrib.data):
        new_sk.data[i].co = attr_point.vector
