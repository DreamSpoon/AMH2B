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
from bpy.props import (BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, StringProperty)
from bpy.types import Operator

from .func import (armature_apply_scale, toggle_preserve_volume, rename_bone_generic, unname_bone_generic,
    cleanup_gizmos, script_pose, load_script_pose_presets, retarget_armature, load_retarget_armature_presets,
    is_mhx2_armature, retarget_armature_preset_items, script_pose_preset_items, remove_retarget_constraints,
    snap_transfer_target_constraints, select_retarget_bones, select_fcurve_bones, copy_action_frame,
    keyframe_copy_action_frame, playback_frames)

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
        armature_apply_scale(context, act_ob, apply_scale=context.scene.amh2b.arm_apply_object_scale)
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
        retarget_armature(context, src_rig_obj, dest_rig_obj, self.retarget_armature_preset, self.use_textblock,
                          self.textblock_name)
        return {'FINISHED'}

    def invoke(self, context, event):
        load_retarget_armature_presets()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.active = not self.use_textblock
        row.prop(self, "retarget_armature_preset", text="Preset")
        layout.separator()
        layout.prop(self, "use_textblock", text="Use Custom Text")
        row = layout.row()
        row.active = self.use_textblock
        row.prop_search(self, "textblock_name", bpy.data, "texts", text="")

class AMH2B_OT_SnapMHX_FK(Operator):
    """Try to use MHX snap FK to IK"""
    bl_idname = "amh2b.snap_mhx_fk"
    bl_label = "Snap MHX FK"
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

class AMH2B_OT_RemoveRetargetConstraints(Operator):
    """Remove constraints on selected Armatures that were used to transfer animation data with Armature -> """ \
        """Retarget -> Retarget function. Consider using Nonlinear Animation -> Edit menu -> Bake Action before """ \
        """using this function"""
    bl_idname = "amh2b.remove_retarget_constraints"
    bl_label = "Remove Retarget Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    include_target_none: BoolProperty(name="Include Blank Targets", description="Remove bone constraints where the " \
        "bone constraint's 'target' is blank (None)", default=False)

    @classmethod
    def poll(cls, context):
        return len([ ob for ob in context.selected_objects if ob.type == 'ARMATURE' ]) > 0

    def execute(self, context):
        total_ob = 0
        total_bc = 0
        total_cc = 0
        for ob in context.selected_objects:
            if ob.type != 'ARMATURE':
                continue
            bone_count, const_count = remove_retarget_constraints(context, ob, self.include_target_none)
            total_bc += bone_count
            total_cc += const_count
            total_ob += 1
        self.report({'INFO'}, "Removed %d constraints from %d bones of %d armatures" % (total_cc, total_bc, total_ob))
        return {'FINISHED'}

class AMH2B_OT_SnapTransferTarget(Operator):
    """Snap Transfer armature to Target armature so Transfer armature will copy animation from Target armature. """ \
        """Select Target armature first and Transfer armature last. See Armature -> Retarget for creation of """ \
        """Transfer armatures"""
    bl_idname = "amh2b.snap_transfer_target"
    bl_label = "Snap Transfer Target"
    bl_options = {'REGISTER', 'UNDO'}

    limit_ct_hips_ik: BoolProperty(name="Limit 'Copy Transforms' to Hips / IK", description="Only Hips / Pelvis / " \
        "IK bones will use 'Copy Transforms' constraint, remaining bones will use 'Copy Rotation' constraint " \
        "instead. Enable to improve accuracy when armatures are different sizes / heights, e.g. Game Rig",
        default=False, options={'HIDDEN'})
    include_game_engine: BoolProperty(name="Include MPFB2 'Game engine' Bones", description="MPFB2 'Game engine' " \
        "armature bones will have 'Copy Transforms' constraints too", default=True, options={'HIDDEN'})
    only_selected: BoolProperty(name="Only Selected Bones", description="Only selected bones will have transfer " \
        "constraints added", default=False, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        sel_obs = [ ob for ob in context.selected_objects if ob.type == 'ARMATURE' ]
        return context.active_object in sel_obs and len(sel_obs) == 2

    def execute(self, context):
        act_ob = context.active_object
        sel_obs = [ ob for ob in context.selected_objects if ob.type == 'ARMATURE' ]
        if act_ob not in sel_obs or len(sel_obs) != 2:
            return {'CANCELLED'}
        other_ob = [ ob for ob in sel_obs if ob != act_ob ][0]
        bone_count = snap_transfer_target_constraints(context, other_ob, act_ob, self.limit_ct_hips_ik,
                                                      self.include_game_engine, self.only_selected)
        self.report({'INFO'}, "Snapped %d Transfer bones to Target bones" % bone_count)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "only_selected")
        layout.label(text="Limit 'Copy Transforms'")
        layout.prop(self, "limit_ct_hips_ik", text="Limit to Hips / IK")
        row = layout.row()
        row.active = self.limit_ct_hips_ik
        row.prop(self, "include_game_engine")

class AMH2B_OT_SelectRetargetBones(Operator):
    """Select all bones in active object Armature that copy animation from another Armature. i.e. remove bone """ \
        """constraints ('Copy Transforms', 'Location', 'Rotation') that have 'target' set to other Armature object"""
    bl_idname = "amh2b.select_retarget_bones"
    bl_label = "Select Retarget Bones"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'ARMATURE'

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            return {'CANCELLED'}
        bone_count = select_retarget_bones(context, act_ob)
        self.report({'INFO'}, "Selected %d retarget bones" % bone_count)
        return {'FINISHED'}

class AMH2B_OT_SelectBonesWithFCurves(Operator):
    """Select all bones in active object Armature that have F-Curves in the current Action (see Dope Sheet -> """ \
        """Action Editor -> Action)"""
    bl_idname = "amh2b.select_bones_w_fcurves"
    bl_label = "Select Bones w F-Curves"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'ARMATURE'

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            return {'CANCELLED'}
        bone_count = select_fcurve_bones(act_ob)
        self.report({'INFO'}, "Selected %d bones with F-Curves" % bone_count)
        return {'FINISHED'}

class AMH2B_OT_ApplyActionFrame(Operator):
    """Copy values at source frame of source Action to active object Pose bones. If 'Auto Keying' is enabled """ \
        """then keyframes will be inserted in current Action"""
    bl_idname = "amh2b.apply_action_frame"
    bl_label = "Apply Action Frame"
    bl_options = {'REGISTER', 'UNDO'}

    src_frame_num: IntProperty(name="Source Frame", description="Frame of source Action to apply to destination Action",
                               default=0)
    blend_factor: FloatProperty(name="Blend Factor", description="Blend between original location/rotation/scale " \
        "values (0.0) and Action frame location/rotation/scale values (1.0)", default=1.0)
    only_selected: BoolProperty(name="Only Selected Bones", description="Only selected bones will be be modified",
        default=False)
    apply_action_uniform_mult: FloatProperty(name="Uniform Multiply", description="Pose bone Action rotation/" \
        "location/scale values will be multiplied/raised to this value when applied", default=1.0)
    apply_action_loc_mult: FloatVectorProperty(name="Location Multiply", description="Pose bone Action location " \
        "values are multiplied by this value when applied", subtype='XYZ', default=(1.0, 1.0, 1.0))
    apply_action_rot_mult: FloatProperty(name="Rotation Multiply", description="Pose bone Action rotation " \
        "values are multiplied by this value when applied", default=1.0)
    apply_action_scl_pow: FloatVectorProperty(name="Scale Power", description="Pose bone Action scale " \
        "values are raised to this value when applied, i.e. value = pow(value, scale_power)", subtype='XYZ',
        default=(1.0, 1.0, 1.0))
    left_factor: FloatProperty(name="Left Factor", description="Left side bone values will be multiplied/raised " \
        "to this value when applied", default=1.0)
    right_factor: FloatProperty(name="Right Factor", description="Right side bone values will be multiplied/raised " \
        "to this value when applied", default=1.0)
    mirror: BoolProperty(name="Mirror", description="Left and right bone values will be swapped", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE' \
            and len([ a for a in bpy.data.actions if a.name == context.scene.amh2b.arm_apply_action ]) > 0

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            return {'CANCELLED'}
        scn = context.scene
        a = scn.amh2b
        loc_mult = [ lv * self.apply_action_uniform_mult for lv in self.apply_action_loc_mult ]
        rot_mult = self.apply_action_uniform_mult * self.apply_action_rot_mult
        scl_pow = [ sv * self.apply_action_uniform_mult for sv in self.apply_action_scl_pow ]
        if scn.tool_settings.use_keyframe_insert_auto:
            keyframe_copy_action_frame(act_ob, a.arm_apply_action, self.src_frame_num, loc_mult, rot_mult, scl_pow,
                                       self.left_factor, self.right_factor, self.mirror, self.only_selected,
                                       scn.frame_current, self.blend_factor)
        else:
            copy_action_frame(act_ob, a.arm_apply_action, self.src_frame_num, loc_mult, rot_mult, scl_pow,
                              self.left_factor, self.right_factor, self.mirror, self.only_selected,
                              blend_factor=self.blend_factor)
        return {'FINISHED'}

class AMH2B_OT_PlayBackFrames(Operator):
    """Use Blender's 'play' function to play forward a given amount of frames, and then back (subtract) another """ \
        """given amount of frames"""
    bl_idname = "amh2b.playback_frames"
    bl_label = "Play Back"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        a = context.scene.amh2b
        playback_frames(context.scene, a.arm_play_forward_frames, a.arm_play_reverse_frames)
        return {'FINISHED'}
