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

from .operator import (AMH2B_OT_AddBlinkTrack, AMH2B_OT_RemoveBlinkTrack)

EBLINK_SUB_FUNC_ADD = "EBLINK_SUB_FUNC_ADD"
EBLINK_SUB_FUNC_REMOVE = "EBLINK_SUB_FUNC_REMOVE"
EBLINK_SUB_FUNC_ITEMS = [
    (EBLINK_SUB_FUNC_ADD, "Add", "Add eyeblink track to active object Armature"),
    (EBLINK_SUB_FUNC_REMOVE, "Remove", "Remove eyeblink track from active object Armature"),
    ]

def draw_panel_eye_blink(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    a = scn.amh2b
    act_ob = context.active_object
    func_grp_box.prop(a, "eblink_sub_func", text="")
    layout.separator()
    if a.eblink_sub_func == EBLINK_SUB_FUNC_ADD:
        layout.operator(AMH2B_OT_AddBlinkTrack.bl_idname)
        layout.prop(a, "eblink_rig_type", text="Rig Type")
        layout.separator()
        layout.label(text="Add Options")
        layout.prop(a, "eblink_frame_rate")
        layout.prop(a, "eblink_start_frame")
        layout.prop(a, "eblink_random_start_frame")
        layout.prop(a, "eblink_allow_random_drift")
        layout.prop(a, "eblink_frame_count")
        layout.prop(a, "eblink_max_count_enable")
        sub = layout.column()
        sub.active = a.eblink_max_count_enable
        sub.prop(a, "eblink_max_count")
        sub = layout.column()
        sub.active = not a.eblink_blink_period_enable
        sub.prop(a, "eblink_blinks_per_min")
        layout.prop(a, "eblink_blink_period_enable")
        sub = layout.column()
        sub.active = a.eblink_blink_period_enable
        sub.prop(a, "eblink_blink_period")
        layout.prop(a, "eblink_random_period_enable")
        if act_ob != None and act_ob.type == 'MESH' and act_ob.data.shape_keys != None:
            layout.prop_search(a, "eblink_shapekey_name", act_ob.data.shape_keys, "key_blocks", text="ShapeKey")
        else:
            layout.prop(a, "eblink_shapekey_name", text="ShapeKey")
        layout.separator()
        layout.label(text="Basis")
        layout.prop(a, "eblink_closing_time")
        layout.prop(a, "eblink_closed_time")
        layout.prop(a, "eblink_opening_time")
        layout.separator()
        layout.label(text="Random")
        layout.prop(a, "eblink_random_closing_time")
        layout.prop(a, "eblink_random_closed_time")
        layout.prop(a, "eblink_random_opening_time")
    elif a.eblink_sub_func == EBLINK_SUB_FUNC_REMOVE:
        layout.operator(AMH2B_OT_RemoveBlinkTrack.bl_idname)
        layout.prop(a, "eblink_rig_type", text="Rig Type")
        layout.separator()
        layout.label(text="Remove Options")
        layout.prop(a, "eblink_remove_start_enable")
        sub = layout.column()
        sub.active = a.eblink_remove_start_enable
        sub.prop(a, "eblink_remove_start_frame")
        layout.prop(a, "eblink_remove_end_enable")
        sub = layout.column()
        sub.active = a.eblink_remove_end_enable
        sub.prop(a, "eblink_remove_end_frame")
