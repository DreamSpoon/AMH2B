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
import traceback

import bpy
from mathutils import Quaternion

from ..bl_util import (ast_literal_eval_lines, get_file_eval_dict, do_tag_redraw, get_next_name,
    keyframe_shapekey_value, get_thing_to_keyframe)
from ..const import ADDON_BASE_FILE
from ..lex_py_attributes import lex_py_attributes
from ..armature.func import (copy_action_frame, is_bone_action)

VISEME_FUNC_VISEME_SCRIPT = "VISEME_SCRIPT"
VISEME_FUNC_VISEME_TEXT = "VISEME_TEXT"
VISEME_FUNC_LOAD_ACTION = "LOAD_ACTION"
VISEME_FUNC_SAVE_ACTION = "SAVE_ACTION"
VISEME_FUNC_ITEMS = [
    (VISEME_FUNC_VISEME_SCRIPT, "Viseme  Script", "Apply a script (e.g. Papagayo MOHO .dat file) with " \
     "named Viseme Actions to create mouth/face animations on selected Armatures/Meshes"),
    (VISEME_FUNC_VISEME_TEXT, "Word to Viseme", "Convert words of text to Viseme Actions and apply to selected " \
     "Armature/Mesh objects"),
    (VISEME_FUNC_LOAD_ACTION, "Load Actions", "Load Pose bone Actions from Text/File/Preset"),
    (VISEME_FUNC_SAVE_ACTION, "Save Actions", "Save Pose bone Actions to Text/File/Preset"),
    ]

EVAL_FRAME_NUM = 0
LOAD_FRAME_NUM = 0

viseme_actions_presets = {}

ROTATION_MODE_STRINGS = {
    -1: 'AXIS_ANGLE',
    0: 'QUATERNION',
    1: 'XYZ',
    2: 'XZY',
    3: 'YXZ',
    4: 'YZX',
    5: 'ZXY',
    6: 'ZYX',
    }

def viseme_actions_preset_items(self, context):
    items = []
    for filename, pose_preset_data in viseme_actions_presets.items():
        label = pose_preset_data.get("label")
        if label is None:
            label = filename
        desc = pose_preset_data.get("description")
        if desc is None:
            desc = ""
        items.append ( (filename, str(label), str(desc)) )
    return sorted(items, key = lambda x: x[0]) if len(items) > 0 else [ (" ", "", "") ]

def refresh_viseme_actions_presets():
    viseme_actions_presets.clear()
    # get paths to presets files
    base_path = os.path.dirname(os.path.realpath(ADDON_BASE_FILE))
    p = os.path.join(base_path, "presets", "anim_viseme")
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
        viseme_actions_presets[fp] = preset_data

def get_ref_bone_loc_data(arm, ref_action_name):
    if arm is None:
        return None
    ref_action = bpy.data.actions.get(ref_action_name)
    if ref_action is None or not is_bone_action(ref_action):
        return None
    result_data = {}
    # initialize a dictionary with the names (only uniques) of pose bones, from F-Curves
    for ref_fc in ref_action.fcurves:
        if not ref_fc.data_path.startswith("pose.bones["):
            continue
        fc_tokens, _ = lex_py_attributes(ref_fc.data_path)
        if len(fc_tokens) < 3:
            continue
        bone_name = ref_fc.data_path[ fc_tokens[2][0]+2 : fc_tokens[2][1]-2 ]
        result_data[bone_name] = None
    for bone_name in result_data.keys():
        if bone_name not in arm.bones:
            continue
        # store a tuple instead of a Vector
        result_data[bone_name] = (arm.edit_bones[bone_name].head[0], arm.edit_bones[bone_name].head[1],
                                  arm.edit_bones[bone_name].head[2])
    return result_data

def get_frame_save_data(context, arm, action_frame_label, ref_bones_action_name):
    action_frames = {}
    for action in bpy.data.actions:
        if not action.select or not is_bone_action(action):
            continue
        frame_data = {}
        for fc in action.fcurves:
            if not fc.data_path.startswith("pose.bones["):
                continue
            if fc.data_path in frame_data:
                frame_data[fc.data_path][fc.array_index] = fc.evaluate(EVAL_FRAME_NUM)
            else:
                frame_data[fc.data_path] = { fc.array_index: fc.evaluate(EVAL_FRAME_NUM) }
        if len(frame_data) > 0:
            action_frames[action.name] = frame_data
    if len(action_frames) == 0:
        return None
    save_data = { "action_frames": action_frames }
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='EDIT')
    ref_bone_loc_data = get_ref_bone_loc_data(arm, ref_bones_action_name)
    bpy.ops.object.mode_set(mode=old_3dview_mode)
    if ref_bone_loc_data != None:
        save_data["ref_bone_locations"] = ref_bone_loc_data
    if isinstance(action_frame_label, str) and action_frame_label != "":
        return { "label": action_frame_label, "data": save_data }
    else:
        return { "data": save_data }

def save_action_frames_to_text(context, arm, text_name, action_frame_label, ref_bones_action_name):
    save_data = get_frame_save_data(context, arm, action_frame_label, ref_bones_action_name)
    if save_data is None:
        return None
    txt = bpy.data.texts.new(text_name)
    txt.write( str(save_data) )
    return txt

def save_action_frames_to_preset(context, arm, filepath, action_frame_label, ref_bones_action_name):
    save_data = get_frame_save_data(context, arm, action_frame_label, ref_bones_action_name)
    if save_data is None:
        return None
    try:
        with open(filepath, "w") as save_file:
            save_file.write( str(save_data) )
        return None
    except:
        return traceback.format_exc()

def add_point_to_bounds(bounds, point):
    if bounds["min"] is None:
        bounds["min"] = point
    else:
        bounds["min"] = [ point[x] if point[x] < bounds["min"][x] else bounds["min"][x] for x in range(3) ]
    if bounds["max"] is None:
        bounds["max"] = point
    else:
        bounds["max"] = [ point[x] if point[x] > bounds["max"][x] else bounds["max"][x] for x in range(3) ]

def create_actions_from_frame_data(ob, frame_data, action_name_prepend, mark_asset):
    if ob.animation_data is None:
        ob.animation_data_create()
    arm = ob.data
    action_frames_data = frame_data.get("action_frames")
    ref_bone_loc_data = frame_data.get("ref_bone_locations")
    if not isinstance(action_frames_data, dict):
        return 0
    ref_location_scale = { 0: 1.0, 1: 1.0, 2: 1.0 }
    # get bounds scaling from bone head location data
    if isinstance(ref_bone_loc_data, dict) and arm != None:
        current_bounds = { "min": None, "max": None }
        ref_bounds = { "min": None, "max": None }
        old_3dview_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='EDIT')
        for ref_bone_name, ref_bone_loc in ref_bone_loc_data.items():
            if not isinstance(ref_bone_name, str) or not isinstance(ref_bone_loc, (list, tuple)) \
                or len(ref_bone_loc) != 3 or not (isinstance(ref_bone_loc[0], int) \
                and isinstance(ref_bone_loc[1], int) and isinstance(ref_bone_loc[2], int)):
                continue
            if not ref_bone_name in arm.bones:
                continue
            current_bone_loc = [ arm.edit_bones[ref_bone_name].head[x] for x in range(3) ]
            add_point_to_bounds(current_bounds, current_bone_loc)
            add_point_to_bounds(ref_bounds, ref_bone_loc)
        bpy.ops.object.mode_set(mode=old_3dview_mode)
        if current_bounds["min"] != None and current_bounds["max"] != None and ref_bounds["min"] != None \
            and ref_bounds["max"] != None:
            current_dims = [ current_bounds["max"][x] - current_bounds["min"][x] for x in range(3) ]
            ref_dims = [ ref_bounds["max"][x] - ref_bounds["min"][x] for x in range(3) ]
            for i in range(3):
                # apply epsilon cutoff to dimension scaling values
                if current_dims[i] > 0.000000001 and ref_dims[i] > 0.000000001:
                    ref_location_scale[i] = current_dims[i] / ref_dims[i]
    num_actions_created = 0
    original_ob_action = ob.animation_data.action
    for action_name, fcurve_data in action_frames_data.items():
        if not isinstance(action_name, str) or action_name == "" or not isinstance(fcurve_data, dict):
            continue
        datapath_value_pairs = []
        for data_path, indexed_values in fcurve_data.items():
            if not isinstance(data_path, str) or data_path == "" or not isinstance(indexed_values, dict):
                continue
            if not data_path.startswith("pose.bones["):
                continue
            index_value_pairs = []
            for i, v in indexed_values.items():
                if not isinstance(i, int) or not isinstance(v, float):
                    continue
                index_value_pairs.append( (i, v) )
            if len(index_value_pairs) == 0:
                continue
            datapath_value_pairs.append( (data_path, index_value_pairs) )
        if len(datapath_value_pairs) == 0:
            continue
        current_action = bpy.data.actions.new(action_name_prepend+action_name)
        ob.animation_data.action = current_action
        for data_path, indexed_values in datapath_value_pairs:
            fc_tokens, _ = lex_py_attributes(data_path)
            if len(fc_tokens) < 4:
                continue
            bone_name = data_path[ fc_tokens[2][0]+2 : fc_tokens[2][1]-2 ]
            if bone_name not in ob.pose.bones:
                continue
            prop_name = data_path[data_path.rfind(".")+1:]
            thing_to_keyframe = get_thing_to_keyframe(ob, data_path, fc_tokens, bone_name)
            if thing_to_keyframe is None:
                continue
            thing_prop_to_keyframe = getattr(thing_to_keyframe, prop_name)
            if thing_prop_to_keyframe is None:
                continue
            for index, value in indexed_values:
                if hasattr(thing_prop_to_keyframe, "__len__"):
                    if not thing_to_keyframe.keyframe_insert(data_path=prop_name, index=index, frame=LOAD_FRAME_NUM,
                                                             group=bone_name):
                        continue
                else:
                    if not thing_to_keyframe.keyframe_insert(data_path=prop_name, frame=LOAD_FRAME_NUM,
                                                             group=bone_name):
                        continue
                fc = current_action.fcurves.find(data_path=data_path, index=index)
                if fc is None:
                    continue
                if hasattr(thing_prop_to_keyframe, "__len__"):
                    fc.color_mode = 'AUTO_RGB'
                actual_value = value
                # apply reference bone location scaling to location F-Curves only
                if len(fc_tokens) == 4 and prop_name == 'location' and index in range(3):
                    actual_value *= ref_location_scale[index]
                kp = fc.keyframe_points[0]
                kp.co = (LOAD_FRAME_NUM, actual_value)
        # stash Action
        track = ob.animation_data.nla_tracks.new()
        track.name = get_next_name(ob.animation_data.nla_tracks, "[Action Stash]")
        track.mute = True
        track.lock = True
        track.strips.new(current_action.name, int(current_action.frame_range[0]), current_action)
        if mark_asset:
            current_action.asset_mark()
        num_actions_created += 1
    ob.animation_data.action = original_ob_action
    return num_actions_created

def load_action_frames_from_text(ob, text_name, action_name_prepend, mark_asset):
    txt = bpy.data.texts.get(text_name)
    if txt is None:
        return 0
    lines = [ l.body for l in txt.lines ]
    if len(lines) == 0:
        return 0
    eval_result = ast_literal_eval_lines(lines)
    if not isinstance(eval_result.get("result"), dict) or not isinstance(eval_result["result"].get("data"), dict):
        return 0
    return create_actions_from_frame_data(ob, eval_result["result"]["data"], action_name_prepend, mark_asset)

def load_action_frames_from_preset(ob, pose_preset, action_name_prepend, mark_asset):
    v_preset = viseme_actions_presets.get(pose_preset)
    if not isinstance(v_preset.get("data"), dict):
        return 0
    return create_actions_from_frame_data(ob, v_preset.get("data"), action_name_prepend, mark_asset)

def convert_moho_file(filepath):
    try:
        with open(filepath) as f:
            lines_read = f.readlines()
    except:
        return None
    script_data = {}
    for line in lines_read:
        if line == "" or line.startswith("Moho"):
            continue
        # tokenize line by whitespace, to try and get two things: key value
        line_tokens = line.split()
        if len(line_tokens) < 2:
            continue
        try:
            key = int(line_tokens[0])
        except:
            continue
        if key in script_data:
            continue
        script_data[key] = line_tokens[1]
    return script_data

def exec_viseme_action_script(arm_list, mesh_list, mod_script_data, action_name_prepend, replace_unknown_action_name,
                              shapekey_name_prepend, replace_unknown_shapekey_name):
    # create animation / Action data if needed, before applying script
    total_list = arm_list.copy()
    total_list.extend(mesh_list)
    for ob in total_list:
        if ob.animation_data is None:
            ob.animation_data_create()
        if ob.animation_data.action is None:
            ob.animation_data.action = bpy.data.actions.new(ob.name+"Action")
    # apply frames of script to Armature and Mesh objects
    prev_action_name = None
    prev_sk_names = { m.name: None for m in mesh_list }
    used_sk_names = { m.name: [] for m in mesh_list }
    prev_frame = None
    for frame, command_name in mod_script_data.items():
        action_name = action_name_prepend + command_name
        if action_name not in bpy.data.actions and replace_unknown_action_name in bpy.data.actions:
            action_name = replace_unknown_action_name
        # copy Action frames with Armature objects
        for arm_ob in arm_list:
            if prev_action_name != None and prev_action_name != action_name:
                copy_action_frame(arm_ob, prev_action_name, (1.0, 1.0, 1.0), 1.0, (1.0, 1.0, 1.0), 1.0, 1.0, False,
                                  False, frame, arm_ob.animation_data.action, True)
            copy_action_frame(arm_ob, action_name, (1.0, 1.0, 1.0), 1.0, (1.0, 1.0, 1.0), 1.0, 1.0, False, False,
                              frame, arm_ob.animation_data.action, False)
        prev_action_name = action_name
        # keyframe Shape Keys with Mesh objects
        shapekey_name = shapekey_name_prepend + command_name
        for mesh_ob in mesh_list:
            if mesh_ob.data is None or mesh_ob.data.shape_keys is None:
                continue
            sk_name = shapekey_name
            if sk_name not in mesh_ob.data.shape_keys.key_blocks:
                if replace_unknown_shapekey_name not in mesh_ob.data.shape_keys.key_blocks:
                    continue
                sk_name = replace_unknown_shapekey_name
            if prev_sk_names[mesh_ob.name] != None:
                keyframe_shapekey_value(mesh_ob, prev_sk_names[mesh_ob.name], frame, 0.0)
            keyframe_shapekey_value(mesh_ob, sk_name, frame, 1.0)
            prev_sk_names[mesh_ob.name] = sk_name
            # check for keyframe 0.0 value before current frame, so that all Shape Keys 'start' with 0.0 instead of 1.0
            if prev_frame != None:
                if sk_name not in used_sk_names[mesh_ob.name]:
                    keyframe_shapekey_value(mesh_ob, sk_name, prev_frame, 0.0)
        prev_frame = frame

def load_viseme_script_moho(filepath, arm_list, mesh_list, frame_scale, frame_offset, replace_unknown_action_name,
                            replace_unknown_shapekey_name, action_name_prepend, shapekey_name_prepend):
    # read script from file
    script_data = convert_moho_file(filepath)
    if script_data is None:
        return "Unable to load MOHO file " % filepath
    # apply frame scale and offset to script
    mod_script_data = {}
    for key_int, val_str in script_data.items():
        mod_key_int = int(key_int * frame_scale) + frame_offset
        if mod_key_int in mod_script_data:
            continue
        mod_script_data[mod_key_int] = val_str
    if len(mod_script_data) == 0:
        return 0
    exec_viseme_action_script(arm_list, mesh_list, mod_script_data, action_name_prepend, replace_unknown_action_name,
                              shapekey_name_prepend, replace_unknown_shapekey_name)
    return None
