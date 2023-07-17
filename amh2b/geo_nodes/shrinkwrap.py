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

from ..node_other import ensure_node_group

SHRINKWRAP_GEO_NG_NAME = "Shrinkwrap_AMH2B_GeoNG"
THICK_SHRINKWRAP_GEO_NG_NAME = "ThickShrinkwrap_AMH2B_GeoNG"
DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME = "DirShrinkwrap_AMH2B_GeoNG"
DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME = "DirThickShrinkwrap_AMH2B_GeoNG"

# depending on the name passed to function, create the right set of nodes in a group and pass back
def create_prereq_shrinkwrap_node_group(node_group_name, node_tree_type):
    if node_tree_type == 'GeometryNodeTree':
        if node_group_name == SHRINKWRAP_GEO_NG_NAME:
            return create_geo_ng_shrinkwrap()
        elif node_group_name == THICK_SHRINKWRAP_GEO_NG_NAME:
            return create_geo_ng_thick_shrinkwrap()
        elif node_group_name == DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME:
            return create_geo_ng_directional_shrinkwrap()
        elif node_group_name == DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME:
            return create_geo_ng_directional_thick_shrinkwrap()
    # error
    print("Unknown name passed to create_prereq_shrinkwrap_node_group: " + str(node_group_name))
    return None

def create_geo_ng_shrinkwrap():
    new_node_group = bpy.data.node_groups.new(name=SHRINKWRAP_GEO_NG_NAME, type='GeometryNodeTree')
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Target Solid")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    new_node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Relative Factor")
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (588, 490)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Output"
    node.location = (588, 627)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.002"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (353, -176)
    new_nodes["Position"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Delta"
    node.location = (353, -39)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.001"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (353, 78)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.003"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (353, 314)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (118, -294)
    node.operation = "DOT_PRODUCT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.007"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-98, -431)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = 1.100000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.003"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-98, -588)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.008"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-98, -706)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.006"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-98, -843)
    new_nodes["Position.004"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (823, 196)
    new_nodes["Position.001"] = node
    # Set Position
    node = tree_nodes.new(type="GeometryNodeSetPosition")
    node.location = (823, 627)
    new_nodes["Set Position"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (1039, 627)
    new_nodes["Group Output"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (823, 333)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.004"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Apply Factor"
    node.location = (823, 470)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.005"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (588, 118)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = -1.000000
    node.inputs[3].default_value = 1.000000
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.001"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (588, 255)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.009"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (118, -137)
    node.operation = "LESS_THAN"
    node.use_clamp = False
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.004"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (118, 39)
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
    # Raycast
    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.location = (-98, -118)
    node.data_type = "FLOAT"
    node.mapping = "NEAREST"
    new_nodes["Raycast"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-98, 39)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = -1.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.005"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (353, 470)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (353, 627)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.002"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-392, -216)
    new_nodes["Position.002"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Solid Nearest"
    node.location = (-392, -59)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-647, 118)
    new_nodes["Group Input"] = node
    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Set Position"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math"].inputs[2])
    tree_links.new(new_nodes["Vector Math.001"].outputs[0], new_nodes["Vector Math.003"].inputs[0])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Vector Math.001"].inputs[0])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Vector Math.002"].inputs[1])
    tree_links.new(new_nodes["Vector Math.002"].outputs[0], new_nodes["Vector Math.004"].inputs[0])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Vector Math.004"].inputs[1])
    tree_links.new(new_nodes["Vector Math.005"].outputs[0], new_nodes["Set Position"].inputs[3])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Math.001"].inputs[1])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Math.002"].inputs[1])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Vector Math"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Vector Math.004"].outputs[0], new_nodes["Vector Math.005"].inputs[0])
    tree_links.new(new_nodes["Position.002"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Raycast"].inputs[8])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.003"].inputs[0])
    tree_links.new(new_nodes["Position.004"].outputs[0], new_nodes["Vector Math.006"].inputs[1])
    tree_links.new(new_nodes["Position.004"].outputs[0], new_nodes["Raycast"].inputs[6])
    tree_links.new(new_nodes["Vector Math.007"].outputs[1], new_nodes["Math.004"].inputs[0])
    tree_links.new(new_nodes["Math.004"].outputs[0], new_nodes["Mix"].inputs[0])
    tree_links.new(new_nodes["Math.004"].outputs[0], new_nodes["Mix.001"].inputs[0])
    tree_links.new(new_nodes["Vector Math.006"].outputs[0], new_nodes["Vector Math.008"].inputs[0])
    tree_links.new(new_nodes["Vector Math.008"].outputs[0], new_nodes["Vector Math.007"].inputs[1])
    tree_links.new(new_nodes["Vector Math.008"].outputs[0], new_nodes["Raycast"].inputs[7])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Raycast"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Vector Math.005"].inputs[3])
    tree_links.new(new_nodes["Mix.001"].outputs[0], new_nodes["Vector Math.009"].inputs[3])
    tree_links.new(new_nodes["Vector Math.003"].outputs[0], new_nodes["Vector Math.009"].inputs[0])
    tree_links.new(new_nodes["Vector Math.009"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Mix"].outputs[0], new_nodes["Math"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.006"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.002"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.001"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.005"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[2], new_nodes["Vector Math.007"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Set Position"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Mix"].inputs[3])
    tree_links.new(new_nodes["Math.005"].outputs[0], new_nodes["Mix"].inputs[2])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_node_group

def create_node_group_node_shrinkwrap(node_tree, override_create):
    ensure_node_group(override_create, SHRINKWRAP_GEO_NG_NAME, 'GeometryNodeTree', create_prereq_shrinkwrap_node_group)

    # create group node that will do the work
    node = node_tree.nodes.new(type='GeometryNodeGroup')
    node.location = (node_tree.view_center[0]/2.5, node_tree.view_center[1]/2.5)
    node.node_tree = bpy.data.node_groups.get(SHRINKWRAP_GEO_NG_NAME)

def create_geo_ng_thick_shrinkwrap():
    new_node_group = bpy.data.node_groups.new(name=THICK_SHRINKWRAP_GEO_NG_NAME, type='GeometryNodeTree')
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Target Solid")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    new_node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Thick Factor")
    new_input.default_value = 1.000000
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (647, -372)
    new_nodes["Position.003"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Delta"
    node.location = (647, -235)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.011"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (176, 686)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (431, 196)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (431, 529)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.003"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (431, 353)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.004"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (647, 372)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Output"
    node.location = (647, 529)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.002"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (882, 78)
    new_nodes["Position.001"] = node
    # Set Position
    node = tree_nodes.new(type="GeometryNodeSetPosition")
    node.location = (882, 529)
    new_nodes["Set Position"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (1098, 529)
    new_nodes["Group Output"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (882, 216)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.004"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Apply Factor"
    node.location = (882, 353)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.005"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (176, 353)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.006"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (176, 529)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.007"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (647, 216)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.010"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (647, 78)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = -1.000000
    node.inputs[3].default_value = 1.000000
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.001"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (647, -118)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.006"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-510, -804)
    new_nodes["Position.004"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-725, -78)
    new_nodes["Position.002"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-510, -666)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.009"] = node
    # Raycast
    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.location = (-510, -78)
    node.data_type = "FLOAT"
    node.mapping = "NEAREST"
    new_nodes["Raycast"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-510, 78)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = -1.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.009"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-294, -255)
    node.operation = "DOT_PRODUCT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.007"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-510, -549)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.008"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-510, -392)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = 1.100000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.011"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Solid Nearest"
    node.location = (-725, 78)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.001"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (-294, 78)
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
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-294, -98)
    node.operation = "LESS_THAN"
    node.use_clamp = False
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.010"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Self Nearest Solid Nearest"
    node.location = (-59, -255)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-59, -98)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (-59, 78)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = 0.000000
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (-59, 274)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.008"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1000, 274)
    new_nodes["Group Input"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (176, 196)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.005"] = node
    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Set Position"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Set Position"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Geometry Proximity.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.008"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[0], new_nodes["Vector Math.002"].inputs[0])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Vector Math.002"].inputs[1])
    tree_links.new(new_nodes["Vector Math.002"].outputs[0], new_nodes["Vector Math.004"].inputs[0])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Vector Math.004"].inputs[1])
    tree_links.new(new_nodes["Vector Math.005"].outputs[0], new_nodes["Set Position"].inputs[3])
    tree_links.new(new_nodes["Math.008"].outputs[0], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Math.003"].inputs[0])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Vector Math"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math.008"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Vector Math.005"].inputs[3])
    tree_links.new(new_nodes["Vector Math.004"].outputs[0], new_nodes["Vector Math.005"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Math.004"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Math.004"].inputs[0])
    tree_links.new(new_nodes["Math.004"].outputs[0], new_nodes["Math.003"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math"].inputs[1])
    tree_links.new(new_nodes["Mix.002"].outputs[0], new_nodes["Math.002"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Math.002"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.005"].inputs[0])
    tree_links.new(new_nodes["Mix.002"].outputs[0], new_nodes["Math.005"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.006"].inputs[0])
    tree_links.new(new_nodes["Math.005"].outputs[0], new_nodes["Math.006"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.007"].inputs[0])
    tree_links.new(new_nodes["Math.006"].outputs[0], new_nodes["Math.007"].inputs[1])
    tree_links.new(new_nodes["Math.007"].outputs[0], new_nodes["Math.001"].inputs[1])
    tree_links.new(new_nodes["Position.002"].outputs[0], new_nodes["Geometry Proximity.001"].inputs[1])
    tree_links.new(new_nodes["Vector Math.011"].outputs[0], new_nodes["Vector Math.006"].inputs[0])
    tree_links.new(new_nodes["Position.003"].outputs[0], new_nodes["Vector Math.011"].inputs[0])
    tree_links.new(new_nodes["Math.011"].outputs[0], new_nodes["Raycast"].inputs[8])
    tree_links.new(new_nodes["Position.004"].outputs[0], new_nodes["Vector Math.009"].inputs[1])
    tree_links.new(new_nodes["Position.004"].outputs[0], new_nodes["Raycast"].inputs[6])
    tree_links.new(new_nodes["Vector Math.007"].outputs[1], new_nodes["Math.010"].inputs[0])
    tree_links.new(new_nodes["Math.010"].outputs[0], new_nodes["Mix"].inputs[0])
    tree_links.new(new_nodes["Math.010"].outputs[0], new_nodes["Mix.001"].inputs[0])
    tree_links.new(new_nodes["Vector Math.009"].outputs[0], new_nodes["Vector Math.008"].inputs[0])
    tree_links.new(new_nodes["Vector Math.008"].outputs[0], new_nodes["Vector Math.007"].inputs[1])
    tree_links.new(new_nodes["Vector Math.008"].outputs[0], new_nodes["Raycast"].inputs[7])
    tree_links.new(new_nodes["Mix.001"].outputs[0], new_nodes["Vector Math.010"].inputs[3])
    tree_links.new(new_nodes["Vector Math.006"].outputs[0], new_nodes["Vector Math.010"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[2], new_nodes["Vector Math.007"].inputs[0])
    tree_links.new(new_nodes["Math.009"].outputs[0], new_nodes["Mix"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[1], new_nodes["Math.011"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[0], new_nodes["Vector Math.009"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[0], new_nodes["Vector Math.011"].inputs[1])
    tree_links.new(new_nodes["Vector Math.010"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[1], new_nodes["Math.009"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[1], new_nodes["Mix"].inputs[3])
    tree_links.new(new_nodes["Mix"].outputs[0], new_nodes["Math.008"].inputs[1])
    tree_links.new(new_nodes["Mix"].outputs[0], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Math.010"].outputs[0], new_nodes["Mix.002"].inputs[0])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Mix.002"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Raycast"].inputs[0])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_node_group

def create_node_group_node_thick_shrinkwrap(node_tree, override_create):
    ensure_node_group(override_create, THICK_SHRINKWRAP_GEO_NG_NAME, 'GeometryNodeTree',
                      create_prereq_shrinkwrap_node_group)
    # create group node that will do the work
    node = node_tree.nodes.new(type='GeometryNodeGroup')
    node.location = (node_tree.view_center[0]/2.5, node_tree.view_center[1]/2.5)
    node.node_tree = bpy.data.node_groups.get(THICK_SHRINKWRAP_GEO_NG_NAME)

def create_geo_ng_directional_shrinkwrap():
    new_node_group = bpy.data.node_groups.new(name=DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME, type='GeometryNodeTree')
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Solid Target")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Direction Target")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    new_node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Direction Factor")
    new_input.min_value = 0.000000
    new_input.max_value = 1.000000
    new_input.default_value = 1.000000
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (510, 0)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = -1.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.010"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (510, -196)
    node.operation = "DOT_PRODUCT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.016"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (255, -274)
    new_nodes["Position.004"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (0, -568)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.008"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-176, -706)
    new_nodes["Position.003"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Direction Nearest"
    node.location = (0, -706)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (0, 39)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = 2.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.007"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (0, -118)
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
    new_nodes["Mix.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (0, -294)
    node.operation = "GREATER_THAN"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.008"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (0, -451)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.009"] = node
    # Raycast
    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.location = (255, 39)
    node.data_type = "FLOAT"
    node.mapping = "NEAREST"
    new_nodes["Raycast"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (745, -176)
    node.operation = "LESS_THAN"
    node.use_clamp = False
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.009"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (745, 0)
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
    new_nodes["Mix.003"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (1000, 137)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.003"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1000, 451)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.005"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1000, 294)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.006"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (1000, -333)
    new_nodes["Position.006"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Direction"
    node.location = (1000, -78)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.015"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Delta"
    node.location = (1000, -196)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.017"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (1235, -39)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = -1.000000
    node.inputs[3].default_value = 1.000000
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.002"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Direction"
    node.location = (1235, 98)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.012"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (1235, 235)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.004"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Output"
    node.location = (1235, 372)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.005"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.label = "Apply Direction Factor"
    node.location = (1470, 706)
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
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (1901, 1058)
    new_nodes["Group Output"] = node
    # Set Position
    node = tree_nodes.new(type="GeometryNodeSetPosition")
    node.location = (1686, 1058)
    new_nodes["Set Position"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (1686, 627)
    new_nodes["Position.005"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (1686, 764)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.010"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Apply Factor"
    node.location = (1686, 902)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.011"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-470, -274)
    new_nodes["Position"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-235, 78)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Delta"
    node.location = (-235, -176)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.001"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-235, -333)
    new_nodes["Position.001"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Output"
    node.location = (-235, 216)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.002"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (-235, -59)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.003"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (-470, 59)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-470, 216)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-470, 372)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.002"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Solid Nearest"
    node.location = (-470, -118)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-745, 176)
    new_nodes["Group Input"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1235, 588)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.004"] = node
    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Set Position"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Set Position"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.001"].inputs[1])
    tree_links.new(new_nodes["Vector Math.001"].outputs[0], new_nodes["Vector Math.003"].inputs[0])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Vector Math.001"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.002"].inputs[0])
    tree_links.new(new_nodes["Vector Math.003"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Vector Math.002"].inputs[1])
    tree_links.new(new_nodes["Position.005"].outputs[0], new_nodes["Vector Math.010"].inputs[1])
    tree_links.new(new_nodes["Vector Math.011"].outputs[0], new_nodes["Set Position"].inputs[3])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Math.001"].inputs[1])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Math.002"].inputs[1])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Vector Math"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Vector Math.011"].inputs[3])
    tree_links.new(new_nodes["Vector Math.010"].outputs[0], new_nodes["Vector Math.011"].inputs[0])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])
    tree_links.new(new_nodes["Position.003"].outputs[0], new_nodes["Geometry Proximity.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Geometry Proximity.001"].inputs[0])
    tree_links.new(new_nodes["Position.004"].outputs[0], new_nodes["Raycast"].inputs[6])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[0], new_nodes["Vector Math.008"].inputs[0])
    tree_links.new(new_nodes["Position.003"].outputs[0], new_nodes["Vector Math.008"].inputs[1])
    tree_links.new(new_nodes["Vector Math.008"].outputs[0], new_nodes["Vector Math.009"].inputs[0])
    tree_links.new(new_nodes["Vector Math.009"].outputs[0], new_nodes["Raycast"].inputs[7])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Raycast"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Vector Math.004"].outputs[0], new_nodes["Vector Math.005"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math.003"].inputs[2])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Math.006"].inputs[1])
    tree_links.new(new_nodes["Math.006"].outputs[0], new_nodes["Math.005"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.003"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.006"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.005"].inputs[0])
    tree_links.new(new_nodes["Math.005"].outputs[0], new_nodes["Vector Math.004"].inputs[3])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Vector Math.005"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[0], new_nodes["Math.004"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.004"].inputs[0])
    tree_links.new(new_nodes["Math.007"].outputs[0], new_nodes["Raycast"].inputs[8])
    tree_links.new(new_nodes["Math.004"].outputs[0], new_nodes["Mix"].inputs[0])
    tree_links.new(new_nodes["Vector Math.002"].outputs[0], new_nodes["Mix"].inputs[4])
    tree_links.new(new_nodes["Vector Math.005"].outputs[0], new_nodes["Mix"].inputs[5])
    tree_links.new(new_nodes["Mix"].outputs[1], new_nodes["Vector Math.010"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.008"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[1], new_nodes["Math.008"].inputs[1])
    tree_links.new(new_nodes["Math.008"].outputs[0], new_nodes["Mix.001"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[1], new_nodes["Mix.001"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Mix.001"].inputs[3])
    tree_links.new(new_nodes["Mix.001"].outputs[0], new_nodes["Math.007"].inputs[0])
    tree_links.new(new_nodes["Vector Math.017"].outputs[0], new_nodes["Vector Math.015"].inputs[0])
    tree_links.new(new_nodes["Position.006"].outputs[0], new_nodes["Vector Math.017"].inputs[0])
    tree_links.new(new_nodes["Vector Math.016"].outputs[1], new_nodes["Math.009"].inputs[0])
    tree_links.new(new_nodes["Math.009"].outputs[0], new_nodes["Mix.003"].inputs[0])
    tree_links.new(new_nodes["Math.009"].outputs[0], new_nodes["Mix.002"].inputs[0])
    tree_links.new(new_nodes["Mix.002"].outputs[0], new_nodes["Vector Math.012"].inputs[3])
    tree_links.new(new_nodes["Vector Math.015"].outputs[0], new_nodes["Vector Math.012"].inputs[0])
    tree_links.new(new_nodes["Math.010"].outputs[0], new_nodes["Mix.003"].inputs[2])
    tree_links.new(new_nodes["Vector Math.009"].outputs[0], new_nodes["Vector Math.016"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[3], new_nodes["Math.010"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[3], new_nodes["Mix.003"].inputs[3])
    tree_links.new(new_nodes["Raycast"].outputs[2], new_nodes["Vector Math.016"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Vector Math.017"].inputs[1])
    tree_links.new(new_nodes["Mix.003"].outputs[0], new_nodes["Math.003"].inputs[1])
    tree_links.new(new_nodes["Vector Math.012"].outputs[0], new_nodes["Vector Math.004"].inputs[0])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_node_group

def create_node_group_node_directional_shrinkwrap(node_tree, override_create):
    ensure_node_group(override_create, DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME, 'GeometryNodeTree',
                      create_prereq_shrinkwrap_node_group)
    # create group node that will do the work
    node = node_tree.nodes.new(type='GeometryNodeGroup')
    node.location = (node_tree.view_center[0]/2.5, node_tree.view_center[1]/2.5)
    node.node_tree = bpy.data.node_groups.get(DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME)

def create_geo_ng_directional_thick_shrinkwrap():
    new_node_group = bpy.data.node_groups.new(name=DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME, type='GeometryNodeTree')
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Solid Target")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Direction Target")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    new_node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Thick Factor")
    new_input.default_value = 1.000000
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Direction Factor")
    new_input.min_value = 0.000000
    new_input.max_value = 1.000000
    new_input.default_value = 1.000000
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (216, 196)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.005"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-39, 353)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.006"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-39, 196)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.008"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (431, 372)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.005"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (902, -216)
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
    new_nodes["Mix.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (902, -59)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = 2.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.020"] = node
    # Raycast
    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.location = (1137, 176)
    node.data_type = "FLOAT"
    node.mapping = "NEAREST"
    new_nodes["Raycast"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (2078, 353)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.011"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (2078, 196)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.015"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (2078, 39)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.016"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1842, 529)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.009"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1842, 353)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.010"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1842, 725)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.012"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1842, 196)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.013"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (1607, 176)
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
    new_nodes["Mix.003"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (1607, 353)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.014"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Output"
    node.location = (2489, 549)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.006"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Direction"
    node.location = (2489, 137)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.007"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (2489, -118)
    new_nodes["Position.005"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Delta"
    node.location = (2489, 20)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.011"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Direction"
    node.location = (2489, 274)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.012"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (2489, 412)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.008"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (1137, -137)
    new_nodes["Position.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1372, 98)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = -1.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.023"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (1372, -98)
    node.operation = "DOT_PRODUCT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.016"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1607, 0)
    node.operation = "LESS_THAN"
    node.use_clamp = False
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.022"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1842, 39)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.019"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1842, -451)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.018"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Self Nearest Solid Nearest"
    node.location = (1842, -608)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.003"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1842, -294)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.017"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (1842, -118)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = 0.000000
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.004"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (902, -392)
    node.operation = "GREATER_THAN"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.021"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-39, -137)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.007"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Self Nearest Solid Nearest"
    node.location = (-39, -294)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.001"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-490, -470)
    node.operation = "DOT_PRODUCT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.014"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (-490, -137)
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
    new_nodes["Mix.005"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-490, -314)
    node.operation = "LESS_THAN"
    node.use_clamp = False
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.024"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-706, -862)
    new_nodes["Position.006"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-706, -725)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.017"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-706, -608)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.015"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-706, -137)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = -1.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.025"] = node
    # Raycast
    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.location = (-706, -294)
    node.data_type = "FLOAT"
    node.mapping = "NEAREST"
    new_nodes["Raycast.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-902, -510)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[1].default_value = 1.100000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.026"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-1117, -412)
    new_nodes["Position.001"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Solid Nearest"
    node.location = (-1117, -255)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (-39, 39)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = 0.000000
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.006"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-39, 510)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-39, 666)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (216, 353)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.004"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (216, 510)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.003"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (647, -294)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.004"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (451, -431)
    new_nodes["Position.003"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Direction Nearest"
    node.location = (647, -431)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.002"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (647, -176)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.003"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Output"
    node.location = (431, 510)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.001"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (431, -157)
    new_nodes["Position"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Delta"
    node.location = (431, -20)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (431, 98)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.002"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (431, 235)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.013"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (216, -78)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = -1.000000
    node.inputs[3].default_value = 1.000000
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.007"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (2293, 98)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    node.inputs[1].default_value = (0.500000, 0.500000, 0.500000)
    node.inputs[2].default_value = -1.000000
    node.inputs[3].default_value = 1.000000
    node.inputs[4].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[5].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[6].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    node.inputs[7].default_value = (0.500000, 0.500000, 0.500000, 1.000000)
    new_nodes["Mix.002"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Apply Factor"
    node.location = (2705, 1019)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    new_nodes["Vector Math.010"] = node
    # Set Position
    node = tree_nodes.new(type="GeometryNodeSetPosition")
    node.location = (2705, 1176)
    new_nodes["Set Position"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (2920, 1176)
    new_nodes["Group Output"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (2705, 745)
    new_nodes["Position.004"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (2705, 882)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.009"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (2489, 764)
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
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (-255, 588)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1470, 255)
    new_nodes["Group Input"] = node
    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math"].inputs[1])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Vector Math.002"].inputs[0])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.001"].inputs[0])
    tree_links.new(new_nodes["Vector Math.005"].outputs[0], new_nodes["Vector Math.001"].inputs[1])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Math.003"].inputs[0])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Vector Math.005"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Geometry Proximity.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Geometry Proximity.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.005"].inputs[0])
    tree_links.new(new_nodes["Math.005"].outputs[0], new_nodes["Math.004"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.004"].inputs[0])
    tree_links.new(new_nodes["Math.004"].outputs[0], new_nodes["Math.003"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.007"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[1], new_nodes["Math.007"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.005"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.008"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.006"].inputs[0])
    tree_links.new(new_nodes["Math.008"].outputs[0], new_nodes["Math.006"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Math.006"].outputs[0], new_nodes["Math.002"].inputs[1])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Math.001"].inputs[1])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])
    tree_links.new(new_nodes["Position.003"].outputs[0], new_nodes["Geometry Proximity.002"].inputs[1])
    tree_links.new(new_nodes["Position.002"].outputs[0], new_nodes["Raycast"].inputs[6])
    tree_links.new(new_nodes["Geometry Proximity.002"].outputs[0], new_nodes["Vector Math.004"].inputs[0])
    tree_links.new(new_nodes["Position.003"].outputs[0], new_nodes["Vector Math.004"].inputs[1])
    tree_links.new(new_nodes["Vector Math.004"].outputs[0], new_nodes["Vector Math.003"].inputs[0])
    tree_links.new(new_nodes["Vector Math.003"].outputs[0], new_nodes["Raycast"].inputs[7])
    tree_links.new(new_nodes["Vector Math.011"].outputs[0], new_nodes["Vector Math.007"].inputs[0])
    tree_links.new(new_nodes["Position.005"].outputs[0], new_nodes["Vector Math.011"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Vector Math.011"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Vector Math.006"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[0], new_nodes["Math.012"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Geometry Proximity.002"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Raycast"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[9], new_nodes["Math.012"].inputs[0])
    tree_links.new(new_nodes["Position.004"].outputs[0], new_nodes["Vector Math.009"].inputs[1])
    tree_links.new(new_nodes["Vector Math.010"].outputs[0], new_nodes["Set Position"].inputs[3])
    tree_links.new(new_nodes["Vector Math.009"].outputs[0], new_nodes["Vector Math.010"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Vector Math.010"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math.014"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.014"].inputs[0])
    tree_links.new(new_nodes["Math.009"].outputs[0], new_nodes["Math.011"].inputs[0])
    tree_links.new(new_nodes["Math.011"].outputs[0], new_nodes["Vector Math.008"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Geometry Proximity.003"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.016"].inputs[0])
    tree_links.new(new_nodes["Math.016"].outputs[0], new_nodes["Math.015"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.015"].inputs[0])
    tree_links.new(new_nodes["Math.015"].outputs[0], new_nodes["Math.011"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity.003"].outputs[1], new_nodes["Math.018"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.016"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.019"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.013"].inputs[0])
    tree_links.new(new_nodes["Math.019"].outputs[0], new_nodes["Math.013"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.010"].inputs[0])
    tree_links.new(new_nodes["Math.013"].outputs[0], new_nodes["Math.010"].inputs[1])
    tree_links.new(new_nodes["Math.010"].outputs[0], new_nodes["Math.009"].inputs[1])
    tree_links.new(new_nodes["Math.014"].outputs[0], new_nodes["Math.009"].inputs[0])
    tree_links.new(new_nodes["Vector Math.008"].outputs[0], new_nodes["Vector Math.006"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Geometry Proximity.003"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[3], new_nodes["Math.018"].inputs[0])
    tree_links.new(new_nodes["Set Position"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Set Position"].inputs[0])
    tree_links.new(new_nodes["Math.018"].outputs[0], new_nodes["Math.017"].inputs[0])
    tree_links.new(new_nodes["Math.021"].outputs[0], new_nodes["Mix.001"].inputs[0])
    tree_links.new(new_nodes["Mix.001"].outputs[0], new_nodes["Math.020"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Mix.001"].inputs[3])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.021"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.002"].outputs[1], new_nodes["Math.021"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity.002"].outputs[1], new_nodes["Mix.001"].inputs[2])
    tree_links.new(new_nodes["Math.020"].outputs[0], new_nodes["Raycast"].inputs[8])
    tree_links.new(new_nodes["Math.012"].outputs[0], new_nodes["Mix"].inputs[0])
    tree_links.new(new_nodes["Vector Math.001"].outputs[0], new_nodes["Mix"].inputs[4])
    tree_links.new(new_nodes["Vector Math.006"].outputs[0], new_nodes["Mix"].inputs[5])
    tree_links.new(new_nodes["Mix"].outputs[1], new_nodes["Vector Math.009"].inputs[0])
    tree_links.new(new_nodes["Vector Math.016"].outputs[1], new_nodes["Math.022"].inputs[0])
    tree_links.new(new_nodes["Math.022"].outputs[0], new_nodes["Mix.003"].inputs[0])
    tree_links.new(new_nodes["Math.022"].outputs[0], new_nodes["Mix.002"].inputs[0])
    tree_links.new(new_nodes["Mix.002"].outputs[0], new_nodes["Vector Math.012"].inputs[3])
    tree_links.new(new_nodes["Math.023"].outputs[0], new_nodes["Mix.003"].inputs[2])
    tree_links.new(new_nodes["Vector Math.003"].outputs[0], new_nodes["Vector Math.016"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[2], new_nodes["Vector Math.016"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[3], new_nodes["Mix.003"].inputs[3])
    tree_links.new(new_nodes["Raycast"].outputs[3], new_nodes["Math.023"].inputs[0])
    tree_links.new(new_nodes["Mix.003"].outputs[0], new_nodes["Math.014"].inputs[1])
    tree_links.new(new_nodes["Vector Math.007"].outputs[0], new_nodes["Vector Math.012"].inputs[0])
    tree_links.new(new_nodes["Vector Math.012"].outputs[0], new_nodes["Vector Math.008"].inputs[0])
    tree_links.new(new_nodes["Math.022"].outputs[0], new_nodes["Mix.004"].inputs[0])
    tree_links.new(new_nodes["Math.017"].outputs[0], new_nodes["Mix.004"].inputs[3])
    tree_links.new(new_nodes["Mix.004"].outputs[0], new_nodes["Math.016"].inputs[1])
    tree_links.new(new_nodes["Mix.004"].outputs[0], new_nodes["Math.019"].inputs[1])
    tree_links.new(new_nodes["Vector Math.014"].outputs[1], new_nodes["Math.024"].inputs[0])
    tree_links.new(new_nodes["Math.024"].outputs[0], new_nodes["Mix.005"].inputs[0])
    tree_links.new(new_nodes["Math.024"].outputs[0], new_nodes["Mix.007"].inputs[0])
    tree_links.new(new_nodes["Vector Math.015"].outputs[0], new_nodes["Vector Math.014"].inputs[1])
    tree_links.new(new_nodes["Vector Math.015"].outputs[0], new_nodes["Raycast.001"].inputs[7])
    tree_links.new(new_nodes["Mix.007"].outputs[0], new_nodes["Vector Math.013"].inputs[3])
    tree_links.new(new_nodes["Raycast.001"].outputs[2], new_nodes["Vector Math.014"].inputs[0])
    tree_links.new(new_nodes["Math.025"].outputs[0], new_nodes["Mix.005"].inputs[2])
    tree_links.new(new_nodes["Math.024"].outputs[0], new_nodes["Mix.006"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.025"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Mix.005"].inputs[3])
    tree_links.new(new_nodes["Position.006"].outputs[0], new_nodes["Vector Math.017"].inputs[1])
    tree_links.new(new_nodes["Vector Math.017"].outputs[0], new_nodes["Vector Math.015"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.017"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.026"].inputs[0])
    tree_links.new(new_nodes["Math.026"].outputs[0], new_nodes["Raycast.001"].inputs[8])
    tree_links.new(new_nodes["Mix.005"].outputs[0], new_nodes["Math"].inputs[1])
    tree_links.new(new_nodes["Math.007"].outputs[0], new_nodes["Mix.006"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Raycast.001"].inputs[0])
    tree_links.new(new_nodes["Mix.006"].outputs[0], new_nodes["Math.008"].inputs[1])
    tree_links.new(new_nodes["Mix.006"].outputs[0], new_nodes["Math.005"].inputs[1])
    tree_links.new(new_nodes["Vector Math.002"].outputs[0], new_nodes["Vector Math.013"].inputs[0])
    tree_links.new(new_nodes["Vector Math.013"].outputs[0], new_nodes["Vector Math.005"].inputs[0])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_node_group

def create_node_group_node_directional_thick_shrinkwrap(node_tree, override_create):
    ensure_node_group(override_create, DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME, 'GeometryNodeTree',
                      create_prereq_shrinkwrap_node_group)
    # create group node that will do the work
    node = node_tree.nodes.new(type='GeometryNodeGroup')
    node.location = (node_tree.view_center[0]/2.5, node_tree.view_center[1]/2.5)
    node.node_tree = bpy.data.node_groups.get(DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME)
