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

from bpy.types import Operator

from .shrinkwrap import (create_node_group_node_shrinkwrap, create_node_group_node_thick_shrinkwrap,
    create_node_group_node_directional_shrinkwrap, create_node_group_node_directional_thick_shrinkwrap)
from .shrinkwrap_obj import (create_obj_directional_shrinkwrap, create_obj_directional_thick_shrinkwrap,
    create_obj_shrinkwrap, create_obj_thick_shrinkwrap)

class AMH2B_OT_CreateGeoNodesShrinkwrap(Operator):
    """Create Shrinkwrap group node, to project one geometry onto another geometry"""
    bl_idname = "amh2b.geo_nodes_create_shrinkwrap"
    bl_label = "Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.space_data
        return s.type == 'NODE_EDITOR' and s.node_tree != None and s.tree_type == 'GeometryNodeTree'

    def execute(self, context):
        create_node_group_node_shrinkwrap(context.space_data.edit_tree, context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

class AMH2B_OT_CreateGeoNodesThickShrinkwrap(Operator):
    """Create Thick Shrinkwrap group node, to project one geometry onto another geometry. Projected geometry """ \
        """will retain it's 'thickness' after projection, by way of secondary 'nearness' check"""
    bl_idname = "amh2b.geo_nodes_create_thick_shrinkwrap"
    bl_label = "Thick Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.space_data
        return s.type == 'NODE_EDITOR' and s.node_tree != None and s.tree_type == 'GeometryNodeTree'

    def execute(self, context):
        create_node_group_node_thick_shrinkwrap(context.space_data.edit_tree,
                                                context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

class AMH2B_OT_CreateGeoNodesDirectionalShrinkwrap(Operator):
    """Create Directional Shrinkwrap group node, to project one geometry onto another geometry. Projected """ \
        """geometry is optionally moved towards 'direction target' instead of original 'solid target'"""
    bl_idname = "amh2b.geo_nodes_create_directional_shrinkwrap"
    bl_label = "Directional Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.space_data
        return s.type == 'NODE_EDITOR' and s.node_tree != None and s.tree_type == 'GeometryNodeTree'

    def execute(self, context):
        create_node_group_node_directional_shrinkwrap(context.space_data.edit_tree,
                                                      context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

class AMH2B_OT_CreateGeoNodesDirectionalThickShrinkwrap(Operator):
    """Create Directional Thick Shrinkwrap group node, to project one geometry onto another geometry. """ \
        """Projected geometry is optionally moved towards 'direction target' instead of original 'solid target'""" \
        """, with projected 'thickness' retained"""
    bl_idname = "amh2b.geo_nodes_create_directional_thick_shrinkwrap"
    bl_label = "Directional Thick Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.space_data
        return s.type == 'NODE_EDITOR' and s.node_tree != None and s.tree_type == 'GeometryNodeTree'

    def execute(self, context):
        create_node_group_node_directional_thick_shrinkwrap(context.space_data.edit_tree,
                                                            context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

class AMH2B_OT_CreateObjModDirectionalShrinkwrap(Operator):
    """Add geometry nodes modifier to active Mesh object to project one geometry onto another geometry. """ \
        """Projected geometry is optionally moved towards 'direction target' instead of original 'solid target'"""
    bl_idname = "amh2b.obj_mod_create_directional_shrinkwrap"
    bl_label = "Directional Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'MESH'

    def execute(self, context):
        create_obj_directional_shrinkwrap(context.active_object, context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

class AMH2B_OT_CreateObjModDirectionalThickShrinkwrap(Operator):
    """Add geometry nodes modifier to active Mesh object to project one geometry onto another geometry. """ \
        """Projected geometry is optionally moved towards 'direction target' instead of original 'solid target'""" \
        """, with projected 'thickness' retained"""
    bl_idname = "amh2b.obj_mod_create_directional_thick_shrinkwrap"
    bl_label = "Directional Thick Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'MESH'

    def execute(self, context):
        create_obj_directional_thick_shrinkwrap(context.active_object, context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

class AMH2B_OT_CreateObjModShrinkwrap(Operator):
    """Add geometry nodes modifier to active Mesh object to project one geometry onto another geometry"""
    bl_idname = "amh2b.obj_mod_create_shrinkwrap"
    bl_label = "Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'MESH'

    def execute(self, context):
        create_obj_shrinkwrap(context.active_object, context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}

class AMH2B_OT_CreateObjModThickShrinkwrap(Operator):
    """Add geometry nodes modifier to active Mesh object to project one geometry onto another geometry. """ \
        """Projected geometry will retain it's 'thickness' after projection, by way of secondary 'nearness' check"""
    bl_idname = "amh2b.obj_mod_create_thick_shrinkwrap"
    bl_label = "Thick Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'MESH'

    def execute(self, context):
        create_obj_thick_shrinkwrap(context.active_object, context.scene.amh2b.nodes_override_create)
        return {'FINISHED'}
