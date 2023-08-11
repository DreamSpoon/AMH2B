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

SB_WEIGHT_GEO_NG_NAME = "WeightSoftBody Geometry Nodes"
SIGNED_NEAREST_GEO_NG_NAME = "SignedNearest_AMH2B_GeoNG"
SPRING_CONNECT_VERT_GEO_NG_NAME = "SpringConnectVert_AMH2B_GeoNG"

def create_geo_ng_signed_nearest():
    new_node_group = bpy.data.node_groups.new(name=SIGNED_NEAREST_GEO_NG_NAME, type='GeometryNodeTree')
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Target")
    new_node_group.outputs.new(type='NodeSocketVector', name="Position")
    new_node_group.outputs.new(type='NodeSocketFloat', name="Distance")
    new_node_group.outputs.new(type='NodeSocketVector', name="Normal")
    new_node_group.outputs.new(type='NodeSocketBool', name="Is Hit")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.width_hidden = 0.000000
    node.location = (-20, 176)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.width_hidden = 0.000000
    node.location = (-20, 294)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.001"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.width_hidden = 0.000000
    node.location = (-20, 39)
    new_nodes["Position"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.width_hidden = 0.000000
    node.location = (196, 196)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    node.inputs[1].default_value = 1.100000
    node.inputs[2].default_value = 0.000100
    new_nodes["Math"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.width_hidden = 0.000000
    node.location = (196, 255)
    new_nodes["Position.001"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.width_hidden = 0.000000
    node.location = (-235, 333)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.width_hidden = 0.000000
    node.location = (-235, 176)
    new_nodes["Position.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.width_hidden = 0.000000
    node.location = (196, 725)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = -1.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.001"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.width_hidden = 0.000000
    node.location = (-451, 392)
    new_nodes["Group Input"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.width_hidden = 0.000000
    node.location = (764, 745)
    new_nodes["Group Output"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.width_hidden = 0.000000
    node.location = (549, 118)
    node.operation = "DOT_PRODUCT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.width_hidden = 0.000000
    node.location = (549, 274)
    node.operation = "GREATER_THAN"
    node.use_clamp = False
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.002"] = node
    # Raycast
    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.width_hidden = 0.000000
    node.location = (196, 568)
    node.data_type = "FLOAT"
    node.mapping = "INTERPOLATED"
    new_nodes["Raycast"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.width_hidden = 0.000000
    node.location = (549, 470)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.003"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.width_hidden = 0.000000
    node.location = (549, 666)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix"] = node
    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Raycast"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Vector Math.001"].inputs[0])
    tree_links.new(new_nodes["Vector Math.001"].outputs[0], new_nodes["Raycast"].inputs[7])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Raycast"].inputs[8])
    tree_links.new(new_nodes["Raycast"].outputs[2], new_nodes["Group Output"].inputs[2])
    tree_links.new(new_nodes["Raycast"].outputs[2], new_nodes["Vector Math.002"].inputs[0])
    tree_links.new(new_nodes["Vector Math.001"].outputs[0], new_nodes["Vector Math.002"].inputs[1])
    tree_links.new(new_nodes["Vector Math.002"].outputs[1], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Mix"].outputs[0], new_nodes["Group Output"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[0], new_nodes["Group Output"].inputs[3])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Position.002"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Vector Math"].inputs[1])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Raycast"].inputs[6])
    tree_links.new(new_nodes["Raycast"].outputs[0], new_nodes["Math.003"].inputs[0])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Math.003"].inputs[1])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Mix"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Mix"].inputs[2])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Mix"].inputs[3])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_node_group

#    node.node_tree = bpy.data.node_groups.get(SIGNED_NEAREST_GEO_NG_NAME)
def create_weight_sb_mod_geo_node_group(new_node_group):
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketObject', name="Goal Object")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Goal From Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Goal From Max")
    new_input.default_value = 1.000000
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Goal To Min")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketFloat', name="Goal To Max")
    new_node_group.inputs.new(type='NodeSocketObject', name="Mask Object")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Mask From Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Mask From Max")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketObject', name="Mass Object")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Mass From Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Mass From Max")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketFloat', name="Mass To Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Mass To Max")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketObject', name="Spring Object")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Spring From Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Spring From Max")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketFloat', name="Spring To Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Spring To Max")
    new_input.default_value = 1.000000
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.outputs.new(type='NodeSocketFloat', name="Goal")
    new_node_group.outputs.new(type='NodeSocketFloat', name="Mask")
    new_node_group.outputs.new(type='NodeSocketFloat', name="Mass")
    new_node_group.outputs.new(type='NodeSocketFloat', name="Spring")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.width_hidden = 0.000000
    node.location = (745, -20)
    new_nodes["Group Output"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Spring Map Range"
    node.width_hidden = 0.000000
    node.location = (529, -451)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[8].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[9].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[10].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[11].default_value = (4.000000, 4.000000, 4.000000)
    new_nodes["Map Range"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Spring Clamp"
    node.width_hidden = 0.000000
    node.location = (529, -294)
    node.operation = "ADD"
    node.use_clamp = True
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Mass Map Range"
    node.width_hidden = 0.000000
    node.location = (314, -412)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[8].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[9].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[10].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[11].default_value = (4.000000, 4.000000, 4.000000)
    new_nodes["Map Range.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Mass Clamp"
    node.width_hidden = 0.000000
    node.location = (314, -255)
    node.operation = "ADD"
    node.use_clamp = True
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Mask Clamp"
    node.width_hidden = 0.000000
    node.location = (98, -216)
    node.operation = "GREATER_THAN"
    node.use_clamp = True
    node.inputs[1].default_value = 0.500000
    node.inputs[2].default_value = 1.120000
    new_nodes["Math.002"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Spring CapAttr"
    node.width_hidden = 0.000000
    node.location = (529, -118)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Mass CapAttr"
    node.width_hidden = 0.000000
    node.location = (314, -78)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute.001"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Mask CapAttr"
    node.width_hidden = 0.000000
    node.location = (98, -39)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Goal Clamp"
    node.width_hidden = 0.000000
    node.location = (-118, -176)
    node.operation = "ADD"
    node.use_clamp = True
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.005"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Goal CapAttr"
    node.width_hidden = 0.000000
    node.location = (-118, 0)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute.003"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Goal Map Range"
    node.width_hidden = 0.000000
    node.location = (-118, -333)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[8].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[9].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[10].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[11].default_value = (4.000000, 4.000000, 4.000000)
    new_nodes["Map Range.002"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Mask Map Range"
    node.width_hidden = 0.000000
    node.location = (98, -372)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    node.inputs[3].default_value = 0.000000
    node.inputs[4].default_value = 1.000000
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[8].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[9].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[10].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[11].default_value = (4.000000, 4.000000, 4.000000)
    new_nodes["Map Range.003"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Goal Object Info"
    node.width_hidden = 0.000000
    node.location = (-118, -764)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info.002"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.width_hidden = 0.000000
    node.location = (98, -627)
    node.node_tree = bpy.data.node_groups.get(SIGNED_NEAREST_GEO_NG_NAME)
    new_nodes["Group.005"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Goal Object Info"
    node.width_hidden = 0.000000
    node.location = (98, -804)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info.004"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.width_hidden = 0.000000
    node.location = (314, -666)
    node.node_tree = bpy.data.node_groups.get(SIGNED_NEAREST_GEO_NG_NAME)
    new_nodes["Group.006"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Goal Object Info"
    node.width_hidden = 0.000000
    node.location = (314, -843)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info.005"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.width_hidden = 0.000000
    node.location = (529, -706)
    node.node_tree = bpy.data.node_groups.get(SIGNED_NEAREST_GEO_NG_NAME)
    new_nodes["Group.007"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Goal Object Info"
    node.width_hidden = 0.000000
    node.location = (529, -882)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info.006"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.width_hidden = 0.000000
    node.location = (-451, -470)
    new_nodes["Group Input"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.width_hidden = 0.000000
    node.location = (-118, -588)
    node.node_tree = bpy.data.node_groups.get(SIGNED_NEAREST_GEO_NG_NAME)
    new_nodes["Group.004"] = node
    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Group Input"].outputs[10], new_nodes["Map Range.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[11], new_nodes["Map Range.001"].inputs[2])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Capture Attribute.001"].inputs[2])
    tree_links.new(new_nodes["Capture Attribute.001"].outputs[2], new_nodes["Group Output"].inputs[3])
    tree_links.new(new_nodes["Map Range.001"].outputs[0], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[12], new_nodes["Map Range.001"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[13], new_nodes["Map Range.001"].inputs[4])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Capture Attribute"].inputs[2])
    tree_links.new(new_nodes["Map Range"].outputs[0], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute"].outputs[2], new_nodes["Group Output"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[15], new_nodes["Map Range"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[16], new_nodes["Map Range"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[17], new_nodes["Map Range"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[18], new_nodes["Map Range"].inputs[4])
    tree_links.new(new_nodes["Math.005"].outputs[0], new_nodes["Capture Attribute.003"].inputs[2])
    tree_links.new(new_nodes["Map Range.002"].outputs[0], new_nodes["Math.005"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute.003"].outputs[2], new_nodes["Group Output"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Object Info.002"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Map Range.002"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Map Range.002"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Map Range.002"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Map Range.002"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Capture Attribute.003"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute.001"].outputs[0], new_nodes["Capture Attribute"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Capture Attribute.002"].inputs[2])
    tree_links.new(new_nodes["Map Range.003"].outputs[0], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute.003"].outputs[0], new_nodes["Capture Attribute.002"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Map Range.003"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Map Range.003"].inputs[2])
    tree_links.new(new_nodes["Capture Attribute.002"].outputs[0], new_nodes["Capture Attribute.001"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute.002"].outputs[2], new_nodes["Group Output"].inputs[2])
    tree_links.new(new_nodes["Group.004"].outputs[1], new_nodes["Map Range.002"].inputs[0])
    tree_links.new(new_nodes["Object Info.002"].outputs[3], new_nodes["Group.004"].inputs[0])
    tree_links.new(new_nodes["Object Info.004"].outputs[3], new_nodes["Group.005"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Object Info.004"].inputs[0])
    tree_links.new(new_nodes["Group.005"].outputs[1], new_nodes["Map Range.003"].inputs[0])
    tree_links.new(new_nodes["Object Info.005"].outputs[3], new_nodes["Group.006"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[9], new_nodes["Object Info.005"].inputs[0])
    tree_links.new(new_nodes["Group.006"].outputs[1], new_nodes["Map Range.001"].inputs[0])
    tree_links.new(new_nodes["Object Info.006"].outputs[3], new_nodes["Group.007"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[14], new_nodes["Object Info.006"].inputs[0])
    tree_links.new(new_nodes["Group.007"].outputs[1], new_nodes["Map Range"].inputs[0])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False

def create_geo_ng_spring_connect_vert():
    new_node_group = bpy.data.node_groups.new(name=SPRING_CONNECT_VERT_GEO_NG_NAME, type='GeometryNodeTree')
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_input = new_node_group.inputs.new(type='NodeSocketBool', name="Include")
    new_input.default_value = True
    new_node_group.inputs.new(type='NodeSocketBool', name="Remove Original")
    new_node_group.inputs.new(type='NodeSocketVector', name="Connect Position")
    new_input = new_node_group.inputs.new(type='NodeSocketFloatDistance', name="Connect Min Length")
    new_input.min_value = 0.000000
    new_input = new_node_group.inputs.new(type='NodeSocketFloatDistance', name="Connect Max Length")
    new_input.min_value = 0.000000
    new_node_group.inputs.new(type='NodeSocketVector', name="Extrude Vec")
    new_input = new_node_group.inputs.new(type='NodeSocketFloatDistance', name="Extrude Length")
    new_input.min_value = 0.000000
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Extrude Bias")
    new_input.min_value = 0.000000
    new_input.max_value = 1.000000
    new_input.default_value = 0.500000
    new_input = new_node_group.inputs.new(type='NodeSocketFloatDistance', name="Merge Distance")
    new_input.min_value = 0.000000
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Inner Solid")
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.outputs.new(type='NodeSocketBool', name="Include")
    new_node_group.outputs.new(type='NodeSocketVector', name="Connect Position")
    new_node_group.outputs.new(type='NodeSocketVector', name="Extrude Vec")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Compare
    node = tree_nodes.new(type="FunctionNodeCompare")
    node.label = "Is Connected?"
    node.location = (20, -216)
    node.data_type = "FLOAT"
    node.mode = "ELEMENT"
    node.operation = "GREATER_EQUAL"
    node.inputs[2].default_value = 0
    node.inputs[3].default_value = 0
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[7].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[8].default_value = ""
    node.inputs[9].default_value = ""
    node.inputs[10].default_value = 0.900000
    node.inputs[11].default_value = 0.087266
    node.inputs[12].default_value = 0.001000
    new_nodes["Compare"] = node
    # Boolean Math
    node = tree_nodes.new(type="FunctionNodeBooleanMath")
    node.location = (20, -98)
    node.operation = "NOT"
    node.inputs[1].default_value = False
    new_nodes["Boolean Math"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Connected CapAttr"
    node.location = (20, 235)
    node.data_type = "BOOLEAN"
    node.domain = "POINT"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = 0.000000
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute"] = node
    # Boolean Math
    node = tree_nodes.new(type="FunctionNodeBooleanMath")
    node.location = (20, 39)
    node.operation = "AND"
    new_nodes["Boolean Math.001"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (20, -529)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "VECTOR"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = 0.000000
    node.inputs[3].default_value = 0.000000
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Extrude Vec * Length"
    node.location = (20, -392)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Connect Vec"
    node.location = (-196, -549)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.001"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Extrude Vec"
    node.location = (-196, -686)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.002"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-431, -608)
    new_nodes["Position"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Connect Offset"
    node.location = (-431, -470)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.003"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-431, -353)
    node.operation = "LENGTH"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.004"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-431, -196)
    node.operation = "GREATER_THAN"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math"] = node
    # Boolean Math
    node = tree_nodes.new(type="FunctionNodeBooleanMath")
    node.location = (-431, -59)
    node.operation = "AND"
    new_nodes["Boolean Math.002"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Connect Pos CapAttr"
    node.location = (490, 627)
    node.data_type = "FLOAT_VECTOR"
    node.domain = "POINT"
    node.inputs[2].default_value = 0.000000
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute.001"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (470, 0)
    node.operation = "LENGTH"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.005"] = node
    # Raycast
    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.location = (470, 372)
    node.data_type = "FLOAT"
    node.mapping = "NEAREST"
    new_nodes["Raycast"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (470, 59)
    new_nodes["Position.001"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (255, 0)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.006"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (255, -118)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "VECTOR"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = 0.000000
    node.inputs[3].default_value = 0.000000
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.001"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Extrude Vec CapAttr"
    node.location = (725, 725)
    node.data_type = "FLOAT_VECTOR"
    node.domain = "POINT"
    node.inputs[2].default_value = 0.000000
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute.002"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (725, 431)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "VECTOR"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = 0.000000
    node.inputs[3].default_value = 0.000000
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.002"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (725, 549)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.007"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (725, 216)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.008"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (1450, 1411)
    new_nodes["Group Output"] = node
    # Boolean Math
    node = tree_nodes.new(type="FunctionNodeBooleanMath")
    node.location = (1176, 843)
    node.operation = "OR"
    new_nodes["Boolean Math.003"] = node
    # Boolean Math
    node = tree_nodes.new(type="FunctionNodeBooleanMath")
    node.label = "Is Bottom?"
    node.location = (1176, 960)
    node.operation = "NOT"
    new_nodes["Boolean Math.004"] = node
    # Boolean Math
    node = tree_nodes.new(type="FunctionNodeBooleanMath")
    node.label = "Is Bottom and Remove Original?"
    node.location = (1176, 1098)
    node.operation = "AND"
    new_nodes["Boolean Math.005"] = node
    # Delete Geometry
    node = tree_nodes.new(type="GeometryNodeDeleteGeometry")
    node.label = "Delete Original Geometry"
    node.location = (1176, 1254)
    node.domain = "EDGE"
    node.mode = "EDGE_FACE"
    new_nodes["Delete Geometry"] = node
    # Merge by Distance
    node = tree_nodes.new(type="GeometryNodeMergeByDistance")
    node.location = (1176, 1411)
    node.mode = "ALL"
    new_nodes["Merge by Distance"] = node
    # Boolean Math
    node = tree_nodes.new(type="FunctionNodeBooleanMath")
    node.location = (941, 882)
    node.operation = "AND"
    new_nodes["Boolean Math.006"] = node
    # Extrude Mesh
    node = tree_nodes.new(type="GeometryNodeExtrudeMesh")
    node.location = (941, 725)
    node.mode = "VERTICES"
    node.inputs[3].default_value = 1.000000
    node.inputs[4].default_value = True
    new_nodes["Extrude Mesh"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-764, -39)
    new_nodes["Group Input"] = node
    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Merge by Distance"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Vector Math.003"].inputs[0])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Vector Math.003"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[9], new_nodes["Merge by Distance"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Vector Math.002"].inputs[0])
    tree_links.new(new_nodes["Vector Math.003"].outputs[0], new_nodes["Vector Math.004"].inputs[0])
    tree_links.new(new_nodes["Mix"].outputs[1], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Vector Math"].inputs[3])
    tree_links.new(new_nodes["Vector Math.004"].outputs[1], new_nodes["Compare"].inputs[1])
    tree_links.new(new_nodes["Compare"].outputs[0], new_nodes["Mix.001"].inputs[0])
    tree_links.new(new_nodes["Vector Math.003"].outputs[0], new_nodes["Mix.001"].inputs[5])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Mix.001"].inputs[4])
    tree_links.new(new_nodes["Vector Math.003"].outputs[0], new_nodes["Vector Math.001"].inputs[0])
    tree_links.new(new_nodes["Vector Math.002"].outputs[0], new_nodes["Mix"].inputs[5])
    tree_links.new(new_nodes["Vector Math.001"].outputs[0], new_nodes["Mix"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Mix"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute"].outputs[4], new_nodes["Boolean Math.006"].inputs[0])
    tree_links.new(new_nodes["Extrude Mesh"].outputs[1], new_nodes["Boolean Math.006"].inputs[1])
    tree_links.new(new_nodes["Boolean Math.001"].outputs[0], new_nodes["Capture Attribute"].inputs[4])
    tree_links.new(new_nodes["Boolean Math.006"].outputs[0], new_nodes["Merge by Distance"].inputs[1])
    tree_links.new(new_nodes["Compare"].outputs[0], new_nodes["Boolean Math"].inputs[0])
    tree_links.new(new_nodes["Boolean Math"].outputs[0], new_nodes["Boolean Math.001"].inputs[1])
    tree_links.new(new_nodes["Mix.001"].outputs[1], new_nodes["Vector Math.006"].inputs[0])
    tree_links.new(new_nodes["Boolean Math.006"].outputs[0], new_nodes["Group Output"].inputs[1])
    tree_links.new(new_nodes["Capture Attribute"].outputs[0], new_nodes["Capture Attribute.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Capture Attribute.001"].inputs[1])
    tree_links.new(new_nodes["Capture Attribute.001"].outputs[1], new_nodes["Group Output"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Capture Attribute"].inputs[0])
    tree_links.new(new_nodes["Extrude Mesh"].outputs[0], new_nodes["Delete Geometry"].inputs[0])
    tree_links.new(new_nodes["Delete Geometry"].outputs[0], new_nodes["Merge by Distance"].inputs[0])
    tree_links.new(new_nodes["Extrude Mesh"].outputs[1], new_nodes["Boolean Math.003"].inputs[0])
    tree_links.new(new_nodes["Extrude Mesh"].outputs[2], new_nodes["Boolean Math.003"].inputs[1])
    tree_links.new(new_nodes["Boolean Math.003"].outputs[0], new_nodes["Boolean Math.004"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Boolean Math.004"].inputs[1])
    tree_links.new(new_nodes["Boolean Math.004"].outputs[0], new_nodes["Boolean Math.005"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Boolean Math.005"].inputs[0])
    tree_links.new(new_nodes["Boolean Math.005"].outputs[0], new_nodes["Delete Geometry"].inputs[1])
    tree_links.new(new_nodes["Vector Math.004"].outputs[1], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Boolean Math.002"].inputs[0])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Boolean Math.002"].inputs[1])
    tree_links.new(new_nodes["Boolean Math.002"].outputs[0], new_nodes["Boolean Math.001"].inputs[0])
    tree_links.new(new_nodes["Boolean Math.002"].outputs[0], new_nodes["Extrude Mesh"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[10], new_nodes["Raycast"].inputs[0])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Raycast"].inputs[6])
    tree_links.new(new_nodes["Vector Math.006"].outputs[0], new_nodes["Raycast"].inputs[7])
    tree_links.new(new_nodes["Mix.001"].outputs[1], new_nodes["Vector Math.005"].inputs[0])
    tree_links.new(new_nodes["Vector Math.005"].outputs[1], new_nodes["Raycast"].inputs[8])
    tree_links.new(new_nodes["Raycast"].outputs[0], new_nodes["Mix.002"].inputs[0])
    tree_links.new(new_nodes["Mix.001"].outputs[1], new_nodes["Mix.002"].inputs[4])
    tree_links.new(new_nodes["Mix.002"].outputs[1], new_nodes["Vector Math.007"].inputs[0])
    tree_links.new(new_nodes["Vector Math.007"].outputs[0], new_nodes["Capture Attribute.002"].inputs[1])
    tree_links.new(new_nodes["Capture Attribute.001"].outputs[0], new_nodes["Capture Attribute.002"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute.002"].outputs[1], new_nodes["Group Output"].inputs[3])
    tree_links.new(new_nodes["Capture Attribute.002"].outputs[0], new_nodes["Extrude Mesh"].inputs[0])
    tree_links.new(new_nodes["Mix.002"].outputs[1], new_nodes["Extrude Mesh"].inputs[2])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Vector Math.008"].inputs[0])
    tree_links.new(new_nodes["Vector Math.008"].outputs[0], new_nodes["Mix.002"].inputs[5])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Vector Math.008"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Compare"].inputs[0])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_node_group

def create_spring_connect_mod_geo_node_group(new_node_group):
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketObject', name="Solid Object")
    new_input = new_node_group.inputs.new(type='NodeSocketFloatFactor', name="Include Ratio")
    new_input.min_value = 0.000000
    new_input.max_value = 1.000000
    new_input.default_value = 1.000000
    new_input = new_node_group.inputs.new(type='NodeSocketVector', name="Connect Position")
    new_input.hide_value = True
    new_node_group.inputs.new(type='NodeSocketBool', name="Use Attribute")
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.width_hidden = 0.000000
    node.location = (1019, 196)
    new_nodes["Group Output"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.width_hidden = 0.000000
    node.location = (510, -196)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = -1.000000
    new_nodes["Vector Math"] = node
    # Normal
    node = tree_nodes.new(type="GeometryNodeInputNormal")
    node.width_hidden = 0.000000
    node.location = (510, -333)
    new_nodes["Normal"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.width_hidden = 0.000000
    node.location = (764, 196)
    node.node_tree = bpy.data.node_groups.get(SPRING_CONNECT_VERT_GEO_NG_NAME)
    node.inputs[2].default_value = False
    node.inputs[4].default_value = 0.000000
    node.inputs[5].default_value = 1.000000
    node.inputs[7].default_value = 1.000000
    node.inputs[8].default_value = 0.000000
    node.inputs[9].default_value = 0.000000
    new_nodes["Group"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.width_hidden = 0.000000
    node.location = (510, 196)
    node.node_tree = bpy.data.node_groups.get(SPRING_CONNECT_VERT_GEO_NG_NAME)
    node.inputs[2].default_value = False
    node.inputs[4].default_value = 0.006180
    node.inputs[5].default_value = 0.061803
    node.inputs[7].default_value = 0.061803
    node.inputs[8].default_value = 0.618034
    node.inputs[9].default_value = 0.016803
    new_nodes["Group.001"] = node
    # ID
    node = tree_nodes.new(type="GeometryNodeInputID")
    node.width_hidden = 0.000000
    node.location = (118, -510)
    new_nodes["ID"] = node
    # Random Value
    node = tree_nodes.new(type="FunctionNodeRandomValue")
    node.width_hidden = 0.000000
    node.location = (118, -353)
    node.data_type = "BOOLEAN"
    node.inputs[0].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[1].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[2].default_value = 0.000000
    node.inputs[3].default_value = 1.000000
    node.inputs[4].default_value = 0
    node.inputs[5].default_value = 100
    node.inputs[8].default_value = 0
    new_nodes["Random Value"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.width_hidden = 0.000000
    node.location = (118, -157)
    node.transform_space = "ORIGINAL"
    node.inputs[1].default_value = False
    new_nodes["Object Info"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.width_hidden = 0.000000
    node.location = (118, -39)
    new_nodes["Position"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.width_hidden = 0.000000
    node.location = (118, 118)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.width_hidden = 0.000000
    node.location = (294, 59)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "VECTOR"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = 0.000000
    node.inputs[3].default_value = 0.000000
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.width_hidden = 0.000000
    node.location = (-78, -78)
    new_nodes["Group Input"] = node
    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Group.001"].inputs[0])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Group.001"].inputs[6])
    tree_links.new(new_nodes["Normal"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Group.001"].outputs[0], new_nodes["Group"].inputs[0])
    tree_links.new(new_nodes["Group.001"].outputs[1], new_nodes["Group"].inputs[1])
    tree_links.new(new_nodes["Group.001"].outputs[3], new_nodes["Group"].inputs[6])
    tree_links.new(new_nodes["Group.001"].outputs[2], new_nodes["Group"].inputs[3])
    tree_links.new(new_nodes["Object Info"].outputs[3], new_nodes["Group.001"].inputs[10])
    tree_links.new(new_nodes["Object Info"].outputs[3], new_nodes["Group"].inputs[10])
    tree_links.new(new_nodes["Group"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Object Info"].inputs[0])
    tree_links.new(new_nodes["ID"].outputs[0], new_nodes["Random Value"].inputs[7])
    tree_links.new(new_nodes["Random Value"].outputs[3], new_nodes["Group.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Random Value"].inputs[6])
    tree_links.new(new_nodes["Object Info"].outputs[3], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Mix"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Mix"].inputs[5])
    tree_links.new(new_nodes["Mix"].outputs[1], new_nodes["Group.001"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Mix"].inputs[0])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_node_group
