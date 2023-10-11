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

import ast
import traceback

import bpy

def strip_line_comment(src_line):
    dest_line = ""
    state_vars = { "backslash": False, "quote": False, "double_quote": False }
    for c in src_line:
        if c == "#":
            # ignore '#' symbols in quotes
            if state_vars["quote"]:
                pass
            # comment found
            else:
                dest_line += "\n"
                break
        elif c == "'":
            if state_vars["backslash"]:
                if state_vars["quote"]:
                    state_vars["backslash"] = False
                else:
                    if not state_vars["double_quote"]:
                        state_vars["quote"] = True
            else:
                if not state_vars["double_quote"]:
                    state_vars["quote"] = not state_vars["quote"]
        elif c == '"':
            if state_vars["backslash"]:
                if state_vars["double_quote"]:
                    state_vars["backslash"] = False
                else:
                    if not state_vars["quote"]:
                        state_vars["double_quote"] = True
            else:
                if not state_vars["quote"]:
                    state_vars["double_quote"] = not state_vars["double_quote"]
        elif c == "\\":
            state_vars["backslash"] = not state_vars["backslash"]
        elif c == "\n":
            dest_line += c
            break
        else:
            state_vars["backslash"] = False
        dest_line += c
    return dest_line

# given 'f' is an iterable set of strings (e.g. open file, or list of strings),
# returns dict() {
#     "result": < result of ast.literal_eval() with file string >,
#     "error": "< True / False >,
# }
def ast_literal_eval_lines(f):
    full_str = ""
    for line in f:
        # remove comments without modifying file line structure
        full_str += strip_line_comment(line)
    if full_str == "":
        return {}
    try:
        eval_result = ast.literal_eval(full_str)
    except:
        return { "error": traceback.format_exc() }
    return { "result": eval_result }

def ast_literal_eval_textblock(text):
    split_lines = []
    for l in text.lines:
        split_lines.append(l.body)
    if len(split_lines) == 0:
        return
    return ast_literal_eval_lines(split_lines)

def get_file_eval_dict(script_file):
    file_eval = ast_literal_eval_lines(script_file)
    if file_eval.get("error") != None:
        return file_eval.get("error")
    script = file_eval.get("result")
    if not isinstance(script, dict):
        return "Error: Script did not evaluate to type 'dict' (dictionary)"
    return script

# force screen to redraw, known to work in Blender 3.3+
def do_tag_redraw():
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D' or a.type == 'TEXT_EDITOR':
            for r in a.regions:
                r.tag_redraw()

def get_next_name(name_list, desired_name):
    if desired_name not in name_list:
        return desired_name
    for i in range(1, 9999):
        test_name = desired_name + "." + str(i).zfill(3)
        if test_name not in name_list:
            return test_name
    return desired_name

def keyframe_shapekey_value(ob, shapekey_name, frame, value):
    if ob.data is None or not hasattr(ob.data, 'shape_keys') or ob.data.shape_keys is None:
        return
    sk = ob.data.shape_keys.key_blocks.get(shapekey_name)
    if sk is None:
        return
    if ob.data.shape_keys.animation_data is None:
        ob.data.shape_keys.animation_data_create()
    if ob.data.shape_keys.animation_data.action is None:
        ob.data.shape_keys.animation_data.action = bpy.data.actions.new(ob.name+"Action")
    datapath = sk.path_from_id('value')
    action = ob.data.shape_keys.animation_data.action
    fc = action.fcurves.find(data_path=datapath)
    # if f-curve does not exist then insert a keyframe to initialize it
    if fc is None:
        if not sk.keyframe_insert(data_path='value', frame=frame):
            return
        fc = action.fcurves.find(data_path=datapath)
        if fc is None:
            return
        kp = fc.keyframe_points[0]
        kp.co = (frame, value)
    else:
        kp = fc.keyframe_points.insert(frame=frame, value=value)
