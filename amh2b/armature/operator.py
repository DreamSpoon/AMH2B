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

from bpy.props import (EnumProperty, StringProperty)
from bpy.types import Operator

from .func import (do_adjust_pose, do_apply_scale, do_bridge_repose_rig, do_bone_woven,
    do_toggle_preserve_volume, do_rename_generic, do_un_name_generic, cleanup_gizmos)
from .items import (amh2b_fk_ik_both_none_items, amh2b_src_rig_type_items, amh2b_yes_no_items)

class AMH2B_OT_AdjustPose(Operator):
    """Apply CSV script to pose active object's Armature (see Blender's Text Editor)"""
    bl_idname = "amh2b.arm_adjust_pose"
    bl_label = "Script Pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}
        err_str = do_adjust_pose(act_ob)
        if err_str != None:
            self.report({'ERROR'}, err_str)
            return {'CANCELLED'}
        return {'FINISHED'}

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
        do_apply_scale(act_ob)
        return {'FINISHED'}

class AMH2B_OT_BridgeRepose(Operator):
    """Create a "bridge rig" to move a shape-keyed mesh into new position, so copy of armature can have pose applied.\nSelect all MESH objects attached to armature first, and select armature last, then use this function"""
    bl_idname = "amh2b.arm_bridge_repose"
    bl_label = "Bridge Re-Pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}

        do_bridge_repose_rig(act_ob, context.selected_objects)
        return {'FINISHED'}

class AMH2B_OT_BoneWoven(Operator):
    """Join two rigs, with bone stitching, to re-target MHX rig to another rig.\nSelect animated rig first and select MHX rig last, then use this function"""
    bl_idname = "amh2b.arm_bone_woven"
    bl_label = "Bone Woven"
    bl_options = {'REGISTER', 'UNDO'}

    src_rig_type_enum : EnumProperty(name="Source Rig Type", description="Rig type that will be joined to MHX rig.", items=amh2b_src_rig_type_items)
    torso_stitch_enum : EnumProperty(name="Torso Stitches", description="Set torso stitches to yes/no.", items=amh2b_yes_no_items)
    arm_left_stitch_enum : EnumProperty(name="Left Arm Stitches", description="Set left arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    arm_right_stitch_enum : EnumProperty(name="Right Arm Stitches", description="Set right arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_left_stitch_enum : EnumProperty(name="Left Leg Stitches", description="Set left leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_right_stitch_enum : EnumProperty(name="Right Leg Stitches", description="Set right leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    fingers_left_stitch_enum : EnumProperty(name="Left Fingers Stitches", description="Set left fingers stitches to yes/no.", items=amh2b_yes_no_items)
    fingers_right_stitch_enum : EnumProperty(name="Right Fingers Stitches", description="Set right fingers stitches to yes/no.", items=amh2b_yes_no_items)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "src_rig_type_enum")
        layout.prop(self, "torso_stitch_enum")
        layout.prop(self, "arm_left_stitch_enum")
        layout.prop(self, "arm_right_stitch_enum")
        layout.prop(self, "leg_left_stitch_enum")
        layout.prop(self, "leg_right_stitch_enum")
        layout.prop(self, "fingers_left_stitch_enum")
        layout.prop(self, "fingers_right_stitch_enum")

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE'

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

        do_bone_woven(self, dest_rig_obj, src_rig_obj)

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
        do_toggle_preserve_volume(True, context.selected_objects)
        return {'FINISHED'}

class AMH2B_OT_DisableModPreserveVolume(Operator):
    """Disable 'Preserve Volume' in all Armature modifiers attached to all selected MESH type objects"""
    bl_idname = "amh2b.arm_disable_preserve_volume"
    bl_label = "Preserve Volume Off"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_toggle_preserve_volume(False, context.selected_objects)
        return {'FINISHED'}

class AMH2B_OT_RenameGeneric(Operator):
    """Rename armature bones to match the format 'aaaa:bbbb', where 'aaaa' is the generic prefix"""
    bl_idname = "amh2b.arm_rename_generic"
    bl_label = "Rename Generic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_rename_generic(context.scene.amh2b.arm_generic_prefix, context.scene.amh2b.arm_generic_mhx, context.selected_objects)
        return {'FINISHED'}

class AMH2B_OT_UnNameGeneric(Operator):
    """Rename bones to remove any formating like 'aaaa:bbbb', where 'aaaa' is removed and the bones name becomes 'bbbb'"""
    bl_idname = "amh2b.arm_un_name_generic"
    bl_label = "Un-name Generic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_un_name_generic(context.scene.amh2b.arm_generic_mhx, context.selected_objects)
        return {'FINISHED'}
