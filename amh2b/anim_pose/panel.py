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

from .func import (POSE_FUNC_LOAD_ACTION, POSE_FUNC_SAVE_ACTION, POSE_FUNC_APPLY_ACTION_FRAME,
    POSE_FUNC_APPLY_ACTION_SCRIPT)
from .operator import (AMH2B_OT_ActionFrameSaveText, AMH2B_OT_ActionFrameLoadText, AMH2B_OT_ActionFrameLoadPreset,
    AMH2B_OT_ActionFrameSavePreset, AMH2B_OT_RefreshPosePresets, AMH2B_OT_ApplyActionFrame,
    AMH2B_OT_LoadActionScriptMOHO)

def draw_panel_anim_pose(self, context, func_grp_box):
    layout = self.layout
    a = context.scene.amh2b
    func_grp_box.prop(a, "pose_function", text="")
    layout.separator()
    if a.pose_function == POSE_FUNC_LOAD_ACTION:
        layout.prop_search(a, "pose_load_action_frame_text", bpy.data, "texts", text="")
        layout.operator(AMH2B_OT_ActionFrameLoadText.bl_idname)
        row = layout.row()
        row.prop(a, "pose_preset", text="")
        row.operator(AMH2B_OT_RefreshPosePresets.bl_idname, text="", icon="FILE_REFRESH")
        layout.operator(AMH2B_OT_ActionFrameLoadPreset.bl_idname)
        layout.separator()
        layout.prop(a, "pose_action_name_prepend", text="Prepend")
        layout.prop(a, "pose_load_mark_asset")
    elif a.pose_function == POSE_FUNC_SAVE_ACTION:
        layout.label(text="Size Reference Bones")
        layout.prop_search(a, "pose_ref_bones_action", bpy.data, "actions", text="Action")
        layout.label(text="Choose Actions")
        layout.template_list("AMH2B_UL_SelectAction", "", bpy.data, "actions", a, "pose_select_action_index", rows=5)
        layout.label(text="Preset Label")
        layout.prop(a, "pose_action_frame_label", text="")
        layout.label(text="Text")
        layout.prop(a, "pose_save_action_frame_text", text="")
        layout.operator(AMH2B_OT_ActionFrameSaveText.bl_idname)
        layout.operator(AMH2B_OT_ActionFrameSavePreset.bl_idname)
    elif a.pose_function == POSE_FUNC_APPLY_ACTION_FRAME:
        layout.operator(AMH2B_OT_ApplyActionFrame.bl_idname)
        layout.prop_search(a, "pose_apply_action", bpy.data, "actions", text="")
    elif a.pose_function == POSE_FUNC_APPLY_ACTION_SCRIPT:
        layout.operator(AMH2B_OT_LoadActionScriptMOHO.bl_idname)
        layout.label(text="Prepend to Names")
        layout.prop(a, "pose_action_name_prepend", text="Action")
        layout.prop(a, "pose_shapekey_name_prepend", text="Shape Key")
        layout.label(text="Timeline")
        layout.prop(a, "pose_script_frame_scale")
        layout.prop(a, "pose_script_frame_offset")
        layout.label(text="Replace Unknown")
        layout.prop_search(a, "pose_script_replace_unknown_action", bpy.data, "actions", text="Action")
        act_ob = context.active_object
        if act_ob != None and act_ob.type == 'MESH' and act_ob.data != None and act_ob.data.shape_keys != None:
            layout.prop_search(a, "pose_script_replace_unknown_shapekey", act_ob.data.shape_keys, "key_blocks",
                               text="Shape Key")
        else:
            layout.prop(a, "pose_script_replace_unknown_shapekey", text="Close")
