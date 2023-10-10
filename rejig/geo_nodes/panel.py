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

from bpy.types import Panel

from .operator import (AMH2B_OT_CreateObjModDirectionalShrinkwrap, AMH2B_OT_CreateObjModDirectionalThickShrinkwrap,
    AMH2B_OT_CreateObjModShrinkwrap, AMH2B_OT_CreateObjModThickShrinkwrap, AMH2B_OT_CreateGeoNodesShrinkwrap,
    AMH2B_OT_CreateGeoNodesThickShrinkwrap, AMH2B_OT_CreateGeoNodesDirectionalShrinkwrap,
    AMH2B_OT_CreateGeoNodesDirectionalThickShrinkwrap)

def draw_panel_geometry_nodes(self, context, func_grp_box):
    scn = context.scene
    layout = self.layout
    layout.prop(scn.amh2b, "nodes_override_create")
    layout.label(text="Shrinkwrap")
    layout.operator(AMH2B_OT_CreateObjModShrinkwrap.bl_idname)
    layout.operator(AMH2B_OT_CreateObjModThickShrinkwrap.bl_idname)
    layout.operator(AMH2B_OT_CreateObjModDirectionalShrinkwrap.bl_idname)
    layout.operator(AMH2B_OT_CreateObjModDirectionalThickShrinkwrap.bl_idname)

class AMH2B_PT_NodeEditorGeoNodes(Panel):
    bl_label = "Geometry Nodes"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "AMH2B"

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        layout.prop(scn.amh2b, "nodes_override_create")
        layout.label(text="Shrinkwrap")
        layout.operator(AMH2B_OT_CreateGeoNodesShrinkwrap.bl_idname)
        layout.operator(AMH2B_OT_CreateGeoNodesThickShrinkwrap.bl_idname)
        layout.operator(AMH2B_OT_CreateGeoNodesDirectionalShrinkwrap.bl_idname)
        layout.operator(AMH2B_OT_CreateGeoNodesDirectionalThickShrinkwrap.bl_idname)
