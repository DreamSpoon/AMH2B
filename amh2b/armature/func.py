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

import fnmatch
import math
import os

import bpy
from mathutils import Quaternion

from ..bl_util import (ast_literal_eval_textblock, get_file_eval_dict, do_tag_redraw, get_thing_to_keyframe)
from ..const import ADDON_BASE_FILE
from ..lex_py_attributes import lex_py_attributes
from ..object_func import (get_scene_user_collection, is_object_in_sub_collection)

ARM_FUNC_RETARGET = "ARM_FUNC_RETARGET"
ARM_FUNC_APPLY_ACTION_FRAME = "ARM_FUNC_APPLY_ACTION_FRAME"
ARM_FUNC_UTILITY = "ARM_FUNC_UTILITY"
ARM_FUNC_SELECT_ACTION_BONES = "ARM_FUNC_SELECT_ACTION_BONES"
ARM_FUNC_ITEMS = [
    (ARM_FUNC_APPLY_ACTION_FRAME, "Apply Action Frame", "Apply single frame of an Action to Pose of active Armature"),
    (ARM_FUNC_RETARGET, "Retarget", "Retarget animations from Mixamo armatures to other armatures"),
    (ARM_FUNC_SELECT_ACTION_BONES, "Select Action Bones", "Select bones that are used by an action"),
    (ARM_FUNC_UTILITY, "Utility", ""),
]
ARM_SELECT_ACTION_CURRENT = "ARM_SELECT_ACTION_CURRENT"
ARM_SELECT_ACTION_CHOOSE = "ARM_SELECT_ACTION_CHOOSE"
ARM_SELECT_ACTION_ITEMS = [
    (ARM_SELECT_ACTION_CURRENT, "Current", "Use current Action of object"),
    (ARM_SELECT_ACTION_CHOOSE, "Choose", "Choose one Action"),
]
ARM_SELECT_FRAME_RANGE_ALL = "ARM_SELECT_FRAME_RANGE_ALL"
ARM_SELECT_FRAME_RANGE_CURRENT = "ARM_SELECT_FRAME_RANGE_CURRENT"
ARM_SELECT_FRAME_RANGE_MIN_MAX = "ARM_SELECT_FRAME_RANGE_MIN_MAX"
ARM_SELECT_FRAME_RANGE_SINGLE = "ARM_SELECT_FRAME_RANGE_SINGLE"
ARM_SELECT_FRAME_RANGE_TYPE_ITEMS = [
    (ARM_SELECT_FRAME_RANGE_ALL, "All", "Select bones with keyframes in any frame of animation"),
    (ARM_SELECT_FRAME_RANGE_CURRENT, "Current", "Select bones with keyframes in the current frame of animation"),
    (ARM_SELECT_FRAME_RANGE_MIN_MAX, "Range",
     "Select bones with keyrames between a minimum and maximum frame of animation"),
    (ARM_SELECT_FRAME_RANGE_SINGLE, "Single", "Select bones with keyrames in a single frame"),
]

script_pose_presets = {}
retarget_armature_presets = {}

RETARGET_CONSTRAINT_NAME_PREFIX = "AMH2B Retarget "

playback_dict = { "return_frame": None, "start_frame": None, "end_frame": None }

GLOBAL_POSE_PROP_DEFAULTS = {
    'location': (0.0, 0.0, 0.0),
    'rotation_mode': 0,
    'rotation_axis_angle': (0.0, 0.0, 1.0, 0.0),
    'rotation_euler': (0.0, 0.0, 0.0),
    'rotation_quaternion': (1.0, 0.0, 0.0, 0.0),
    'scale': (1.0, 1.0, 1.0),
    'influence': 1.0,
    }
GLOBAL_POSE_PROP_NAMES = [ x for x in GLOBAL_POSE_PROP_DEFAULTS.keys() ]

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

# check all values for matches with types, where values and types can be individuals, or arrays / tuples
def is_types(values, types):
    # try to get 'length' of 'values and types, in case of array / tuple
    values_len = None
    types_len = None
    if isinstance(values, (list, tuple)):
        values_len = len(values)
    if isinstance(types, (list, tuple)):
        types_len = len(types)
    # if number of items in arrays / tuples is not the same then return False because mismatch, while allowing for
    # types to have extra nested arrays / tuples so a single value can be checked against multiple types
    if values_len != None and values_len != types_len:
        return False
    # if not array/tuple then check for match
    if values_len is None:
        return isinstance(values, types)
    # else recursively check each item in array/tuple
    else:
        for i in range(len(values)):
            # if recursive check is False then return False because mismatch
            if not is_types(values[i], types[i]):
                return False
    # all given values matched given types
    return True

def get_textblock_eval_dict(textblock_name):
    text = bpy.data.texts.get(textblock_name)
    if text is None:
        return None
    text_eval = ast_literal_eval_textblock(text)
    if text_eval.get("error") != None:
        return text_eval.get("error")
    script = text_eval.get("result")
    if not isinstance(script, dict):
        return "Error: Script did not evaluate to type 'dict' (dictionary)"
    return script

def script_pose_preset_items(self, context):
    items = []
    for filename, pose_script in script_pose_presets.items():
        label = pose_script.get("label")
        if label is None:
            label = filename
        desc = pose_script.get("description")
        if desc is None:
            desc = ""
        items.append ( (filename, str(label), str(desc)) )
    return sorted(items, key = lambda x: x[0]) if len(items) > 0 else [ (" ", "", "") ]

def load_script_pose_presets():
    # do not re-load
    if len(script_pose_presets) > 0:
        return
    # get paths to presets files
    base_path = os.path.dirname(os.path.realpath(ADDON_BASE_FILE))
    preset_path = os.path.join(base_path, "presets", "script_pose")
    try:
        file_paths = [ f for f in os.listdir(preset_path) if os.path.isfile(os.path.join(preset_path, f)) ]
    except:
        return
    # safely read each file and get pose script, trying ALL FILES in the presets path
    for fp in file_paths:
        try:
            with open(os.path.join(preset_path, fp), 'r') as f:
                pose_script = get_file_eval_dict(f)
        except:
            continue
        if not isinstance(pose_script, dict):
            continue
        script_pose_presets[fp] = pose_script

def global_rotate_bone(arm_ob, bone_name, axis_name, offset_deg):
    if bone_name is None:
        return
    the_bone = arm_ob.pose.bones.get(bone_name)
    if the_bone is None:
        return
    the_bone.bone.select = True
    if axis_name.lower() == "x":
        bpy.ops.transform.rotate(value=(math.pi * offset_deg / 180), orient_axis='X', orient_type='GLOBAL',
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                 constraint_axis=(True, False, False))
    elif axis_name.lower() == "y":
        bpy.ops.transform.rotate(value=(math.pi * offset_deg / 180), orient_axis='Y', orient_type='GLOBAL',
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                 constraint_axis=(False, True, False))
    elif axis_name.lower() == "z":
        bpy.ops.transform.rotate(value=(math.pi * offset_deg / 180), orient_axis='Z', orient_type='GLOBAL',
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                 constraint_axis=(False, False, True))
    the_bone.bone.select = False

def op_global_rotate_bone(arm_ob, op_data, in_reverse):
    if not isinstance(op_data, (list, tuple)):
        return
    all_bone_names = [ bone.name for bone in arm_ob.data.bones ]
    bone_name_trans = {}
    if in_reverse:
        op_data = reversed(op_data)
    for pose_data in op_data:
        if not is_types(pose_data, (str, str, (float, int)) ):
            continue
        trans_name = bone_name_translation(bone_name_trans, all_bone_names, pose_data[0])
        rot_value = -float(pose_data[2]) if in_reverse else float(pose_data[2])
        global_rotate_bone(arm_ob, trans_name, pose_data[1], rot_value)

def apply_run_pose_script(pose_ob, pose_script, in_reverse):
    pose_data = pose_script.get("data")
    try:
        if len(pose_data) < 1:
            return
    except:
        return
    operation_functions = {
        "global_rotate_bone": op_global_rotate_bone,
        }
    for item in pose_data:
        if not isinstance(item, dict):
            continue
        op_func = operation_functions.get(item.get("op"))
        if op_func is None:
            continue
        op_func(pose_ob, item.get("data"), in_reverse)

def script_pose(context, arm_ob, preset_name, use_textblock, textblock_name, in_reverse):
    old_3dview_mode = context.object.mode
    # deselect all bones and run script to (select, pose, unselect) each bone individually
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='DESELECT')
    if use_textblock:
        pose_script = get_textblock_eval_dict(textblock_name)
    else:
        pose_script = script_pose_presets.get(preset_name)
    if pose_script != None:
        apply_run_pose_script(arm_ob, pose_script, in_reverse)
    bpy.ops.object.mode_set(mode=old_3dview_mode)

#####################################################
#     Apply Scale
# Apply scale to armature (this is only needed for armature scale apply),
# and adjust it"s bone location animation f-curve values to match the scaling.
# If this operation is not done, then the bones that have changing location values
# will appear to move incorrectly.
def armature_apply_scale(context, ob, apply_location=False, apply_rotation=False, apply_scale=False):
    # save state
    old_act_ob = context.active_object
    old_3dview_mode = context.object.mode
    # set active object to Object that needs scale applied
    context.view_layer.objects.active = ob
    # keep copy of old scale values
    old_scale = ob.scale.copy()
    bpy.ops.object.mode_set(mode='OBJECT')
    # do not apply scale if scale is already 1.0 in all dimensions!
    if old_scale.x == 1 and old_scale.y == 1 and old_scale.z == 1:
        # apply other transforms to active object
        if apply_location or apply_rotation:
            bpy.ops.object.transform_apply(location=apply_location, rotation=apply_rotation, scale=False)
        return
    # apply scale to active object
    bpy.ops.object.transform_apply(location=apply_location, rotation=apply_rotation, scale=apply_scale)
    # if no f-curves then no exit, because only needed 'apply scale'
    action = ob.animation_data.action
    if action is None:
        return
    if action.fcurves is None:
        return
    # get only location f-curves
    fcurves = [fc for fc in action.fcurves if fc.data_path.endswith("location")]
    # scale only location f-curves
    for fc in fcurves:
        axis = fc.array_index
        for p in fc.keyframe_points:
            if axis == 0:
                p.co.y *= old_scale.x
            elif axis == 1:
                p.co.y *= old_scale.y
            elif axis == 2:
                p.co.y *= old_scale.z
    # update the scene by incrementing the frame, then decrementing it again,
    # because the apply scale will probably move the posed bones to a wrong location
    context.scene.frame_set(context.scene.frame_current+1)
    context.scene.frame_set(context.scene.frame_current-1)
    # restore state
    context.view_layer.objects.active = old_act_ob
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def toggle_preserve_volume(context, new_state, sel_ob_list):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    for ob in sel_ob_list:
        if ob.type != 'MESH':
            continue
        for mod in ob.modifiers:
            if mod.type == 'ARMATURE':
                mod.use_deform_preserve_volume = new_state
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def get_generic_bone_name(bone_name, generic_prefix):
    if bone_name.rfind(":") != -1:
        return generic_prefix + bone_name[ bone_name.rfind(":") : len(bone_name) ]
    else:
        return generic_prefix + ":" + bone_name

def rename_bone_generic(context, new_generic_prefix, sel_ob_list):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    for ob in sel_ob_list:
        if ob.type != 'ARMATURE':
            continue
        for ebone in ob.data.edit_bones.data.bones:
            ebone.name = get_generic_bone_name(ebone.name, new_generic_prefix)
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def get_non_generic_bone_name(bone_name):
    if bone_name.rfind(":") != -1:
        return bone_name[ bone_name.rfind(":")+1 : len(bone_name) ]
    else:
        return bone_name

def unname_bone_generic(context, sel_ob_list):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    for ob in sel_ob_list:
        if ob.type != 'ARMATURE':
            continue
        for ebone in ob.data.edit_bones.data.bones:
            old_name = ebone.name
            new_name = get_non_generic_bone_name(old_name)
            # change name of bone, if needed
            if new_name != old_name:
                ebone.name = new_name
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def cleanup_gizmos(context):
    # iterate over all Armature type Objects,
    # iterate over bones in each Armature, searching for 'bone shape' Objects,
    # verifying each 'bone shape' Object is in a Collection under Armature's Collection,
    # and adding 'hidden' Collections as needed and moving gizmos to 'hidden' Collections as needed
    for arm_ob in bpy.data.objects:
        if arm_ob.type != 'ARMATURE':
            continue
        arm_coll = get_scene_user_collection(context.scene, arm_ob.users_collection)
        if arm_coll is None:
            continue
        for pose_bone in arm_ob.pose.bones:
            cs_ob = pose_bone.custom_shape
            if cs_ob is None:
                continue
            cs_coll = get_scene_user_collection(context.scene, cs_ob.users_collection)
            if cs_coll is None or is_object_in_sub_collection(cs_ob, arm_coll):
                continue
            hidden_coll = arm_coll.children.get("Hidden")
            if hidden_coll is None:
                hidden_coll = bpy.data.collections.new(name="Hidden")
                hidden_coll.hide_viewport = True
                hidden_coll.hide_render = True
                arm_coll.children.link(hidden_coll)
            cs_coll.objects.unlink(cs_ob)
            hidden_coll.objects.link(cs_ob)

def retarget_armature_preset_items(self, context):
    items = []
    for filename, retarget_script in retarget_armature_presets.items():
        label = retarget_script.get("label")
        if label is None:
            label = filename
        desc = retarget_script.get("description")
        if desc is None:
            desc = ""
        items.append ( (filename, str(label), str(desc)) )
    return sorted(items, key = lambda x: x[0]) if len(items) > 0 else [ (" ", "", "") ]

def load_retarget_armature_presets():
    # do not re-load
    if len(retarget_armature_presets) > 0:
        return
    # get paths to presets files
    base_path = os.path.dirname(os.path.realpath(ADDON_BASE_FILE))
    p = os.path.join(base_path, "presets", "retarget_armature")
    try:
        file_paths = [ f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f)) ]
    except:
        return
    # safely read each file and get retarget armature script
    for fp in file_paths:
        try:
            with open(os.path.join(p, fp), 'r') as f:
                retarget_script = get_file_eval_dict(f)
        except:
            retarget_script = "Error: cannot open Retarget Armature preset file named: " + fp
        if not isinstance(retarget_script, dict):
            continue
        retarget_armature_presets[fp] = retarget_script

# allow for filename match filtering (use of '*' operator) with case-sensitive bone name lookups,
# uses first bone name found in case of multiple matches,
# previously found translations are stored in bone_name_trans and reused for efficiency
def bone_name_translation(bone_name_trans, all_bone_names, bone_name):
    trans_name = bone_name_trans.get(bone_name)
    if trans_name != None:
        return trans_name
    found_names = fnmatch.filter(all_bone_names, bone_name)
    if found_names is not None:
        # case sensitive filter
        found_names = [ name for name in found_names if fnmatch.fnmatchcase(name, bone_name) ]
        if len(found_names) > 0:
            # use first bone name found
            bone_name_trans[bone_name] = found_names[0]
            return found_names[0]
    return None

def get_translation_vec(bone_from, bone_to, from_dist, to_dist):
    delta_x_from = bone_from.tail.x - bone_from.head.x
    delta_y_from = bone_from.tail.y - bone_from.head.y
    delta_z_from = bone_from.tail.z - bone_from.head.z
    delta_x_to = bone_to.tail.x - bone_to.head.x
    delta_y_to = bone_to.tail.y - bone_to.head.y
    delta_z_to = bone_to.tail.z - bone_to.head.z
    # to
    t_x = bone_to.head.x + delta_x_to * to_dist - bone_from.head.x
    t_y = bone_to.head.y + delta_y_to * to_dist - bone_from.head.y
    t_z = bone_to.head.z + delta_z_to * to_dist - bone_from.head.z
    # from
    t_x = t_x - delta_x_from * from_dist
    t_y = t_y - delta_y_from * from_dist
    t_z = t_z - delta_z_from * from_dist
    # translation vector
    return (t_x, t_y, t_z)

def op_create_transfer_armature(context, op_data, script_state):
    if script_state["transfer_armature_ob"] != None:
        return
    if context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    loc = context.active_object.location
    bpy.ops.object.armature_add(enter_editmode=False, align='WORLD',  location=loc, scale=(1, 1, 1))
    script_state["transfer_armature_ob"] = context.active_object
    script_state["transfer_armature_ob"].name = "TransferRig"
    xfer_arm = context.active_object.data
    xfer_arm.name = "TransferArmature"
    # remove all bones, to start with empty armature
    bpy.ops.object.mode_set(mode='EDIT')
    for b in xfer_arm.edit_bones:
        xfer_arm.edit_bones.remove(b)

def op_transfer_constraint(context, op_data, script_state, constraint_type):
    if script_state["transfer_armature_ob"] is None:
        return
    if not isinstance(op_data, (list, tuple)):
        return
    if constraint_type not in ( 'COPY_TRANSFORMS', 'COPY_ROTATION' ):
        return
    source_arm = script_state["source_object"].data
    dest_arm = script_state["dest_object"].data
    all_src_bone_names = [ bone.name for bone in source_arm.bones ]
    all_dest_bone_names = [ bone.name for bone in dest_arm.bones ]
    src_name_trans = {}
    dest_name_trans = {}
    if script_state["transfer_armature_ob"] is None:
        return
    xfer_arm = script_state["transfer_armature_ob"].data
    constraint_inputs = []
    if context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    # ensure these armatures are selected in order to get their edit_bone.roll values later
    script_state["source_object"].select_set(True)
    script_state["dest_object"].select_set(True)
    if bpy.app.version >= (4, 0, 0):
        if "Src Bones" not in xfer_arm.collections:
            xfer_arm.collections.new("Src Bones")
        if "Dest Bones" not in xfer_arm.collections:
            xfer_arm.collections.new("Dest Bones")
    bpy.ops.object.mode_set(mode='EDIT')
    for d in op_data:
        if not isinstance(d, tuple):
            continue
        if constraint_type == 'COPY_TRANSFORMS':
            if len(d) != 5 or not isinstance(d[0], str) or not isinstance(d[1], str) \
                or not isinstance(d[2], (float, int)) or not isinstance(d[3], (float, int)) \
                or not isinstance(d[4], (float, int)):
                continue
        elif constraint_type == 'COPY_ROTATION':
            if len(d) != 2 or not isinstance(d[0], str) or not isinstance(d[1], str):
                continue
        source_bone_name = bone_name_translation(src_name_trans, all_src_bone_names, d[0])
        dest_bone_name = bone_name_translation(dest_name_trans, all_dest_bone_names, d[1])
        if source_bone_name is None or dest_bone_name is None:
            continue
        source_bone = source_arm.bones.get(source_bone_name)
        dest_bone = dest_arm.bones.get(dest_bone_name)
        if source_bone is None or dest_bone is None:
            continue
        # create bones in Transfer Armature, copying from Source and Destination Armatures, only if bones don't
        # already exist
        xfer_source_bone = xfer_arm.edit_bones.get(source_bone_name)
        if xfer_source_bone is None:
            xfer_source_bone = xfer_arm.edit_bones.new(source_bone_name)
        # prevent doubling of 'destination' bones in Transfer armature, only create bone if it doesn't already exist
        xfer_dest_bone = xfer_arm.edit_bones.get(dest_bone_name)
        if xfer_dest_bone is None:
            xfer_dest_bone = xfer_arm.edit_bones.new(dest_bone_name)
        dest_bone_name = xfer_dest_bone.name
        # copy source bone exactly to Transfer Armature
        xfer_source_bone.head.x = source_arm.edit_bones[source_bone_name].head.x
        xfer_source_bone.head.y = source_arm.edit_bones[source_bone_name].head.y
        xfer_source_bone.head.z = source_arm.edit_bones[source_bone_name].head.z
        xfer_source_bone.tail.x = source_arm.edit_bones[source_bone_name].tail.x
        xfer_source_bone.tail.y = source_arm.edit_bones[source_bone_name].tail.y
        xfer_source_bone.tail.z = source_arm.edit_bones[source_bone_name].tail.z
        xfer_source_bone.roll = source_arm.edit_bones[source_bone_name].roll

        t_vec = (0, 0, 0)
        fac = 0
        if constraint_type == 'COPY_TRANSFORMS':
            # get 3d translation vector as a point coincident with both bones, along a factor of each bone's length
            t_vec = get_translation_vec(source_bone, dest_bone, d[2], d[3])
            # copy destination bone head and tail locations, with offset by distance factor along original bones' length,
            # to Transfer Armature - with a factor from 0.0 to 1.0 applied, where 0 is 100% translate new destination bone
            # to source bone position, and 1 is keep destination bone at its original location
            fac = d[4] if d[4] < 1.0 else 1.0
            fac = fac if fac > 0.0 else 0.0
            fac = 1.0 - fac
        xfer_dest_bone.head.x = dest_arm.edit_bones[dest_bone_name].head.x - t_vec[0] * fac
        xfer_dest_bone.head.y = dest_arm.edit_bones[dest_bone_name].head.y - t_vec[1] * fac
        xfer_dest_bone.head.z = dest_arm.edit_bones[dest_bone_name].head.z - t_vec[2] * fac
        xfer_dest_bone.tail.x = dest_arm.edit_bones[dest_bone_name].tail.x - t_vec[0] * fac
        xfer_dest_bone.tail.y = dest_arm.edit_bones[dest_bone_name].tail.y - t_vec[1] * fac
        xfer_dest_bone.tail.z = dest_arm.edit_bones[dest_bone_name].tail.z - t_vec[2] * fac
        xfer_dest_bone.roll = dest_arm.edit_bones[dest_bone_name].roll
        # parent new destination bone to new source bone
        xfer_dest_bone.parent = xfer_source_bone
        # keep references to bones so bone constraints can be added later
        constraint_inputs.append( (source_bone_name, dest_bone_name, xfer_source_bone.name, xfer_dest_bone.name) )

        if bpy.app.version >= (4, 0 , 0):
            # put new bones in their own layer collections
            xfer_arm.collections["Src Bones"].assign(xfer_source_bone)
            xfer_arm.collections["Dest Bones"].assign(xfer_dest_bone)
        else:
            # put new bones in first and second layers
            for i in range(32):
                xfer_source_bone.layers[i] = i == 0
                xfer_dest_bone.layers[i] = i == 1

    # add constraints in Pose mode
    bpy.ops.object.mode_set(mode='POSE')
    xfer_pose_bones = script_state["transfer_armature_ob"].pose.bones
    dest_pose_bones = script_state["dest_object"].pose.bones
    src_pose_bones = script_state["source_object"].pose.bones
    for s_bone_name, d_bone_name, x_source_bone_name, x_dest_bone_name in constraint_inputs:
        # Copy Transforms constraint from: s_bone_name, to: x_source_bone_name
        xfer_ctc = xfer_pose_bones[x_source_bone_name].constraints.new('COPY_TRANSFORMS')
        xfer_ctc.name = RETARGET_CONSTRAINT_NAME_PREFIX + "Copy Transforms"
        # if source pose bone has a Copy Transforms bone constraint, then copy its data
        constraints = [ c for c in src_pose_bones[s_bone_name].constraints if c.type == 'COPY_TRANSFORMS' ]
        if len(constraints) > 0:
            # copy targets of first Copy Transforms constraint found
            xfer_ctc.target = constraints[0].target
            xfer_ctc.subtarget = constraints[0].subtarget
        # otherwise link bone constraint to source bone
        else:
            xfer_ctc.target = script_state["source_object"]
            xfer_ctc.subtarget = s_bone_name
        xfer_ctc.target_space = 'WORLD'
        xfer_ctc.owner_space = 'WORLD'
        xfer_ctc.mix_mode = 'REPLACE'
        # Copy X constraint from: x_dest_bone_name, to: d_bone_name
        dest_ctc = dest_pose_bones[d_bone_name].constraints.new(constraint_type)
        dest_ctc.name = RETARGET_CONSTRAINT_NAME_PREFIX + constraint_type
        dest_ctc.target = script_state["transfer_armature_ob"]
        dest_ctc.subtarget = x_dest_bone_name
        dest_ctc.target_space = 'WORLD'
        dest_ctc.owner_space = 'WORLD'
        dest_ctc.mix_mode = 'REPLACE'

        # copy pose bone Custom Shape data to Transfer armature pose bones
        dub_list = [ (src_pose_bones[s_bone_name], xfer_pose_bones[x_source_bone_name]),
                    (dest_pose_bones[d_bone_name], xfer_pose_bones[x_dest_bone_name]) ]
        for from_pb, to_pb in dub_list:
            to_pb.custom_shape = from_pb.custom_shape
            to_pb.custom_shape_scale_xyz = from_pb.custom_shape_scale_xyz
            to_pb.custom_shape_translation = from_pb.custom_shape_translation
            to_pb.custom_shape_transform = from_pb.custom_shape_transform
            to_pb.use_custom_shape_bone_size = from_pb.use_custom_shape_bone_size

def op_transfer_transforms(context, op_data, script_state):
    op_transfer_constraint(context, op_data, script_state, 'COPY_TRANSFORMS')

def op_transfer_rotation(context, op_data, script_state):
    op_transfer_constraint(context, op_data, script_state, 'COPY_ROTATION')

def apply_retarget_armature_script(context, source_ob, dest_ob, retarget_script):
    retarget_data = retarget_script.get("data")
    try:
        if len(retarget_data) < 1:
            return
    except:
        return
    operation_functions = {
        "create_transfer_armature": op_create_transfer_armature,
        "transfer_transforms": op_transfer_transforms,
        "transfer_rotation": op_transfer_rotation,
        }
    script_state = {
        "source_object": source_ob,
        "dest_object": dest_ob,
        "transfer_armature_ob": None,
        }
    for item in retarget_data:
        if not isinstance(item, dict):
            continue
        op_func = operation_functions.get(item.get("op"))
        if op_func is None:
            continue
        op_func(context, item.get("data"), script_state)
    if context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

# Retarget via Transfer Armature:
# Create a Transfer Armature, with bones copied from source and destination rigs, bones parented together only
# in the Transfer Armature. Bones in Transfer Armature will be given bone constraints to copy location/rotation
# from Mixamo armature. Then, bones in MPFB2 armature will be given constraints to copy locaiton/rotation from
# Transfer Armature.
def retarget_armature(context, src_arm_ob, targ_arm_ob, preset_name, use_textblock, textblock_name):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    if use_textblock:
        retarget_script = get_textblock_eval_dict(textblock_name)
    else:
        retarget_script = retarget_armature_presets.get(preset_name)
    if retarget_script is None:
        ret_val = False
    else:
        ret_val = apply_retarget_armature_script(context, src_arm_ob, targ_arm_ob, retarget_script)
    bpy.ops.object.mode_set(mode=old_3dview_mode)
    return ret_val

def is_mhx2_armature(ob):
    return ob != None and hasattr(ob, "MhxRig") and ob.MhxRig in ('MHX', 'EXPORTED_MHX')

def remove_retarget_constraints(context, ob, include_target_none):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='POSE')
    bone_count = 0
    const_count = 0
    for pose_bone in ob.pose.bones:
        remove_c_list = []
        for const in pose_bone.constraints:
            if hasattr(const, "target") and const.target != ob:
                if const.target is None and not include_target_none:
                    continue
                remove_c_list.append(const)
        for const in remove_c_list:
            pose_bone.constraints.remove(const)
            const_count += 1
        if len(remove_c_list) > 0:
            bone_count += 1
    bpy.ops.object.mode_set(mode=old_3dview_mode)
    return bone_count, const_count

def is_hips_ik_bone_name(bone_name, all_bone_names, include_game_engine):
    bn = bone_name.lower()
    # Rigify
    if "root" in all_bone_names and "torso" in all_bone_names:
        return bn == "torso"
    if "_ik." in bn and not bn.startswith("thigh_"):
        return True
    if "tweak" in bn:
        return True
    # MHX import
    if "master" in all_bone_names and "root" in all_bone_names and "hips" in all_bone_names:
        return bn == "root"
    # Game engine
    if include_game_engine and bn in ("clavicle_l", "clavicle_r", "neck_01"):
        return True
    # everything else
    return bn.endswith( ("_ik", ".ik") ) or bn in ("hips", "pelvis", "root") or bn.endswith("hips") or ".ik." in bn

def snap_transfer_target_constraints(context, target_ob, transfer_ob, limit_ct_hips_ik, include_game_engine,
                                     only_selected):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='POSE')
    target_bone_names = [ b.name for b in target_ob.data.bones ]
    transfer_bone_names = [ b.name for b in transfer_ob.data.bones ]
    bone_count = 0
    for xfer_bone in transfer_ob.pose.bones:
        if only_selected and not transfer_ob.data.bones[xfer_bone.name].select:
            continue
        if xfer_bone.name not in target_bone_names:
            continue
        if limit_ct_hips_ik and not is_hips_ik_bone_name(xfer_bone.name, transfer_bone_names, include_game_engine):
            c_type = 'COPY_ROTATION'
            c_name_str = "Copy Rotation"
        else:
            c_type = 'COPY_TRANSFORMS'
            c_name_str = "Copy Transforms"
        ct_const = xfer_bone.constraints.new(type=c_type)
        ct_const.name = RETARGET_CONSTRAINT_NAME_PREFIX + c_name_str
        ct_const.target = target_ob
        ct_const.subtarget = xfer_bone.name
        ct_const.mix_mode = 'REPLACE'
        ct_const.target_space = 'WORLD'
        ct_const.owner_space = 'WORLD'
        bone_count += 1
    if context.object.mode != old_3dview_mode:
        bpy.ops.object.mode_set(mode=old_3dview_mode)
    return bone_count

def select_retarget_bones(ob):
    bone_count = 0
    for pose_bone in ob.pose.bones:
        did_sel = False
        for const in pose_bone.constraints:
            if hasattr(const, "target") and const.target != None and const.target != ob:
                did_sel = True
                ob.data.bones[pose_bone.name].select = True
        if did_sel:
            bone_count += 1
    return bone_count

def select_fcurve_bones(ob, action, frame_range_min, frame_range_max):
    select_bone_names = {}
    for fc in action.fcurves:
        fc_tokens, _ = lex_py_attributes(fc.data_path)
        if len(fc_tokens) < 4:
            continue
        bone_name = fc.data_path[ fc_tokens[2][0]+2 : fc_tokens[2][1]-2 ]
        if bone_name not in ob.data.bones or select_bone_names.get(bone_name) == True:
            continue
        if frame_range_min == None and frame_range_max == None:
            select_bone_names[bone_name] = True
            ob.data.bones[bone_name].select = True
            continue
        for p in fc.keyframe_points:
            if frame_range_min != None and p.co[0] < frame_range_min:
                continue
            if frame_range_max != None and p.co[0] > frame_range_max:
                continue
            select_bone_names[bone_name] = True
            ob.data.bones[bone_name].select = True
            break
    return len(select_bone_names)

def is_bone_action(action):
    if not isinstance(action, bpy.types.Action):
        return False
    for fc in action.fcurves:
        if fc.data_path.startswith("pose.bones"):
            return True
    return False

def get_scaled_quaternion_from_indexed_values(indexed_values, rot_scale):
    build_quat = { 0: 1.0, 1: 0.0, 2: 0.0, 3: 0.0 }
    for i, v in indexed_values.items():
        build_quat[i] = v
    build_quat = Quaternion( (build_quat[0], build_quat[1], build_quat[2], build_quat[3]) )
    scaled_quat_exp_map = build_quat.to_exponential_map() * rot_scale
    return Quaternion(scaled_quat_exp_map)

def getBoneSideAndBaseName(bone_name):
    lb_name = bone_name.lower()
    # check for number extension and remove from name before doing left/right check
    number_ext = ""
    for c in reversed(lb_name):
        if c in [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ]:
            number_ext = c + number_ext
        elif c in [ ".", "-", "_" ]:
            number_ext = c + number_ext
            break
        else:
            break
    ext_len = len(number_ext)
    if ext_len > 0:
        lb_name = lb_name[:-ext_len]
        bone_name = bone_name[:-ext_len]
    # check for left/right name and return left(0) or right(1) or center(-1), with base name (including number extension)
    if lb_name.startswith("left"):
        return (0, bone_name[4:] + number_ext)
    elif lb_name[0] == "l" and lb_name[1] in [".", "_", "-"]:
        return (0, bone_name[2:] + number_ext)
    elif lb_name.endswith("left"):
        return (0, bone_name[:-4] + number_ext)
    elif lb_name[-1] == "l" and lb_name[-2] in [".", "_", "-"]:
        return (0, bone_name[:-2] + number_ext)
    elif lb_name.startswith("right"):
        return (1, bone_name[5:] + number_ext)
    elif lb_name[0] == "r" and lb_name[1] in [".", "_", "-"]:
        return (1, bone_name[2:] + number_ext)
    elif lb_name.endswith("right"):
        return (1, bone_name[:-5] + number_ext)
    elif lb_name[-1] == "r" and lb_name[-2] in [".", "_", "-"]:
        return (1, bone_name[:-2] + number_ext)
    else:
        return (-1, None)

def getBoneLeftRightLookups(bone_names):
    bone_side = {}
    bone_base_lr = {}
    for b_name in bone_names:
        side, base_name = getBoneSideAndBaseName(b_name)
        bone_side[b_name] = (side, base_name)
        if side == -1:
            continue
        if base_name not in bone_base_lr:
            bone_base_lr[base_name] = [ None, None ]
        bone_base_lr[base_name][side] = b_name
    return bone_side, bone_base_lr

def copy_action_frame(ob, action_name, src_frame_num, loc_mult, rot_mult, scl_pow, left_factor, right_factor, mirror, only_selected,
                      frame=None, result_action=None, use_defaults=None, blend_factor=1.0):
    arm = ob.data
    if arm is None:
        return {}
    apply_action = bpy.data.actions.get(action_name)
    if apply_action is None:
        return {}
    if not is_bone_action(apply_action):
        return {}
    pose_bones = ob.pose.bones
    bone_side_lookup, bone_base_lr_lookup = getBoneLeftRightLookups(pose_bones.keys())
    frame_data = {}
    for fc in apply_action.fcurves:
        if not fc.data_path.startswith("pose.bones["):
            continue
        fc_tokens, _ = lex_py_attributes(fc.data_path)
        if len(fc_tokens) < 4:
            continue
        bone_name = fc.data_path[ fc_tokens[2][0]+2 : fc_tokens[2][1]-2 ]
        if bone_name not in pose_bones:
            continue
        if only_selected and not ob.data.bones[bone_name].select:
            continue
        prop_name = fc.data_path[fc.data_path.rfind(".")+1:]
        if fc.data_path not in frame_data:
            frame_data[fc.data_path] = {}
        # check for 'use default value', and store the result value
        value = fc.evaluate(src_frame_num)
        if use_defaults == True and prop_name in GLOBAL_POSE_PROP_DEFAULTS:
            default_val = GLOBAL_POSE_PROP_DEFAULTS[prop_name]
            if hasattr(default_val, "__len__") and len(default_val) > 0:
                if fc.array_index < len(default_val):
                    value = default_val[fc.array_index]
                else:
                    value = default_val[0]
            else:
                value = default_val
        frame_data[fc.data_path][fc.array_index] = value
    # set Armature Pose properties, and keyframe if needed - these keyframes will automatically replace any keyframes
    # created by 'F Curves to reset' code
    for data_path, indexed_values in frame_data.items():
        fc_tokens, _ = lex_py_attributes(data_path)
        bone_name = data_path[ fc_tokens[2][0]+2 : fc_tokens[2][1]-2 ]
        bone_side = bone_side_lookup[bone_name][0]
        if mirror and bone_side != -1:
            bone_name = bone_base_lr_lookup[bone_side_lookup[bone_name][1]][1 - bone_side]
            bone_side = 1 - bone_side
            mirror_applied = True
        else:
            mirror_applied = False
        if bone_side == -1:
            bone_side_mult = 1.0
        elif bone_side == 0:
            bone_side_mult = left_factor
        else:
            bone_side_mult = right_factor
        thing_to_keyframe = get_thing_to_keyframe(ob, data_path, fc_tokens, bone_name)
        if thing_to_keyframe is None:
            continue
        prop_name = data_path[data_path.rfind(".")+1:]
        new_quat_value = None
        if prop_name == "rotation_quaternion":
            new_quat_value = get_scaled_quaternion_from_indexed_values(indexed_values, rot_mult * bone_side_mult)
            old_quat_value = pose_bones[bone_name].rotation_quaternion
        rotation_euler_mirror_axes = []
        if prop_name == "rotation_euler":
            if pose_bones[bone_name].rotation_mode in [ "XYZ", "XZY" ]:
                rotation_euler_mirror_axes = [ 1, 2 ]
            elif pose_bones[bone_name].rotation_mode in [ "YXZ", "ZXY" ]:
                rotation_euler_mirror_axes = [ 0, 2 ]
            elif pose_bones[bone_name].rotation_mode in [ "YZX", "ZYX" ]:
                rotation_euler_mirror_axes = [ 0, 1 ]
        for array_index, value in indexed_values.items():
            if prop_name == "location":
                value = value * loc_mult[array_index] * bone_side_mult
                if mirror_applied and array_index == 0:
                    value = value * -1
                if blend_factor != 1.0:
                    value *= blend_factor
                    value += pose_bones[bone_name].location[array_index] * (1.0 - blend_factor)
            elif prop_name == "rotation_euler":
                value = value * rot_mult * bone_side_mult
                if mirror_applied and array_index in rotation_euler_mirror_axes:
                    value = value * -1
                if blend_factor != 1.0:
                    value *= blend_factor
                    value += pose_bones[bone_name].rotation_euler[array_index] * (1.0 - blend_factor)
            elif prop_name == "rotation_axis_angle":
                if array_index == 0:
                    value = value * rot_mult * bone_side_mult
                if mirror_applied and array_index in [ 0, 1 ]:
                    value = value * -1
                if blend_factor != 1.0:
                    value *= blend_factor
                    value += pose_bones[bone_name].rotation_axis_angle[array_index] * (1.0 - blend_factor)
            elif prop_name == "rotation_quaternion" and new_quat_value != None:
                if mirror_applied:
                    new_quat_value[1] = -new_quat_value[1]
                    new_quat_value[3] = -new_quat_value[3]
                if blend_factor >= 0.0 and blend_factor <= 1.0:
                    blend_quat_value = old_quat_value.slerp(new_quat_value, blend_factor)
                else:
                    q1 = old_quat_value.to_exponential_map()
                    q2 = new_quat_value.to_exponential_map()
                    q3 = q1 * (1.0 - blend_factor) + q2 * blend_factor
                    blend_quat_value = Quaternion(q3)
                value = blend_quat_value[array_index]
            elif prop_name == "scale":
                # prevent divide by zero exception
                if value != 0.0 or scl_pow[array_index] * bone_side_mult >= 0.0:
                    value = pow(value, scl_pow[array_index] * bone_side_mult)
                if blend_factor != 1.0:
                    value *= blend_factor
                    value += pose_bones[bone_name].scale[array_index] * (1.0 - blend_factor)
            # keyframe property values
            if isinstance(frame, (float, int)) and result_action != None:
                fc = result_action.fcurves.find(data_path=data_path, index=array_index)
                if fc is None:
                    color_mode = 'AUTO_RAINBOW'
                    if prop_name == 'rotation_mode' or prop_name == 'influence':
                        if not thing_to_keyframe.keyframe_insert(data_path=prop_name, frame=frame, group=bone_name):
                            continue
                        fc = result_action.fcurves.find(data_path=data_path)
                    else:
                        if not thing_to_keyframe.keyframe_insert(data_path=prop_name, index=array_index, frame=frame,
                                                                 group=bone_name):
                            continue
                        fc = result_action.fcurves.find(data_path=data_path, index=array_index)
                        color_mode = 'AUTO_RGB'
                    if fc is None:
                        continue
                    fc.color_mode = color_mode
                    kp = fc.keyframe_points[0]
                    kp.co = (frame, value)
                else:
                    fc.keyframe_points.insert(frame, value, keyframe_type='KEYFRAME')
            # only set property values
            else:
                if len(fc_tokens) == 4:
                    if prop_name == 'rotation_mode' and value in ROTATION_MODE_STRINGS:
                        setattr(thing_to_keyframe, prop_name, ROTATION_MODE_STRINGS[value])
                    else:
                        prop = getattr(thing_to_keyframe, prop_name)
                        if hasattr(prop, "__len__"):
                            prop[array_index] = value
                        else:
                            setattr(thing_to_keyframe, prop_name, value)
                elif len(fc_tokens) == 6 and data_path[ fc_tokens[3][0] : fc_tokens[3][1] ] == 'constraints':
                    prop = getattr(thing_to_keyframe, prop_name)
                    if hasattr(prop, "__len__"):
                        prop[array_index] = value
                    else:
                        setattr(thing_to_keyframe, prop_name, value)
    return frame_data

def keyframe_copy_action_frame(ob, action_name, src_frame_num, loc_mult, rot_mult, scl_pow, left_factor, right_factor,
                               mirror, only_selected, frame, blend_factor):
    # create animation / Action data if needed, before applying script
    if ob.animation_data is None:
        ob.animation_data_create()
    if ob.animation_data.action is None:
        ob.animation_data.action = bpy.data.actions.new(ob.name+"Action")
    copy_action_frame(ob, action_name, src_frame_num, loc_mult, rot_mult, scl_pow, left_factor, right_factor, mirror,
                      only_selected, frame, ob.animation_data.action, blend_factor=blend_factor)
    do_tag_redraw()

def playback_frame_handler(scene):
    if scene.frame_current >= playback_dict["end_frame"] or scene.frame_current >= scene.frame_end:
        bpy.ops.screen.animation_cancel()

def playback_remove_handler(scene):
    if playback_frame_handler in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(playback_frame_handler)
    if playback_remove_handler in bpy.app.handlers.animation_playback_post:
        bpy.app.handlers.animation_playback_post.remove(playback_remove_handler)
    scene.frame_current = playback_dict["return_frame"]
    playback_dict["return_frame"] = None
    playback_dict["start_frame"] = None
    playback_dict["end_frame"] = None

def playback_frames(scene, forward_frames, reverse_frames):
    # if already playing animation via playback_frames then restart at start_frame
    if playback_dict["return_frame"] != None:
        scene.frame_current = playback_dict["start_frame"]
    else:
        # ensure no previous instances of this handler are present before appending the handler
        if playback_frame_handler in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.remove(playback_frame_handler)
        if playback_remove_handler in bpy.app.handlers.animation_playback_post:
            bpy.app.handlers.animation_playback_post.remove(playback_remove_handler)
        playback_dict["return_frame"] = scene.frame_current
        if scene.frame_current + forward_frames > scene.frame_end:
            playback_dict["end_frame"] = scene.frame_end
        else:
            playback_dict["end_frame"] = scene.frame_current + forward_frames
        if scene.frame_current - reverse_frames < scene.frame_start:
            playback_dict["start_frame"] = scene.frame_start
        else:
            playback_dict["start_frame"] = scene.frame_current - reverse_frames
        scene.frame_current = playback_dict["start_frame"]
        bpy.app.handlers.frame_change_pre.append(playback_frame_handler)
        bpy.app.handlers.animation_playback_post.append(playback_remove_handler)
        bpy.ops.screen.animation_play()
