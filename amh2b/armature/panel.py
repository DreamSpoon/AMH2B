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

from .operator import (AMH2B_OT_AdjustPose, AMH2B_OT_ApplyScale, AMH2B_OT_BoneWoven,
    AMH2B_OT_EnableModPreserveVolume, AMH2B_OT_DisableModPreserveVolume, AMH2B_OT_RenameGeneric,
    AMH2B_OT_UnNameGeneric, AMH2B_OT_CleanupGizmos)

def draw_panel_armature(self, context, box):
    layout = self.layout
    scn = context.scene
    layout.separator()
    layout.operator(AMH2B_OT_CleanupGizmos.bl_idname)
    layout.operator(AMH2B_OT_EnableModPreserveVolume.bl_idname)
    layout.operator(AMH2B_OT_DisableModPreserveVolume.bl_idname)
    layout.operator(AMH2B_OT_ApplyScale.bl_idname)
    layout.separator()
    layout.operator(AMH2B_OT_AdjustPose.bl_idname)
    layout.prop_search(scn.amh2b, "arm_textblock_name", bpy.data, "texts", text="")
    layout.separator()
    layout.operator(AMH2B_OT_BoneWoven.bl_idname)
    layout.separator()
    layout.label(text="Bone Names")
    layout.operator(AMH2B_OT_RenameGeneric.bl_idname)
    layout.prop(scn.amh2b, "arm_generic_prefix", text="")
    layout.prop(scn.amh2b, "arm_generic_mhx")
    layout.separator()
    layout.operator(AMH2B_OT_UnNameGeneric.bl_idname)
