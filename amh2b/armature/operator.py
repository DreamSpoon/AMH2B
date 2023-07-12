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
from bpy.props import (EnumProperty, StringProperty)
from bpy.types import Operator

from .func import (armature_apply_scale, toggle_preserve_volume, rename_bone_generic, unname_bone_generic,
    cleanup_gizmos, script_pose, load_script_pose_presets, stitch_armature, load_stitch_armature_presets)

class AMH2B_OT_ScriptPose(Operator):
    """Apply script to pose active object Armature's bones with World space rotations"""
    bl_idname = "amh2b.script_pose"
    bl_label = "Script Pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        a = context.scene.amh2b
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}
        script_pose(context, act_ob, a.arm_script_pose_preset, a.arm_use_textblock, a.arm_textblock_name,
                    a.arm_script_pose_reverse)
        return {'FINISHED'}

    def invoke(self, context, event):
        load_script_pose_presets()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        a = context.scene.amh2b
        row = layout.row()
        row.active = not a.arm_use_textblock
        row.prop(a, "arm_script_pose_preset", text="Preset")
        layout.separator()
        layout.prop(a, "arm_use_textblock", text="Use Custom Text")
        row = layout.row()
        row.active = a.arm_use_textblock
        row.prop_search(a, "arm_textblock_name", bpy.data, "texts", text="")
        layout.separator()
        layout.prop(a, "arm_script_pose_reverse")

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

class AMH2B_OT_StitchArmature(Operator):
    """Stitch source Armature to target Armature, to retarget animation from source Armature to target """ \
        """Armature. Select source Armature first, select target Armature last - so target Armature is active object"""
    bl_idname = "amh2b.stitch_armature"
    bl_label = "Stitch Armature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        sel_obs = context.selected_objects
        return act_ob != None and len(sel_obs) == 2 and sel_obs[0].type == 'ARMATURE' and sel_obs[1].type == 'ARMATURE'

    def execute(self, context):
        a = context.scene.amh2b
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
        stitch_armature(context, a.arm_apply_transforms, a.arm_add_layer_index, src_rig_obj, dest_rig_obj,
                        a.arm_stitch_armature_preset, a.arm_use_textblock, a.arm_textblock_name)
        return {'FINISHED'}

    def invoke(self, context, event):
        load_stitch_armature_presets()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        a = context.scene.amh2b
        layout.prop(a, "arm_add_layer_index")
        layout.prop(a, "arm_apply_transforms")
        row = layout.row()
        row.active = not a.arm_use_textblock
        row.prop(a, "arm_stitch_armature_preset", text="Preset")
        layout.separator()
        layout.prop(a, "arm_use_textblock", text="Use Custom Text")
        row = layout.row()
        row.active = a.arm_use_textblock
        row.prop_search(a, "arm_textblock_name", bpy.data, "texts", text="")
