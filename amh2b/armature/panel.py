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

from .func import (ARM_FUNC_APPLY_ACTION_FRAME, ARM_FUNC_RETARGET, ARM_FUNC_SELECT_ACTION_BONES, ARM_FUNC_UTILITY,
    ARM_SELECT_ACTION_CHOOSE, ARM_SELECT_FRAME_RANGE_MIN_MAX, ARM_SELECT_FRAME_RANGE_SINGLE)
from .operator import (AMH2B_OT_ScriptPose, AMH2B_OT_ApplyScale, AMH2B_OT_EnableModPreserveVolume,
    AMH2B_OT_DisableModPreserveVolume, AMH2B_OT_RenameGeneric, AMH2B_OT_UnNameGeneric, AMH2B_OT_CleanupGizmos,
    AMH2B_OT_RetargetArmature, AMH2B_OT_SnapMHX_FK, AMH2B_OT_SnapMHX_IK, AMH2B_OT_RemoveRetargetConstraints,
    AMH2B_OT_SnapTransferTarget, AMH2B_OT_SelectRetargetBones, AMH2B_OT_SelectBonesWithFCurves,
    AMH2B_OT_ApplyActionFrame, AMH2B_OT_PlayBackFrames)

def draw_panel_armature(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    a = scn.amh2b
    func_grp_box.prop(a, "arm_function", text="")
    layout.separator()
    if a.arm_function == ARM_FUNC_RETARGET:
        src_name = " "
        dest_name = " "
        act_ob = context.active_object
        sel_obs = [ ob for ob in context.selected_objects if ob.type == 'ARMATURE' ]
        if act_ob in sel_obs and len(sel_obs) == 2:
            other_ob = [ ob for ob in sel_obs if ob != act_ob ][0]
            dest_name += act_ob.name
            src_name += other_ob.name
        layout.operator(AMH2B_OT_ScriptPose.bl_idname)
        layout.separator()
        layout.operator(AMH2B_OT_SnapMHX_FK.bl_idname)
        layout.operator(AMH2B_OT_SnapMHX_IK.bl_idname)
        layout.separator()
        box = layout.box()
        box.label(text="Source:" + src_name)
        box.label(text="Dest:" + dest_name)
        box.operator(AMH2B_OT_RetargetArmature.bl_idname)
        box.separator()
        box.operator(AMH2B_OT_SnapTransferTarget.bl_idname)
        layout.separator()
        layout.operator(AMH2B_OT_SelectRetargetBones.bl_idname)
        layout.separator()
        layout.operator(AMH2B_OT_RemoveRetargetConstraints.bl_idname)
    elif a.arm_function == ARM_FUNC_APPLY_ACTION_FRAME:
        layout.operator(AMH2B_OT_ApplyActionFrame.bl_idname)
        layout.prop_search(a, "arm_apply_action", bpy.data, "actions", text="")
        layout.separator()
        layout.operator(AMH2B_OT_PlayBackFrames.bl_idname)
        col = layout.column()
        col.prop(a, "arm_play_reverse_frames")
        col.prop(a, "arm_play_forward_frames")
    elif a.arm_function == ARM_FUNC_SELECT_ACTION_BONES:
        layout.operator(AMH2B_OT_SelectBonesWithFCurves.bl_idname)
        layout.prop(a, "arm_select_action_bone_type")
        if a.arm_select_action_bone_type == ARM_SELECT_ACTION_CHOOSE:
            layout.prop_search(a, "arm_select_action_bone_action", bpy.data, "actions")
        layout.prop(a, "arm_select_action_bone_frame_range_type")
        if a.arm_select_action_bone_frame_range_type == ARM_SELECT_FRAME_RANGE_MIN_MAX:
            layout.prop(a, "arm_select_action_bone_frame_range_min")
            layout.prop(a, "arm_select_action_bone_frame_range_max")
        elif a.arm_select_action_bone_frame_range_type == ARM_SELECT_FRAME_RANGE_SINGLE:
            layout.prop(a, "arm_select_action_bone_frame_range_min", text="Frame")
    elif a.arm_function == ARM_FUNC_UTILITY:
        layout.operator(AMH2B_OT_CleanupGizmos.bl_idname)
        layout.separator()
        layout.operator(AMH2B_OT_EnableModPreserveVolume.bl_idname)
        layout.operator(AMH2B_OT_DisableModPreserveVolume.bl_idname)
        layout.separator()
        layout.operator(AMH2B_OT_ApplyScale.bl_idname)
        layout.prop(a, "arm_apply_object_scale")
        layout.separator()
        layout.label(text="Bone Names")
        layout.operator(AMH2B_OT_RenameGeneric.bl_idname)
        layout.prop(a, "arm_generic_prefix", text="")
        layout.separator()
        layout.operator(AMH2B_OT_UnNameGeneric.bl_idname)
