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

from .node_other import ensure_node_group
from .shrinkwrap import (DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME, DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME,
    SHRINKWRAP_GEO_NG_NAME, THICK_SHRINKWRAP_GEO_NG_NAME, create_prereq_shrinkwrap_node_group)

def create_obj_mod_geo_nodes_directional_shrinkwrap(node_group):
    # initialize variables
    new_nodes = {}
    node_group.inputs.clear()
    node_group.outputs.clear()
    node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.000000
    node_group.inputs.new(type='NodeSocketObject', name="Solid Target")
    node_group.inputs.new(type='NodeSocketObject', name="Direction Target")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input.default_value = 0.000000
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Direction Factor")
    new_input.min_value = 0.000000
    new_input.max_value = 1.000000
    new_input.default_value = 1.000000
    new_input = node_group.inputs.new(type='NodeSocketFloatDistance', name="Solid Ray Length")
    new_input.min_value = 0.000000
    new_input.default_value = 10.000000
    node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = node_group.nodes
    # delete all nodes
    tree_nodes.clear()

    # create nodes
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -120)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info"] = node

    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -320)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info.001"] = node

    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (-780, -80)
    node.node_tree = bpy.data.node_groups.get(DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME)
    new_nodes["Group"] = node

    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1180, -80)
    new_nodes["Group Input"] = node

    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (-500, -80)
    new_nodes["Group Output"] = node

    # create links
    tree_links = node_group.links
    tree_links.new(new_nodes["Group"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Group"].inputs[1])
    tree_links.new(new_nodes["Object Info"].outputs[3], new_nodes["Group"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Object Info"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Object Info.001"].inputs[0])
    tree_links.new(new_nodes["Object Info.001"].outputs[3], new_nodes["Group"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Group"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Group"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Group"].inputs[5])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Group"].inputs[6])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Group"].inputs[7])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Group"].inputs[8])
    tree_links.new(new_nodes["Group Input"].outputs[9], new_nodes["Group"].inputs[9])

    # deselect all new nodes
    for n in new_nodes.values(): n.select = False

def create_obj_directional_shrinkwrap(ob, override_create):
    ensure_node_group(override_create, DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME, 'GeometryNodeTree',
                      create_prereq_shrinkwrap_node_group)
    geo_nodes_mod = ob.modifiers.new(name="Directional Shrinkwrap Geometry Nodes", type='NODES')
    if geo_nodes_mod.node_group is None:
        node_group = bpy.data.node_groups.new(name="DirectionalShrinkwrapGeometryNodes", type='GeometryNodeTree')
    else:
        # copy ref to node_group, and remove modifier's ref to node_group, so that default values can be
        # populated
        node_group = geo_nodes_mod.node_group
        geo_nodes_mod.node_group = None
    create_obj_mod_geo_nodes_directional_shrinkwrap(node_group)
    # assign node_group to Geometry Nodes modifier, which will populate modifier's default input
    # values from node_group's default input values
    geo_nodes_mod.node_group = node_group

class AMH2B_OT_CreateObjModDirectionalShrinkwrap(bpy.types.Operator):
    bl_description = "Add geometry nodes modifier to active Mesh object to project one geometry onto " \
        "another geometry. Projected geometry is optionally moved towards 'direction target' instead of original " \
        "'solid target'"
    bl_idname = "amh2b.obj_mod_create_directional_shrinkwrap"
    bl_label = "Directional Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'MESH'

    def execute(self, context):
        create_obj_directional_shrinkwrap(context.active_object, context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

def create_obj_mod_geo_nodes_directional_thick_shrinkwrap(node_group):
    # initialize variables
    new_nodes = {}
    node_group.inputs.clear()
    node_group.outputs.clear()
    node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.000000
    node_group.inputs.new(type='NodeSocketObject', name="Solid Target")
    node_group.inputs.new(type='NodeSocketObject', name="Direction Target")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input.default_value = 0.000000
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Thick Factor")
    new_input.default_value = 1.000000
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Direction Factor")
    new_input.min_value = 0.000000
    new_input.max_value = 1.000000
    new_input.default_value = 1.000000
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Solid Ray Length")
    new_input.min_value = 0.000000
    new_input.default_value = 10.000000
    node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = node_group.nodes
    # delete all nodes
    tree_nodes.clear()

    # create nodes
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -320)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info.001"] = node

    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -120)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info"] = node

    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (-780, -80)
    node.node_tree = bpy.data.node_groups.get(DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME)
    new_nodes["Group"] = node

    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1180, -80)
    new_nodes["Group Input"] = node

    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (-480, -80)
    new_nodes["Group Output"] = node

    # create links
    tree_links = node_group.links
    tree_links.new(new_nodes["Group"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Group"].inputs[1])
    tree_links.new(new_nodes["Object Info"].outputs[3], new_nodes["Group"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Object Info"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Object Info.001"].inputs[0])
    tree_links.new(new_nodes["Object Info.001"].outputs[3], new_nodes["Group"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Group"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Group"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Group"].inputs[5])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Group"].inputs[6])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Group"].inputs[7])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Group"].inputs[8])
    tree_links.new(new_nodes["Group Input"].outputs[9], new_nodes["Group"].inputs[9])
    tree_links.new(new_nodes["Group Input"].outputs[10], new_nodes["Group"].inputs[10])

    # deselect all new nodes
    for n in new_nodes.values(): n.select = False

def create_obj_directional_thick_shrinkwrap(ob, override_create):
    ensure_node_group(override_create, DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME, 'GeometryNodeTree',
                      create_prereq_shrinkwrap_node_group)
    geo_nodes_mod = ob.modifiers.new(name="Directional Thick Shrinkwrap Geometry Nodes", type='NODES')
    if geo_nodes_mod.node_group is None:
        node_group = bpy.data.node_groups.new(name="DirectionalThickShrinkwrapGeometryNodes",
                                              type='GeometryNodeTree')
    else:
        # copy ref to node_group, and remove modifier's ref to node_group, so that default values can be
        # populated
        node_group = geo_nodes_mod.node_group
        geo_nodes_mod.node_group = None
    create_obj_mod_geo_nodes_directional_thick_shrinkwrap(node_group)
    # assign node_group to Geometry Nodes modifier, which will populate modifier's default input
    # values from node_group's default input values
    geo_nodes_mod.node_group = node_group

class AMH2B_OT_CreateObjModDirectionalThickShrinkwrap(bpy.types.Operator):
    bl_description = "Add geometry nodes modifier to active Mesh object to project one geometry onto " \
        "another geometry. Projected geometry is optionally moved towards 'direction target' instead of original " \
        "'solid target', with projected 'thickness' retained"
    bl_idname = "amh2b.obj_mod_create_directional_thick_shrinkwrap"
    bl_label = "Directional Thick Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'MESH'

    def execute(self, context):
        create_obj_directional_thick_shrinkwrap(context.active_object, context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

def create_obj_mod_geo_nodes_shrinkwrap(node_group):
    # initialize variables
    new_nodes = {}
    node_group.inputs.clear()
    node_group.outputs.clear()
    node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.000000
    new_input = node_group.inputs.new(type='NodeSocketObject', name="Solid Target")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input.default_value = 0.000000
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = node_group.nodes
    # delete all nodes
    tree_nodes.clear()

    # create nodes
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -120)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info"] = node

    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (-780, -80)
    node.node_tree = bpy.data.node_groups.get(SHRINKWRAP_GEO_NG_NAME)
    new_nodes["Group"] = node

    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1180, -80)
    new_nodes["Group Input"] = node

    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (-500, -80)
    new_nodes["Group Output"] = node

    # create links
    tree_links = node_group.links
    tree_links.new(new_nodes["Group"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Group"].inputs[1])
    tree_links.new(new_nodes["Object Info"].outputs[3], new_nodes["Group"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Object Info"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Group"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Group"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Group"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Group"].inputs[5])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Group"].inputs[6])

    # deselect all new nodes
    for n in new_nodes.values(): n.select = False

def create_obj_shrinkwrap(ob, override_create):
    ensure_node_group(override_create, SHRINKWRAP_GEO_NG_NAME, 'GeometryNodeTree',
                      create_prereq_shrinkwrap_node_group)
    geo_nodes_mod = ob.modifiers.new(name="Shrinkwrap Geometry Nodes", type='NODES')
    if geo_nodes_mod.node_group is None:
        node_group = bpy.data.node_groups.new(name="ShrinkwrapGeometryNodes", type='GeometryNodeTree')
    else:
        # copy ref to node_group, and remove modifier's ref to node_group, so that default values can be
        # populated
        node_group = geo_nodes_mod.node_group
        geo_nodes_mod.node_group = None
    create_obj_mod_geo_nodes_shrinkwrap(node_group)
    # assign node_group to Geometry Nodes modifier, which will populate modifier's default input
    # values from node_group's default input values
    geo_nodes_mod.node_group = node_group

class AMH2B_OT_CreateObjModShrinkwrap(bpy.types.Operator):
    bl_description = "Add geometry nodes modifier to active Mesh object to project one geometry onto " \
        "another geometry"
    bl_idname = "amh2b.obj_mod_create_shrinkwrap"
    bl_label = "Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'MESH'

    def execute(self, context):
        create_obj_shrinkwrap(context.active_object, context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

def create_obj_mod_geo_nodes_thick_shrinkwrap(node_group):
    # initialize variables
    new_nodes = {}
    node_group.inputs.clear()
    node_group.outputs.clear()
    node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Factor")
    new_input.default_value = 1.000000
    node_group.inputs.new(type='NodeSocketObject', name="Solid Target")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
    new_input.default_value = 0.000000
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
    new_input.default_value = 3.4028234663852886e+38
    node_group.inputs.new(type='NodeSocketFloat', name="Distance")
    node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_input = node_group.inputs.new(type='NodeSocketFloat', name="Thick Factor")
    new_input.default_value = 1.000000
    node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = node_group.nodes
    # delete all nodes
    tree_nodes.clear()

    # create nodes
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -120)
    node.transform_space = "RELATIVE"
    node.inputs[1].default_value = False
    new_nodes["Object Info"] = node

    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (-780, -80)
    node.node_tree = bpy.data.node_groups.get(THICK_SHRINKWRAP_GEO_NG_NAME)
    new_nodes["Group"] = node

    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1180, -80)
    new_nodes["Group Input"] = node

    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (-500, -80)
    new_nodes["Group Output"] = node

    # create links
    tree_links = node_group.links
    tree_links.new(new_nodes["Group"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Group"].inputs[1])
    tree_links.new(new_nodes["Object Info"].outputs[3], new_nodes["Group"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Object Info"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Group"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Group"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Group"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Group"].inputs[5])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Group"].inputs[6])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Group"].inputs[7])

    # deselect all new nodes
    for n in new_nodes.values(): n.select = False

def create_obj_thick_shrinkwrap(ob, override_create):
    ensure_node_group(override_create, THICK_SHRINKWRAP_GEO_NG_NAME, 'GeometryNodeTree',
                      create_prereq_shrinkwrap_node_group)
    geo_nodes_mod = ob.modifiers.new(name="Thick Shrinkwrap Geometry Nodes", type='NODES')
    if geo_nodes_mod.node_group is None:
        node_group = bpy.data.node_groups.new(name="ThickShrinkwrapGeometryNodes", type='GeometryNodeTree')
    else:
        # copy ref to node_group, and remove modifier's ref to node_group, so that default values can be
        # populated
        node_group = geo_nodes_mod.node_group
        geo_nodes_mod.node_group = None
    create_obj_mod_geo_nodes_thick_shrinkwrap(node_group)
    # assign node_group to Geometry Nodes modifier, which will populate modifier's default input
    # values from node_group's default input values
    geo_nodes_mod.node_group = node_group

class AMH2B_OT_CreateObjModThickShrinkwrap(bpy.types.Operator):
    bl_description = "Add geometry nodes modifier to active Mesh object to project one geometry onto " \
        "another geometry. Projected geometry will retain it's 'thickness' after projection, by way of secondary " \
        "'nearness' check"
    bl_idname = "amh2b.obj_mod_create_thick_shrinkwrap"
    bl_label = "Thick Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'MESH'

    def execute(self, context):
        create_obj_thick_shrinkwrap(context.active_object, context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}
