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
from bpy.props import (BoolProperty, FloatProperty, FloatVectorProperty, StringProperty)
from bpy.types import Operator

from ..const import ADDON_BASE_FILE
from .func import (load_action_frames_from_text, save_action_frames_to_text, load_action_frames_from_preset,
    save_action_frames_to_preset, refresh_viseme_actions_presets, copy_action_frame, keyframe_copy_action_frame,
    load_viseme_script_moho)
from .func_word_viseme import (load_word_phonemes_dictionary, clear_word_phonemes_dictionary,
    refresh_phoneme_viseme_presets, viseme_keyframe_words_actions_string, viseme_keyframe_preview_text,
    viseme_keyframe_marker_words, get_word_phonemes_dictionary_len)

class AMH2B_OT_ActionFrameLoadText(Operator):
    """Load Action F-Curves from Text, available in the Text Editor. Creates keyframes at frame zero of each Action"""
    bl_idname = "amh2b.action_frame_load_text"
    bl_label = "Load Text"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.data.texts.get(context.scene.amh2b.viseme.load_action_frame_text) != None

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            return {'CANCELLED'}
        v_pg = context.scene.amh2b.viseme
        result = load_action_frames_from_text(act_ob, v_pg.load_action_frame_text, v_pg.action_name_prepend,
                                              v_pg.load_mark_asset)
        self.report({'INFO'}, "Created %i Actions from Text" % result)
        return {'FINISHED'}

class AMH2B_OT_ActionFrameSaveText(Operator):
    """Evaluate currently selected Action F-Curves at frame 0 and save result to Text, available in the Text Editor"""
    bl_idname = "amh2b.action_frame_save_text"
    bl_label = "Save to Text"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.amh2b.viseme.save_action_frame_text != ""

    def execute(self, context):
        act_ob = context.active_object
        act_arm = None
        if act_ob != None and act_ob.type == 'ARMATURE':
            act_arm = act_ob.data
        v_pg = context.scene.amh2b.viseme
        result = save_action_frames_to_text(context, act_arm, v_pg.save_action_frame_text, v_pg.action_frame_label,
                                            v_pg.ref_bones_action)
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
        return context.scene.amh2b.viseme.actions_preset != " "

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            return {'CANCELLED'}
        v_pg = context.scene.amh2b.viseme
        result = load_action_frames_from_preset(act_ob, v_pg.actions_preset, v_pg.action_name_prepend,
                                                v_pg.load_mark_asset)
        self.report({'INFO'}, "Created %i Actions from Preset" % result)
        return {'FINISHED'}

class AMH2B_OT_ActionFrameSavePreset(Operator, ImportHelper):
    """Evaluate currently selected Action F-Curves at frame 0 and save result to file in """ \
        """\\amh2b\\presets\\anim_viseme\\ directory"""
    bl_idname = "amh2b.action_frame_save_preset"
    bl_label = "Save to File"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH', options={'HIDDEN'})

    def execute(self, context):
        # if a dir is selected then return finished
        if os.path.isdir(self.filepath):
            self.report({'ERROR'}, "Unable to save Preset, invalid filepath")
            return {'CANCELLED'}
        act_ob = context.active_object
        act_arm = None
        if act_ob != None and act_ob.type == 'ARMATURE':
            act_arm = act_ob.data
        v_pg = context.scene.amh2b.viseme
        result = save_action_frames_to_preset(context, act_arm, self.filepath, v_pg.action_frame_label,
                                              v_pg.ref_bones_action)
        if result is None:
            self.report({'INFO'}, "Saved Action Frame to Preset in file named " + self.filepath)
            return {'FINISHED'}
        self.report({'ERROR'}, result)
        return {'CANCELLED'}

    def invoke(self, context, event):
        base_path = os.path.dirname(os.path.realpath(ADDON_BASE_FILE))
        self.filepath = os.path.join(base_path, "presets", "anim_viseme", "")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class AMH2B_OT_RefreshVisemeActionsPresets(Operator):
    """Refresh listing of Pose Presets. This will reload files in \\amh2b\\presets\\anim_viseme\\ directory"""
    bl_idname = "amh2b.refresh_viseme_actions_presets"
    bl_label = "Refresh Presets"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        refresh_viseme_actions_presets()
        return {'FINISHED'}

class AMH2B_OT_RefreshPhonemeVisemePresets(Operator):
    """Refresh listing of Phoneme to Viseme translation presets. This will reload files in """ \
        """\\amh2b\\presets\\phoneme_viseme\\ directory"""
    bl_idname = "amh2b.refresh_phoneme_viseme_presets"
    bl_label = "Refresh Presets"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        refresh_phoneme_viseme_presets()
        return {'FINISHED'}

class AMH2B_OT_ApplyActionFrame(Operator):
    """Copy values at frame zero of selected Action to active object Pose bones. If 'Auto Keying' is enabled """ \
        """then keyframes will be inserted in current Action"""
    bl_idname = "amh2b.apply_action_frame"
    bl_label = "Apply Action Frame"
    bl_options = {'REGISTER', 'UNDO'}

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

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE' \
            and len([ a for a in bpy.data.actions if a.name == context.scene.amh2b.viseme.apply_action ]) > 0

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            return {'CANCELLED'}
        scn = context.scene
        v_pg = scn.amh2b.viseme
        loc_mult = [ lv * self.apply_action_uniform_mult for lv in self.apply_action_loc_mult ]
        rot_mult = self.apply_action_uniform_mult * self.apply_action_rot_mult
        scl_pow = [ sv * self.apply_action_uniform_mult for sv in self.apply_action_scl_pow ]
        if scn.tool_settings.use_keyframe_insert_auto:
            keyframe_copy_action_frame(act_ob, v_pg.apply_action, loc_mult, rot_mult, scl_pow, self.only_selected,
                                       scn.frame_current, blend_factor=self.blend_factor)
        else:
            copy_action_frame(act_ob, scn.amh2b.viseme.apply_action, loc_mult, rot_mult, scl_pow, self.only_selected,
                              blend_factor=self.blend_factor)
        return {'FINISHED'}

class AMH2B_OT_LoadActionScriptMOHO(Operator, ImportHelper):
    """Load a .dat file containing MOHO data and apply named Actions to create Pose animation on active """ \
        """Armature. e.g. Papagayo-NG .dat file"""
    bl_idname = "amh2b.load_viseme_script_moho"
    bl_label = "Load MOHO"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob: StringProperty(default="*.dat", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return len( [ o for o in context.selected_objects if o.type in ['ARMATURE', 'MESH'] ] ) > 0

    def execute(self, context):
        # if no file selected then return finished
        if not os.path.isfile(self.filepath):
            return {'FINISHED'}
        # check selected objects for ARMATURE or MESH
        arm_list = []
        mesh_list = []
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                arm_list.append(obj)
            elif obj.type == 'MESH':
                mesh_list.append(obj)
        # exit if zero objects to work with
        if len(arm_list) == 0 and len(mesh_list) == 0:
            self.report({'ERROR'}, "No ARMATURE or MESH selected to load Action script")
            return {'CANCELLED'}
        v_pg = context.scene.amh2b.viseme
        result = load_viseme_script_moho(self.filepath, arm_list, mesh_list, v_pg.script_frame_scale,
                                         v_pg.script_frame_offset, v_pg.script_replace_unknown_action,
                                         v_pg.script_replace_unknown_shapekey, v_pg.action_name_prepend,
                                         v_pg.shapekey_name_prepend)
        if isinstance(result, str):
            self.report({'ERROR'}, result)
            return {'CANCELLED'}
        elif isinstance(result, int) and result == 0:
            self.report({'INFO'}, "Zero Actions found in MOHO script")
            return {'CANCELLED'}
        else:
            if context.active_object.animation_data.action:
                action_name = context.active_object.animation_data.action.name
            else:
                action_name = ""
            self.report({'INFO'}, "Loaded MOHO script and added keyframes to Action named %s" % action_name)
            return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class AMH2B_OT_LoadWordPhonemesDictionary(Operator):
    """Load a word-to-phonemes dictionary from file, e.g. Carnegie Mellon University phoneme dictionary"""
    bl_idname = "amh2b.load_word_phonemes_dictionary"
    bl_label = "Load Dictionary"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH', options={'HIDDEN'})

    def execute(self, context):
        # if no file selected then return finished
        if not os.path.isfile(self.filepath):
            return {'FINISHED'}
        result = load_word_phonemes_dictionary(self.filepath)
        if isinstance(result, str):
            self.report({'ERROR'}, result)
            return {'CANCELLED'}
        if isinstance(result, int):
            self.report({'INFO'}, "Loaded %i words from word-phoneme dictionary file" % result)
        return {'FINISHED'}

    def invoke(self, context, event):
        base_path = os.path.dirname(os.path.realpath(ADDON_BASE_FILE))
        self.filepath = os.path.join(base_path, "presets", "word_phoneme", "")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class AMH2B_OT_ClearWordPhonemesDictionary(Operator):
    """Clear current word-to-phonemes dictionary"""
    bl_idname = "amh2b.clear_word_phonemes_dictionary"
    bl_label = "Clear Dictionary"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        clear_word_phonemes_dictionary()
        self.report({'INFO'}, "Word-phonemes dictionary has been cleared")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Clear phoneme dictionary?")
        layout.label(text="This operation cannot be undone.")

class AMH2B_OT_VisemeKeyframeWordsActionsString(Operator):
    """Create talking animation keyframes on current Armatures/Meshes, using Words String as input. """ \
        """Words-to-phonemes dictionary and phonemes-to-viseme translation will be used to create viseme """ \
        """sequence, each viseme is a named Action"""
    bl_idname = "amh2b.viseme_keyframe_words_actions_string"
    bl_label = "Keyframe"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.amh2b.viseme.words_actions_string != "" and \
            len( [ o for o in context.selected_objects if o.type in ['ARMATURE', 'MESH'] ] ) > 0

    def execute(self, context):
        if get_word_phonemes_dictionary_len() == 0:
            self.report({'ERROR'}, "Cannot get visemes to keyframe because word-phoneme dictionary is empty. See " \
                        "Translation panel and Load Dictionary")
            return {'CANCELLED'}
        # check selected objects for ARMATURE or MESH
        arm_list = []
        mesh_list = []
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                arm_list.append(obj)
            elif obj.type == 'MESH':
                mesh_list.append(obj)
        # exit if zero objects to work with
        if len(arm_list) == 0 and len(mesh_list) == 0:
            self.report({'ERROR'}, "No ARMATURE or MESH selected to keyframe visemes from Words string")
            return {'CANCELLED'}
        v_pg = context.scene.amh2b.viseme
        viseme_keyframe_words_actions_string(arm_list, mesh_list, v_pg.words_actions_string,
            v_pg.phoneme_viseme_preset, v_pg.rest_action, v_pg.frames_rest_attack, v_pg.frames_rest_decay,
            v_pg.frames_per_viseme, v_pg.frames_inter_word, context.scene.frame_current, v_pg.translate_output_text,
            v_pg.moho_output_text, v_pg.action_name_prepend, v_pg.script_replace_unknown_action,
            v_pg.shapekey_name_prepend, v_pg.script_replace_unknown_shapekey)
        return {'FINISHED'}

class AMH2B_OT_VisemeKeyframePreviewText(Operator):
    """Create talking animation keyframes on current Armatures/Meshes, using Text Preview Line as input. """ \
        """Words-to-phonemes dictionary and phonemes-to-viseme translation will be used to create viseme """ \
        """sequence, each viseme is a named Action"""
    bl_idname = "amh2b.viseme_keyframe_preview_text"
    bl_label = "Keyframe"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        v_pg = context.scene.amh2b.viseme
        if v_pg.preview_lines == " " or v_pg.preview_lines == "":
            return False
        if v_pg.preview_text not in bpy.data.texts:
            return False
        return len( [ o for o in context.selected_objects if o.type in ['ARMATURE', 'MESH'] ] ) > 0

    def execute(self, context):
        if get_word_phonemes_dictionary_len() == 0:
            self.report({'ERROR'}, "Cannot get visemes to keyframe because word-phoneme dictionary is empty. See " \
                        "Translation panel and Load Dictionary")
            return {'CANCELLED'}
        # check selected objects for ARMATURE or MESH
        arm_list = []
        mesh_list = []
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                arm_list.append(obj)
            elif obj.type == 'MESH':
                mesh_list.append(obj)
        # exit if zero objects to work with
        if len(arm_list) == 0 and len(mesh_list) == 0:
            self.report({'ERROR'}, "No ARMATURE or MESH selected to keyframe visemes from Text Preview")
            return {'CANCELLED'}
        v_pg = context.scene.amh2b.viseme
        viseme_keyframe_preview_text(arm_list, mesh_list, v_pg.preview_text, v_pg.preview_lines,
            v_pg.phoneme_viseme_preset, v_pg.rest_action, v_pg.frames_rest_attack, v_pg.frames_rest_decay,
            v_pg.frames_per_viseme, v_pg.frames_inter_word, context.scene.frame_current, v_pg.translate_output_text,
            v_pg.moho_output_text, v_pg.action_name_prepend, v_pg.script_replace_unknown_action,
            v_pg.shapekey_name_prepend, v_pg.script_replace_unknown_shapekey)
        return {'FINISHED'}

class AMH2B_OT_VisemeTextPreviewToWordString(Operator):
    """Copy line from Text Preview to Translate Words String"""
    bl_idname = "amh2b.viseme_text_preview_to_word_string"
    bl_label = "Text Preview to Word String"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        v_pg = context.scene.amh2b.viseme
        if v_pg.preview_text not in bpy.data.texts:
            return False
        if v_pg.preview_lines == " " or v_pg.preview_lines == "":
            return False
        try:
            _ = int(v_pg.preview_lines)
        except:
            return False
        return True

    def execute(self, context):
        v_pg = context.scene.amh2b.viseme
        if v_pg.preview_lines == " " or v_pg.preview_text not in bpy.data.texts:
            return {'CANCELLED'}
        try:
            line_num = int(v_pg.preview_lines)
        except:
            return {'CANCELLED'}
        preview_text = bpy.data.texts[v_pg.preview_text]
        if line_num >= len(preview_text.lines):
            return {'CANCELLED'}
        v_pg.words_actions_string = preview_text.lines[line_num].body
        return {'FINISHED'}

class AMH2B_OT_VisemeKeyframeMarkerWords(Operator):
    """Create talking animation keyframes on current Armatures/Meshes, by converting words in labels on Markers """ \
        """(in Dopesheet Action Editor) to visemes. Blank Markers are used as end of word Markers - 'rest' Markers"""
    bl_idname = "amh2b.viseme_keyframe_marker_words"
    bl_label = "Keyframe Markers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len( [ o for o in context.selected_objects if o.type in ['ARMATURE', 'MESH'] ] ) > 0

    def execute(self, context):
        if get_word_phonemes_dictionary_len() == 0:
            self.report({'ERROR'}, "Cannot get visemes to keyframe because word-phoneme dictionary is empty. See " \
                        "Translation panel and Load Dictionary")
            return {'CANCELLED'}
        # check selected objects for ARMATURE or MESH
        arm_list = []
        mesh_list = []
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                arm_list.append(obj)
            elif obj.type == 'MESH':
                mesh_list.append(obj)
        # exit if zero objects to work with
        if len(arm_list) == 0 and len(mesh_list) == 0:
            self.report({'ERROR'}, "No ARMATURE or MESH selected to keyframe visemes from Words string")
            return {'CANCELLED'}
        if context.space_data.show_pose_markers:
            markers = context.space_data.action.pose_markers
        else:
            markers = context.scene.timeline_markers
        v_pg = context.scene.amh2b.viseme
        viseme_keyframe_marker_words(markers, arm_list, mesh_list, v_pg.phoneme_viseme_preset, v_pg.rest_action,
            v_pg.frames_rest_attack, v_pg.frames_rest_decay, v_pg.frames_per_viseme, v_pg.frames_inter_word,
            v_pg.translate_output_text, v_pg.moho_output_text, v_pg.action_name_prepend,
            v_pg.script_replace_unknown_action, v_pg.shapekey_name_prepend, v_pg.script_replace_unknown_shapekey)
        return {'FINISHED'}
