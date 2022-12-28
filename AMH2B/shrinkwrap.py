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

from .node_other import ensure_node_group

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
    # initialize variables
    new_nodes = {}
    new_node_group = bpy.data.node_groups.new(name=SHRINKWRAP_GEO_NG_NAME, type='GeometryNodeTree')
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Target Solid")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input.default_value = 0.000000
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    new_node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Relative Factor")
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()

    # create nodes
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-80, 100)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math.005"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Delta"
    node.location = (-80, -160)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.007"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-80, -300)
    new_nodes["Position.001"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Output"
    node.location = (-80, 240)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.006"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (-300, 80)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.005"] = node

    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Solid Nearest"
    node.location = (-300, -100)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (-80, -40)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.004"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (120, 100)
    new_nodes["Position.002"] = node

    node = tree_nodes.new(type="GeometryNodeSetPosition")
    node.location = (120, 540)
    new_nodes["Set Position"] = node

    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (340, 540)
    new_nodes["Group Output"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (120, 240)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.001"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-300, 240)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Apply Factor"
    node.location = (120, 380)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-300, -260)
    new_nodes["Position"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-300, 400)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.009"] = node

    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-560, 200)
    new_nodes["Group Input"] = node

    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Set Position"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Set Position"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.005"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.005"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.007"].inputs[1])
    tree_links.new(new_nodes["Vector Math.007"].outputs[0], new_nodes["Vector Math.004"].inputs[0])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Vector Math.007"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.006"].inputs[0])
    tree_links.new(new_nodes["Vector Math.004"].outputs[0], new_nodes["Vector Math.005"].inputs[0])
    tree_links.new(new_nodes["Vector Math.005"].outputs[0], new_nodes["Vector Math.006"].inputs[1])
    tree_links.new(new_nodes["Vector Math.006"].outputs[0], new_nodes["Vector Math.001"].inputs[0])
    tree_links.new(new_nodes["Position.002"].outputs[0], new_nodes["Vector Math.001"].inputs[1])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Set Position"].inputs[3])
    tree_links.new(new_nodes["Math.005"].outputs[0], new_nodes["Math"].inputs[1])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Math.009"].inputs[1])
    tree_links.new(new_nodes["Math.009"].outputs[0], new_nodes["Vector Math.005"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math.005"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Vector Math"].inputs[3])
    tree_links.new(new_nodes["Vector Math.001"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Math.009"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math"].inputs[0])

    # deselect all new nodes
    for n in new_nodes.values(): n.select = False

    return new_node_group

def create_node_group_node_shrinkwrap(node_tree, override_create):
    ensure_node_group(override_create, SHRINKWRAP_GEO_NG_NAME, 'GeometryNodeTree', create_prereq_shrinkwrap_node_group)

    # create group node that will do the work
    node = node_tree.nodes.new(type='GeometryNodeGroup')
    node.location = (node_tree.view_center[0]/2.5, node_tree.view_center[1]/2.5)
    node.node_tree = bpy.data.node_groups.get(SHRINKWRAP_GEO_NG_NAME)

class AMH2B_CreateGeoNodesShrinkwrap(Operator):
    bl_description = "Create Shrinkwrap group node, to project one geometry onto another geometry"
    bl_idname = "amh2b.geo_nodes_create_shrinkwrap"
    bl_label = "Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.space_data
        return s.type == 'NODE_EDITOR' and s.node_tree != None and s.tree_type == 'GeometryNodeTree'

    def execute(self, context):
        create_node_group_node_shrinkwrap(context.space_data.edit_tree, context.scene.Amh2bPropNodesOverrideCreate)
        return {'FINISHED'}

def create_geo_ng_thick_shrinkwrap():
    # initialize variables
    new_nodes = {}
    new_node_group = bpy.data.node_groups.new(name=THICK_SHRINKWRAP_GEO_NG_NAME, type='GeometryNodeTree')
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.0
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Target Solid")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input.default_value = 0.000000
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    new_node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Thick Factor")
    new_input.default_value = 1.0
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()

    # create nodes
    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 40)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.003"] = node

    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Self Nearest Solid Nearest"
    node.location = (-40, -120)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.001"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 680)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (220, 200)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.001"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (220, 520)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.009"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (220, 360)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.002"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (440, 380)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math.005"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Delta"
    node.location = (440, 120)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.007"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (440, -20)
    new_nodes["Position.001"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Output"
    node.location = (440, 520)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.006"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (440, 240)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.004"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (660, 80)
    new_nodes["Position.002"] = node

    node = tree_nodes.new(type="GeometryNodeSetPosition")
    node.location = (660, 520)
    new_nodes["Set Position"] = node

    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (880, 520)
    new_nodes["Group Output"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (660, 220)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.001"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Apply Factor"
    node.location = (660, 360)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 200)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.006"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 360)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.007"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 520)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.004"] = node

    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Solid Nearest"
    node.location = (-260, -120)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-260, -280)
    new_nodes["Position"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (-260, 500)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.005"] = node

    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-560, 320)
    new_nodes["Group Input"] = node

    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Set Position"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Set Position"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.005"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.005"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.007"].inputs[1])
    tree_links.new(new_nodes["Vector Math.007"].outputs[0], new_nodes["Vector Math.004"].inputs[0])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Vector Math.007"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.006"].inputs[0])
    tree_links.new(new_nodes["Vector Math.004"].outputs[0], new_nodes["Vector Math.005"].inputs[0])
    tree_links.new(new_nodes["Vector Math.005"].outputs[0], new_nodes["Vector Math.006"].inputs[1])
    tree_links.new(new_nodes["Vector Math.006"].outputs[0], new_nodes["Vector Math.001"].inputs[0])
    tree_links.new(new_nodes["Position.002"].outputs[0], new_nodes["Vector Math.001"].inputs[1])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Set Position"].inputs[3])
    tree_links.new(new_nodes["Math.005"].outputs[0], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Math.009"].inputs[0])
    tree_links.new(new_nodes["Math.009"].outputs[0], new_nodes["Vector Math.005"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math.005"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Vector Math"].inputs[3])
    tree_links.new(new_nodes["Vector Math.001"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Geometry Proximity.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Geometry Proximity.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Math.002"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Math.009"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.003"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[1], new_nodes["Math.003"].inputs[1])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Math.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Math.001"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.006"].inputs[0])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Math.006"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.007"].inputs[0])
    tree_links.new(new_nodes["Math.006"].outputs[0], new_nodes["Math.007"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.004"].inputs[0])
    tree_links.new(new_nodes["Math.007"].outputs[0], new_nodes["Math.004"].inputs[1])
    tree_links.new(new_nodes["Math.004"].outputs[0], new_nodes["Math"].inputs[1])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])

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

class AMH2B_CreateGeoNodesThickShrinkwrap(Operator):
    bl_description = "Create Thick Shrinkwrap group node, to project one geometry onto another geometry. Projected " \
        "geometry will retain it's 'thickness' after projection, by way of secondary 'nearness' check"
    bl_idname = "amh2b.geo_nodes_create_thick_shrinkwrap"
    bl_label = "Thick Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.space_data
        return s.type == 'NODE_EDITOR' and s.node_tree != None and s.tree_type == 'GeometryNodeTree'

    def execute(self, context):
        create_node_group_node_thick_shrinkwrap(context.space_data.edit_tree,
                                                context.scene.Amh2bPropNodesOverrideCreate)
        return {'FINISHED'}

def create_geo_ng_directional_shrinkwrap():
    # initialize variables
    new_nodes = {}
    new_node_group = bpy.data.node_groups.new(name=DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME, type='GeometryNodeTree')
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.0
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Solid Target")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Direction Target")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input.default_value = 0.000000
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    new_node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Direction Factor")
    new_input.min_value = 0.0
    new_input.max_value = 1.0
    new_input.default_value = 1.0
    new_input = new_node_group.inputs.new(type='NodeSocketFloatDistance', name="Solid Ray Length")
    new_input.min_value = 0.0
    new_input.default_value = 10.0
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()

    # create nodes
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Solid Nearest"
    node.location = (-640, -60)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-640, -220)
    new_nodes["Position"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-420, 140)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math.005"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Delta"
    node.location = (-420, -120)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.007"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-420, -260)
    new_nodes["Position.001"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Output"
    node.location = (-420, 280)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.006"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (-420, 0)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.004"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (-640, 120)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.005"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-640, 280)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-640, 440)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.009"] = node

    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-920, 240)
    new_nodes["Group Input"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (340, 460)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math.008"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (340, 60)
    new_nodes["Position.005"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Output"
    node.location = (340, 600)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.010"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Direction"
    node.location = (340, 320)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.011"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Delta"
    node.location = (340, 200)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.009"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (120, 280)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.006"] = node

    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Direction Nearest"
    node.location = (-60, -380)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.001"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-60, -240)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.002"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-240, -380)
    new_nodes["Position.003"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (120, -220)
    new_nodes["Position.004"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-60, -120)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.003"] = node

    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.location = (120, 100)
    node.data_type = "FLOAT"
    node.mapping = "NEAREST"
    new_nodes["Raycast"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (340, 840)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.002"] = node

    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (980, 1280)
    new_nodes["Group Output"] = node

    node = tree_nodes.new(type="GeometryNodeSetPosition")
    node.location = (760, 1280)
    new_nodes["Set Position"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (760, 840)
    new_nodes["Position.002"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (760, 980)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.001"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Apply Factor"
    node.location = (760, 1120)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math"] = node

    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Apply Direction Factor"
    node.location = (560, 980)
    node.clamp = True
    node.data_type = "FLOAT_VECTOR"
    node.interpolation_type = "LINEAR"
    node.inputs[0].default_value = 1.000000
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 1.000000
    node.inputs[3].default_value = 0.000000
    node.inputs[4].default_value = 1.000000
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.0, 0.0, 0.0)
    node.inputs[8].default_value = (1.0, 1.0, 1.0)
    node.inputs[11].default_value = (4.0, 4.0, 4.0)
    new_nodes["Map Range"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (120, 600)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.010"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (120, 440)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.001"] = node

    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Set Position"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Set Position"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math.005"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.005"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.007"].inputs[1])
    tree_links.new(new_nodes["Vector Math.007"].outputs[0], new_nodes["Vector Math.004"].inputs[0])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Vector Math.007"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.006"].inputs[0])
    tree_links.new(new_nodes["Vector Math.004"].outputs[0], new_nodes["Vector Math.005"].inputs[0])
    tree_links.new(new_nodes["Vector Math.005"].outputs[0], new_nodes["Vector Math.006"].inputs[1])
    tree_links.new(new_nodes["Position.002"].outputs[0], new_nodes["Vector Math.001"].inputs[1])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Set Position"].inputs[3])
    tree_links.new(new_nodes["Math.005"].outputs[0], new_nodes["Math"].inputs[1])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Math.009"].inputs[1])
    tree_links.new(new_nodes["Math.009"].outputs[0], new_nodes["Vector Math.005"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.005"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Vector Math"].inputs[3])
    tree_links.new(new_nodes["Vector Math.001"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])
    tree_links.new(new_nodes["Position.003"].outputs[0], new_nodes["Geometry Proximity.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Geometry Proximity.001"].inputs[0])
    tree_links.new(new_nodes["Position.004"].outputs[0], new_nodes["Raycast"].inputs[6])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[0], new_nodes["Vector Math.002"].inputs[0])
    tree_links.new(new_nodes["Position.003"].outputs[0], new_nodes["Vector Math.002"].inputs[1])
    tree_links.new(new_nodes["Vector Math.002"].outputs[0], new_nodes["Vector Math.003"].inputs[0])
    tree_links.new(new_nodes["Vector Math.003"].outputs[0], new_nodes["Raycast"].inputs[7])
    tree_links.new(new_nodes["Group Input"].outputs[9], new_nodes["Raycast"].inputs[8])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Raycast"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.009"].inputs[0])
    tree_links.new(new_nodes["Vector Math.009"].outputs[0], new_nodes["Vector Math.011"].inputs[0])
    tree_links.new(new_nodes["Position.005"].outputs[0], new_nodes["Vector Math.009"].inputs[0])
    tree_links.new(new_nodes["Vector Math.011"].outputs[0], new_nodes["Vector Math.008"].inputs[0])
    tree_links.new(new_nodes["Vector Math.008"].outputs[0], new_nodes["Vector Math.010"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Vector Math.009"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math.006"].inputs[2])
    tree_links.new(new_nodes["Math.006"].outputs[0], new_nodes["Math.001"].inputs[1])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Math.010"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.006"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.010"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[3], new_nodes["Math.006"].inputs[1])
    tree_links.new(new_nodes["Math.010"].outputs[0], new_nodes["Vector Math.008"].inputs[3])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Vector Math.010"].inputs[0])
    tree_links.new(new_nodes["Vector Math.006"].outputs[0], new_nodes["Map Range"].inputs[9])
    tree_links.new(new_nodes["Vector Math.010"].outputs[0], new_nodes["Map Range"].inputs[10])
    tree_links.new(new_nodes["Map Range"].outputs[1], new_nodes["Vector Math.001"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[0], new_nodes["Math.002"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Map Range"].inputs[6])

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

class AMH2B_CreateGeoNodesDirectionalShrinkwrap(Operator):
    bl_description = "Create Directional Shrinkwrap group node, to project one geometry onto another geometry. " \
        "Projected geometry is optionally moved towards 'direction target' instead of original 'solid target'"
    bl_idname = "amh2b.geo_nodes_create_directional_shrinkwrap"
    bl_label = "Directional Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.space_data
        return s.type == 'NODE_EDITOR' and s.node_tree != None and s.tree_type == 'GeometryNodeTree'

    def execute(self, context):
        create_node_group_node_directional_shrinkwrap(context.space_data.edit_tree,
                                                      context.scene.Amh2bPropNodesOverrideCreate)
        return {'FINISHED'}

def create_geo_ng_directional_thick_shrinkwrap():
    # initialize variables
    new_nodes = {}
    new_node_group = bpy.data.node_groups.new(name=DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME, type='GeometryNodeTree')
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.0
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Solid Target")
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Direction Target")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input.default_value = 0.000000
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    new_node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Thick Factor")
    new_input.default_value = 1.0
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Direction Factor")
    new_input.min_value = 0.0
    new_input.max_value = 1.0
    new_input.default_value = 1.0
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Solid Ray Length")
    new_input.min_value = 0.0
    new_input.default_value = 10.0
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()

    # create nodes
    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Delta"
    node.location = (440, 120)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.007"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (440, -20)
    new_nodes["Position.001"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Output"
    node.location = (440, 520)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.006"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Solid Away Direction"
    node.location = (440, 240)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.004"] = node

    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Solid Nearest"
    node.location = (-260, -120)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (-260, -280)
    new_nodes["Position"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (820, -140)
    new_nodes["Position.004"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (640, -40)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.003"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (640, -160)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.002"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (460, -300)
    new_nodes["Position.003"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (-260, 500)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.005"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 680)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 520)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.004"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (220, 520)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.009"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (220, 360)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.002"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (220, 200)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.001"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 360)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.007"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 40)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.003"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (-40, 200)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.006"] = node

    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Self Nearest Solid Nearest"
    node.location = (-40, -120)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.001"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (440, 380)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math.005"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1040, 520)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.013"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1040, 360)
    node.operation = "MINIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.014"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1300, 360)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.015"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1040, 720)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.012"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Output"
    node.location = (1520, 540)
    node.operation = "ADD"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.010"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Direction"
    node.location = (1520, 260)
    node.operation = "NORMALIZE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.011"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (1520, 400)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math.014"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (1920, 800)
    new_nodes["Position.006"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (1920, 940)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.012"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Apply Factor"
    node.location = (1920, 1080)
    node.operation = "SCALE"
    node.inputs[1].default_value = (0.0, 0.0, 0.0)
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    new_nodes["Vector Math.013"] = node

    node = tree_nodes.new(type="GeometryNodeSetPosition")
    node.location = (1920, 1240)
    new_nodes["Set Position.001"] = node

    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (2140, 1240)
    new_nodes["Group Output.001"] = node

    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Apply Direction Factor"
    node.location = (1720, 880)
    node.clamp = True
    node.data_type = "FLOAT_VECTOR"
    node.interpolation_type = "LINEAR"
    node.inputs[0].default_value = 1.000000
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 1.000000
    node.inputs[3].default_value = 0.000000
    node.inputs[4].default_value = 1.000000
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.0, 0.0, 0.0)
    node.inputs[8].default_value = (1.0, 1.0, 1.0)
    node.inputs[11].default_value = (4.0, 4.0, 4.0)
    new_nodes["Map Range"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1040, 200)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.018"] = node

    node = tree_nodes.new(type="GeometryNodeInputPosition")
    node.location = (1520, 0)
    new_nodes["Position.005"] = node

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.label = "Direction Away Delta"
    node.location = (1520, 140)
    node.operation = "SUBTRACT"
    node.inputs[2].default_value = (0.0, 0.0, 0.0)
    node.inputs[3].default_value = 1.000000
    new_nodes["Vector Math.009"] = node

    node = tree_nodes.new(type="GeometryNodeRaycast")
    node.location = (820, 180)
    node.data_type = "FLOAT"
    node.mapping = "NEAREST"
    new_nodes["Raycast"] = node

    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Direction Nearest"
    node.location = (640, -300)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.002"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Relative Distance"
    node.location = (820, 360)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.010"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1300, 200)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.016"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1300, 40)
    node.operation = "MULTIPLY_ADD"
    node.use_clamp = False
    new_nodes["Math.017"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1040, -120)
    node.operation = "MAXIMUM"
    node.use_clamp = False
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.021"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1040, -280)
    node.operation = "SUBTRACT"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.019"] = node

    node = tree_nodes.new(type="GeometryNodeProximity")
    node.label = "Self Nearest Solid Nearest"
    node.location = (1040, -440)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.003"] = node

    node = tree_nodes.new(type="ShaderNodeMath")
    node.location = (1040, 40)
    node.operation = "MULTIPLY"
    node.use_clamp = False
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.020"] = node

    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-580, 260)
    new_nodes["Group Input"] = node

    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math.005"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.005"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.007"].inputs[1])
    tree_links.new(new_nodes["Vector Math.007"].outputs[0], new_nodes["Vector Math.004"].inputs[0])
    tree_links.new(new_nodes["Position.001"].outputs[0], new_nodes["Vector Math.007"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Vector Math.006"].inputs[0])
    tree_links.new(new_nodes["Vector Math.004"].outputs[0], new_nodes["Vector Math.005"].inputs[0])
    tree_links.new(new_nodes["Vector Math.005"].outputs[0], new_nodes["Vector Math.006"].inputs[1])
    tree_links.new(new_nodes["Math.005"].outputs[0], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Math.009"].inputs[0])
    tree_links.new(new_nodes["Math.009"].outputs[0], new_nodes["Vector Math.005"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.005"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[0], new_nodes["Geometry Proximity.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Geometry Proximity.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Math.002"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Math.009"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Math.003"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[1], new_nodes["Math.003"].inputs[1])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Math.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.001"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.006"].inputs[0])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Math.006"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.007"].inputs[0])
    tree_links.new(new_nodes["Math.006"].outputs[0], new_nodes["Math.007"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.004"].inputs[0])
    tree_links.new(new_nodes["Math.007"].outputs[0], new_nodes["Math.004"].inputs[1])
    tree_links.new(new_nodes["Math.004"].outputs[0], new_nodes["Math"].inputs[1])
    tree_links.new(new_nodes["Position"].outputs[0], new_nodes["Geometry Proximity"].inputs[1])
    tree_links.new(new_nodes["Position.003"].outputs[0], new_nodes["Geometry Proximity.002"].inputs[1])
    tree_links.new(new_nodes["Position.004"].outputs[0], new_nodes["Raycast"].inputs[6])
    tree_links.new(new_nodes["Geometry Proximity.002"].outputs[0], new_nodes["Vector Math.002"].inputs[0])
    tree_links.new(new_nodes["Position.003"].outputs[0], new_nodes["Vector Math.002"].inputs[1])
    tree_links.new(new_nodes["Vector Math.002"].outputs[0], new_nodes["Vector Math.003"].inputs[0])
    tree_links.new(new_nodes["Vector Math.003"].outputs[0], new_nodes["Raycast"].inputs[7])
    tree_links.new(new_nodes["Vector Math.009"].outputs[0], new_nodes["Vector Math.011"].inputs[0])
    tree_links.new(new_nodes["Position.005"].outputs[0], new_nodes["Vector Math.009"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Vector Math.009"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[3], new_nodes["Math.010"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Vector Math.010"].inputs[0])
    tree_links.new(new_nodes["Raycast"].outputs[0], new_nodes["Math.012"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Geometry Proximity.002"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Raycast"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[10], new_nodes["Raycast"].inputs[8])
    tree_links.new(new_nodes["Group Input"].outputs[9], new_nodes["Math.012"].inputs[0])
    tree_links.new(new_nodes["Position.006"].outputs[0], new_nodes["Vector Math.012"].inputs[1])
    tree_links.new(new_nodes["Vector Math.013"].outputs[0], new_nodes["Set Position.001"].inputs[3])
    tree_links.new(new_nodes["Vector Math.012"].outputs[0], new_nodes["Vector Math.013"].inputs[0])
    tree_links.new(new_nodes["Map Range"].outputs[1], new_nodes["Vector Math.012"].inputs[0])
    tree_links.new(new_nodes["Math.012"].outputs[0], new_nodes["Map Range"].inputs[6])
    tree_links.new(new_nodes["Vector Math.010"].outputs[0], new_nodes["Map Range"].inputs[10])
    tree_links.new(new_nodes["Vector Math.006"].outputs[0], new_nodes["Map Range"].inputs[9])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Vector Math.013"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Math.010"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Math.010"].inputs[0])
    tree_links.new(new_nodes["Math.013"].outputs[0], new_nodes["Math.015"].inputs[0])
    tree_links.new(new_nodes["Math.015"].outputs[0], new_nodes["Vector Math.014"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Geometry Proximity.003"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.017"].inputs[0])
    tree_links.new(new_nodes["Math.017"].outputs[0], new_nodes["Math.016"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.016"].inputs[0])
    tree_links.new(new_nodes["Math.016"].outputs[0], new_nodes["Math.015"].inputs[1])
    tree_links.new(new_nodes["Geometry Proximity.003"].outputs[1], new_nodes["Math.019"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Math.017"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Math.020"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.018"].inputs[0])
    tree_links.new(new_nodes["Math.020"].outputs[0], new_nodes["Math.018"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Math.014"].inputs[0])
    tree_links.new(new_nodes["Math.018"].outputs[0], new_nodes["Math.014"].inputs[1])
    tree_links.new(new_nodes["Math.014"].outputs[0], new_nodes["Math.013"].inputs[1])
    tree_links.new(new_nodes["Math.010"].outputs[0], new_nodes["Math.013"].inputs[0])
    tree_links.new(new_nodes["Vector Math.011"].outputs[0], new_nodes["Vector Math.014"].inputs[0])
    tree_links.new(new_nodes["Vector Math.014"].outputs[0], new_nodes["Vector Math.010"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[1], new_nodes["Geometry Proximity.003"].inputs[1])
    tree_links.new(new_nodes["Raycast"].outputs[3], new_nodes["Math.019"].inputs[0])
    tree_links.new(new_nodes["Set Position.001"].outputs[0], new_nodes["Group Output.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Set Position.001"].inputs[0])
    tree_links.new(new_nodes["Math.019"].outputs[0], new_nodes["Math.021"].inputs[0])
    tree_links.new(new_nodes["Math.021"].outputs[0], new_nodes["Math.017"].inputs[1])
    tree_links.new(new_nodes["Math.021"].outputs[0], new_nodes["Math.020"].inputs[1])

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

class AMH2B_CreateGeoNodesDirectionalThickShrinkwrap(Operator):
    bl_description = "Create Directional Thick Shrinkwrap group node, to project one geometry onto another " \
        "geometry. Projected geometry is optionally moved towards 'direction target' instead of original " \
        "'solid target', with projected 'thickness' retained"
    bl_idname = "amh2b.geo_nodes_create_directional_thick_shrinkwrap"
    bl_label = "Directional Thick Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.space_data
        return s.type == 'NODE_EDITOR' and s.node_tree != None and s.tree_type == 'GeometryNodeTree'

    def execute(self, context):
        create_node_group_node_directional_thick_shrinkwrap(context.space_data.edit_tree,
                                                            context.scene.Amh2bPropNodesOverrideCreate)
        return {'FINISHED'}
