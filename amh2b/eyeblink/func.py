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
from mathutils import Euler, Matrix, Quaternion
import bpy

from ..eyelid.func import (LL_COPY_ROT_CONST_NAME, LL_LIMIT_ROT_CONST_NAME, LL_RIG_MPFB2_DEFAULT,
    LL_RIG_MHX_IMPORT, get_lidlook_data_by_rig_type)

EULER_ROT_MODES = [ 'XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX' ]

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
    "framerate": 30,
    "eblink_start_frame": 1,
    "eblink_random_start_frame": 0,
    "eblink_frame_count": 250,
    "max_blink_count": 10,
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
    "shapekey_name": "",
}

F_MIN_CLOSING_TIME = 0.0001
F_MIN_OPENING_TIME = 0.0001

EB_RIG_SELECT_BONES = "SELECT_BONES"

EYEBLINK_DATA = [
    {
        "rig_type": LL_RIG_MPFB2_DEFAULT,
        "label": "MPFB2 Default",
        "data": [
            {
                "bone_name": "orbicularis03.L",
                "location": (0.0, 0.0, 0.0),
                "rotation_mode": "XYZ",
                "rotation_euler": (-0.321170, 0.088349, -0.036050),
                },
            {
                "bone_name": "orbicularis04.L",
                "location": (0.0, 0.0, 0.0),
                "rotation_mode": "XYZ",
                "rotation_euler": (0.236586, -0.017397, -0.002989),
                },
            {
                "bone_name": "orbicularis03.R",
                "location": (0.0, 0.0, 0.0),
                "rotation_mode": "XYZ",
                "rotation_euler": (-0.321170, -0.088349, 0.036050),
                },
            {
                "bone_name": "orbicularis04.R",
                "location": (0.0, 0.0, 0.0),
                "rotation_mode": "XYZ",
                "rotation_euler": (0.236586, 0.017397, 0.002989),
                },
            ],
        },
    {
        "rig_type": LL_RIG_MHX_IMPORT,
        "label": "MHX Import",
        "data": [
            {
                "bone_name": "uplid.L",
                "location": (0.0, 0.0, 0.0),
                "rotation_mode": "QUATERNION",
                "rotation_quaternion": (0.984808, 0.173648, 0, 0),
                },
            {
                "bone_name": "lolid.L",
                "location": (0.0, 0.0, 0.0),
                "rotation_mode": "QUATERNION",
                "rotation_quaternion": (0.992546, -0.121869, 0, 0),
                },
            {
                "bone_name": "uplid.R",
                "location": (0.0, 0.0, 0.0),
                "rotation_mode": "QUATERNION",
                "rotation_quaternion": (0.984808, 0.173648, 0, 0),
                },
            {
                "bone_name": "lolid.R",
                "location": (0.0, 0.0, 0.0),
                "rotation_mode": "QUATERNION",
                "rotation_quaternion": (0.992546, -0.121869, 0, 0),
                },
            ],
        },
    ]

def eblink_rig_type_items(self, context):
    items = []
    for eb_data in EYEBLINK_DATA:
        rt = eb_data.get("rig_type")
        if rt is None:
            continue
        label = eb_data.get("label")
        desc = eb_data.get("description")
        if label is None:
            label = rt
        if desc is None:
            desc = ""
        items.append((rt, label, desc))
    items.append( (EB_RIG_SELECT_BONES, "Selected Bones", "Use current location/rotation of currently selected pose " \
        "bones for 'closed' eye position, when generating eye blink track. 'Open' eye position is reset pose " \
        "location/rotation, i.e. zero location/rotation") )
    return sorted(items, key = lambda x: x[0])

def get_eyeblink_data_by_rig_type(eblink_rig_type):
    for d in EYEBLINK_DATA:
        if not isinstance(d, dict):
            continue
        if d.get("rig_type") == eblink_rig_type:
            return d.get("data")

def blink_bone_data_path_match(bone_path, bone_name_match_list):
    for b_name in bone_name_match_list:
        b_match_path = "pose.bones[\"" + b_name + "\"]"
        # check the first part of the bone_path for a match, up to the length of the "match path"
        if bone_path.startswith(b_match_path + '.location') or bone_path.startswith(b_match_path + '.rotation'):
            # match found so return True
            return True
    # zero matches found so return False
    return False

def remove_blink_kf_points(action, fc, start_frame, end_frame):
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

def remove_blink_track(arm_list, mesh_list, rig_type, shapekey_name, start_frame, end_frame):
    lidlook_bone_names = []
    if rig_type != EB_RIG_SELECT_BONES:
        ll_data = get_lidlook_data_by_rig_type(rig_type)
        if ll_data != None:
            for d in ll_data:
                bone_name = d.get("bone_name")
                if isinstance(bone_name, str):
                    lidlook_bone_names.append(bone_name)
    blink_bone_names_dict = {}
    if rig_type == EB_RIG_SELECT_BONES:
        for arm_ob in arm_list:
            blink_bone_names_dict[arm_ob.name] = [ bone.name for bone in arm_ob.pose.bones ]
    else:
        rig_eb_data = get_eyeblink_data_by_rig_type(rig_type)
        if rig_eb_data != None:
            blink_bone_names_dict[rig_type] = [ d.get("bone_name") for d in rig_eb_data ]
    for arm_ob in arm_list:
        fc_to_remove = []
        action = arm_ob.animation_data.action
        if action is None:
            continue
        for bone_name in lidlook_bone_names:
            # get list of LidLook f-curves to remove
            pose_bone = arm_ob.pose.bones.get(bone_name)
            if pose_bone is None:
                continue
            # search through constraints for 'influence' f-curve
            for const in pose_bone.constraints:
                if (const.type == 'COPY_ROTATION' and const.name.startswith(LL_COPY_ROT_CONST_NAME)) \
                    or (const.type == 'LIMIT_ROTATION' and const.name.startswith(LL_LIMIT_ROT_CONST_NAME)):
                    dp = const.path_from_id('influence')
                    fc = action.fcurves.find(dp)
                    if fc is not None:
                        fc_to_remove.append(fc)
        if rig_type == EB_RIG_SELECT_BONES:
            blink_bone_names = blink_bone_names_dict.get(arm_ob.name)
        else:
            blink_bone_names = blink_bone_names_dict.get(rig_type)
        if blink_bone_names != None:
            # get list of Eyeblink f-curves to remove
            for fc in action.fcurves:
                if blink_bone_data_path_match(fc.data_path, blink_bone_names):
                    fc_to_remove.append(fc)
            # remove collected f-curves
            for fc in fc_to_remove:
                # remove bone f-curve if no start/end frames given
                if start_frame is None and end_frame is None:
                    action.fcurves.remove(fc)
                    continue
                # otherwise remove keyframe points
                remove_blink_kf_points(action, fc, start_frame, end_frame)
    # check meshes for shapekey f-curve to remove
    for mesh_obj in mesh_list:
        if mesh_obj.data.shape_keys is None:
            continue
        sk = mesh_obj.data.shape_keys.key_blocks.get(shapekey_name)
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
            remove_blink_kf_points(action, fc, start_frame, end_frame)

# linear interpolation from y1 to y2, as x varies from 0 to 1
def d_lerp(y1, y2, x):
    if x < 0:
        return y1
    elif x > 1:
        return y2
    else:
        return (1 - x) * y1 + x * y2

def random_plus_minus_half(input_val):
    return random.uniform(input_val / -2, input_val / 2)

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
        if axis_index == None:
            fc = action.fcurves.find(data_path=dp)
        else:
            fc = action.fcurves.find(data_path=dp, index=axis_index)
    # if f-curve does not exist then insert a keyframe to initialize it
    skip_first = False
    if fc is None:
        # create the f-curve by inserting the first keyframe
        if axis_index == None:
            if not obj.keyframe_insert(data_path=dp, frame=kf_data[0][0]):
                return
        else:
            if not obj.keyframe_insert(data_path=dp, index=axis_index, frame=kf_data[0][0]):
                return
        # get the f-curve for the shapekey value
        action = obj.animation_data.action
        if axis_index == None:
            fc = action.fcurves.find(data_path=dp)
        else:
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

def generate_kf_data(eb_data):
    kf_data = []
    for d in eb_data:
        bone_name = d.get("bone_name")
        if bone_name is None:
            continue
        loc = d.get("location")
        if isinstance(loc, (list, tuple)) and len(loc) == 3:
            for i in range(3):
                kf_data.append( (bone_name, 'location', i, 0.0, loc[i]) )
        rot_mode = d.get("rotation_mode")
        if rot_mode == 'QUATERNION':
            rot_val = d.get("rotation_quaternion")
            if rot_val != None and isinstance(rot_val, (list, tuple, Quaternion)) and len(rot_val) == 4:
                kf_data.append( (bone_name, 'rotation_mode', None, 0.0, 0.0) )
                for i in range(4):
                    if i == 0:
                        kf_data.append( (bone_name, 'rotation_quaternion', i, 1.0, rot_val[i]) )
                    else:
                        kf_data.append( (bone_name, 'rotation_quaternion', i, 0.0, rot_val[i]) )
        elif rot_mode == 'AXIS_ANGLE':
            rot_val = d.get("rotation_axis_angle")
            if rot_val != None and isinstance(rot_val, (list, tuple, bpy.types.bpy_prop_array)) and len(rot_val) == 4:
                kf_data.append( (bone_name, 'rotation_mode', None, -1.0, -1.0) )
                for i in range(4):
                    if i == 2:
                        kf_data.append( (bone_name, 'rotation_axis_angle', i, 1.0, rot_val[i]) )
                    else:
                        kf_data.append( (bone_name, 'rotation_axis_angle', i, 0.0, rot_val[i]) )
        elif rot_mode in EULER_ROT_MODES:
            rot_val = d.get("rotation_euler")
            if isinstance(rot_val, (list, tuple, Euler)) and len(rot_val) == 3:
                try:
                    rm = EULER_ROT_MODES.index(rot_mode) + 1
                except:
                    rm = 1
                kf_data.append( (bone_name, 'rotation_mode', None, rm, rm) )
                # TODO check if X, Y, Z need re-arranging when rot_mode != 'XYZ'
                for i in range(3):
                    kf_data.append( (bone_name, 'rotation_euler', i, 0.0, rot_val[i]) )
    return kf_data

# return dictionary with entries that are lists of tuples:
#   (bone_name, data_type, axis_index, opened_value, closed_value)
def get_eyeblink_kf_data_by_select_bones(arm_list):
    items = {}
    for arm_ob in arm_list:
        kf_data = []
        for pose_bone in arm_ob.pose.bones:
            if not pose_bone.bone.select:
                continue
            for i in range(3):
                kf_data.append( (pose_bone.name, 'location', i, 0.0, pose_bone.location[i]) )
            if pose_bone.rotation_mode == 'QUATERNION':
                # new_d["rotation_quaternion"] = pose_bone.rotation_quaternion
                kf_data.append( (pose_bone.name, 'rotation_mode', None, 0.0, 0.0) )
                for i in range(4):
                    if i == 0:
                        kf_data.append(
                            (pose_bone.name, 'rotation_quaternion', i, 1.0, pose_bone.rotation_quaternion[i]) )
                    else:
                        kf_data.append(
                            (pose_bone.name, 'rotation_quaternion', i, 0.0, pose_bone.rotation_quaternion[i]) )
            elif pose_bone.rotation_mode == 'AXIS_ANGLE':
                kf_data.append( (pose_bone.name, 'rotation_mode', None, -1.0, -1.0) )
                for i in range(4):
                    if i == 2:
                        kf_data.append(
                            (pose_bone.name, 'rotation_axis_angle', i, 1.0, pose_bone.rotation_axis_angle[i]) )
                    else:
                        kf_data.append(
                            (pose_bone.name, 'rotation_axis_angle', i, 0.0, pose_bone.rotation_axis_angle[i]) )
            elif pose_bone.rotation_mode in EULER_ROT_MODES:
                try:
                    rm = EULER_ROT_MODES.index(pose_bone.rotation_mode) + 1
                except:
                    rm = 1
                kf_data.append( (pose_bone.name, 'rotation_mode', None, rm, rm) )
                # TODO check if X, Y, Z need re-arranging when rot_mode != 'XYZ'
                for i in range(3):
                    kf_data.append( (pose_bone.name, 'rotation_euler', i, 0.0, pose_bone.rotation_euler[i]) )
        items[arm_ob.name] = kf_data
    return items

def generate_blink_track(arm_list, mesh_list, rig_type, blink_settings):
    if rig_type == EB_RIG_SELECT_BONES:
        eblink_kf_data_dict = get_eyeblink_kf_data_by_select_bones(arm_list)
    else:
        rig_eb_data = get_eyeblink_data_by_rig_type(rig_type)
        if rig_eb_data is None:
            return
        kd = generate_kf_data(rig_eb_data)
        if kd is None:
            return
        eblink_kf_data_dict = { rig_type: kd }
    ll_data = get_lidlook_data_by_rig_type(rig_type)
    lidlook_bone_names = []
    if ll_data != None:
        for d in ll_data:
            bone_name = d.get("bone_name")
            if isinstance(bone_name, str):
                lidlook_bone_names.append(bone_name)
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
        # insert bone keyframes into armature(s)
        for arm_ob in arm_list:
            if rig_type == EB_RIG_SELECT_BONES:
                kf_data_list = eblink_kf_data_dict[arm_ob.name]
            else:
                kf_data_list = eblink_kf_data_dict[rig_type]
            # generate keyframes for each used data type (i.e. location, rotation) and axis
            for bone_name, data_type, axis_index, opened_value, closed_value in kf_data_list:
                # get keyframe data for the blink
                single_blink_data = generate_blink(blink_settings["frame_rate"], cur_start_frame, closing_time,
                                                   closed_time, opening_time, opened_value, closed_value)
                # insert bone keyframes
                bone_insert_keyframes(arm_ob, bone_name, data_type, axis_index, single_blink_data)
            # generate keyframes for every LidLook 'Copy Rotation' / 'Limit Rotation' bone constraint
            for bone_name in lidlook_bone_names:
                bone = arm_ob.pose.bones.get(bone_name)
                for b_constraint in bone.constraints:
                    if b_constraint.type != 'LIMIT_ROTATION' and b_constraint.type != 'COPY_ROTATION':
                        continue
                    if not b_constraint.name.startswith(LL_COPY_ROT_CONST_NAME) \
                        and not b_constraint.name.startswith(LL_LIMIT_ROT_CONST_NAME):
                        continue
                    dp = b_constraint.path_from_id() + ".influence"
                    # get keyframe data for the 'bone constraint' blink
                    kf_data = generate_blink(blink_settings["frame_rate"], cur_start_frame, closing_time,
                                             closed_time, opening_time, b_constraint.influence, 0)
                    bone_constraint_insert_keyframes(arm_ob, dp, kf_data)
        # insert shapekey keyframes into mesh(es), if needed
        if blink_settings["shapekey_name"] != "":
            for mesh_obj in mesh_list:
                # get keyframe data for the shapekey blink
                kf_data = generate_blink(blink_settings["frame_rate"], cur_start_frame, closing_time, closed_time,
                                         opening_time, 0, 1)
                shapekey_insert_keyframes(mesh_obj, blink_settings["shapekey_name"], kf_data)
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
