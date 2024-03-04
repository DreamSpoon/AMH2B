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

def ensure_node_group(override_create, node_group_name, node_tree_type, create_group_func):
    # check if custom node group already exists, and create/override if necessary
    node_group = bpy.data.node_groups.get(node_group_name)
    if node_group is None or node_group.type != node_tree_type or override_create:
        # create the custom node group
        node_group = create_group_func(node_group_name, node_tree_type)
        if node_group is None:
            return None
        # if override create is enabled, then ensure new group name will be "first", meaning:
        #     group name does not have suffix like '.001', '.002', etc.
        if override_create:
            node_group.name = node_group_name
    return node_group

def ensure_node_groups(override_create, ng_name_list, ng_type, create_group_func):
    for ng_name in ng_name_list:
        ensure_node_group(override_create, ng_name, ng_type, create_group_func)

def set_node_io_values(node, is_input, io_values):
    io_name_counts = {}
    if is_input:
        node_io = node.inputs
    else:
        node_io = node.outputs
    for io_instance in node_io:
        if io_instance.name not in io_values:
            continue
        name_count = io_name_counts.get(io_instance.name)
        if name_count is None:
            name_count = 1
        else:
            name_count += 1
        io_name_counts[io_instance.name] = name_count
        io_val = io_values[io_instance.name].get(name_count-1)
        if io_val != None:
            io_instance.default_value = io_val

def create_nodetree_link(tree_links, from_node, from_name, from_name_count, to_node, to_name, to_name_count):
    for out_s in from_node.outputs:
        if out_s.name == from_name:
            if from_name_count == 0:
                for in_s in to_node.inputs:
                    if in_s.name == to_name:
                        if to_name_count == 0:
                            return tree_links.new(out_s, in_s)
                        to_name_count -= 1
                return None
            from_name_count -= 1
    return None
