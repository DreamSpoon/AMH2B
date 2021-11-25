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
#
# Automate MakeHuman 2 Blender (AMH2B)
#   Blender 2.79 - 2.93 Addon
# A set of tools to automate the process of shading/texturing, and animating MakeHuman data imported in Blender.

import copy
import csv
import random
from mathutils import Euler, Quaternion
import bpy

# basis, in seconds
# format of kf_data = [ (time, value, handle_left_x, handle_left_y, handle_right_x, handle_right_y), ... ]
basis_blink_closing_kf_data = [
    (0.000000, 0.000000,
     0.000000, 0.000000,
     0.066666, 0.000000),
    (0.100000, 1.000000,
     0.033333, 1.000000,
     0.200000, 1.000000),
]
basis_blink_opening_kf_data = [
    (0.000000, 1.000000,
     0.000000, 1.000000,
     0.100000, 1.000000),
    (0.166666, 0.166666,
     0.033333, 0.333333,
     0.300000, 0.000000),
    (0.475000, 0.000000,
     0.400000, 0.000000,
     0.500000, 0.000000),
]
basis_blink_closing_time = 0.100000
basis_blink_opening_time = 0.475000

default_blink_settings = {
    "closing_time": 0.1,
    "random_closing_time": 0,
    "closed_time": 0.0,
    "random_closed_time": 0,
    "opening_time": 0.475,
    "random_opening_time": 0,
    "use_period": False,
    "allow_random_drift": False,
    "blink_period": 6,
    "blinks_per_minute": 10,
    "random_blink_period": 0,
    "enable_left": True,
    "enable_right": True,
    "shapekey_name": "",
}

current_blink_settings = copy.deepcopy(default_blink_settings)

# 0 is left eye, 1 is right eye
default_eye_name_settings = [
    [ "lolid.L", "uplid.L" ],
    [ "lolid.R", "uplid.R" ]
]

current_eye_name_settings = copy.deepcopy(default_eye_name_settings)

# default_eye_opened_closed_settings[left_and_right][lo_and_up][open_and_close]
default_eye_opened_closed_settings = [
    [
        [
            ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ),
            ( (0, 0, 0), 'QUATERNION', (0.992546, -0.121869, 0, 0) )
        ],
        [
            ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ),
            ( (0, 0, 0), 'QUATERNION', (0.984808, 0.173648, 0, 0) )
        ]
    ],
    [
        [
            ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ),
            ( (0, 0, 0), 'QUATERNION', (0.992546, -0.121869, 0, 0) )
        ],
        [
            ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ),
            ( (0, 0, 0), 'QUATERNION', (0.984808, 0.173648, 0, 0) )
        ]
    ]
]

current_eye_opened_closed_settings = copy.deepcopy(default_eye_opened_closed_settings)

csv_eoc_record_names = [
    [
        [ "left_lo_opened", "left_lo_closed" ],
        [ "left_up_opened", "left_up_closed" ]
    ],
    [
        [ "right_lo_opened", "right_lo_closed" ],
        [ "right_up_opened", "right_up_closed" ]
    ]
]

I_LEFT = 0
I_RIGHT = 1

I_LOWER = 0
I_UPPER = 1

I_OPENED = 0
I_CLOSED = 1

D_LOC = 0
D_ROT_MODE = 1
D_ROT = 2

F_MIN_CLOSING_TIME = 0.0001
F_MIN_OPENING_TIME = 0.0001

# linear interpolation from y1 to y2, as x varies from 0 to 1
def d_lerp(y1, y2, x):
    if x < 0:
        return y1
    elif x > 1:
        return y2
    else:
        # ref: https://en.wikipedia.org/wiki/Linear_interpolation
        return (1 - x) * y1 + x * y2

def random_plus_minus_half(input_val):
    return random.uniform( input_val / -2, input_val / 2 )

def set_keyframe_point_from_data(kp, data_point):
    kp.handle_left_type = 'ALIGNED'
    kp.handle_right_type = 'ALIGNED'
    kp.interpolation = 'BEZIER'
    kp.easing = 'AUTO'
    kp.co = (data_point[0], data_point[1])
    kp.handle_left = (data_point[2], data_point[3])
    kp.handle_right = (data_point[4], data_point[5])

# format of kf_data = [ (frame, value, handle_left_x, handle_left_y, handle_right_x, handle_right_y), ... ]
# frame is Also Known As time (if between 0 and 1)
def bone_insert_keyframes(obj, bone_name, kf_type, axis_index, kf_data):
    if len(kf_data) < 1:
        return
    # try to get data path for bone, e.g. rotation, location
    dp = None
    try:
        dp = obj.pose.bones[bone_name].path_from_id(kf_type)
    except:
        return
    fc = None
    action = None
    if obj.animation_data is not None:
        action = obj.animation_data.action
    # if keyframe data exists then try to get f-curve for given keyframe type and axis
    if action is not None:
        fc = action.fcurves.find(data_path=dp, index=axis_index)
    # if f-curve does not exist then insert a keyframe to initialize it
    skip_first = False
    if fc is None:
        # create the f-curve by inserting the first keyframe
        if not obj.keyframe_insert(data_path=dp, index=axis_index, frame=kf_data[0][0]):
            return
        # get the f-curve for the shapekey value
        action = obj.animation_data.action
        fc = action.fcurves.find(data_path=dp, index=axis_index)
        if fc is None:
            return
        # get the first point on the f-curve, and set it, then set flag to ignore the first point
        kp = fc.keyframe_points[0]
        set_keyframe_point_from_data(kp, kf_data[0])
        skip_first = True
    # insert point into the f-curve
    for data_point in kf_data:
        if skip_first:
            skip_first = False
            continue
        # insert the point and set it's keyframe data (e.g. Bezier handles)
        kp = fc.keyframe_points.insert(frame=data_point[0], value=data_point[1])
        set_keyframe_point_from_data(kp, data_point)

def bone_constraint_insert_keyframes(obj, datapath, kf_data):
    if len(kf_data) < 1:
        return
    fc = None
    action = None
    if obj.animation_data is not None:
        action = obj.animation_data.action
    # if keyframe data exists then try to get f-curve for given keyframe type and axis
    if action is not None:
        fc = action.fcurves.find(data_path=datapath)
    # if f-curve does not exist then insert a keyframe to initialize it
    skip_first = False
    if fc is None:
        # create the f-curve by inserting the first keyframe
        if not obj.keyframe_insert(data_path=datapath, frame=kf_data[0][0]):
            return
        # get the f-curve for the shapekey value
        action = obj.animation_data.action
        fc = action.fcurves.find(data_path=datapath)
        if fc is None:
            return
        # get the first point on the f-curve, and set it, then set flag to ignore the first point
        kp = fc.keyframe_points[0]
        set_keyframe_point_from_data(kp, kf_data[0])
        skip_first = True
    # insert point into the f-curve
    for data_point in kf_data:
        if skip_first:
            skip_first = False
            continue
        # insert the point and set it's keyframe data (e.g. Bezier handles)
        kp = fc.keyframe_points.insert(frame=data_point[0], value=data_point[1])
        set_keyframe_point_from_data(kp, data_point)

def shapekey_insert_keyframes(obj, shapekey_name, kf_data):
    if len(kf_data) < 1:
        return
    if obj.data.shape_keys is None:
        return
    sk = obj.data.shape_keys.key_blocks.get(shapekey_name)
    if sk is None:
        return
    dp = sk.path_from_id('value')
    action = None
    if obj.data.shape_keys.animation_data is not None:
        action = obj.data.shape_keys.animation_data.action
    fc = None
    # if keyframe data exists then try to get f-curve for given keyframe type
    if action is not None:
        fc = action.fcurves.find(data_path=dp)
    # if f-curve does not exist then insert a keyframe to initialize it
    skip_first = False
    if fc is None:
        # create the f-curve by inserting the first keyframe
        if not sk.keyframe_insert(data_path='value', frame=kf_data[0][0]):
            return
        # get the f-curve for the shapekey value
        action = obj.data.shape_keys.animation_data.action
        fc = action.fcurves.find(data_path=dp)
        if fc is None:
            return
        # get the first point on the f-curve, and set it, then set flag to ignore the first point
        kp = fc.keyframe_points[0]
        set_keyframe_point_from_data(kp, kf_data[0])
        skip_first = True
    # insert point into the f-curve
    for data_point in kf_data:
        if skip_first:
            skip_first = False
            continue
        # insert the point and set it's keyframe data (e.g. Bezier handles)
        kp = fc.keyframe_points.insert(frame=data_point[0], value=data_point[1])
        set_keyframe_point_from_data(kp, data_point)

# hint: open eye is zero (0), closed eye is one (1)
def generate_blink(frame_rate, start_frame, closing_time, closed_time, opening_time, open_val, closed_val):
    kf_data_out = []

    mark_frame = start_frame
    closing_mult = closing_time / basis_blink_closing_time
    opening_mult = opening_time / basis_blink_opening_time

    # first closing point; y = 0 override
    point_time, point_value, handle_left_x, handle_left_y, handle_right_x, handle_right_y = basis_blink_closing_kf_data[0]
    pt = mark_frame + (point_time * closing_mult * frame_rate)
    pv = d_lerp(open_val, closed_val, point_value)
    # set left handle x to blink start time less half of a frame
    hl_x = mark_frame - 0.5
    hl_y = d_lerp(open_val, closed_val, handle_left_y)
    hr_x = mark_frame + (handle_right_x * closing_mult * frame_rate)
    hr_y = d_lerp(open_val, closed_val, handle_right_y)
    # append point
    kf_data_out.append((pt, pv, hl_x, hl_y, hr_x, hr_y))

    if closed_time > 0:
        # end of closing_time, and start of closed_time
        point_time, point_value, handle_left_x, handle_left_y, handle_right_x, handle_right_y = basis_blink_closing_kf_data[1]
        pt = mark_frame + (point_time * closing_mult * frame_rate)
        pv = d_lerp(open_val, closed_val, point_value)
        hl_x = mark_frame + (handle_left_x * closing_mult * frame_rate)
        hl_y = d_lerp(open_val, closed_val, handle_left_y)

        # ..., and start of closed_time
        hr_x = mark_frame + (closed_time / 2 * frame_rate)
        hr_y = d_lerp(open_val, closed_val, 1)
        # append point
        kf_data_out.append((pt, pv, hl_x, hl_y, hr_x, hr_y))

        mark_frame = mark_frame + ((closing_time + closed_time) * frame_rate)
        point_time, point_value, handle_left_x, handle_left_y, handle_right_x, handle_right_y = basis_blink_opening_kf_data[0]
        pt = mark_frame + (point_time * opening_mult * frame_rate)
        pv = d_lerp(open_val, closed_val, point_value)
        hl_x = mark_frame - (closed_time / 2 * frame_rate)
        hl_y = d_lerp(open_val, closed_val, 1)
        hr_x = mark_frame + (handle_right_x * opening_mult * frame_rate)
        hr_y = d_lerp(open_val, closed_val, handle_right_y)
        # append point
        kf_data_out.append((pt, pv, hl_x, hl_y, hr_x, hr_y))
    else:
        # end of closing_time, and start of opening_time
        point_time, point_value, handle_left_x, handle_left_y, handle_right_x, handle_right_y = basis_blink_closing_kf_data[1]
        pt = mark_frame + (point_time * closing_mult * frame_rate)
        pv = d_lerp(open_val, closed_val, point_value)
        hl_x = mark_frame + (handle_left_x * closing_mult * frame_rate)
        hl_y = d_lerp(open_val, closed_val, handle_left_y)

        mark_frame = mark_frame + (closing_time * frame_rate)

        # ..., and start of opening_time
        point_time, point_value, handle_left_x, handle_left_y, handle_right_x, handle_right_y = basis_blink_opening_kf_data[0]
        hr_x = mark_frame + (handle_right_x * opening_mult * frame_rate)
        hr_y = d_lerp(open_val, closed_val, 1)
        # append point
        kf_data_out.append((pt, pv, hl_x, hl_y, hr_x, hr_y))

    # middle point in opening data
    point_time, point_value, handle_left_x, handle_left_y, handle_right_x, handle_right_y = basis_blink_opening_kf_data[1]
    pt = mark_frame + (point_time * opening_mult * frame_rate)
    pv = d_lerp(open_val, closed_val, point_value)
    hl_x = mark_frame + (handle_left_x * opening_mult * frame_rate)
    hl_y = d_lerp(open_val, closed_val, handle_left_y)
    hr_x = mark_frame + (handle_right_x * opening_mult * frame_rate)
    hr_y = d_lerp(open_val, closed_val, handle_right_y)
    # append point
    kf_data_out.append((pt, pv, hl_x, hl_y, hr_x, hr_y))

    # end point in opening data
    point_time, point_value, handle_left_x, handle_left_y, handle_right_x, handle_right_y = basis_blink_opening_kf_data[2]
    pt = mark_frame + (point_time * opening_mult * frame_rate)
    pv = d_lerp(open_val, closed_val, point_value)
    hl_x = mark_frame + (handle_left_x * opening_mult * frame_rate)
    hl_y = d_lerp(open_val, closed_val, handle_left_y)
    hr_x = mark_frame + (opening_time * opening_mult * frame_rate) + 0.5
    hr_y = d_lerp(open_val, closed_val, 0)
    # append point
    kf_data_out.append((pt, pv, hl_x, hl_y, hr_x, hr_y))

    return kf_data_out

# TODO: choose non-default rot_mode, e.g. when user clicks the 'set' button for opened/closed data setting
default_use_rot_mode = I_OPENED
# return only the modified (open vs. closed) values from eoc_settings, modified settings is array of 5-tuples:
#   [("bone_name", "data_type", axis_index, opened_value, closed_value), ...]
def get_mod_eoc_settings(en_settings, eoc_settings, enable_left, enable_right):
    eye_range = []
    if enable_left:
        eye_range.append(0)
    if enable_right:
        eye_range.append(1)
    if len(eye_range) < 1:
        return []
    result_mods = []
    # left and right
    for i in eye_range:
        # lower and upper
        for lu in range(2):
            # location
            t1 = eoc_settings[i][lu][I_OPENED][D_LOC]
            t2 = eoc_settings[i][lu][I_CLOSED][D_LOC]
            for ax_index in range(3):
                if t1[ax_index] != t2[ax_index]:
                    result_mods.append((en_settings[i][lu], "location", ax_index, t1[ax_index], t2[ax_index]))
            # rotation
            rot_mode = eoc_settings[i][lu][default_use_rot_mode][D_ROT_MODE]
            if rot_mode == 'QUATERNION':
                r = [(1, 0, 0, 0), (1, 0, 0, 0)]
                # opened and closed
                for oc in range(2):
                    if eoc_settings[i][lu][oc][D_ROT_MODE] == 'QUATERNION':
                        r[oc] = (eoc_settings[i][lu][oc][D_ROT][0], eoc_settings[i][lu][oc][D_ROT][1],
                            eoc_settings[i][lu][oc][D_ROT][2], eoc_settings[i][lu][oc][D_ROT][3])
                    elif eoc_settings[i][lu][oc][D_ROT_MODE] == 'AXIS_ANGLE':
                        angle = eoc_settings[i][lu][oc][D_ROT][0]
                        axis = (eoc_settings[i][lu][oc][D_ROT][1],
                            eoc_settings[i][lu][oc][D_ROT][2],
                            eoc_settings[i][lu][oc][D_ROT][3])
                        rot_mat = Matrix.Rotation(angle, 4, axis)
                        r[oc] = rot_mat.to_quaternion()
                    else:   # euler
                        r[oc] = Euler(eoc_settings[i][lu][oc][D_ROT],
                            eoc_settings[i][lu][oc][D_ROT_MODE]).to_quaternion()
                # check w, x, y, z for modifications
                for ax_index in range(4):
                    if r[0][ax_index] != r[1][ax_index]:
                        result_mods.append((en_settings[i][lu], "rotation_quaternion", ax_index, r[0][ax_index], r[1][ax_index]))
            elif rot_mode == 'AXIS_ANGLE':
                r = [(0, 0, 1, 0), (0, 0, 1, 0)]
                # opened and closed
                for oc in range(2):
                    if eoc_settings[i][lu][oc][D_ROT_MODE] == 'QUATERNION':
                        axis, angle = Quaternion(eoc_settings[i][lu][oc][D_ROT]).to_axis_angle()
                        r[oc] = (angle, axis[0], axis[1], axis[2])
                    elif eoc_settings[i][lu][oc][D_ROT_MODE] == 'AXIS_ANGLE':
                        r[oc] = (eoc_settings[i][lu][oc][D_ROT][0], eoc_settings[i][lu][oc][D_ROT][1],
                            eoc_settings[i][lu][oc][D_ROT][2], eoc_settings[i][lu][oc][D_ROT][3])
                    else:   # euler
                        axis, angle = Quaternion(Euler(eoc_settings[i][lu][oc][D_ROT],
                            eoc_settings[i][lu][oc][D_ROT_MODE]).to_quaternion()).to_axis_angle()
                        r[oc] = (angle, axis[0], axis[1], axis[2])
                # check angle, x, y, z for modifications
                for ax_index in range(4):
                    if r[0][ax_index] != r[1][ax_index]:
                        result_mods.append((en_settings[i][lu], "rotation_axis_angle", ax_index, r[0][ax_index], r[1][ax_index]))
            else:   # euler
                r = [(0, 0, 0), (0, 0, 0)]
                # opened and closed
                for oc in range(2):
                    if eoc_settings[i][lu][oc][D_ROT_MODE] == 'QUATERNION':
                        r[oc] = Quaternion(eoc_settings[i][lu][oc][D_ROT]).to_euler(rot_mode)
                    elif eoc_settings[i][lu][oc][D_ROT_MODE] == 'AXIS_ANGLE':
                        angle = eoc_settings[i][lu][oc][D_ROT][0]
                        axis = (eoc_settings[i][lu][oc][D_ROT][1],
                            eoc_settings[i][lu][oc][D_ROT][2],
                            eoc_settings[i][lu][oc][D_ROT][3])
                        rot_mat = Matrix.Rotation(angle, 4, axis)
                        r[oc] = rot_mat.to_euler(rot_mode)
                    else:
                        r[oc] = (eoc_settings[i][lu][oc][D_ROT][0], eoc_settings[i][lu][oc][D_ROT][1], eoc_settings[i][lu][oc][D_ROT][2])
                # check x, y, z for modifications
                for ax_index in range(3):
                    if r[0][ax_index] != r[1][ax_index]:
                        result_mods.append((en_settings[i][lu], "rotation_euler", ax_index, r[0][ax_index], r[1][ax_index]))

    return result_mods

def generate_blink_track(arm_obj, mesh_obj, frame_rate, start_frame, random_start_frame, frame_count, max_blink_count,
                         b_settings, en_settings, eoc_settings):
    # get start frame of first blink
    rsf = random.uniform(0, random_start_frame)
    cur_start_frame = start_frame + rsf
    # get blink period
    if b_settings["use_period"]:
        blink_period = b_settings["blink_period"]
    else:
        if b_settings["blinks_per_minute"] <= 0:
            return
        blink_period = 60 / b_settings["blinks_per_minute"]

    # get bones and datapaths that need keyframes added
    sub_eoc_settings = get_mod_eoc_settings(en_settings, eoc_settings,
        b_settings["enable_left"], b_settings["enable_right"])

    # generate blink track
    blink_count = 0
    blinking = True
    while blinking == True:
        blink_count = blink_count + 1
        # calc timing
        closing_time = b_settings["closing_time"] + random_plus_minus_half(b_settings["random_closing_time"])
        if closing_time < F_MIN_CLOSING_TIME:
            closing_time = F_MIN_CLOSING_TIME
        closed_time = b_settings["closed_time"] + random_plus_minus_half(b_settings["random_closed_time"])
        if closed_time < 0:
            closed_time = 0
        opening_time = b_settings["opening_time"] + random_plus_minus_half(b_settings["random_opening_time"])
        if opening_time < F_MIN_OPENING_TIME:
            opening_time = F_MIN_OPENING_TIME
        # insert bone keyframes, if needed
        if arm_obj is not None:
            # generate keyframes for each used data type (i.e. location, rotation) and axis
            for bone_name, data_type, axis_index, opened_value, closed_value in sub_eoc_settings:
                # get keyframe data for the blink
                kf_data = generate_blink(frame_rate, cur_start_frame, closing_time, closed_time, opening_time,
                    opened_value, closed_value)
                # insert bone keyframes
                bone_insert_keyframes(arm_obj, bone_name, data_type, axis_index, kf_data)

            # generate keyframes for every 'Copy Rotation' bone constraint on every eye bone
            for i in range(2):
                for lu in range(2):
                    bone = arm_obj.pose.bones.get(current_eye_name_settings[i][lu])
                    for b_constraint in bone.constraints:
                        if b_constraint.type != 'COPY_ROTATION':
                            continue
                        dp = b_constraint.path_from_id() + ".influence"
                        # get keyframe data for the 'bone constraint' blink
                        kf_data = generate_blink(frame_rate, cur_start_frame, closing_time, closed_time, opening_time,
                                                 b_constraint.influence, 0)
                        bone_constraint_insert_keyframes(arm_obj, dp, kf_data)

        # insert shapekey keyframes, if needed
        if mesh_obj is not None and b_settings["shapekey_name"] != "":
            # get keyframe data for the shapekey blink
            kf_data = generate_blink(frame_rate, cur_start_frame, closing_time, closed_time, opening_time, 0, 1)
            shapekey_insert_keyframes(mesh_obj, b_settings["shapekey_name"], kf_data)

        # allow random drift of beat timing, or ...
        if b_settings["allow_random_drift"]:
            cur_start_frame = cur_start_frame + blink_period * frame_rate
        # ..., or no drift
        else:
            cur_start_frame = start_frame + rsf + blink_count * blink_period * frame_rate
        # offset random
        cur_start_frame = cur_start_frame + random_plus_minus_half(b_settings["random_blink_period"]) * frame_rate

        # check for end of blinking due to max number of blinks
        if max_blink_count > 0 and blink_count >= max_blink_count:
            blinking = False
        # check for end of blinking due to max number of frames
        elif cur_start_frame >= start_frame + frame_count:
            blinking = False

def set_current_b_settings(scn):
    current_blink_settings["closing_time"] = scn.Amh2bPropEBlinkClosingTime
    current_blink_settings["random_closing_time"] = scn.Amh2bPropEBlinkRndClosingTime
    current_blink_settings["closed_time"] = scn.Amh2bPropEBlinkClosedTime
    current_blink_settings["random_closed_time"] = scn.Amh2bPropEBlinkRndClosedTime
    current_blink_settings["opening_time"] = scn.Amh2bPropEBlinkOpeningTime
    current_blink_settings["random_opening_time"] = scn.Amh2bPropEBlinkRndOpeningTime
    current_blink_settings["blinks_per_minute"] = scn.Amh2bPropEBlinkBlinksPerMinute
    current_blink_settings["use_period"] = scn.Amh2bPropEBlinkUseBlinkPeriod
    current_blink_settings["blink_period"] = scn.Amh2bPropEBlinkPeriod
    current_blink_settings["random_blink_period"] = scn.Amh2bPropEBlinkRndPeriod
    current_blink_settings["allow_random_drift"] = scn.Amh2bPropEBlinkAllowRndDrift
    current_blink_settings["enable_left"] = scn.Amh2bPropEBlinkEnableLeft
    current_blink_settings["enable_right"] = scn.Amh2bPropEBlinkEnableRight
    current_blink_settings["shapekey_name"] = scn.Amh2bPropEBlinkShapekeyName

def set_current_en_settings(scn):
    current_eye_name_settings[0][0] = scn.Amh2bPropEBlinkBNameLeftLower
    current_eye_name_settings[0][1] = scn.Amh2bPropEBlinkBNameLeftUpper
    current_eye_name_settings[1][0] = scn.Amh2bPropEBlinkBNameRightLower
    current_eye_name_settings[1][1] = scn.Amh2bPropEBlinkBNameRightUpper

class AMH2B_AddBlinkTrack(bpy.types.Operator):
    """Add blink track to list of selected objects plus active object. Total list must include at least one MESH or ARMATURE object to receive the blink track.\nMESH object may receive Shapekey keyframes, ARMATURE object may receive bone keyframes"""
    bl_idname = "amh2b.eblink_add_blink_track"
    bl_label = "Add Blink Track"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        arm_obj = None
        mesh_obj = None
        # create list of all selected objects and active object, without duplicates
        o_bunch = bpy.context.selected_objects.copy()
        if bpy.context.active_object not in o_bunch:
            o_bunch.append(bpy.context.active_object)
        # check selected objects, and active object, for ARMATURE or MESH
        for obj in o_bunch:
            if arm_obj is None and obj.type == 'ARMATURE':
                arm_obj = obj
            if mesh_obj is None and obj.type == 'MESH':
                mesh_obj = obj
        # exit if no object to work with
        if arm_obj is None and mesh_obj is None:
            self.report({'ERROR'}, "No ARMATURE or MESH selected to add Blink Track")
            return {'CANCELLED'}
        # get settings from UI
        scn = context.scene
        frame_rate = scn.Amh2bPropEBlinkFrameRate
        start_frame = scn.Amh2bPropEBlinkStartFrame
        random_start_frame = scn.Amh2bPropEBlinkRndStartFrame
        frame_count = scn.Amh2bPropEBlinkFrameCount
        max_blink_count = 0
        if scn.Amh2bPropEBlinkUseMaxCount:
            max_blink_count = scn.Amh2bPropEBlinkMaxCount
        set_current_b_settings(scn)
        set_current_en_settings(scn)
        # do work
        generate_blink_track(arm_obj, mesh_obj, frame_rate, start_frame, random_start_frame, frame_count, max_blink_count,
            current_blink_settings, current_eye_name_settings, current_eye_opened_closed_settings)

        return {'FINISHED'}

def get_str_from_b_settings(b_settings):
    ret_str = str(b_settings["closing_time"])
    ret_str = ret_str + "," + str(b_settings["random_closing_time"])
    ret_str = ret_str + "," + str(b_settings["closed_time"])
    ret_str = ret_str + "," + str(b_settings["random_closed_time"])
    ret_str = ret_str + "," + str(b_settings["opening_time"])
    ret_str = ret_str + "," + str(b_settings["random_opening_time"])
    ret_str = ret_str + "," + str(b_settings["use_period"])
    ret_str = ret_str + "," + str(b_settings["allow_random_drift"])
    ret_str = ret_str + "," + str(b_settings["blink_period"])
    ret_str = ret_str + "," + str(b_settings["blinks_per_minute"])
    ret_str = ret_str + "," + str(b_settings["random_blink_period"])
    ret_str = ret_str + "," + str(b_settings["enable_left"])
    ret_str = ret_str + "," + str(b_settings["enable_right"])
    # add quotes around shapekey_name, and use escape characters in it, so that commas don't cause problems with CSV
    ret_str = ret_str + ",\"" + b_settings["shapekey_name"].replace('"','\\"') + "\""
    return ret_str + "\n"

def get_str_from_en_settings(en_settings):
    # add quotes around shapekey_name, and use escape characters in it, so that commas don't cause problems with CSV
    return "\""+en_settings[0][0].replace('"','\\"')+"\",\""+en_settings[0][1].replace('"','\\"')+"\",\""+ \
        en_settings[1][0].replace('"','\\"')+"\",\""+en_settings[1][1].replace('"','\\"')+"\"\n"

def get_str_from_eoc_settings(eoc_settings):
    ret_str = ""
    for i in range(2):
        for lu in range(2):
            for opcl in range(2):
                loc = eoc_settings[i][lu][opcl][D_LOC]
                ret_str = ret_str + csv_eoc_record_names[i][lu][opcl] + "," + str(loc[0]) + "," + str(loc[1]) + "," + str(loc[2])

                rot_mode = eoc_settings[i][lu][opcl][D_ROT_MODE]
                rot = eoc_settings[i][lu][opcl][D_ROT]
                if rot_mode != 'QUATERNION' and rot_mode != 'AXIS_ANGLE':
                    # euler xyz coordinates
                    ret_str = ret_str + "," + rot_mode + "," + str(rot[0]) + "," + str(rot[1]) + "," + str(rot[2])
                else:
                    # wxyz coordinates
                    ret_str = ret_str + "," + rot_mode + "," + str(rot[0]) + "," + str(rot[1]) + "," + str(rot[2]) + "," + str(rot[3])

                ret_str = ret_str + "\n"

    return ret_str

def save_blink_data_to_csv(textblock_name, b_settings, en_settings, eoc_settings):
    # create new text block
    new_textname = bpy.data.texts.new(textblock_name)

    text_str = get_str_from_b_settings(b_settings) + get_str_from_en_settings(en_settings) + get_str_from_eoc_settings(eoc_settings)
    new_textname.from_string(text_str)

class AMH2B_SaveBlinkCSV(bpy.types.Operator):
    """Write current blink data settings (timing, eye names, opened and closed locations/rotations) to a textblock in the text editor"""
    bl_idname = "amh2b.eblink_save_csv"
    bl_label = "Write Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_current_b_settings(context.scene)
        set_current_en_settings(context.scene)

        save_blink_data_to_csv(context.scene.Amh2bPropEBlinkTextSaveName, current_blink_settings, current_eye_name_settings,
                               current_eye_opened_closed_settings)
        return {'FINISHED'}

def get_bool(input_str):
    try:
        if input_str.strip().lower() == "true":
            return True
    except:
        return False
    return False

def get_b_settings_from_data(blink_data_record):
    return {
        "closing_time": float(blink_data_record[0]),
        "random_closing_time": float(blink_data_record[1]),
        "closed_time": float(blink_data_record[2]),
        "random_closed_time": float(blink_data_record[3]),
        "opening_time": float(blink_data_record[4]),
        "random_opening_time": float(blink_data_record[5]),
        "use_period": get_bool(blink_data_record[6]),
        "allow_random_drift": get_bool(blink_data_record[7]),
        "blink_period": float(blink_data_record[8]),
        "blinks_per_minute": float(blink_data_record[9]),
        "random_blink_period": float(blink_data_record[10]),
        "enable_left": get_bool(blink_data_record[11]),
        "enable_right": get_bool(blink_data_record[12]),
        "shapekey_name": blink_data_record[13],
    }

def get_en_settings_from_data(blink_data_record):
    return [
        [ blink_data_record[0], blink_data_record[1] ],
        [ blink_data_record[2], blink_data_record[3] ]
    ]

def get_eoc_settings_from_data(blink_data_records):
    eoc_settings = [
        [
            [ ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ), ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ) ],
            [ ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ), ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ) ]
        ],
        [
            [ ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ), ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ) ],
            [ ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ), ( (0, 0, 0), 'QUATERNION', (1, 0, 0, 0) ) ]
        ]
    ]
    for record in blink_data_records:
        record_name = record[0].strip()
        loc = (float(record[1]), float(record[2]), float(record[3]))
        rot_mode = record[4].strip()
        rot = None
        if rot_mode != 'QUATERNION' and rot_mode != 'AXIS_ANGLE':
            rot = (float(record[5]), float(record[6]), float(record[7]))
        else:
            rot = (float(record[5]), float(record[6]), float(record[7]), float(record[8]))

        for i in range(2):
            for lu in range(2):
                for oc in range(2):
                    if record_name == csv_eoc_record_names[i][lu][oc]:
                        eoc_settings[i][lu][oc] = (loc, rot_mode, rot)

    return eoc_settings

def load_blink_data_from_csv_lines(blink_data_lines, datablock_textname):
    rec_count = 0
    b_settings = None
    try:
        b_settings = get_b_settings_from_data(blink_data_lines[rec_count])
    except:
        return "Error while parsing CSV record #" + str(rec_count) + " in text block: " + datablock_textname

    rec_count = 1
    en_settings = None
    try:
        en_settings = get_en_settings_from_data(blink_data_lines[rec_count])
    except:
        return "Error while parsing CSV record #" + str(rec_count) + " in text block: " + datablock_textname

    rec_count = 2
    eoc_settings = None
    try:
        eoc_settings = get_eoc_settings_from_data(blink_data_lines[rec_count:len(blink_data_lines)])
    except:
        return "Error while parsing CSV record(s) #" + str(rec_count) + " to " + str(len(blink_data_lines)) + \
            " in text block: " + datablock_textname

    return b_settings, en_settings, eoc_settings

def get_csv_lines(datablock_textname):
    bl = bpy.data.texts.get(datablock_textname)
    if bl is None:
        return

    bl_str = bl.as_string()
    if bl_str == '':
        return

    csv_lines = csv.reader(bl_str.splitlines(), quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
    return list(csv_lines)

def load_blink_data_from_csv(datablock_textname):
    # get CSV user data text block and convert to array of data
    blink_data_lines = get_csv_lines(datablock_textname)
    if blink_data_lines is None:
        return "Data text block not found: " + datablock_textname
    # if a string was returned then return the string (error string)
    temp = load_blink_data_from_csv_lines(blink_data_lines, datablock_textname)
    if isinstance(temp, str):
        return temp
    # otherwise, copy the settings
    temp_blink_settings, temp_eye_name_settings, temp_eye_opened_closed_settings = temp
    # blink timing settings, etc.
    current_blink_settings["closing_time"] = temp_blink_settings["closing_time"]
    current_blink_settings["random_closing_time"] = temp_blink_settings["random_closing_time"]
    current_blink_settings["closed_time"] = temp_blink_settings["closed_time"]
    current_blink_settings["random_closed_time"] = temp_blink_settings["random_closed_time"]
    current_blink_settings["opening_time"] = temp_blink_settings["opening_time"]
    current_blink_settings["random_opening_time"] = temp_blink_settings["random_opening_time"]
    current_blink_settings["use_period"] = temp_blink_settings["use_period"]
    current_blink_settings["allow_random_drift"] = temp_blink_settings["allow_random_drift"]
    current_blink_settings["blink_period"] = temp_blink_settings["blink_period"]
    current_blink_settings["blinks_per_minute"] = temp_blink_settings["blinks_per_minute"]
    current_blink_settings["random_blink_period"] = temp_blink_settings["random_blink_period"]
    current_blink_settings["enable_left"] = temp_blink_settings["enable_left"]
    current_blink_settings["enable_right"] = temp_blink_settings["enable_right"]
    current_blink_settings["shapekey_name"] = temp_blink_settings["shapekey_name"]
    # eye bone name settings
    current_eye_name_settings[0][0] = temp_eye_name_settings[0][0]
    current_eye_name_settings[0][1] = temp_eye_name_settings[0][1]
    current_eye_name_settings[1][0] = temp_eye_name_settings[1][0]
    current_eye_name_settings[1][1] = temp_eye_name_settings[1][1]
    # eye opened/closed settings
    for i in range(2):
        for lu in range(2):
            for oc in range(2):
                current_eye_opened_closed_settings[i][lu][oc] = temp_eye_opened_closed_settings[i][lu][oc]

class AMH2B_LoadBlinkCSV(bpy.types.Operator):
    """Read blink data settings (timing, eye names, opened and closed locations/rotations) from a textblock in the text editor"""
    bl_idname = "amh2b.eblink_load_csv"
    bl_label = "Read Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene

        temp = load_blink_data_from_csv(context.scene.Amh2bPropEBlinkTextLoadName)
        if isinstance(temp, str):
            self.report({'ERROR'}, "AMH2B_LoadBlinkCSV error: " + temp)
            return {'CANCELLED'}

        scn.Amh2bPropEBlinkClosingTime = current_blink_settings["closing_time"]
        scn.Amh2bPropEBlinkRndClosingTime = current_blink_settings["random_closing_time"]
        scn.Amh2bPropEBlinkClosedTime = current_blink_settings["closed_time"]
        scn.Amh2bPropEBlinkRndClosedTime = current_blink_settings["random_closed_time"]
        scn.Amh2bPropEBlinkOpeningTime = current_blink_settings["opening_time"]
        scn.Amh2bPropEBlinkRndOpeningTime = current_blink_settings["random_opening_time"]
        scn.Amh2bPropEBlinkBlinksPerMinute = current_blink_settings["blinks_per_minute"]
        scn.Amh2bPropEBlinkUseBlinkPeriod = current_blink_settings["use_period"]
        scn.Amh2bPropEBlinkPeriod = current_blink_settings["blink_period"]
        scn.Amh2bPropEBlinkRndPeriod = current_blink_settings["random_blink_period"]
        scn.Amh2bPropEBlinkAllowRndDrift = current_blink_settings["allow_random_drift"]
        scn.Amh2bPropEBlinkEnableLeft = current_blink_settings["enable_left"]
        scn.Amh2bPropEBlinkEnableRight = current_blink_settings["enable_right"]
        scn.Amh2bPropEBlinkShapekeyName = current_blink_settings["shapekey_name"]
        scn.Amh2bPropEBlinkBNameLeftLower = current_eye_name_settings[0][0]
        scn.Amh2bPropEBlinkBNameLeftUpper = current_eye_name_settings[0][1]
        scn.Amh2bPropEBlinkBNameRightLower = current_eye_name_settings[1][0]
        scn.Amh2bPropEBlinkBNameRightUpper = current_eye_name_settings[1][1]

        # update the UI
        self.report({'INFO'}, "Read settings complete")

        return {'FINISHED'}

def reset_eye_opened_settings():
    for i in range(2):
        for lu in range(2):
            current_eye_opened_closed_settings[i][lu][I_OPENED] = \
                copy.deepcopy(default_eye_opened_closed_settings[i][lu][I_OPENED])

class AMH2B_ResetEyeOpened(bpy.types.Operator):
    """Reset eye opened blink data (locations/rotations) to defaults"""
    bl_idname = "amh2b.eblink_reset_opened"
    bl_label = "Reset Opened"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reset_eye_opened_settings()
        return {'FINISHED'}

def reset_eye_closed_settings():
    for i in range(2):
        for lu in range(2):
            current_eye_opened_closed_settings[i][lu][I_CLOSED] = \
                copy.deepcopy(default_eye_opened_closed_settings[i][lu][I_CLOSED])

class AMH2B_ResetEyeClosed(bpy.types.Operator):
    """Reset eye closed blink data (locations/rotations) to defaults"""
    bl_idname = "amh2b.eblink_reset_closed"
    bl_label = "Reset Closed"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reset_eye_closed_settings()

        return {'FINISHED'}

def set_eye_opened_settings(obj):
    for i in range(2):
        for lu in range(2):
            b_name = current_eye_name_settings[i][lu]
            bone = obj.pose.bones.get(b_name)
            if bone is None:
                continue

            loc = bone.location
            if bone.rotation_mode == 'QUATERNION':
                rot = bone.rotation_quaternion
                current_eye_opened_closed_settings[i][lu][I_OPENED] = \
                    ((loc[0], loc[1], loc[2]), bone.rotation_mode, (rot[0], rot[1], rot[2], rot[3]))
            elif bone.rotation_mode == 'AXIS_ANGLE':
                rot = bone.rotation_axis_angle
                current_eye_opened_closed_settings[i][lu][I_OPENED] = \
                    ((loc[0], loc[1], loc[2]), bone.rotation_mode, (rot[0], rot[1], rot[2], rot[3]))
            else:
                rot = bone.rotation_euler
                current_eye_opened_closed_settings[i][lu][I_OPENED] = \
                    ((loc[0], loc[1], loc[2]), bone.rotation_mode, (rot[0], rot[1], rot[2]))

class AMH2B_SetEyeOpened(bpy.types.Operator):
    """Set eye opened blink data (locations/rotations) from active object, active object must be ARMATURE type"""
    bl_idname = "amh2b.eblink_set_opened"
    bl_label = "Set Opened"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = bpy.context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}

        set_eye_opened_settings(act_ob)
        return {'FINISHED'}

def set_eye_closed_settings(obj):
    for i in range(2):
        for lu in range(2):
            b_name = current_eye_name_settings[i][lu]
            bone = obj.pose.bones.get(b_name)
            if bone is None:
                continue

            loc = bone.location
            if bone.rotation_mode == 'QUATERNION':
                rot = bone.rotation_quaternion
                current_eye_opened_closed_settings[i][lu][I_CLOSED] = \
                    ((loc[0], loc[1], loc[2]), bone.rotation_mode, (rot[0], rot[1], rot[2], rot[3]))
            elif bone.rotation_mode == 'AXIS_ANGLE':
                rot = bone.rotation_axis_angle
                current_eye_opened_closed_settings[i][lu][I_CLOSED] = \
                    ((loc[0], loc[1], loc[2]), bone.rotation_mode, (rot[0], rot[1], rot[2], rot[3]))
            else:
                rot = bone.rotation_euler
                current_eye_opened_closed_settings[i][lu][I_CLOSED] = \
                    ((loc[0], loc[1], loc[2]), bone.rotation_mode, (rot[0], rot[1], rot[2]))


class AMH2B_SetEyeClosed(bpy.types.Operator):
    """Set eye closed blink data (locations/rotations) from active object, active object must be ARMATURE type"""
    bl_idname = "amh2b.eblink_set_closed"
    bl_label = "Set Closed"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = bpy.context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}

        set_eye_closed_settings(act_ob)
        return {'FINISHED'}
