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

from ..const import ADDON_BASE_FILE
from ..bl_util import (get_file_eval_dict, do_tag_redraw)

from .func import exec_viseme_action_script

word_phonemes_dict = {}
phoneme_viseme_presets = {}

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

PREVIEW_LINE_LEN = 24

def get_word_phonemes_dictionary_len():
    return len(word_phonemes_dict)

def load_word_phonemes_dictionary(filepath):
    # read file and remove non-utf8 chars, to prevent errors later
    lines_read = []
    try:
        with open(filepath, "rb") as read_file:
            for read_line in read_file:
                read_line = read_line.decode('utf-8','ignore')
                lines_read.append(read_line)
    except:
        return "Unable to load word-phoneme dictionary from file:\n" + filepath
    check_for_comments = True
    stress_values = {}
    load_word_count = 0
    for line in lines_read:
        # skip empty lines and commented lines
        s_line = line.strip()
        if s_line == "" or (check_for_comments and s_line[0] == "#"):
            continue
        check_for_comments = False
        # skip lines that start with non-alphanumeric character
        if s_line[0].upper() not in ALPHABET:
            continue
        line_tokens = s_line.split()
        if len(line_tokens) < 2:
            continue
        word_name = line_tokens[0].upper()
        sv = 0
        if word_name.endswith(")"):
            word_name = word_name[ : word_name.rfind("(") ]
            # if 'stress' is indicated by parentheses then discard the parentheses and get the value
            try:
                sv = int(word_name[ word_name.rfind("(")+1 : -1 ])
            except:
                pass
        # keep lowest stress value, ideally zero stress
        if word_name in stress_values and sv > stress_values[word_name]:
            continue
        if word_name not in word_phonemes_dict:
            load_word_count += 1
        # if word_name is already in the dict then it will be overwritten
        word_phonemes_dict[word_name] = line_tokens[1:]
    do_tag_redraw()
    return load_word_count

def clear_word_phonemes_dictionary():
    word_phonemes_dict.clear()
    do_tag_redraw()

def phoneme_viseme_preset_items(self, context):
    items = []
    for filename, preset_data in phoneme_viseme_presets.items():
        label = preset_data.get("label")
        if label is None:
            label = filename
        desc = preset_data.get("description")
        if desc is None:
            desc = ""
        items.append ( (filename, str(label), str(desc)) )
    return sorted(items, key = lambda x: x[0]) if len(items) > 0 else [ (" ", "", "") ]

def refresh_phoneme_viseme_presets():
    phoneme_viseme_presets.clear()
    # get paths to presets files
    base_path = os.path.dirname(os.path.realpath(ADDON_BASE_FILE))
    p = os.path.join(base_path, "presets", "phoneme_viseme")
    try:
        file_paths = [ f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f)) ]
    except:
        return
    # safely read each file and get pose script, trying ALL FILES in the presets path
    for fp in file_paths:
        try:
            with open(os.path.join(p, fp), 'r') as f:
                preset_data = get_file_eval_dict(f)
        except:
            continue
        if not isinstance(preset_data, dict) or not isinstance(preset_data.get("data"), dict):
            continue
        phoneme_viseme_presets[fp] = preset_data

def preview_lines_items(self, context):
    v_pg = context.scene.amh2b.viseme
    if v_pg.preview_text not in bpy.data.texts:
        return [ (" ", "", "") ]
    pr_text = bpy.data.texts[v_pg.preview_text]
    if v_pg.preview_line_offset >= len(pr_text.lines):
        return [ (" ", "", "") ]
    items = []
    if v_pg.preview_line_offset + v_pg.preview_line_count > len(pr_text.lines):
        end_index = len(pr_text.lines)
    else:
        end_index = v_pg.preview_line_count + v_pg.preview_line_offset
    for line_index in range(v_pg.preview_line_offset, end_index):
        items.append( (str(line_index), pr_text.lines[line_index].body[:PREVIEW_LINE_LEN], "Line " + str(line_index)))
    return items if len(items) > 0 else [ (" ", "", "") ]

# convert non-alphanumeric, and non-apostrophe, characters to spaces based on English spelling conventions
# e.g. "(Spain's)rains'" becomes " Spain's rains "
def non_alphanumpostrophe_to_space(in_str):
    result = ""
    prev_apostrophe = 0
    for ch in in_str:
        if ch.upper() in ALPHABET:
            if prev_apostrophe == 1:
                result += "'"
            prev_apostrophe = 0
            result += ch.upper()
        elif ch == "'":
            if prev_apostrophe == 1:
                result += "  "
            elif prev_apostrophe > 1:
                result += " "
            prev_apostrophe += 1
        else:
            result += " "
            prev_apostrophe = 0
    return result

def append_str_to_text(out_text, out_str):
    if out_text is None:
        return
    last_line = len(out_text.lines) - 1
    c = len(out_text.lines[last_line].body) - 1
    c = 0 if c < 0 else c
    out_text.cursor_set(last_line, character=c)
    out_text.write(out_str)

def words_to_visemes(words_string, phoneme_viseme_preset, translate_out_text):
    pv_preset = phoneme_viseme_presets.get(phoneme_viseme_preset)
    if pv_preset is None:
        return None
    pv_preset_data = pv_preset.get("data")
    if not isinstance(pv_preset_data, dict):
        return None
    # convert certain characters to whitespace, to leave only words (no parentheses, double-quotes, etc.)
    words_string = non_alphanumpostrophe_to_space(words_string)
    append_str_to_text(translate_out_text, words_string+"\n")
    word_tokens = words_string.split()
    word_visemes = []
    word_phonemes = []
    for wt in word_tokens:
        phonemes = word_phonemes_dict.get(wt.upper())
        if phonemes is None:
            # empty list indicates unknown word
            word_visemes.append( [] )
            word_phonemes.append( [] )
            continue
        word_phonemes.append(phonemes)
        p_visemes = []
        for phon in phonemes:
            vis_name = pv_preset_data.get(phon)
            if vis_name is None:
                # empty string indicates unknown phoneme-viseme translation
                p_visemes.append("")
                continue
            p_visemes.append(vis_name)
        word_visemes.append(p_visemes)
    append_str_to_text(translate_out_text, str(word_phonemes)+"\n")
    append_str_to_text(translate_out_text, str(word_visemes)+"\n")
    return word_visemes

def visemes_lists_to_frames(visemes_lists, rest_action_name, frames_rest_attack, frames_rest_decay, frames_per_viseme,
                           frames_inter_word, frame_start, frame_end):
    current_frame = 0
    viseme_frames = []
    for visemes in visemes_lists:
        if frames_rest_attack > 0:
            viseme_frames.append( {
                "frame": current_frame,
                "viseme": rest_action_name,
                } )
            current_frame += frames_rest_attack
        for vis in visemes:
            # keyframe each phoneme in the middle of its time duration, if possible
            half_frames_per_viseme = int(frames_per_viseme / 2)
            current_frame += half_frames_per_viseme
            viseme_frames.append( {
                "frame": current_frame,
                "viseme": vis,
                } )
            current_frame += frames_per_viseme - half_frames_per_viseme
        if frames_rest_decay > 0:
            current_frame += frames_rest_decay
            viseme_frames.append( {
                "frame": current_frame,
                "viseme": rest_action_name,
                } )
        current_frame += frames_inter_word
    if len(viseme_frames) == 0:
        return {}
    # if frame_end exists then scale the animation keyframes
    frame_mult = 1
    if frame_end != None:
        from_duration = current_frame - frames_inter_word
        to_duration = frame_end - frame_start
        frame_mult = to_duration / from_duration
    result = {}
    for vf in viseme_frames:
        # scale the frame number and add frame_start
        f = int(vf["frame"] * frame_mult + frame_start)
        # prioritize 'rest' frames
        if f in result and result[f] == rest_action_name:
            continue
        result[f] = vf["viseme"]
    return result

def append_moho_to_text(out_text, viseme_frames):
    out_str = ""
    for frame, vis_name in viseme_frames.items():
        out_str += "%s %s\n" % (str(frame), vis_name)
    append_str_to_text(out_text, out_str)

def keyframe_word_viseme_actions(arm_list, mesh_list, words_string, phoneme_viseme_preset, rest_action_name,
                                 frames_rest_attack, frames_rest_decay, frames_per_viseme, frames_inter_word,
                                 frame_start, frame_end, translate_output_text_name, moho_output_text_name,
                                 action_name_prepend, replace_unknown_action_name, shapekey_name_prepend,
                                 replace_unknown_shapekey_name):
    translate_out_text = bpy.data.texts.get(translate_output_text_name)
    moho_out_text = bpy.data.texts.get(moho_output_text_name)
    visemes_lists = words_to_visemes(words_string, phoneme_viseme_preset, translate_out_text)
    if visemes_lists is None:
        return
    viseme_frames = visemes_lists_to_frames(visemes_lists, rest_action_name, frames_rest_attack, frames_rest_decay,
                                            frames_per_viseme, frames_inter_word, frame_start, frame_end)
    append_str_to_text(translate_out_text, str(viseme_frames)+"\n")
    append_moho_to_text(moho_out_text, viseme_frames)
    exec_viseme_action_script(arm_list, mesh_list, viseme_frames, action_name_prepend, replace_unknown_action_name,
                              shapekey_name_prepend, replace_unknown_shapekey_name, rest_action_name)

def viseme_keyframe_words_actions_string(arm_list, mesh_list, words_string, phoneme_viseme_preset, rest_action_name, frames_rest_attack,
                                         frames_rest_decay, frames_per_viseme, frames_inter_word, frame_start,
                                         translate_output_text_name, moho_output_text_name, action_name_prepend,
                                         replace_unknown_action_name, shapekey_name_prepend,
                                         replace_unknown_shapekey_name):
    if words_string == "":
        return
    if rest_action_name != "" and rest_action_name not in bpy.data.actions:
        # blank string indicates 'use defaults' rest frame (e.g. scale=(1,1,1) )
        rest_action_name = ""
    if bpy.data.texts.get(translate_output_text_name):
        translate_out_line_count = len(bpy.data.texts[translate_output_text_name].lines)
    else:
        translate_out_line_count = 0
    if bpy.data.texts.get(moho_output_text_name):
        moho_out_line_count = len(bpy.data.texts[moho_output_text_name].lines)
    else:
        moho_out_line_count = 0
    keyframe_word_viseme_actions(arm_list, mesh_list, words_string, phoneme_viseme_preset, rest_action_name,
                                 frames_rest_attack, frames_rest_decay, frames_per_viseme, frames_inter_word,
                                 frame_start, None, translate_output_text_name, moho_output_text_name,
                                 action_name_prepend, replace_unknown_action_name, shapekey_name_prepend,
                                 replace_unknown_shapekey_name)
    # append newlines if needed
    translate_out_text = bpy.data.texts.get(translate_output_text_name)
    if translate_out_text:
        if len(translate_out_text.lines) > translate_out_line_count:
            translate_out_text.write("\n")
    moho_out_text = bpy.data.texts.get(moho_output_text_name)
    if moho_out_text:
        if len(moho_out_text.lines) > moho_out_line_count:
            moho_out_text.write("\n")

def viseme_keyframe_preview_text(arm_list, mesh_list, text_name, preview_line_offset_str, phoneme_viseme_preset,
                                 rest_action_name, frames_rest_attack, frames_rest_decay, frames_per_viseme,
                                 frames_inter_word, frame_start, translate_output_text_name, moho_output_text_name,
                                 action_name_prepend, replace_unknown_action_name, shapekey_name_prepend,
                                 replace_unknown_shapekey_name):
    if text_name not in bpy.data.texts or preview_line_offset_str.strip() == "":
        return
    try:
        preview_line_offset = int(preview_line_offset_str)
    except:
        return
    words_string = bpy.data.texts[text_name].lines[preview_line_offset].body
    if words_string == "":
        return
    if rest_action_name != "" and rest_action_name not in bpy.data.actions:
        # blank string indicates 'use defaults' rest frame (e.g. scale=(1,1,1) )
        rest_action_name = ""
    if bpy.data.texts.get(translate_output_text_name):
        translate_out_line_count = len(bpy.data.texts[translate_output_text_name].lines)
    else:
        translate_out_line_count = 0
    if bpy.data.texts.get(moho_output_text_name):
        moho_out_line_count = len(bpy.data.texts[moho_output_text_name].lines)
    else:
        moho_out_line_count = 0
    keyframe_word_viseme_actions(arm_list, mesh_list, words_string, phoneme_viseme_preset, rest_action_name,
                                 frames_rest_attack, frames_rest_decay, frames_per_viseme, frames_inter_word,
                                 frame_start, None, translate_output_text_name, moho_output_text_name,
                                 action_name_prepend, replace_unknown_action_name, shapekey_name_prepend,
                                 replace_unknown_shapekey_name)
    # append newlines if needed
    translate_out_text = bpy.data.texts.get(translate_output_text_name)
    if translate_out_text:
        if len(translate_out_text.lines) > translate_out_line_count:
            translate_out_text.write("\n")
    moho_out_text = bpy.data.texts.get(moho_output_text_name)
    if moho_out_text:
        if len(moho_out_text.lines) > moho_out_line_count:
            moho_out_text.write("\n")

def viseme_keyframe_marker_words(markers, arm_list, mesh_list, phoneme_viseme_preset, rest_action_name,
                                 frames_rest_attack, frames_rest_decay, frames_per_viseme, frames_inter_word,
                                 translate_output_text_name, moho_output_text_name, action_name_prepend,
                                 replace_unknown_action_name, shapekey_name_prepend, replace_unknown_shapekey_name):
    filtered_markers = {}
    # ensure only integer frames are present, and no overlapping markers
    for mrk in markers:
        filtered_markers[ int(mrk.frame) ] = mrk.name
    words_frames = []
    prev_name = None
    prev_frame = None
    for m_frame, m_name in sorted(filtered_markers.items()):
        if prev_name != None and prev_frame != None:
            words_frames.append( { "words": prev_name, "frame_start": prev_frame, "frame_end": m_frame } )
            prev_name = None
            prev_frame = None
        if m_name != "":
            prev_name = m_name
            prev_frame = m_frame
    if prev_name != None and prev_frame != None:
        words_frames.append( { "words": prev_name, "frame_start": prev_frame } )
    if bpy.data.texts.get(translate_output_text_name):
        translate_out_line_count = len(bpy.data.texts[translate_output_text_name].lines)
    else:
        translate_out_line_count = 0
    if bpy.data.texts.get(moho_output_text_name):
        moho_out_line_count = len(bpy.data.texts[moho_output_text_name].lines)
    else:
        moho_out_line_count = 0
    for wf in words_frames:
        keyframe_word_viseme_actions(arm_list, mesh_list, wf.get("words"), phoneme_viseme_preset, rest_action_name,
                                 frames_rest_attack, frames_rest_decay, frames_per_viseme, frames_inter_word,
                                 wf.get("frame_start"), wf.get("frame_end"), translate_output_text_name,
                                 moho_output_text_name, action_name_prepend, replace_unknown_action_name,
                                 shapekey_name_prepend, replace_unknown_shapekey_name)
    # append newlines if needed
    translate_out_text = bpy.data.texts.get(translate_output_text_name)
    if translate_out_text:
        if len(translate_out_text.lines) > translate_out_line_count:
            translate_out_text.write("\n")
    moho_out_text = bpy.data.texts.get(moho_output_text_name)
    if moho_out_text:
        if len(moho_out_text.lines) > moho_out_line_count:
            moho_out_text.write("\n")
