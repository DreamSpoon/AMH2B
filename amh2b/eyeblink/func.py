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

import random

import bpy

from ..armature.func import copy_action_frame
from ..bl_util import keyframe_shapekey_value

F_MIN_CLOSING_TIME = 0.0001
F_MIN_OPENING_TIME = 0.0001

BLINK_FRAME_OPEN = "blink_frame_open"
BLINK_FRAME_CLOSE = "blink_frame_close"

def random_plus_minus_half(input_val):
    return random.uniform(input_val / -2, input_val / 2)

def generate_blink_frames(frame_rate, start_frame, closing_time, closed_time, opening_time):
    frames = { start_frame: BLINK_FRAME_OPEN }
    next_frame = start_frame + closing_time * frame_rate
    frames[next_frame] = BLINK_FRAME_CLOSE
    if closed_time > 0.0:
        next_frame = start_frame + (closing_time + closed_time) * frame_rate
        frames[next_frame] = BLINK_FRAME_CLOSE
    next_frame = start_frame + (closing_time + closed_time + opening_time) * frame_rate
    frames[next_frame] = BLINK_FRAME_OPEN
    return frames

def generate_blink_action(arm_list, mesh_list, blink_settings):
    # get start frame of first blink
    rsf = random.uniform(0, blink_settings["random_start_frame"])
    cur_start_frame = blink_settings["start_frame"] + rsf
    # get blink period
    if blink_settings["use_period"]:
        blink_period = blink_settings["blink_period"]
    else:
        if blink_settings["blinks_per_minute"] <= 0:
            return
        blink_period = 60 / blink_settings["blinks_per_minute"]
    # generate blink track
    blink_count = 0
    blinking = True
    while blinking:
        blink_count = blink_count + 1
        # calc timing
        closing_time = blink_settings["closing_time"] + random_plus_minus_half(blink_settings["random_closing_time"])
        if closing_time < F_MIN_CLOSING_TIME:
            closing_time = F_MIN_CLOSING_TIME
        closed_time = blink_settings["closed_time"] + random_plus_minus_half(blink_settings["random_closed_time"])
        if closed_time < 0:
            closed_time = 0
        opening_time = blink_settings["opening_time"] + random_plus_minus_half(blink_settings["random_opening_time"])
        if opening_time < F_MIN_OPENING_TIME:
            opening_time = F_MIN_OPENING_TIME
        # create blink (frame, close/open type) tuples
        b_frames = generate_blink_frames(blink_settings["frame_rate"], cur_start_frame, closing_time, closed_time,
                                   opening_time)
        # insert Armature Pose Bone keyframes, if needed
        if blink_settings["open_action"] != "" or blink_settings["close_action"] != "":
            for arm_ob in arm_list:
                # create animation / Action data if needed, before applying Actions
                if arm_ob.animation_data is None:
                    arm_ob.animation_data_create()
                if arm_ob.animation_data.action is None:
                    arm_ob.animation_data.action = bpy.data.actions.new(arm_ob.name+"Action")
                result_action = arm_ob.animation_data.action
                prev_a_name = None
                for frame_num, b_type in b_frames.items():
                    a_name = ""
                    use_default = False
                    if b_type == BLINK_FRAME_CLOSE:
                        if blink_settings["close_action"] == "":
                            a_name = blink_settings["open_action"]
                            use_default = True
                        else:
                            a_name = blink_settings["close_action"]
                    if b_type == BLINK_FRAME_OPEN:
                        if blink_settings["open_action"] == "":
                            a_name = blink_settings["close_action"]
                            use_default = True
                        else:
                            a_name = blink_settings["open_action"]
                    if prev_a_name != None and prev_a_name != a_name:
                        copy_action_frame(arm_ob, prev_a_name, 0, (1.0, 1.0, 1.0), 1.0, (1.0, 1.0, 1.0), 1.0, 1.0, False,
                                          False, frame_num, result_action, True)
                    copy_action_frame(arm_ob, a_name, 0, (1.0, 1.0, 1.0), 1.0, (1.0, 1.0, 1.0), 1.0, 1.0, False, False,
                                      frame_num, result_action, use_default)
                    prev_a_name = a_name
        # insert Mesh Shapekey value keyframes, if needed
        if blink_settings["close_shapekey"] != "":
            for mesh_ob in mesh_list:
                for frame_num, b_type in b_frames.items():
                    if b_type == BLINK_FRAME_CLOSE:
                        val = blink_settings["close_shapekey_on"]
                    elif b_type == BLINK_FRAME_OPEN:
                        val = blink_settings["close_shapekey_off"]
                    keyframe_shapekey_value(mesh_ob, blink_settings["close_shapekey"], frame_num, val)
        # allow random drift of beat timing, or ...
        if blink_settings["allow_random_drift"]:
            cur_start_frame = cur_start_frame + blink_period * blink_settings["frame_rate"]
        # ..., or no drift
        else:
            cur_start_frame = blink_settings["start_frame"] + rsf + blink_count * blink_period * \
                blink_settings["frame_rate"]
        # offset random
        cur_start_frame = cur_start_frame + random_plus_minus_half(blink_settings["random_blink_period"]) * \
            blink_settings["frame_rate"]
        # check for end of blinking due to max number of blinks
        if blink_settings["max_blink_count"] > 0 and blink_count >= blink_settings["max_blink_count"]:
            blinking = False
        # check for end of blinking due to max number of frames
        elif cur_start_frame >= blink_settings["start_frame"] + blink_settings["frame_count"]:
            blinking = False

def remove_keyframe_points(action, fc, start_frame, end_frame):
    # iterate through keyframe points, and remove points based on start/end frame
    # each time a point is removed, all the other points are shifted in the list
    # so deleting a point will change the references to all other points -
    # that's why the following "while" loop is used
    i = 0
    keep_going = True
    while keep_going and i < len(fc.keyframe_points):
        kp = fc.keyframe_points[i]
        if start_frame is not None and kp.co.x < start_frame:
            i = i + 1
            continue
        if end_frame is not None and kp.co.x > end_frame:
            i = i + 1
            continue
        # if only one point remains on the f-curve, and the point needs to be removed,
        # then remove the f-curve to prevent errors
        if len(fc.keyframe_points) == 1:
            action.fcurves.remove(fc)
            keep_going = False
        else:
            fc.keyframe_points.remove(fc.keyframe_points[i])

def remove_blink_fcurves(arm_list, mesh_list, open_action_name, close_action_name, close_shapekey_name, start_frame,
                         end_frame):
    remove_fcurve_datapaths = []
    if open_action_name in bpy.data.actions:
        for fc in bpy.data.actions[open_action_name].fcurves:
            if not fc.data_path in remove_fcurve_datapaths:
                remove_fcurve_datapaths.append(fc.data_path)
    if close_action_name in bpy.data.actions:
        for fc in bpy.data.actions[close_action_name].fcurves:
            if not fc.data_path in remove_fcurve_datapaths:
                remove_fcurve_datapaths.append(fc.data_path)
    if len(remove_fcurve_datapaths) > 0:
        # check Armature objects for open/close F-Curve remove by data_path
        for arm_ob in arm_list:
            action = arm_ob.animation_data.action
            if action is None:
                continue
            for fc in action.fcurves:
                if fc.data_path not in remove_fcurve_datapaths:
                    continue
                # remove bone f-curve if no start/end frames given
                if start_frame is None and end_frame is None:
                    action.fcurves.remove(fc)
                    continue
                # otherwise remove keyframe points
                remove_keyframe_points(action, fc, start_frame, end_frame)
    # check Mesh objects for Shapekey F-Curves to remove
    for mesh_obj in mesh_list:
        if mesh_obj.data.shape_keys is None:
            continue
        sk = mesh_obj.data.shape_keys.key_blocks.get(close_shapekey_name)
        if sk is None:
            continue
        dp = sk.path_from_id('value')
        if mesh_obj.data.shape_keys.animation_data is None or mesh_obj.data.shape_keys.animation_data.action is None:
            continue
        action = mesh_obj.data.shape_keys.animation_data.action
        fc = action.fcurves.find(data_path=dp)
        if fc is not None:
            # remove shapekey f-curve if no start/end frame is given
            if start_frame is None and end_frame is None:
                action.fcurves.remove(fc)
                continue
            # otherwise remove keyframe points
            remove_keyframe_points(action, fc, start_frame, end_frame)
