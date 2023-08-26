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
from bpy.props import (BoolProperty, EnumProperty, IntProperty, StringProperty)
from bpy.types import Operator

from .func import (armature_apply_scale, toggle_preserve_volume, rename_bone_generic, unname_bone_generic,
    cleanup_gizmos, script_pose, load_script_pose_presets, retarget_armature, load_retarget_armature_presets,
    copy_armature_transforms, is_mhx2_armature, retarget_armature_preset_items, script_pose_preset_items)

class AMH2B_OT_ScriptPose(Operator):
    """Apply script to pose active object Armature's bones with World space rotations"""
    bl_idname = "amh2b.script_pose"
    bl_label = "Script Pose"
    bl_options = {'REGISTER', 'UNDO'}

    use_textblock: BoolProperty(name="Use Custom Text", default=False)
    textblock_name: StringProperty(name="Text Editor Script Name",
                                       description="Script data-block name in text editor")
    script_pose_reverse: BoolProperty(name="Reverse Order", description="Run Pose Script in reverse order, " \
        "e.g. to undo previous use of Pose Script", default=False)
    script_pose_preset: EnumProperty(name="Script Pose Preset", items=script_pose_preset_items)

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}
        script_pose(context, act_ob, self.script_pose_preset, self.use_textblock, self.textblock_name,
                    self.script_pose_reverse)
        return {'FINISHED'}

    def invoke(self, context, event):
        load_script_pose_presets()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.active = not self.use_textblock
        row.prop(self, "script_pose_preset", text="Preset")
        layout.separator()
        layout.prop(self, "use_textblock", text="Use Custom Text")
        row = layout.row()
        row.active = self.use_textblock
        row.prop_search(self, "textblock_name", bpy.data, "texts", text="")
        layout.separator()
        layout.prop(self, "script_pose_reverse")

class AMH2B_OT_ApplyScale(Operator):
    """Apply Object Scale to active object Armature without corrupting Armature pose data (i.e. location)"""
    bl_idname = "amh2b.arm_apply_scale"
    bl_label = "Apply Scale"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}
        armature_apply_scale(context, act_ob)
        return {'FINISHED'}

class AMH2B_OT_CleanupGizmos(Operator):
    """Detect Objects used by Armature Bones to customize bone shapes (gizmos), and move them to 'Hidden' """ \
        """Collection under their parent Armature Object's Collection"""
    bl_idname = "amh2b.arm_cleanup_gizmos"
    bl_label = "Cleanup Gizmos"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cleanup_gizmos(context)
        return {'FINISHED'}

class AMH2B_OT_EnableModPreserveVolume(Operator):
    """Enable 'Preserve Volume' in all Armature modifiers attached to all selected MESH type objects"""
    bl_idname = "amh2b.arm_enable_preserve_volume"
    bl_label = "Preserve Volume On"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        toggle_preserve_volume(context, True, context.selected_objects)
        return {'FINISHED'}

class AMH2B_OT_DisableModPreserveVolume(Operator):
    """Disable 'Preserve Volume' in all Armature modifiers attached to all selected MESH type objects"""
    bl_idname = "amh2b.arm_disable_preserve_volume"
    bl_label = "Preserve Volume Off"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        toggle_preserve_volume(context, False, context.selected_objects)
        return {'FINISHED'}

class AMH2B_OT_RenameGeneric(Operator):
    """Rename armature bones to match the format 'aaaa:bbbb', where 'aaaa' is the generic prefix"""
    bl_idname = "amh2b.arm_rename_generic"
    bl_label = "Rename Generic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        a = context.scene.amh2b
        rename_bone_generic(context, a.arm_generic_prefix, context.selected_objects)
        return {'FINISHED'}

class AMH2B_OT_UnNameGeneric(Operator):
    """Rename active object Armature bones to remove any formating like 'aaaa:bbbb', where 'aaaa' is removed """ \
        """and the bones name becomes 'bbbb'"""
    bl_idname = "amh2b.arm_un_name_generic"
    bl_label = "Un-name Generic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        unname_bone_generic(context, context.selected_objects)
        return {'FINISHED'}

class AMH2B_OT_RetargetArmature(Operator):
    """Select exactly two Armatures. Retarget animation from source Armature to destination Armature via script. """ \
        """Select source Armature first, select destination Armature last - so destination Armature is active object"""
    bl_idname = "amh2b.retarget_armature"
    bl_label = "Retarget"
    bl_options = {'REGISTER', 'UNDO'}

    retarget_armature_preset: EnumProperty(name="Retarget Armature Preset", items=retarget_armature_preset_items)
    apply_transforms: BoolProperty(name="Apply Transforms", description="Apply all transforms to 'source' " \
        "Armature before joining with 'target' Armature", default=True)
    add_layer_index: IntProperty(name="Bone Layer Index", description="Index of Bone Layer assigned to bones " \
        "added to 'destination' with Retarget Armature", default=24, min=0, max=31)
    use_textblock: BoolProperty(name="Use Custom Text", default=False)
    textblock_name: StringProperty(name="Text Editor Script Name", description="Script data-block name in text editor")

    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        sel_obs = context.selected_objects
        return act_ob != None and len(sel_obs) == 2 and sel_obs[0].type == 'ARMATURE' and sel_obs[1].type == 'ARMATURE'

    def execute(self, context):
        act_ob = context.active_object
        sel_obs = context.selected_objects
        if act_ob is None or len(sel_obs) != 2 or sel_obs[0].type != 'ARMATURE' or sel_obs[1].type != 'ARMATURE':
            self.report({'ERROR'}, "Select exactly 2 ARMATURES and try again")
            return {'CANCELLED'}
        dest_rig_obj = act_ob
        src_rig_obj = None
        if sel_obs[0] != act_ob:
            src_rig_obj = sel_obs[0]
        else:
            src_rig_obj = sel_obs[1]
        retarget_armature(context, self.apply_transforms, src_rig_obj, dest_rig_obj,
                          self.retarget_armature_preset, self.use_textblock, self.textblock_name,
                          self.add_layer_index)
        return {'FINISHED'}

    def invoke(self, context, event):
        load_retarget_armature_presets()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "add_layer_index")
        layout.prop(self, "apply_transforms")
        row = layout.row()
        row.active = not self.use_textblock
        row.prop(self, "retarget_armature_preset", text="Preset")
        layout.separator()
        layout.prop(self, "use_textblock", text="Use Custom Text")
        row = layout.row()
        row.active = self.use_textblock
        row.prop_search(self, "textblock_name", bpy.data, "texts", text="")

class AMH2B_OT_CopyArmatureTransforms(Operator):
    """Copy animation, with keyframes, from one Armature to another Armature. Temporary bone constraints are """ \
        """used to Copy All Transforms, then 'NLA Bake Action' is used to bake bone animation keyframes. """ \
        """Select source Armature first (from Retarget), and destination Armature last"""
    bl_idname = "amh2b.copy_armature_transforms"
    bl_label = "Copy Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    copy_transforms_selected: BoolProperty(name="Copy Transforms Selected Only", description="Use only " \
        "selected bones, to Copy ALl Transforms")
    copy_transforms_frame_start: IntProperty(name="Copy Transforms Frame Start", description="Add keyframes " \
        "bones starting this frame", min=0, default=1)
    copy_transforms_frame_end: IntProperty(name="Copy Transforms Frame End", description="Add keyframes " \
        "bones ending this frame", min=0, default=250)
    copy_transforms_frame_step: IntProperty(name="Copy Transforms Frame Step", description="Increment this " \
        "many frames between keyframes", min=1, default=1)

    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        sel_obs = context.selected_objects
        return act_ob != None and len(sel_obs) == 2 and sel_obs[0].type == 'ARMATURE' and sel_obs[1].type == 'ARMATURE'

    def execute(self, context):
        act_ob = context.active_object
        sel_obs = context.selected_objects
        if act_ob is None or len(sel_obs) != 2 or sel_obs[0].type != 'ARMATURE' or sel_obs[1].type != 'ARMATURE':
            self.report({'ERROR'}, "Select exactly 2 Armatures and try again")
            return {'CANCELLED'}
        dest_rig_obj = act_ob
        src_rig_obj = None
        if sel_obs[0] != act_ob:
            src_rig_obj = sel_obs[0]
        else:
            src_rig_obj = sel_obs[1]
        copy_armature_transforms(context, src_rig_obj, dest_rig_obj, self.copy_transforms_selected,
                                 self.copy_transforms_frame_start, self.copy_transforms_frame_end,
                                 self.copy_transforms_frame_step)
        return {'FINISHED'}

    def invoke(self, context, event):
        load_retarget_armature_presets()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "copy_transforms_frame_start", text="Frame Start")
        layout.prop(self, "copy_transforms_frame_end", text="Frame End")
        layout.prop(self, "copy_transforms_frame_step", text="Frame Step")
        layout.prop(self, "copy_transforms_selected", text="Only Selected")

class AMH2B_OT_SnapMHX_FK(Operator):
    """Try to use MHX snap FK to IK"""
    bl_idname = "amh2b.snap_mhx_fk"
    bl_label = "Snap MHX FK"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
#        act_ob = context.active_object
#        return act_ob != None and act_ob.type == 'ARMATURE'
        return is_mhx2_armature(context.active_object)

    def execute(self, context):
        if not is_mhx2_armature(context.active_object):
            return {'CANCELLED'}
        old_mode = context.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        try:
            bpy.ops.mhx2.snap_fk_ik(data="MhaArmIk_L 2 3 12")
            bpy.ops.mhx2.snap_fk_ik(data="MhaArmIk_R 18 19 28")
            bpy.ops.mhx2.snap_fk_ik(data="MhaLegIk_L 4 5 12")
            bpy.ops.mhx2.snap_fk_ik(data="MhaLegIk_R 20 21 28")
        except:
            self.report({'ERROR'}, "Unable to use MHX snap FK, ensure that Import MHX2 addon is enabled")
            bpy.ops.object.mode_set(mode=old_mode)
            return {'CANCELLED'}
        bpy.ops.object.mode_set(mode=old_mode)
        return {'FINISHED'}

class AMH2B_OT_SnapMHX_IK(Operator):
    """Try to use MHX snap IK to FK"""
    bl_idname = "amh2b.snap_mhx_ik"
    bl_label = "Snap MHX IK"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return is_mhx2_armature(context.active_object)

    def execute(self, context):
        if not is_mhx2_armature(context.active_object):
            return {'CANCELLED'}
        old_mode = context.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        try:
            bpy.ops.mhx2.snap_ik_fk(data="MhaArmIk_L 2 3 12")
            bpy.ops.mhx2.snap_ik_fk(data="MhaArmIk_R 18 19 28")
            bpy.ops.mhx2.snap_ik_fk(data="MhaLegIk_L 4 5 12")
            bpy.ops.mhx2.snap_ik_fk(data="MhaLegIk_R 20 21 28")
            context.active_object.pose.bones["elbow.pt.ik.L"].location = (0, 0, 0)
            context.active_object.pose.bones["elbow.pt.ik.R"].location = (0, 0, 0)
        except:
            self.report({'ERROR'}, "Unable to use MHX snap IK, ensure that Import MHX2 addon is enabled")
            bpy.ops.object.mode_set(mode=old_mode)
            return {'CANCELLED'}
        bpy.ops.object.mode_set(mode=old_mode)
        return {'FINISHED'}
