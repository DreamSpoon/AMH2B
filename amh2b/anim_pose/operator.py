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

import os

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

from ..const import ADDON_BASE_FILE
from .func import (load_action_frames_from_text, save_action_frames_to_text, load_action_frames_from_preset,
    save_action_frames_to_preset, refresh_pose_action_frame_presets, apply_action_frame, keyframe_apply_action_frame,
    load_action_script_moho)

class AMH2B_OT_ActionFrameLoadText(Operator):
    """Load Action F-Curves from Text, available in the Text Editor. Creates keyframes at frame zero of each Action"""
    bl_idname = "amh2b.action_frame_load_text"
    bl_label = "Load Text"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.data.texts.get(context.scene.amh2b.pose_load_action_frame_text) != None

    def execute(self, context):
        a = context.scene.amh2b
        act_ob = context.active_object
        act_arm = None
        if act_ob != None and act_ob.type == 'ARMATURE':
            act_arm = act_ob.data
        result = load_action_frames_from_text(act_arm, a.pose_load_action_frame_text, a.pose_action_name_prepend,
                                              a.pose_load_mark_asset)
        self.report({'INFO'}, "Created %i Actions from Text" % result)
        return {'FINISHED'}

class AMH2B_OT_ActionFrameSaveText(Operator):
    """Evaluate currently selected Action F-Curves at frame 0 and save result to Text, available in the Text Editor"""
    bl_idname = "amh2b.action_frame_save_text"
    bl_label = "Save Text"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.amh2b.pose_save_action_frame_text != ""

    def execute(self, context):
        a = context.scene.amh2b
        act_ob = context.active_object
        act_arm = None
        if act_ob != None and act_ob.type == 'ARMATURE':
            act_arm = act_ob.data
        result = save_action_frames_to_text(context, act_arm, a.pose_save_action_frame_text, a.pose_action_frame_label,
                                            a.pose_ref_bones_action)
        if isinstance(result, bpy.types.Text):
            self.report({'INFO'}, "Output Action frame to Text named " + result.name)
            return {'FINISHED'}
        if isinstance(result, str):
            self.report({'ERROR'}, result)
        return {'CANCELLED'}

class AMH2B_OT_ActionFrameLoadPreset(Operator):
    """Load Action F-Curves from Pose Preset. Creates keyframes at frame zero of each Action"""
    bl_idname = "amh2b.action_frame_load_preset"
    bl_label = "Load Preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.amh2b.pose_preset != " "

    def execute(self, context):
        a = context.scene.amh2b
        act_ob = context.active_object
        act_arm = None
        if act_ob != None and act_ob.type == 'ARMATURE':
            act_arm = act_ob.data
        result = load_action_frames_from_preset(act_arm, a.pose_preset, a.pose_action_name_prepend,
                                                a.pose_load_mark_asset)
        self.report({'INFO'}, "Created %i Actions from Preset" % result)
        return {'FINISHED'}

class AMH2B_OT_ActionFrameSavePreset(Operator, ImportHelper):
    """Evaluate currently selected Action F-Curves at frame 0 and save result to file in Presets folder"""
    bl_idname = "amh2b.action_frame_save_preset"
    bl_label = "Save Preset"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH', options={'HIDDEN'})

    def execute(self, context):
        # if a dir is selected then return finished
        if os.path.isdir(self.filepath):
            self.report({'ERROR'}, "Unable to save Preset, invalid filepath")
            return {'CANCELLED'}
        a = context.scene.amh2b
        act_ob = context.active_object
        act_arm = None
        if act_ob != None and act_ob.type == 'ARMATURE':
            act_arm = act_ob.data
        result = save_action_frames_to_preset(context, act_arm, self.filepath, a.pose_action_frame_label,
                                              a.pose_ref_bones_action)
        if result is None:
            self.report({'INFO'}, "Saved Action Frame to Preset in file named " + self.filepath)
            return {'FINISHED'}
        self.report({'ERROR'}, result)
        return {'CANCELLED'}

    def invoke(self, context, event):
        base_path = os.path.dirname(os.path.realpath(ADDON_BASE_FILE))
        self.filepath = os.path.join(base_path, "presets", "anim_pose", "")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class AMH2B_OT_RefreshPosePresets(Operator):
    """Refresh listing of Pose Presets"""
    bl_idname = "amh2b.refresh_pose_presets"
    bl_label = "Refresh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        refresh_pose_action_frame_presets()
        return {'FINISHED'}

class AMH2B_OT_ApplyActionFrame(Operator):
    """Apply frame zero of selected Action"""
    bl_idname = "amh2b.apply_action_frame"
    bl_label = "Apply Action Frame"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE' \
            and len([ a for a in bpy.data.actions if a.name == context.scene.amh2b.pose_apply_action ]) > 0

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            return {'CANCELLED'}
        scn = context.scene
        if scn.tool_settings.use_keyframe_insert_auto:
            keyframe_apply_action_frame(act_ob, scn.amh2b.pose_apply_action, scn.frame_current)
        else:
            apply_action_frame(act_ob, scn.amh2b.pose_apply_action)
        return {'FINISHED'}

class AMH2B_OT_LoadActionScriptMOHO(Operator, ImportHelper):
    """Load a .dat file containing MOHO data and apply named Actions to create Pose animation on active """ \
        """Armature. e.g. Papagayo-NG .dat file"""
    bl_idname = "amh2b.load_action_script_moho"
    bl_label = "Load MOHO"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob: StringProperty(default="*.dat", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        # if no file selected then return finished
        if not os.path.isfile(self.filepath):
            return {'FINISHED'}
        if context.active_object is None or context.active_object.type != 'ARMATURE':
            return {'CANCELLED'}
        a = context.scene.amh2b
        result = load_action_script_moho(self.filepath, context.active_object, a.pose_script_frame_scale,
                                         a.pose_script_frame_offset, a.pose_script_replace_unknown_action,
                                         a.pose_action_name_prepend)
        if result == {'FINISHED'}:
            if context.active_object.animation_data.action is None:
                self.report({'INFO'}, "Zero Actions found in MOHO script")
            else:
                self.report({'INFO'}, "Loaded MOHO script and added keyframes to Action named %s" %
                            context.active_object.animation_data.action.name)
            return {'FINISHED'}
        if isinstance(result, str):
            self.report({'ERROR'}, result)
        return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # def draw(self, context):
    #     layout = self.layout
    #     layout.label(text="")
