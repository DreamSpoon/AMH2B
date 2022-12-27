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
