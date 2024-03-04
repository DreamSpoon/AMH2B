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

from ..node_other import (set_node_io_values, create_nodetree_link)

def create_weight_test_mat_nodes(material, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name):
    tree_nodes = material.node_tree.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Material Output
    node = tree_nodes.new(type="ShaderNodeOutputMaterial")
    node.location = (470, 314)
    node.target = "ALL"
    new_nodes["Material Output"] = node
    # Emission
    node = tree_nodes.new(type="ShaderNodeEmission")
    node.location = (274, 314)
    set_node_io_values(node, True, {
        "Strength": { 0: 1.000000 },
        "Weight": { 0: 0.000000 },
        })
    new_nodes["Emission"] = node
    # Color Ramp
    node = tree_nodes.new(type="ShaderNodeValToRGB")
    node.location = (-20, 314)
    node.color_ramp.color_mode = "RGB"
    node.color_ramp.interpolation = "EASE"
    node.color_ramp.elements.remove(node.color_ramp.elements[0])
    elem = node.color_ramp.elements[0]
    elem.position = 0.000000
    elem.color = (0.000000, 0.000000, 1.000000, 1.000000)
    elem = node.color_ramp.elements.new(0.500000)
    elem.color = (0.000000, 1.000000, 0.000000, 1.000000)
    elem = node.color_ramp.elements.new(1.000000)
    elem.color = (1.000000, 0.000000, 0.000000, 1.000000)
    new_nodes["Color Ramp"] = node
    # Attribute
    node = tree_nodes.new(type="ShaderNodeAttribute")
    node.location = (-333, 98)
    node.attribute_name = mass_vg_name+"-test"
    node.attribute_type = "GEOMETRY"
    new_nodes["Attribute.001"] = node
    # Attribute
    node = tree_nodes.new(type="ShaderNodeAttribute")
    node.location = (-333, -78)
    node.attribute_name = spring_vg_name+"-test"
    node.attribute_type = "GEOMETRY"
    new_nodes["Attribute.002"] = node
    # Attribute
    node = tree_nodes.new(type="ShaderNodeAttribute")
    node.location = (-333, 274)
    node.attribute_name = mask_vg_name+"-test"
    node.attribute_type = "GEOMETRY"
    new_nodes["Attribute.003"] = node
    # Attribute
    node = tree_nodes.new(type="ShaderNodeAttribute")
    node.location = (-333, 451)
    node.attribute_name = goal_vg_name+"-test"
    node.attribute_type = "GEOMETRY"
    new_nodes["Attribute"] = node
    # create links
    tree_links = material.node_tree.links
    create_nodetree_link(tree_links, new_nodes["Color Ramp"], "Color", 0, new_nodes["Emission"], "Color", 0)
    create_nodetree_link(tree_links, new_nodes["Emission"], "Emission", 0, new_nodes["Material Output"], "Surface", 0)
    create_nodetree_link(tree_links, new_nodes["Attribute"], "Fac", 0, new_nodes["Color Ramp"], "Fac", 0)
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_nodes
