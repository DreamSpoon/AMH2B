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

from bpy.types import Panel

from .func import (VISEME_FUNC_LOAD_ACTION, VISEME_FUNC_SAVE_ACTION, VISEME_FUNC_APPLY_ACTION_FRAME,
    VISEME_FUNC_VISEME_SCRIPT, VISEME_FUNC_VISEME_TEXT)
from .func_word_viseme import get_word_phonemes_dictionary_len
from .operator import (AMH2B_OT_ActionFrameSaveText, AMH2B_OT_ActionFrameLoadText, AMH2B_OT_ActionFrameLoadPreset,
    AMH2B_OT_ActionFrameSavePreset, AMH2B_OT_RefreshVisemeActionsPresets, AMH2B_OT_ApplyActionFrame,
    AMH2B_OT_LoadActionScriptMOHO, AMH2B_OT_LoadWordPhonemesDictionary, AMH2B_OT_ClearWordPhonemesDictionary,
    AMH2B_OT_RefreshPhonemeVisemePresets, AMH2B_OT_VisemeKeyframeWordsActionsString,
    AMH2B_OT_VisemeKeyframePreviewText, AMH2B_OT_VisemeTextPreviewToWordString,
    AMH2B_OT_VisemeKeyframeMarkerWords, AMH2B_OT_PlayBackFrames)

FUNC_GRP_ANIM_VISEME = "FUNC_GRP_ANIM_VISEME"

def draw_panel_anim_viseme(self, context, func_grp_box):
    layout = self.layout
    v_pg = context.scene.amh2b.viseme
    func_grp_box.prop(v_pg, "sub_function", text="")
    layout.separator()
    if v_pg.sub_function == VISEME_FUNC_LOAD_ACTION:
        layout.operator(AMH2B_OT_ActionFrameLoadText.bl_idname)
        layout.prop_search(v_pg, "load_action_frame_text", bpy.data, "texts", text="")
        layout.separator()
        layout.operator(AMH2B_OT_ActionFrameLoadPreset.bl_idname)
        row = layout.row()
        row.prop(v_pg, "actions_preset", text="")
        row.operator(AMH2B_OT_RefreshVisemeActionsPresets.bl_idname, text="", icon="FILE_REFRESH")
        layout.separator()
        layout.label(text="Options")
        layout.prop(v_pg, "action_name_prepend", text="Prepend")
        layout.prop(v_pg, "load_mark_asset")
    elif v_pg.sub_function == VISEME_FUNC_SAVE_ACTION:
        layout.label(text="Size Reference Bones")
        layout.prop_search(v_pg, "ref_bones_action", bpy.data, "actions", text="Action")
        layout.label(text="Choose Actions")
        layout.template_list("AMH2B_UL_SelectAction", "", bpy.data, "actions", v_pg, "select_action_index", rows=5)
        layout.label(text="Preset Label")
        layout.prop(v_pg, "action_frame_label", text="")
        layout.separator()
        layout.operator(AMH2B_OT_ActionFrameSavePreset.bl_idname)
        layout.operator(AMH2B_OT_ActionFrameSaveText.bl_idname)
        layout.prop(v_pg, "save_action_frame_text", text="")
    elif v_pg.sub_function == VISEME_FUNC_APPLY_ACTION_FRAME:
        layout.operator(AMH2B_OT_ApplyActionFrame.bl_idname)
        layout.prop_search(v_pg, "apply_action", bpy.data, "actions", text="")
        layout.separator()
        layout.operator(AMH2B_OT_PlayBackFrames.bl_idname)
        col = layout.column()
        col.prop(v_pg, "play_forward_frames")
        col.prop(v_pg, "play_back_frames")
    elif v_pg.sub_function == VISEME_FUNC_VISEME_SCRIPT:
        layout.operator(AMH2B_OT_LoadActionScriptMOHO.bl_idname)
        layout.label(text="Prepend to Names")
        layout.prop(v_pg, "action_name_prepend", text="Action")
        layout.prop(v_pg, "shapekey_name_prepend", text="Shape Key")
        layout.label(text="Timeline")
        layout.prop(v_pg, "script_frame_scale")
        layout.prop(v_pg, "script_frame_offset")
        layout.label(text="Replace Unknown")
        layout.prop_search(v_pg, "script_replace_unknown_action", bpy.data, "actions", text="Action")
        act_ob = context.active_object
        if act_ob != None and act_ob.type == 'MESH' and act_ob.data != None and act_ob.data.shape_keys != None:
            layout.prop_search(v_pg, "script_replace_unknown_shapekey", act_ob.data.shape_keys, "key_blocks",
                               text="Shape Key")
        else:
            layout.prop(v_pg, "script_replace_unknown_shapekey", text="Shape Key")

class AMH2B_PT_DopesheetVisemeBase(Panel):
    bl_idname = "AMH2B_PT_DopesheetVisemeBase"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_label = "AMH2B"
    bl_category = "AMH2B"

    @classmethod
    def poll(cls, context):
        return context.space_data.mode == 'ACTION'

    def draw(self, context):
        v_pg = context.scene.amh2b.viseme
        layout = self.layout
        layout.operator(AMH2B_OT_PlayBackFrames.bl_idname)
        col = layout.column()
        col.prop(v_pg, "play_forward_frames")
        col.prop(v_pg, "play_back_frames")
        layout.separator()
        layout.label(text="Marker Words to Visemes")

class AMH2B_PT_VisemeTranslation(Panel):
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_label = "Translation"

    @classmethod
    def poll(cls, context):
        a = context.scene.amh2b
        return a.function_group == FUNC_GRP_ANIM_VISEME and a.viseme.sub_function == VISEME_FUNC_VISEME_TEXT \
            or (context.space_data.type == 'DOPESHEET_EDITOR' and context.space_data.mode == 'ACTION')

    def draw(self, context):
        v_pg = context.scene.amh2b.viseme
        layout = self.layout
        layout.label(text="Word to Phonemes")
        layout.operator(AMH2B_OT_LoadWordPhonemesDictionary.bl_idname)
        layout.operator(AMH2B_OT_ClearWordPhonemesDictionary.bl_idname)
        layout.label(text="Dictionary Word Count: " + str(get_word_phonemes_dictionary_len()) )
        layout.separator()
        layout.label(text="Phoneme to Viseme")
        row = layout.row()
        row.prop(v_pg, "phoneme_viseme_preset", text="")
        row.operator(AMH2B_OT_RefreshPhonemeVisemePresets.bl_idname, text="", icon="FILE_REFRESH")

class AMH2B_PT_View3dVisemeTranslation(AMH2B_PT_VisemeTranslation):
    bl_space_type = "VIEW_3D"
    bl_parent_id = "AMH2B_PT_View3d"

class AMH2B_PT_DopesheetVisemeTranslation(AMH2B_PT_VisemeTranslation):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_parent_id = "AMH2B_PT_DopesheetVisemeBase"

class AMH2B_PT_VisemeTiming(Panel):
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_label = "Timing"

    @classmethod
    def poll(cls, context):
        a = context.scene.amh2b
        return a.function_group == FUNC_GRP_ANIM_VISEME and a.viseme.sub_function == VISEME_FUNC_VISEME_TEXT \
            or (context.space_data.type == 'DOPESHEET_EDITOR' and context.space_data.mode == 'ACTION')

    def draw(self, context):
        v_pg = context.scene.amh2b.viseme
        layout = self.layout
        layout.label(text="Frame Counts")
        row = layout.row()
        row.prop(v_pg, "frames_rest_attack", text="Rest Attack")
        row.prop(v_pg, "frames_rest_decay", text="Rest Decay")
        layout.prop(v_pg, "frames_per_viseme", text="Viseme")
        layout.prop(v_pg, "frames_inter_word", text="Between Words")

class AMH2B_PT_View3dVisemeTiming(AMH2B_PT_VisemeTiming):
    bl_space_type = "VIEW_3D"
    bl_parent_id = "AMH2B_PT_View3d"

class AMH2B_PT_DopesheetVisemeTiming(AMH2B_PT_VisemeTiming):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_parent_id = "AMH2B_PT_DopesheetVisemeBase"

class AMH2B_PT_VisemeAnimation(Panel):
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_label = "Animation"

    @classmethod
    def poll(cls, context):
        a = context.scene.amh2b
        return a.function_group == FUNC_GRP_ANIM_VISEME and a.viseme.sub_function == VISEME_FUNC_VISEME_TEXT \
            or (context.space_data.type == 'DOPESHEET_EDITOR' and context.space_data.mode == 'ACTION')

    def draw(self, context):
        v_pg = context.scene.amh2b.viseme
        layout = self.layout
        if context.space_data.type == 'DOPESHEET_EDITOR' and context.space_data.mode == 'ACTION':
            layout.operator(AMH2B_OT_VisemeKeyframeMarkerWords.bl_idname)
            layout.label(text="Marker Frame Cutoff")
            layout.prop(v_pg, "marker_cutoff_use", text="Enable Cutoff")
            row = layout.row()
            row.active = v_pg.marker_cutoff_use
            row.prop(v_pg, "marker_cutoff_start", text="Start Frame")
            row.prop(v_pg, "marker_cutoff_end", text="End Frame")
        else:
            layout.operator(AMH2B_OT_VisemeKeyframeWordsActionsString.bl_idname)
            row = layout.row()
            row.prop(v_pg, "words_actions_string", text="")
            row.operator(AMH2B_OT_VisemeTextPreviewToWordString.bl_idname, text="", icon="COPY_ID")
            layout.separator()
            layout.operator(AMH2B_OT_VisemeKeyframePreviewText.bl_idname)
            layout.prop(v_pg, "preview_lines", text="")
            layout.prop_search(v_pg, "preview_text", bpy.data, "texts", text="")
            layout.prop(v_pg, "preview_line_offset", text="Line Offset")
            layout.prop(v_pg, "preview_line_count", text="Line Count")
            layout.separator()
        layout.label(text="Rest Viseme")
        layout.prop(v_pg, "rest_viseme", text="")
        layout.label(text="Prepend to Names")
        layout.prop(v_pg, "action_name_prepend", text="Action")
        layout.prop(v_pg, "shapekey_name_prepend", text="Shape Key")
        layout.label(text="Replace Unknown")
        layout.prop_search(v_pg, "script_replace_unknown_action", bpy.data, "actions", text="Action")
        act_ob = context.active_object
        if act_ob != None and act_ob.type == 'MESH' and act_ob.data != None and act_ob.data.shape_keys != None:
            layout.prop_search(v_pg, "script_replace_unknown_shapekey", act_ob.data.shape_keys, "key_blocks",
                               text="Shape Key")
        else:
            layout.prop(v_pg, "script_replace_unknown_shapekey", text="Shape Key")

class AMH2B_PT_View3dVisemeAnimation(AMH2B_PT_VisemeAnimation):
    bl_space_type = "VIEW_3D"
    bl_parent_id = "AMH2B_PT_View3d"

class AMH2B_PT_DopesheetVisemeAnimation(AMH2B_PT_VisemeAnimation):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_parent_id = "AMH2B_PT_DopesheetVisemeBase"

class AMH2B_PT_VisemeOutput(Panel):
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_label = "Output"

    @classmethod
    def poll(cls, context):
        a = context.scene.amh2b
        return a.function_group == FUNC_GRP_ANIM_VISEME and a.viseme.sub_function == VISEME_FUNC_VISEME_TEXT \
            or (context.space_data.type == 'DOPESHEET_EDITOR' and context.space_data.mode == 'ACTION')

    def draw(self, context):
        v_pg = context.scene.amh2b.viseme
        layout = self.layout
        layout.label(text="Save Output to Text")
        layout.prop_search(v_pg, "translate_output_text", bpy.data, "texts", text="Translation")
        layout.prop_search(v_pg, "moho_output_text", bpy.data, "texts", text="MOHO")

class AMH2B_PT_View3dVisemeOutput(AMH2B_PT_VisemeOutput):
    bl_space_type = "VIEW_3D"
    bl_parent_id = "AMH2B_PT_View3d"

class AMH2B_PT_DopesheetVisemeOutput(AMH2B_PT_VisemeOutput):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_parent_id = "AMH2B_PT_DopesheetVisemeBase"

class AMH2B_PT_SequenceEditorVisemeBase(Panel):
    bl_idname = "AMH2B_PT_SequenceEditorVisemeBase"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_label = "AMH2B"
    bl_category = "AMH2B"

    def draw(self, context):
        v_pg = context.scene.amh2b.viseme
        layout = self.layout
        layout.operator(AMH2B_OT_PlayBackFrames.bl_idname)
        col = layout.column()
        col.prop(v_pg, "play_forward_frames")
        col.prop(v_pg, "play_back_frames")
