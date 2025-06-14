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

from ..node_other import (set_node_io_values, create_nodetree_link)

SB_WEIGHT_GEO_NG_NAME = "WeightSoftBody Geometry Nodes"
SIGNED_NEAREST_GEO_NG_NAME = "SignedNearest_AMH2B_GeoNG"

def create_geo_ng_signed_nearest():
    new_node_group = bpy.data.node_groups.new(name=SIGNED_NEAREST_GEO_NG_NAME, type='GeometryNodeTree')
    # remove old group inputs and outputs
    if bpy.app.version >= (4, 0, 0):
        for item in new_node_group.interface.items_tree:
            if item.item_type == 'SOCKET':
                new_node_group.interface.remove(item)
    else:
        new_node_group.inputs.clear()
        new_node_group.outputs.clear()
    # create new group inputs and outputs
    if bpy.app.version >= (4, 0, 0):
        new_node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Target", in_out='INPUT')
    else:
        new_node_group.inputs.new(type='NodeSocketGeometry', name="Target")
    if bpy.app.version >= (4, 0, 0):
        new_node_group.interface.new_socket(socket_type='NodeSocketVector', name="Position", in_out='OUTPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Distance", in_out='OUTPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketVector', name="Normal", in_out='OUTPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketBool', name="Is Hit", in_out='OUTPUT')
    else:
        new_node_group.outputs.new(type='NodeSocketVector', name="Position")
        new_node_group.outputs.new(type='NodeSocketFloat', name="Distance")
        new_node_group.outputs.new(type='NodeSocketVector', name="Normal")
        new_node_group.outputs.new(type='NodeSocketBool', name="Is Hit")
    tree_nodes = new_node_group.nodes
    # delete all existing nodes before creating new nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-20, 176)
    node.operation = "SUBTRACT"
    set_node_io_values(node, True, {
        "Vector": { 2: (0.000000, 0.000000, 0.000000) },
        "Scale": { 0: 1.000000 },
        })
    new_nodes["Vector Math"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-20, 294)
    node.operation = "NORMALIZE"
    set_node_io_values(node, True, {
        "Vector": {
            1: (0.000000, 0.000000, 0.000000),
            2: (0.000000, 0.000000, 0.000000),
            },
        "Scale": { 0: 1.000000 },
        })
    new_nodes["Vector Math.001"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-20, 39)
    new_nodes["Position"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (196, 196)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    set_node_io_values(node, True, {
        "Value": {
            1: 1.100000,
            2: 0.000100,
            },
        })
    new_nodes["Math"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (196, 255)
    new_nodes["Position.001"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.location = (-235, 333)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node
    # Position
    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-235, 176)
    new_nodes["Position.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (196, 725)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    set_node_io_values(node, True, {
        "Value": {
            1: -1.000000,
            2: 0.500000,
            },
        })
    new_nodes["Math.001"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-451, 392)
    new_nodes["Group Input"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (764, 745)
    new_nodes["Group Output"] = node
    # Vector Math
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (549, 118)
    node.operation = "DOT_PRODUCT"
    set_node_io_values(node, True, {
        "Vector": { 2: (0.000000, 0.000000, 0.000000) },
        "Scale": { 0: 1.000000 },
        })
    new_nodes["Vector Math.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (549, 274)
    node.operation = "GREATER_THAN"
    node.use_clamp = False
    set_node_io_values(node, True, {
        "Value": {
            1: 0.000000,
            2: 0.500000,
            },
        })
    new_nodes["Math.002"] = node
    # Raycast
    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.location = (196, 568)
    node.data_type = "FLOAT"
    node.mapping = "INTERPOLATED"
    new_nodes["Raycast"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (549, 470)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    set_node_io_values(node, True, {
        "Value": { 2: 0.500000 },
        })
    new_nodes["Math.003"] = node
    # Mix
    node = tree_nodes.new(type="ShaderNodeMix")
    node.location = (549, 666)
    node.blend_type = "MIX"
    node.clamp_factor = True
    node.clamp_result = False
    node.data_type = "FLOAT"
    node.factor_mode = "UNIFORM"
    set_node_io_values(node, True, {
        "Factor": { 1: (0.500000, 0.500000, 0.500000) },
        "A": {
            1: (0.000000, 0.000000, 0.000000),
            2: (0.500000, 0.500000, 0.500000, 1.000000),
            },
        "B": {
            1: (0.000000, 0.000000, 0.000000),
            2: (0.500000, 0.500000, 0.500000, 1.000000),
            },
        })
    new_nodes["Mix"] = node
    # create links
    tree_links = new_node_group.links
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Target", 0, new_nodes["Geometry Proximity"], "Target", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Target", 0, new_nodes["Raycast"], "Target Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Geometry Proximity"], "Position", 0, new_nodes["Vector Math"], "Vector", 0)
    create_nodetree_link(tree_links, new_nodes["Vector Math"], "Vector", 0, new_nodes["Vector Math.001"], "Vector", 0)
    create_nodetree_link(tree_links, new_nodes["Vector Math.001"], "Vector", 0, new_nodes["Raycast"], "Ray Direction", 0)
    create_nodetree_link(tree_links, new_nodes["Geometry Proximity"], "Distance", 0, new_nodes["Math"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Math"], "Value", 0, new_nodes["Raycast"], "Ray Length", 0)
    create_nodetree_link(tree_links, new_nodes["Raycast"], "Hit Normal", 0, new_nodes["Group Output"], "Normal", 0)
    create_nodetree_link(tree_links, new_nodes["Raycast"], "Hit Normal", 0, new_nodes["Vector Math.002"], "Vector", 0)
    create_nodetree_link(tree_links, new_nodes["Vector Math.001"], "Vector", 0, new_nodes["Vector Math.002"], "Vector", 1)
    create_nodetree_link(tree_links, new_nodes["Vector Math.002"], "Value", 0, new_nodes["Math.002"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Geometry Proximity"], "Distance", 0, new_nodes["Math.001"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Mix"], "Result", 0, new_nodes["Group Output"], "Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Raycast"], "Is Hit", 0, new_nodes["Group Output"], "Is Hit", 0)
    create_nodetree_link(tree_links, new_nodes["Geometry Proximity"], "Position", 0, new_nodes["Group Output"], "Position", 0)
    create_nodetree_link(tree_links, new_nodes["Position.002"], "Position", 0, new_nodes["Geometry Proximity"], "Source Position", 0)
    create_nodetree_link(tree_links, new_nodes["Position"], "Position", 0, new_nodes["Vector Math"], "Vector", 1)
    create_nodetree_link(tree_links, new_nodes["Position.001"], "Position", 0, new_nodes["Raycast"], "Source Position", 0)
    create_nodetree_link(tree_links, new_nodes["Raycast"], "Is Hit", 0, new_nodes["Math.003"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Math.002"], "Value", 0, new_nodes["Math.003"], "Value", 1)
    create_nodetree_link(tree_links, new_nodes["Math.003"], "Value", 0, new_nodes["Mix"], "Factor", 0)
    create_nodetree_link(tree_links, new_nodes["Geometry Proximity"], "Distance", 0, new_nodes["Mix"], "A", 0)
    create_nodetree_link(tree_links, new_nodes["Math.001"], "Value", 0, new_nodes["Mix"], "B", 0)
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_node_group


def create_weight_sb_mod_geo_node_group(new_node_group):
     # remove old group inputs and outputs
    if bpy.app.version >= (4, 0, 0):
        for item in new_node_group.interface.items_tree:
            if item.item_type == 'SOCKET':
                new_node_group.interface.remove(item)
    else:
        new_node_group.inputs.clear()
        new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_in_socket = {}
    if bpy.app.version >= (4, 0, 0):
        new_node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketObject', name="Goal Object", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Goal From Min", in_out='INPUT')
        new_in_socket[3] = new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Goal From Max", in_out='INPUT')
        new_in_socket[4] = new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Goal To Min", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Goal To Max", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketObject', name="Mask Object", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Mask From Min", in_out='INPUT')
        new_in_socket[8] = new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Mask From Max", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketObject', name="Mass Object", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Mass From Min", in_out='INPUT')
        new_in_socket[11] = new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Mass From Max", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Mass To Min", in_out='INPUT')
        new_in_socket[13] = new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Mass To Max", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketObject', name="Spring Object", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Spring From Min", in_out='INPUT')
        new_in_socket[16] = new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Spring From Max", in_out='INPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Spring To Min", in_out='INPUT')
        new_in_socket[18] = new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Spring To Max", in_out='INPUT')
    else:
        new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
        new_node_group.inputs.new(type='NodeSocketObject', name="Goal Object")
        new_node_group.inputs.new(type='NodeSocketFloat', name="Goal From Min")
        new_in_socket[3] = new_node_group.inputs.new(type='NodeSocketFloat', name="Goal From Max")
        new_in_socket[4] = new_node_group.inputs.new(type='NodeSocketFloat', name="Goal To Min")
        new_node_group.inputs.new(type='NodeSocketFloat', name="Goal To Max")
        new_node_group.inputs.new(type='NodeSocketObject', name="Mask Object")
        new_node_group.inputs.new(type='NodeSocketFloat', name="Mask From Min")
        new_in_socket[8] = new_node_group.inputs.new(type='NodeSocketFloat', name="Mask From Max")
        new_node_group.inputs.new(type='NodeSocketObject', name="Mass Object")
        new_node_group.inputs.new(type='NodeSocketFloat', name="Mass From Min")
        new_in_socket[11] = new_node_group.inputs.new(type='NodeSocketFloat', name="Mass From Max")
        new_node_group.inputs.new(type='NodeSocketFloat', name="Mass To Min")
        new_in_socket[13] = new_node_group.inputs.new(type='NodeSocketFloat', name="Mass To Max")
        new_node_group.inputs.new(type='NodeSocketObject', name="Spring Object")
        new_node_group.inputs.new(type='NodeSocketFloat', name="Spring From Min")
        new_in_socket[16] = new_node_group.inputs.new(type='NodeSocketFloat', name="Spring From Max")
        new_node_group.inputs.new(type='NodeSocketFloat', name="Spring To Min")
        new_in_socket[18] = new_node_group.inputs.new(type='NodeSocketFloat', name="Spring To Max")
    new_in_socket[3].default_value = 1.000000
    new_in_socket[4].default_value = 1.000000
    new_in_socket[8].default_value = 1.000000
    new_in_socket[11].default_value = 1.000000
    new_in_socket[13].default_value = 1.000000
    new_in_socket[16].default_value = 1.000000
    new_in_socket[18].default_value = 1.000000
    if bpy.app.version >= (4, 0, 0):
        new_node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='OUTPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Goal", in_out='OUTPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Mask", in_out='OUTPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Mass", in_out='OUTPUT')
        new_node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Spring", in_out='OUTPUT')
    else:
        new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
        new_node_group.outputs.new(type='NodeSocketFloat', name="Goal")
        new_node_group.outputs.new(type='NodeSocketFloat', name="Mask")
        new_node_group.outputs.new(type='NodeSocketFloat', name="Mass")
        new_node_group.outputs.new(type='NodeSocketFloat', name="Spring")
    tree_nodes = new_node_group.nodes
    # delete all existing nodes before creating new nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (745, -20)
    new_nodes["Group Output"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Spring Map Range"
    node.location = (529, -451)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    set_node_io_values(node, True, {
        "Steps": {
            0: 4.000000,
            1: (4.000000, 4.000000, 4.000000),
            },
        "From Min": { 1: (0.000000, 0.000000, 0.000000) },
        "From Max": { 1: (1.000000, 1.000000, 1.000000) },
        "To Min": { 1: (0.000000, 0.000000, 0.000000) },
        "To Max": { 1: (1.000000, 1.000000, 1.000000) },
        })
    new_nodes["Map Range"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Spring Clamp"
    node.location = (529, -294)
    node.operation = "ADD"
    node.use_clamp = True
    set_node_io_values(node, True, {
        "Value": {
            1: 0.000000,
            2: 0.500000,
            },
        })
    new_nodes["Math"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Mass Map Range"
    node.location = (314, -412)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    set_node_io_values(node, True, {
        "Steps": {
            0: 4.000000,
            1: (4.000000, 4.000000, 4.000000),
            },
        "From Min": { 1: (0.000000, 0.000000, 0.000000) },
        "From Max": { 1: (1.000000, 1.000000, 1.000000) },
        "To Min": { 1: (0.000000, 0.000000, 0.000000) },
        "To Max": { 1: (1.000000, 1.000000, 1.000000) },
        })
    new_nodes["Map Range.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Mass Clamp"
    node.location = (314, -255)
    node.operation = "ADD"
    node.use_clamp = True
    set_node_io_values(node, True, {
        "Value": {
            1: 0.000000,
            2: 0.500000,
            },
        })
    new_nodes["Math.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Mask Clamp"
    node.location = (98, -216)
    node.operation = "GREATER_THAN"
    node.use_clamp = True
    set_node_io_values(node, True, {
        "Value": {
            1: 0.500000,
            2: 1.120000,
            },
        })
    new_nodes["Math.002"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Spring CapAttr"
    node.location = (529, -118)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    set_node_io_values(node, True, {
        "Value": {
            0: (0.000000, 0.000000, 0.000000),
            2: (0.000000, 0.000000, 0.000000, 0.000000),
            3: False,
            4: 0,
            },
        })
    new_nodes["Capture Attribute"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Mass CapAttr"
    node.location = (314, -78)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    set_node_io_values(node, True, {
        "Value": {
            0: (0.000000, 0.000000, 0.000000),
            2: (0.000000, 0.000000, 0.000000, 0.000000),
            3: False,
            4: 0,
            },
        })
    new_nodes["Capture Attribute.001"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Mask CapAttr"
    node.location = (98, -39)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    set_node_io_values(node, True, {
        "Value": {
            0: (0.000000, 0.000000, 0.000000),
            2: (0.000000, 0.000000, 0.000000, 0.000000),
            3: False,
            4: 0,
            },
        })
    new_nodes["Capture Attribute.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Goal Clamp"
    node.location = (-118, -176)
    node.operation = "ADD"
    node.use_clamp = True
    set_node_io_values(node, True, {
        "Value": {
            1: 0.000000,
            2: 0.500000,
            },
        })
    new_nodes["Math.003"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Goal CapAttr"
    node.location = (-118, 0)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    set_node_io_values(node, True, {
        "Value": {
            0: (0.000000, 0.000000, 0.000000),
            2: (0.000000, 0.000000, 0.000000, 0.000000),
            3: False,
            4: 0,
            },
        })
    new_nodes["Capture Attribute.003"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Goal Map Range"
    node.location = (-118, -333)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    set_node_io_values(node, True, {
        "Steps": {
            0: 4.000000,
            1: (4.000000, 4.000000, 4.000000),
            },
        "From Min": { 1: (0.000000, 0.000000, 0.000000) },
        "From Max": { 1: (1.000000, 1.000000, 1.000000) },
        "To Min": { 1: (0.000000, 0.000000, 0.000000) },
        "To Max": { 1: (1.000000, 1.000000, 1.000000) },
        })
    new_nodes["Map Range.002"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Mask Map Range"
    node.location = (98, -372)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    set_node_io_values(node, True, {
        "To Min": {
            0: 0.000000,
            1: (0.000000, 0.000000, 0.000000),
            },
        "To Max": {
            0: 1.000000,
            1: (1.000000, 1.000000, 1.000000),
            },
        "Steps": {
            0: 4.000000,
            1: (4.000000, 4.000000, 4.000000),
            },
        "From Min": { 1: (0.000000, 0.000000, 0.000000) },
        "From Max": { 1: (1.000000, 1.000000, 1.000000) },
        })
    new_nodes["Map Range.003"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Goal Object Info"
    node.location = (-118, -764)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (98, -627)
    node.node_tree = bpy.data.node_groups.get(SIGNED_NEAREST_GEO_NG_NAME)
    new_nodes["Group"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Goal Object Info"
    node.location = (98, -804)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info.001"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Goal Object Info"
    node.location = (314, -843)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info.002"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (314, -666)
    node.node_tree = bpy.data.node_groups.get(SIGNED_NEAREST_GEO_NG_NAME)
    new_nodes["Group.001"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (529, -706)
    node.node_tree = bpy.data.node_groups.get(SIGNED_NEAREST_GEO_NG_NAME)
    new_nodes["Group.002"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (-118, -588)
    node.node_tree = bpy.data.node_groups.get(SIGNED_NEAREST_GEO_NG_NAME)
    new_nodes["Group.003"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Goal Object Info"
    node.location = (529, -882)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info.003"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-451, -470)
    new_nodes["Group Input"] = node
    # create links
    tree_links = new_node_group.links
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Mass From Min", 0, new_nodes["Map Range.001"], "From Min", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Mass From Max", 0, new_nodes["Map Range.001"], "From Max", 0)
    create_nodetree_link(tree_links, new_nodes["Math.001"], "Value", 0, new_nodes["Capture Attribute.001"], "Value", 1)
    create_nodetree_link(tree_links, new_nodes["Capture Attribute.001"], "Attribute", 1, new_nodes["Group Output"], "Mass", 0)
    create_nodetree_link(tree_links, new_nodes["Map Range.001"], "Result", 0, new_nodes["Math.001"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Mass To Min", 0, new_nodes["Map Range.001"], "To Min", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Mass To Max", 0, new_nodes["Map Range.001"], "To Max", 0)
    create_nodetree_link(tree_links, new_nodes["Math"], "Value", 0, new_nodes["Capture Attribute"], "Value", 1)
    create_nodetree_link(tree_links, new_nodes["Map Range"], "Result", 0, new_nodes["Math"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Capture Attribute"], "Attribute", 1, new_nodes["Group Output"], "Spring", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Spring From Min", 0, new_nodes["Map Range"], "From Min", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Spring From Max", 0, new_nodes["Map Range"], "From Max", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Spring To Min", 0, new_nodes["Map Range"], "To Min", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Spring To Max", 0, new_nodes["Map Range"], "To Max", 0)
    create_nodetree_link(tree_links, new_nodes["Math.003"], "Value", 0, new_nodes["Capture Attribute.003"], "Value", 1)
    create_nodetree_link(tree_links, new_nodes["Map Range.002"], "Result", 0, new_nodes["Math.003"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Capture Attribute.003"], "Attribute", 1, new_nodes["Group Output"], "Goal", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Goal Object", 0, new_nodes["Object Info"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Goal From Min", 0, new_nodes["Map Range.002"], "From Min", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Goal From Max", 0, new_nodes["Map Range.002"], "From Max", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Goal To Min", 0, new_nodes["Map Range.002"], "To Min", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Goal To Max", 0, new_nodes["Map Range.002"], "To Max", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Geometry", 0, new_nodes["Capture Attribute.003"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Capture Attribute.001"], "Geometry", 0, new_nodes["Capture Attribute"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Capture Attribute"], "Geometry", 0, new_nodes["Group Output"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Math.002"], "Value", 0, new_nodes["Capture Attribute.002"], "Value", 1)
    create_nodetree_link(tree_links, new_nodes["Map Range.003"], "Result", 0, new_nodes["Math.002"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Capture Attribute.003"], "Geometry", 0, new_nodes["Capture Attribute.002"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Mask From Min", 0, new_nodes["Map Range.003"], "From Min", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Mask From Max", 0, new_nodes["Map Range.003"], "From Max", 0)
    create_nodetree_link(tree_links, new_nodes["Capture Attribute.002"], "Geometry", 0, new_nodes["Capture Attribute.001"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Capture Attribute.002"], "Attribute", 1, new_nodes["Group Output"], "Mask", 0)
    create_nodetree_link(tree_links, new_nodes["Group.003"], "Distance", 0, new_nodes["Map Range.002"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info"], "Geometry", 0, new_nodes["Group.003"], "Target", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info.001"], "Geometry", 0, new_nodes["Group"], "Target", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Mask Object", 0, new_nodes["Object Info.001"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Group"], "Distance", 0, new_nodes["Map Range.003"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info.002"], "Geometry", 0, new_nodes["Group.001"], "Target", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Mass Object", 0, new_nodes["Object Info.002"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Group.001"], "Distance", 0, new_nodes["Map Range.001"], "Value", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info.003"], "Geometry", 0, new_nodes["Group.002"], "Target", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Spring Object", 0, new_nodes["Object Info.003"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Group.002"], "Distance", 0, new_nodes["Map Range"], "Value", 0)
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
