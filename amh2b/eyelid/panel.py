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

from .operator import (AMH2B_OT_AddLidLook, AMH2B_OT_RemoveLidLook)

def draw_panel_eye_lid(self, context, func_grp_box):
    layout = self.layout
    a = context.scene.amh2b
    layout.separator()
    layout.prop(a, "elid_rig_type")
    layout.operator(AMH2B_OT_AddLidLook.bl_idname)
    layout.operator(AMH2B_OT_RemoveLidLook.bl_idname)
