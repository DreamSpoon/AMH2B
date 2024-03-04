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

from ..node_other import (ensure_node_group, set_node_io_values, create_nodetree_link)
from .shrinkwrap import (DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME, DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME,
    SHRINKWRAP_GEO_NG_NAME, THICK_SHRINKWRAP_GEO_NG_NAME, create_prereq_shrinkwrap_node_group)

def create_obj_mod_geo_nodes_shrinkwrap(node_group):
    # remove old group inputs and outputs
    if bpy.app.version >= (4, 0, 0):
        for item in node_group.interface.items_tree:
            if item.item_type == 'SOCKET':
                node_group.interface.remove(item)
    else:
        node_group.inputs.clear()
        node_group.outputs.clear()
    # create new group inputs and outputs
    new_in_socket = {}
    if bpy.app.version >= (4, 0, 0):
        node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='INPUT')
        new_in_socket[1] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Factor", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketObject', name="Solid Target", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Min Distance", in_out='INPUT')
        new_in_socket[4] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Max Distance", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Distance", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Relative Offset Factor", in_out='INPUT')
    else:
        node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
        new_in_socket[1] = node_group.inputs.new(type='NodeSocketFloat', name="Factor")
        node_group.inputs.new(type='NodeSocketObject', name="Solid Target")
        node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
        new_in_socket[4] = node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
        node_group.inputs.new(type='NodeSocketFloat', name="Distance")
        node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
    new_in_socket[1].default_value = 1.000000
    new_in_socket[4].default_value = 340282346638528859811704183484516925440.000000
    new_out_socket = {}
    if bpy.app.version >= (4, 0, 0):
        node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='OUTPUT')
    else:
        node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = node_group.nodes
    # delete all existing nodes before creating new nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -120)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1180, -80)
    new_nodes["Group Input"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (-500, -80)
    new_nodes["Group Output"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (-780, -80)
    node.node_tree = bpy.data.node_groups.get(SHRINKWRAP_GEO_NG_NAME)
    new_nodes["Group"] = node
    # create links
    tree_links = node_group.links
    create_nodetree_link(tree_links, new_nodes["Group"], "Geometry", 0, new_nodes["Group Output"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Geometry", 0, new_nodes["Group"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info"], "Geometry", 0, new_nodes["Group"], "Target Solid", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Solid Target", 0, new_nodes["Object Info"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Factor", 0, new_nodes["Group"], "Factor", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Min Distance", 0, new_nodes["Group"], "Min Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Max Distance", 0, new_nodes["Group"], "Max Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Distance", 0, new_nodes["Group"], "Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Relative Offset Factor", 0, new_nodes["Group"], "Relative Factor", 0)
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

def create_obj_mod_geo_nodes_thick_shrinkwrap(node_group):
    # remove old group inputs and outputs
    if bpy.app.version >= (4, 0, 0):
        for item in node_group.interface.items_tree:
            if item.item_type == 'SOCKET':
                node_group.interface.remove(item)
    else:
        node_group.inputs.clear()
        node_group.outputs.clear()
    # create new group inputs and outputs
    new_in_socket = {}
    if bpy.app.version >= (4, 0, 0):
        node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='INPUT')
        new_in_socket[1] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Factor", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketObject', name="Solid Target", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Min Distance", in_out='INPUT')
        new_in_socket[4] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Max Distance", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Distance", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Relative Offset Factor", in_out='INPUT')
        new_in_socket[7] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Thick Factor", in_out='INPUT')
    else:
        node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
        new_in_socket[1] = node_group.inputs.new(type='NodeSocketFloat', name="Factor")
        node_group.inputs.new(type='NodeSocketObject', name="Solid Target")
        node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
        new_in_socket[4] = node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
        node_group.inputs.new(type='NodeSocketFloat', name="Distance")
        node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
        new_in_socket[7] = node_group.inputs.new(type='NodeSocketFloat', name="Thick Factor")
    new_in_socket[1].default_value = 1.000000
    new_in_socket[4].default_value = 340282346638528859811704183484516925440.000000
    new_in_socket[7].default_value = 1.000000
    new_out_socket = {}
    if bpy.app.version >= (4, 0, 0):
        node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='OUTPUT')
    else:
        node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = node_group.nodes
    # delete all existing nodes before creating new nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -120)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (-780, -80)
    node.node_tree = bpy.data.node_groups.get(THICK_SHRINKWRAP_GEO_NG_NAME)
    new_nodes["Group"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1180, -80)
    new_nodes["Group Input"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (-500, -80)
    new_nodes["Group Output"] = node
    # create links
    tree_links = node_group.links
    create_nodetree_link(tree_links, new_nodes["Group"], "Geometry", 0, new_nodes["Group Output"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Geometry", 0, new_nodes["Group"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info"], "Geometry", 0, new_nodes["Group"], "Target Solid", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Solid Target", 0, new_nodes["Object Info"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Factor", 0, new_nodes["Group"], "Factor", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Min Distance", 0, new_nodes["Group"], "Min Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Max Distance", 0, new_nodes["Group"], "Max Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Distance", 0, new_nodes["Group"], "Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Relative Offset Factor", 0, new_nodes["Group"], "Relative Offset Factor", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Thick Factor", 0, new_nodes["Group"], "Thick Factor", 0)
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

def create_obj_mod_geo_nodes_directional_shrinkwrap(node_group):
    # remove old group inputs and outputs
    if bpy.app.version >= (4, 0, 0):
        for item in node_group.interface.items_tree:
            if item.item_type == 'SOCKET':
                node_group.interface.remove(item)
    else:
        node_group.inputs.clear()
        node_group.outputs.clear()
    # create new group inputs and outputs
    new_in_socket = {}
    if bpy.app.version >= (4, 0, 0):
        node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='INPUT')
        new_in_socket[1] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Factor", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketObject', name="Solid Target", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketObject', name="Direction Target", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Min Distance", in_out='INPUT')
        new_in_socket[5] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Max Distance", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Distance", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Relative Offset Factor", in_out='INPUT')
        new_in_socket[8] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Direction Factor", in_out='INPUT')
    else:
        node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
        new_in_socket[1] = node_group.inputs.new(type='NodeSocketFloat', name="Factor")
        node_group.inputs.new(type='NodeSocketObject', name="Solid Target")
        node_group.inputs.new(type='NodeSocketObject', name="Direction Target")
        node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
        new_in_socket[5] = node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
        node_group.inputs.new(type='NodeSocketFloat', name="Distance")
        node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
        new_in_socket[8] = node_group.inputs.new(type='NodeSocketFloat', name="Direction Factor")
    new_in_socket[1].default_value = 1.000000
    new_in_socket[5].default_value = 340282346638528859811704183484516925440.000000
    new_in_socket[8].min_value = 0.000000
    new_in_socket[8].max_value = 1.000000
    new_in_socket[8].default_value = 1.000000
    new_out_socket = {}
    if bpy.app.version >= (4, 0, 0):
        node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='OUTPUT')
    else:
        node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = node_group.nodes
    # delete all existing nodes before creating new nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -120)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -320)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info.001"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (-500, -80)
    new_nodes["Group Output"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1180, -80)
    new_nodes["Group Input"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (-780, -80)
    node.node_tree = bpy.data.node_groups.get(DIRECTIONAL_SHRINKWRAP_GEO_NG_NAME)
    new_nodes["Group"] = node
    # create links
    tree_links = node_group.links
    create_nodetree_link(tree_links, new_nodes["Group"], "Geometry", 0, new_nodes["Group Output"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Geometry", 0, new_nodes["Group"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info"], "Geometry", 0, new_nodes["Group"], "Solid Target", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Solid Target", 0, new_nodes["Object Info"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Direction Target", 0, new_nodes["Object Info.001"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info.001"], "Geometry", 0, new_nodes["Group"], "Direction Target", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Factor", 0, new_nodes["Group"], "Factor", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Min Distance", 0, new_nodes["Group"], "Min Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Max Distance", 0, new_nodes["Group"], "Max Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Distance", 0, new_nodes["Group"], "Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Relative Offset Factor", 0, new_nodes["Group"], "Relative Offset Factor", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Direction Factor", 0, new_nodes["Group"], "Direction Factor", 0)
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

def create_obj_mod_geo_nodes_directional_thick_shrinkwrap(node_group):
    # remove old group inputs and outputs
    if bpy.app.version >= (4, 0, 0):
        for item in node_group.interface.items_tree:
            if item.item_type == 'SOCKET':
                node_group.interface.remove(item)
    else:
        node_group.inputs.clear()
        node_group.outputs.clear()
    # create new group inputs and outputs
    new_in_socket = {}
    if bpy.app.version >= (4, 0, 0):
        node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='INPUT')
        new_in_socket[1] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Factor", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketObject', name="Solid Target", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketObject', name="Direction Target", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Min Distance", in_out='INPUT')
        new_in_socket[5] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Max Distance", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Distance", in_out='INPUT')
        node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Relative Offset Factor", in_out='INPUT')
        new_in_socket[8] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Thick Factor", in_out='INPUT')
        new_in_socket[9] = node_group.interface.new_socket(socket_type='NodeSocketFloat', name="Direction Factor", in_out='INPUT')
    else:
        node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
        new_in_socket[1] = node_group.inputs.new(type='NodeSocketFloat', name="Factor")
        node_group.inputs.new(type='NodeSocketObject', name="Solid Target")
        node_group.inputs.new(type='NodeSocketObject', name="Direction Target")
        node_group.inputs.new(type='NodeSocketFloat', name="Min Distance")
        new_in_socket[5] = node_group.inputs.new(type='NodeSocketFloat', name="Max Distance")
        node_group.inputs.new(type='NodeSocketFloat', name="Distance")
        node_group.inputs.new(type='NodeSocketFloat', name="Relative Offset Factor")
        new_in_socket[8] = node_group.inputs.new(type='NodeSocketFloat', name="Thick Factor")
        new_in_socket[9] = node_group.inputs.new(type='NodeSocketFloat', name="Direction Factor")
    new_in_socket[1].default_value = 1.000000
    new_in_socket[5].default_value = 340282346638528859811704183484516925440.000000
    new_in_socket[8].default_value = 1.000000
    new_in_socket[9].min_value = 0.000000
    new_in_socket[9].max_value = 1.000000
    new_in_socket[9].default_value = 1.000000
    new_out_socket = {}
    if bpy.app.version >= (4, 0, 0):
        node_group.interface.new_socket(socket_type='NodeSocketGeometry', name="Geometry", in_out='OUTPUT')
    else:
        node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    tree_nodes = node_group.nodes
    # delete all existing nodes before creating new nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -320)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Target Object info"
    node.location = (-980, -120)
    node.transform_space = "RELATIVE"
    set_node_io_values(node, True, {
        "As Instance": { 0: False },
        })
    new_nodes["Object Info.001"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-1180, -80)
    new_nodes["Group Input"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (-480, -80)
    new_nodes["Group Output"] = node
    # Group
    node = tree_nodes.new(type="GeometryNodeGroup")
    node.location = (-780, -80)
    node.node_tree = bpy.data.node_groups.get(DIRECTIONAL_THICK_SHRINKWRAP_GEO_NG_NAME)
    new_nodes["Group"] = node
    # create links
    tree_links = node_group.links
    create_nodetree_link(tree_links, new_nodes["Group"], "Geometry", 0, new_nodes["Group Output"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Geometry", 0, new_nodes["Group"], "Geometry", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info.001"], "Geometry", 0, new_nodes["Group"], "Solid Target", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Solid Target", 0, new_nodes["Object Info.001"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Direction Target", 0, new_nodes["Object Info"], "Object", 0)
    create_nodetree_link(tree_links, new_nodes["Object Info"], "Geometry", 0, new_nodes["Group"], "Direction Target", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Factor", 0, new_nodes["Group"], "Factor", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Min Distance", 0, new_nodes["Group"], "Min Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Max Distance", 0, new_nodes["Group"], "Max Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Distance", 0, new_nodes["Group"], "Distance", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Relative Offset Factor", 0, new_nodes["Group"], "Relative Offset Factor", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Thick Factor", 0, new_nodes["Group"], "Thick Factor", 0)
    create_nodetree_link(tree_links, new_nodes["Group Input"], "Direction Factor", 0, new_nodes["Group"], "Direction Factor", 0)
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
