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
import fnmatch
import math
import os
import traceback

import bpy

from ..const import ADDON_BASE_FILE
from ..object_func import (get_scene_user_collection, is_object_in_sub_collection)

ARM_FUNC_RETARGET = "ARM_FUNC_RETARGET"
ARM_FUNC_UTILITY = "ARM_FUNC_UTILITY"
ARM_FUNC_ITEMS = [
    (ARM_FUNC_RETARGET, "Retarget", ""),
    (ARM_FUNC_UTILITY, "Utility", ""),
    ]

script_pose_presets = {}
retarget_armature_presets = {}

RETARGET_CONSTRAINT_NAME_PREFIX = "AMH2B Retarget "

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

# returns dict() {
#     "result": < result of ast.literal_eval() with file string >,
#     "error": "< True / False >,
# }
def ast_literal_eval_textblock(text):
    full_str = ""
    for line in text.lines:
        line_body = line.body
        find_comment = line_body.find("#")
        if find_comment != -1:
            line_body = line_body[:find_comment] + "\n"
        full_str += line_body
    try:
        eval_result = ast.literal_eval(full_str)
    except:
        return { "error": traceback.format_exc() }
    return { "result": eval_result }

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

# returns dict() {
#     "result": < result of ast.literal_eval() with file string >,
#     "error": "< True / False >,
# }
def ast_literal_eval_file(f):
    full_str = ""
    for line in f:
        find_comment = line.find("#")
        if find_comment != -1:
            line = line[:find_comment] + "\n"
        full_str += line
    try:
        eval_result = ast.literal_eval(full_str)
    except:
        return { "error": traceback.format_exc() }
    return { "result": eval_result }

def get_file_eval_dict(script_file):
    file_eval = ast_literal_eval_file(script_file)
    if file_eval.get("error") != None:
        return file_eval.get("error")
    script = file_eval.get("result")
    if not isinstance(script, dict):
        return "Error: Script did not evaluate to type 'dict' (dictionary)"
    return script

def script_pose_preset_items(self, context):
    items = []
    for filename, pose_script in script_pose_presets.items():
        label = pose_script.get("label")
        if label is None:
            label = filename
        items.append ( (filename, label, "") )
    if len(items) < 1:
        return [ (" ", "", "") ]
    return items

def load_script_pose_presets():
    # do not re-load
    if len(script_pose_presets) > 0:
        return
    # get paths to presets files
    base_path = os.path.dirname(os.path.realpath(ADDON_BASE_FILE))
    p = os.path.join(base_path, "presets", "script_pose")
    file_paths = [ f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f)) ]
    # safely read each file and get pose script, trying ALL FILES in the presets path
    for fp in file_paths:
        try:
            with open(os.path.join(p, fp), 'r') as f:
                pose_script = get_file_eval_dict(f)
        except:
            pose_script = "Error: cannot open Script Pose preset file named: " + fp
        if not isinstance(pose_script, dict):
            continue
        script_pose_presets[fp] = pose_script

def global_rotate_bone(arm_ob, bone_name, axis_name, offset_deg):
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
def armature_apply_scale(context, ob, apply_location=False, apply_rotation=False):
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
    bpy.ops.object.transform_apply(location=apply_location, rotation=apply_rotation, scale=True)
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
        items.append ( (filename, label, "") )
    if len(items) < 1:
        return [ (" ", "", "") ]
    return items

def load_retarget_armature_presets():
    # do not re-load
    if len(retarget_armature_presets) > 0:
        return
    # get paths to presets files
    base_path = os.path.dirname(os.path.realpath(ADDON_BASE_FILE))
    p = os.path.join(base_path, "presets", "retarget_armature")
    file_paths = [ f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f)) ]
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

def op_join_armatures(context, op_data, script_state):
    if script_state["armatures_joined"]:
        return
    script_state["armatures_joined"] = True
    old_bone_names = [ bone.name for bone in script_state["dest_object"].data.bones ]
    dest_ob_name = script_state["dest_object"].name
    if context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.join()
    script_state["dest_object"] = context.active_object
    # ensure 'joined' armature has original 'target object' name
    script_state["dest_object"].name = dest_ob_name
    script_state["source_object"] = None
    # assign bone layers
    for bone in script_state["dest_object"].data.bones:
        # do not change bone layers of original bones
        if bone.name in old_bone_names:
            continue
        # new bones will be visible in layer 'add_layer_index' only
        for i in range(32):
            bone.layers[i] = script_state["add_layer_index"] == i

def op_rename_bone(context, op_data, script_state):
    if not isinstance(op_data, (list, tuple)):
        return
    if script_state["source_object"] is None:
        source_bone_names = []
    else:
        source_bone_names = [ bone.name for bone in script_state["source_object"].data.bones ]
    if script_state["dest_object"] is None:
        dest_bone_names = []
    else:
        dest_bone_names = [ bone.name for bone in script_state["dest_object"].data.bones ]
    bone_name_trans = {}
    for rename_data in op_data:
        if not is_types(rename_data, (str, str, str) ) or rename_data[2] == "":
            continue
        bone = None
        if rename_data[0].lower() == "source":
            if script_state["source_object"] != None:
                trans_name = bone_name_translation(bone_name_trans, source_bone_names, rename_data[1])
                bone = script_state["source_object"].data.bones.get(trans_name)
        elif rename_data[0].lower() == "target":
            trans_name = bone_name_translation(bone_name_trans, dest_bone_names, rename_data[1])
            bone = script_state["dest_object"].data.bones.get(trans_name)
        if bone != None:
            bone.name = rename_data[2]

def op_set_parent_bone(context, op_data, script_state):
    if not isinstance(op_data, (list, tuple)):
        return
    if context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    if script_state["source_object"] is None:
        source_bone_names = []
    else:
        source_bone_names = [ bone.name for bone in script_state["source_object"].data.bones ]
    if script_state["dest_object"] is None:
        dest_bone_names = []
    else:
        dest_bone_names = [ bone.name for bone in script_state["dest_object"].data.bones ]
    bone_name_trans = {}
    for set_parent_data in op_data:
        if not is_types(set_parent_data, (str, str, str) ):
            continue
        bone_from = None
        bone_to = None
        if set_parent_data[0].lower() == "source":
            if script_state.get("source_object") != None:
                from_trans_name = bone_name_translation(bone_name_trans, source_bone_names, set_parent_data[1])
                to_trans_name = bone_name_translation(bone_name_trans, source_bone_names, set_parent_data[2])
                if from_trans_name is None or to_trans_name is None:
                    continue
                bone_from = script_state["source_object"].data.edit_bones.get(from_trans_name)
                bone_to = script_state["source_object"].data.edit_bones.get(to_trans_name)
        elif set_parent_data[0].lower() == "target":
            from_trans_name = bone_name_translation(bone_name_trans, dest_bone_names, set_parent_data[1])
            to_trans_name = bone_name_translation(bone_name_trans, dest_bone_names, set_parent_data[2])
            if from_trans_name is None or to_trans_name is None:
                continue
            bone_from = script_state["dest_object"].data.edit_bones.get(from_trans_name)
            bone_to = script_state["dest_object"].data.edit_bones.get(to_trans_name)
        if bone_from is None or bone_to is None:
            continue
        bone_from.use_connect = False
        bone_to.use_connect = False
        bone_from.parent = bone_to

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

def op_dup_swap_stitch(context, op_data, script_state):
    if not isinstance(op_data, (list, tuple)):
        return
    # duplicate / move bones in Edit mode
    if context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    if script_state["source_object"] is None:
        source_bone_names = []
    else:
        source_bone_names = [ bone.name for bone in script_state["source_object"].data.bones ]
    if script_state["dest_object"] is None:
        dest_bone_names = []
    else:
        dest_bone_names = [ bone.name for bone in script_state["dest_object"].data.bones ]
    source_bone_name_trans = {}
    dest_bone_name_trans = {}
    constraint_inputs = []
    for dup_swap_data in op_data:
        # e.g. ("target", "LeftArm", "arm_base.L", 0.35, 0)
        if not is_types(dup_swap_data, (str, str, str, (float, int), (float, int)) ):
            continue
        arm_ob = None
        if dup_swap_data[0].lower() == "source":
            arm_ob = script_state["source_object"]
            bone_to_dup_name = bone_name_translation(source_bone_name_trans, source_bone_names, dup_swap_data[1])
            ref_bone_name = bone_name_translation(source_bone_name_trans, source_bone_names, dup_swap_data[2])
        elif dup_swap_data[0].lower() == "target":
            arm_ob = script_state["dest_object"]
            bone_to_dup_name = bone_name_translation(dest_bone_name_trans, dest_bone_names, dup_swap_data[1])
            ref_bone_name = bone_name_translation(dest_bone_name_trans, dest_bone_names, dup_swap_data[2])
        else:
            continue
        if bone_to_dup_name is None or ref_bone_name is None:
            continue
        dist_on_dup = dup_swap_data[3]
        dist_on_ref = dup_swap_data[4]
        # set the parenting type to offset (connect=False), to prevent geometry being warped when re-parented
        arm_ob.data.edit_bones[bone_to_dup_name].use_connect = False
        arm_ob.data.edit_bones[ref_bone_name].use_connect = False
        # get 3d translation vector as a point coincident with both bones, along a factor of each bone's length
        t_vec = get_translation_vec(arm_ob.data.edit_bones[bone_to_dup_name], arm_ob.data.edit_bones[ref_bone_name],
                                    dist_on_dup, dist_on_ref)
        # duplicate bone
        new_bone = arm_ob.data.edit_bones.new(arm_ob.data.edit_bones[bone_to_dup_name].name)
        # put new_bone in the 'added bones' layer
        for i in range(32):
            new_bone.layers[i] = script_state["add_layer_index"] == i
        # copy head and tail locations, with offset by distance factor along original bones' length
        new_bone.head.x = arm_ob.data.edit_bones[bone_to_dup_name].head.x + t_vec[0]
        new_bone.head.y = arm_ob.data.edit_bones[bone_to_dup_name].head.y + t_vec[1]
        new_bone.head.z = arm_ob.data.edit_bones[bone_to_dup_name].head.z + t_vec[2]
        new_bone.tail.x = arm_ob.data.edit_bones[bone_to_dup_name].tail.x + t_vec[0]
        new_bone.tail.y = arm_ob.data.edit_bones[bone_to_dup_name].tail.y + t_vec[1]
        new_bone.tail.z = arm_ob.data.edit_bones[bone_to_dup_name].tail.z + t_vec[2]
        new_bone.roll = arm_ob.data.edit_bones[bone_to_dup_name].roll
        # swap new bone for ref_bone
        new_bone.parent = arm_ob.data.edit_bones[ref_bone_name].parent
        arm_ob.data.edit_bones[ref_bone_name].parent = new_bone
        # keep references to bones so bone constraints can be added later
        constraint_inputs.append( (new_bone.name, bone_to_dup_name) )
    # add constraints in Pose mode
    bpy.ops.object.mode_set(mode='POSE')
    for new_bone_name, bone_to_dup_name in constraint_inputs:
        # new bone will copy rotation from bone_to_dup
        crc = arm_ob.pose.bones[new_bone_name].constraints.new('COPY_ROTATION')
        crc.name = RETARGET_CONSTRAINT_NAME_PREFIX + "Copy Rotation"
        crc.target = arm_ob
        crc.subtarget = bone_to_dup_name
        crc.target_space = 'LOCAL'
        crc.owner_space = 'LOCAL'
        crc.use_offset = True
        # new bone will also copy location from bone_to_dup (user can turn off / remove if needed)
        clc = arm_ob.pose.bones[new_bone_name].constraints.new('COPY_LOCATION')
        clc.name = RETARGET_CONSTRAINT_NAME_PREFIX + "Copy Location"
        clc.target = arm_ob
        clc.subtarget = bone_to_dup_name
        clc.target_space = 'LOCAL'
        clc.owner_space = 'LOCAL'
        clc.use_offset = True

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
        # create bones in Transfer Armature, copying from Source and Destination Armatures
        xfer_source_bone = xfer_arm.edit_bones.new(source_bone_name)
        xfer_dest_bone = xfer_arm.edit_bones.new(dest_bone_name)
        # put new bones in first and second layers
        for i in range(32):
            xfer_source_bone.layers[i] = i == 0
            xfer_dest_bone.layers[i] = i == 1
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
        print("tvec =", t_vec, ", fac =", fac)
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

    # add constraints in Pose mode
    bpy.ops.object.mode_set(mode='POSE')
    xfer_pose_bones = script_state["transfer_armature_ob"].pose.bones
    dest_pose_bones = script_state["dest_object"].pose.bones
    for s_bone_name, d_bone_name, x_source_bone_name, x_dest_bone_name in constraint_inputs:
        # Copy Transforms constraint from: s_bone_name, to: x_source_bone_name
        xfer_ctc = xfer_pose_bones[x_source_bone_name].constraints.new('COPY_TRANSFORMS')
        xfer_ctc.name = RETARGET_CONSTRAINT_NAME_PREFIX + "Copy Transforms"
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

def op_transfer_transforms(context, op_data, script_state):
    op_transfer_constraint(context, op_data, script_state, 'COPY_TRANSFORMS')

def op_transfer_rotation(context, op_data, script_state):
    op_transfer_constraint(context, op_data, script_state, 'COPY_ROTATION')

def set_mono_bone_layer(ob, layer_index):
    bones = ob.data.bones
    mono_layers = [ layer_index == i for i in range(32) ]
    for b in bones:
        if b.layers[layer_index]:
            b.layers = mono_layers

def apply_retarget_armature_script(context, source_ob, dest_ob, retarget_script, add_layer_index):
    retarget_data = retarget_script.get("data")
    try:
        if len(retarget_data) < 1:
            return
    except:
        return
    operation_functions = {
        "join_armatures": op_join_armatures,
        "rename_bone": op_rename_bone,
        "set_parent_bone": op_set_parent_bone,
        "dup_swap_stitch": op_dup_swap_stitch,
        "create_transfer_armature": op_create_transfer_armature,
        "transfer_transforms": op_transfer_transforms,
        "transfer_rotation": op_transfer_rotation,
        }
    script_state = {
        "add_layer_index": add_layer_index,
        "source_object": source_ob,
        "dest_object": dest_ob,
        "armatures_joined": False,
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
    if script_state["armatures_joined"]:
        set_mono_bone_layer(context.active_object, add_layer_index)

# Retarget Armature has two Methods:
#    1) Stitch Armature (old method)
#    2) Transfer Armature (new method)
#   Stitch Armature
# Simplify the MakeHuman rig animation process re: Mixamo et al. via a stitched (joined) armature that connects
# imported animated rigs to imported MHX2 rigs - leaving face panel and visemes intact, while allowing
# for great functionality e.g. finger movements.
# In a perfect world, Blender and MakeHuman would work seamlessly with any and all motion capture data,
# and any motion capture sharing website (including body, facial, etc. rig).
# The real world includes problems with bone names, "bone roll", vertex groups, etc.
# This addon bridges some real world gaps between different rigs.
# Basically, bones from Rig B (this could be a downloaded rig from a mocap sharing website, etc.)
# are mapped to Rig A so that Rig B acts like "marionettist" to the Rig A "marionette".
# Rig B controls Rig A, allowing the user to tweak the final animation by animating Rig A.
# Caveat: Rig A and Rig B should be in the same pose.
#   Transfer Armature:
# Create a Transfer Armature, with bones copied from source and destination rigs, bones parented together only
# in the Transfer Armature. Bones in Transfer Armature will be given bone constraints to copy location/rotation
# from Mixamo armature. Then, bones in MPFB2 armature will be given constraints to copy locaiton/rotation from
# Transfer Armature.
def retarget_armature(context, apply_transforms, src_arm_ob, targ_arm_ob, preset_name,
                      use_textblock, textblock_name, add_layer_index):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    if apply_transforms:
        armature_apply_scale(context, src_arm_ob, True, True)
    if use_textblock:
        retarget_script = get_textblock_eval_dict(textblock_name)
    else:
        retarget_script = retarget_armature_presets.get(preset_name)
    if retarget_script is None:
        ret_val = False
    else:
        ret_val = apply_retarget_armature_script(context, src_arm_ob, targ_arm_ob, retarget_script, add_layer_index)
    bpy.ops.object.mode_set(mode=old_3dview_mode)
    return ret_val

# intended to be used after Stitch Armature (Retarget Armature), to remove extra bones from Armature while
# retaining animation of all bones of Armature
def copy_armature_transforms(context, src_arm_ob, dest_arm_ob, only_selected, frame_start, frame_end, frame_step):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='POSE')
    remove_const = []
    for bone in dest_arm_ob.pose.bones:
        if only_selected and not dest_arm_ob.data.bones[bone.name].select:
            continue
        ct_const = bone.constraints.new(type='COPY_TRANSFORMS')
        ct_const.name = RETARGET_CONSTRAINT_NAME_PREFIX + "Copy Transforms"
        ct_const.target = src_arm_ob
        ct_const.subtarget = bone.name
        ct_const.head_tail = 0.0
        ct_const.remove_target_shear = False
        ct_const.mix_mode = 'REPLACE'
        ct_const.target_space = 'WORLD'
        ct_const.owner_space = 'WORLD'
        ct_const.influence = 1.0
        remove_const.append( (bone, ct_const) )
    src_arm_ob.select_set(False)
    bpy.ops.nla.bake(frame_start=frame_start, frame_end=frame_end, step=frame_step, only_selected=only_selected,
                     bake_types={'POSE'})
    for bone, const in remove_const:
        bone.constraints.remove(const)
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def is_mhx2_armature(ob):
    return ob != None and hasattr(ob, "MhxRig") and ob.MhxRig in ('MHX', 'EXPORTED_MHX')

def remove_transfer_constraints(context, ob):
    old_3dview_mode = context.object.mode
    bpy.ops.object.mode_set(mode='POSE')
    for pose_bone in ob.pose.bones:
        remove_c_list = []
        for const in pose_bone.constraints:
            if const.name.startswith(RETARGET_CONSTRAINT_NAME_PREFIX):
                remove_c_list.append(const)
        for const in remove_c_list:
            pose_bone.constraints.remove(const)
    bpy.ops.object.mode_set(mode=old_3dview_mode)
