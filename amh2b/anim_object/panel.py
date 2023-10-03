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

from .operator import (AMH2B_OT_RatchetHold, AMH2B_OT_RatchetPoint)

def draw_panel_anim_object(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    layout.label(text="Object Location")
    layout.operator(AMH2B_OT_RatchetPoint.bl_idname)
    layout.separator()
    layout.operator(AMH2B_OT_RatchetHold.bl_idname)
    layout.prop_search(scn.amh2b, "anim_ratchet_point_object", bpy.data, "objects", text="Point")
    layout.prop_search(scn.amh2b, "anim_ratchet_target_object", bpy.data, "objects", text="Target")
    layout.prop(scn.amh2b, "anim_ratchet_frames")
