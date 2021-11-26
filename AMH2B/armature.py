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

import bpy
import csv
import fnmatch

from .bone_strings import *
from .armature_func import *
from .object_func import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

#####################################################
#     Adjust Pose
# Script rotations of bones to reduce time waste. Input is from TextBlock named 'Text', in CSV format.
# Get the rotations correct once, type it up as a CSV file, then use the script repeatedly.

def global_rotate_bone(rig_object, bone_name, axis_name, offset_deg):
    the_bone = rig_object.pose.bones.get(bone_name)
    if the_bone is None:
        return
    the_bone.bone.select = True
    do_global_rotate(axis_name, offset_deg)
    the_bone.bone.select = False

def run_offsets(rig_obj, offsets, datablock_textname):
    rec_count = 0
    try:
        for of_bone_name, of_axis, of_deg in offsets:
            global_rotate_bone(rig_obj, of_bone_name.strip(), of_axis.strip(), float(of_deg))
            rec_count = rec_count+1

    except ValueError:
        return "ValueError while parsing CSV record #" + str(rec_count) + " in text block: " + datablock_textname

    return None

def get_scripted_offsets(datablock_textname):
    bl = bpy.data.texts.get(datablock_textname)
    if bl is None:
        return

    bl_str = bl.as_string()
    if bl_str == '':
        return
    csv_lines = csv.reader(bl_str.splitlines(), quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL,
                           skipinitialspace=True)
    return list(csv_lines)

def do_adjust_pose(mhx_arm_obj):
    # get CSV user data text block and convert to array of offsets data
    offsets = get_scripted_offsets(bpy.context.scene.Amh2bPropArmTextBlockName)
    if offsets is None:
        return "Scripted offsets text block not found: " + bpy.context.scene.Amh2bPropArmTextBlockName

    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='POSE')

    # deselect all bones and run script to (select, pose, unselect) each bone individually
    bpy.ops.pose.select_all(action='DESELECT')
    err_str = run_offsets(mhx_arm_obj, offsets, bpy.context.scene.Amh2bPropArmTextBlockName)

    bpy.ops.object.mode_set(mode=old_3dview_mode)
    return err_str

class AMH2B_AdjustPose(AMH2B_AdjustPoseInner, bpy.types.Operator):
    """Add to rotations of pose of active object by way of CSV script in Blender's Text Editor. Default script name is Text"""
    bl_idname = "amh2b.arm_adjust_pose"
    bl_label = "Adjust Pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        # quit if Active Object is None or not an armature
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}

        err_str = do_adjust_pose(act_ob)
        if err_str is None:
            return {'FINISHED'}

        self.report({'ERROR'}, err_str)
        return {'CANCELLED'}

#####################################################
#     Apply Scale
# Apply scale to armature (this is only needed for armature scale apply),
# and adjust it"s bone location animation f-curve values to match the scaling.
# If this operation is not done, then the bones that have changing location values
# will appear to move incorrectly.
def do_apply_scale(act_ob):
    old_3dview_mode = bpy.context.object.mode

    # keep copy of old scale values
    old_scale = act_ob.scale.copy()
    bpy.ops.object.mode_set(mode='OBJECT')

    # do not apply scale if scale is already 1.0 in all dimensions!
    if old_scale.x == 1 and old_scale.y == 1 and old_scale.z == 1:
        return

    # apply scale to active object
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    action = act_ob.animation_data.action
    if action is None:
        return

    # if no f-curves then no exit, because only needed 'apply scale'
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
    bpy.context.scene.frame_set(bpy.context.scene.frame_current+1)
    bpy.context.scene.frame_set(bpy.context.scene.frame_current-1)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_ApplyScale(bpy.types.Operator):
    """Apply Scale to active object (ARMATURE type) without corrupting the armature pose data (i.e. location)"""
    bl_idname = "amh2b.arm_apply_scale"
    bl_label = "Apply Scale to Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}

        do_apply_scale(act_ob)
        return {'FINISHED'}

#####################################################
#     Bridge Re-Pose Rig
# Re-pose original rig (which has shape keys, hence this work-around) by way of a duplicate of original
# that moves mesh to desired pose, then original rig is pose-apply'ed and takes over from duplicate rig.
# Basically, a duplicate rig moves the underlying mesh to the place where the reposed original rig will be.

def do_bridge_repose_rig(act_ob, sel_obj_list):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # copy list of selected objects, minus the active object
    # (0 selected objects is allowed, because armature can be re-posed independently)
    selection_list = []
    for ob in sel_obj_list:
        if ob.name != act_ob.name:
            selection_list.append(ob)

    # de-select all objects
    bpy.ops.object.select_all(action='DESELECT')

    # select the old active_object in the 3D viewport
    select_object(act_ob)
    # make it the active selected object
    set_active_object(act_ob)

    # duplicate the original armature
    new_arm = dup_selected()
    # parent the duplicated armature to the original armature, to prevent mesh tearing if the armatures move apart
    new_arm.parent = act_ob
    # reset location/rotation of duplicate, relative to parent, to zero - and reset scale to 1
    new_arm.location = (0, 0, 0)
    if new_arm.rotation_mode == 'AXIS_ANGLE':
        new_arm.rotation_axis_angle = (0, 0, 1, 0)
    elif new_arm.rotation_mode == 'QUATERNION':
        new_arm.rotation_quaternion = (1, 0, 0, 0)
    else:
        new_arm.rotation_euler = (0, 0, 0)
    new_arm.scale = (1, 1, 1)

    # add modifiers to the other selected objects, so the other selected objects will use the new armature
    add_armature_to_objects(new_arm, selection_list)

    # ensure original armature is selected
    select_object(act_ob)
    # make original armature the active object
    set_active_object(act_ob)

    bpy.ops.object.mode_set(mode='POSE')
    # apply pose to original armature
    bpy.ops.pose.armature_apply()

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_BridgeRepose(bpy.types.Operator):
    """Create a "bridge rig" to move a shape-keyed mesh into new position, so copy of armature can have pose applied.\nSelect all MESH objects attached to armature first, and select armature last, then use this function"""
    bl_idname = "amh2b.arm_bridge_repose"
    bl_label = "Bridge Re-Pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}

        do_bridge_repose_rig(act_ob, context.selected_objects)
        return {'FINISHED'}

#####################################################
#     Bone Woven
# Simplify the MakeHuman rig animation process re: Mixamo et al. via a bridge that connects
# imported animation rigs to imported MHX2 rigs - leaving face panel and visemes intact, while allowing
# for great functionality e.g. finger movements.
# In a perfect world, Blender and MakeHuman would work seamlessly with any and all motion capture data,
# and any motion capture sharing website (including body, facial, etc. rig).
# The real world includes problems with bone names, "bone roll", vertex groups, etc.
# This addon bridges some real world gaps between different rigs.
# Basically, bones from Rig B (this could be a downloaded rig from a mocap sharing website, etc.)
# are mapped to Rig A so that Rig B acts like "marionettist" to the Rig A "marionette".
# Rig B controls Rig A, allowing the user to tweak the final animation by animating Rig A.
# Caveat: Rig A and Rig B should be in the same pose.
# Side-note: Ugly, But Works

# minimum number of bones matching by string to justify matching rig found = true
amh2b_min_bones_for_rig_match = 10  # 10 is estimate, TODO: check estimate

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

def stitchdata_concat_3(stitch_data1, stitch_data2):
    if stitch_data1 is None:
        return stitch_data2
    elif stitch_data2 is None:
        return stitch_data1
    else:
        data_concat = stitch_data1.copy()
        for temp1, temp2, temp3 in stitch_data2:
            data_concat.append((temp1, temp2, temp3))
        return data_concat

def stitchdata_concat_4(stitch_data1, stitch_data2):
    if stitch_data1 is None:
        return stitch_data2
    elif stitch_data2 is None:
        return stitch_data1
    else:
        data_concat = stitch_data1.copy()
        for temp1, temp2, temp3, temp4 in stitch_data2:
            data_concat.append((temp1, temp2, temp3, temp4))
        return data_concat

# other_rig_obj is source, mhx_rig_obj is destination
def do_bridge_rigs(self, mhx_rig_obj, mhx_rig_type, other_rig_obj, other_rig_type, bone_name_trans):
    dest_stitch = amh2b_rig_stitch_dest_list.get(mhx_rig_type).get(other_rig_type)
    if dest_stitch is None:
        return

    bpy.ops.object.mode_set(mode='OBJECT')

    set_active_object(other_rig_obj)

    bpy.ops.object.mode_set(mode='EDIT')
    # Rename before join so that animation is attached to correct bones, to prevent mismatches
    # from bones being auto-renamed when rigs are joined.
    rename_bones_before_join(other_rig_obj, dest_stitch.get("blist_rename"))

    bpy.ops.object.mode_set(mode='OBJECT')

    set_active_object(mhx_rig_obj)

    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode='EDIT')
    stitch_bones(self, mhx_rig_obj, dest_stitch, bone_name_trans)
    bpy.ops.object.mode_set(mode='OBJECT')

def rename_bones_before_join(rig_obj, bone_rename_tuples):
    if bone_rename_tuples is not None:
        for old_bn, new_bn in bone_rename_tuples:
            # ignore missing bones
            if rig_obj.data.edit_bones.get(old_bn) is None:
                continue
            # change name of bone
            rig_obj.data.edit_bones[old_bn].name = new_bn

def stitch_bones(self, rig_obj, stitch_datapack, bone_name_trans):
    batch_do_dup_swap_stitches(self, rig_obj, stitch_datapack, bone_name_trans)
    batch_do_move_bones(self, rig_obj, stitch_datapack, bone_name_trans)
    batch_do_set_parents(self, rig_obj, stitch_datapack, bone_name_trans)

def batch_do_dup_swap_stitches(self, rig_obj, stitch_datapack, bone_name_trans):
    # TORSO
    if self.torso_stitch_enum == 'YES':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_torso"), bone_name_trans)

    # ARM LEFT
    if self.arm_left_stitch_enum == 'FORWARDK':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_arm_L_fk"), bone_name_trans)
    elif self.arm_left_stitch_enum == 'INVERSEK':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_arm_L_ik"), bone_name_trans)
    elif self.arm_left_stitch_enum == 'BOTH':
        inner_batch_dup_swap_stitches(rig_obj, stitchdata_concat_4(stitch_datapack.get("blist_dup_swap_stitch_arm_L_fk"), stitch_datapack.get("blist_dup_swap_stitch_arm_L_ik")), bone_name_trans)

    # ARM RIGHT
    if self.arm_right_stitch_enum == 'FORWARDK':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_arm_R_fk"), bone_name_trans)
    elif self.arm_right_stitch_enum == 'INVERSEK':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_arm_R_ik"), bone_name_trans)
    elif self.arm_right_stitch_enum == 'BOTH':
        inner_batch_dup_swap_stitches(rig_obj, stitchdata_concat_4(stitch_datapack.get("blist_dup_swap_stitch_arm_R_fk"), stitch_datapack.get("blist_dup_swap_stitch_arm_R_ik")), bone_name_trans)

    # LEG LEFT
    if self.leg_left_stitch_enum == 'FORWARDK':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_leg_L_fk"), bone_name_trans)
    elif self.leg_left_stitch_enum == 'INVERSEK':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_leg_L_ik"), bone_name_trans)
    elif self.leg_left_stitch_enum == 'BOTH':
        inner_batch_dup_swap_stitches(rig_obj, stitchdata_concat_4(stitch_datapack.get("blist_dup_swap_stitch_leg_L_fk"), stitch_datapack.get("blist_dup_swap_stitch_leg_L_ik")), bone_name_trans)

    # LEG RIGHT
    if self.leg_right_stitch_enum == 'FORWARDK':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_leg_R_fk"), bone_name_trans)
    elif self.leg_right_stitch_enum == 'INVERSEK':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_leg_R_ik"), bone_name_trans)
    elif self.leg_right_stitch_enum == 'BOTH':
        inner_batch_dup_swap_stitches(rig_obj, stitchdata_concat_4(stitch_datapack.get("blist_dup_swap_stitch_leg_R_fk"), stitch_datapack.get("blist_dup_swap_stitch_leg_R_ik")), bone_name_trans)

    # FINGERS LEFT
    if self.fingers_left_stitch_enum == 'YES':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_fingers_L"), bone_name_trans)
    # FINGERS RIGHT
    if self.fingers_right_stitch_enum == 'YES':
        inner_batch_dup_swap_stitches(rig_obj, stitch_datapack.get("blist_dup_swap_stitch_fingers_R"), bone_name_trans)

def inner_batch_dup_swap_stitches(rig_obj, stitch_list, bone_name_trans):
    if stitch_list is not None:
        for bone_to_dup, ref_bone, dist_on_dup, dist_on_ref in stitch_list:
            stitch_dup_swap(rig_obj, bone_to_dup, ref_bone, dist_on_dup, dist_on_ref, bone_name_trans)

def stitch_dup_swap(rig_obj, bone_to_dup, ref_bone, dist_on_dup, dist_on_ref, bone_name_trans):
    bone_to_dup_trans = bone_name_trans.get(bone_to_dup)
    ref_bone_trans = bone_name_trans.get(ref_bone)
    if bone_to_dup_trans is None or ref_bone_trans is None:
        return

    # set the parenting type to offset (connect=False), to prevent geometry being warped when re-parented
    rig_obj.data.edit_bones[bone_to_dup_trans].use_connect = False
    rig_obj.data.edit_bones[ref_bone_trans].use_connect = False

    t_vec = get_translation_vec(rig_obj.data.edit_bones[bone_to_dup_trans], rig_obj.data.edit_bones[ref_bone_trans], dist_on_dup, dist_on_ref)

    # duplicate bone
    new_bone = rig_obj.data.edit_bones.new(rig_obj.data.edit_bones[bone_to_dup_trans].name)
    new_bone.head.x = rig_obj.data.edit_bones[bone_to_dup_trans].head.x + t_vec[0]
    new_bone.head.y = rig_obj.data.edit_bones[bone_to_dup_trans].head.y + t_vec[1]
    new_bone.head.z = rig_obj.data.edit_bones[bone_to_dup_trans].head.z + t_vec[2]
    new_bone.tail.x = rig_obj.data.edit_bones[bone_to_dup_trans].tail.x + t_vec[0]
    new_bone.tail.y = rig_obj.data.edit_bones[bone_to_dup_trans].tail.y + t_vec[1]
    new_bone.tail.z = rig_obj.data.edit_bones[bone_to_dup_trans].tail.z + t_vec[2]
    new_bone.roll = rig_obj.data.edit_bones[bone_to_dup_trans].roll
    # swap new bone for ref_bone
    new_bone.parent = rig_obj.data.edit_bones[ref_bone_trans].parent
    rig_obj.data.edit_bones[ref_bone_trans].parent = new_bone

    # need to make copy of new_bone.name because of mode_set change,
    # somehow cannot access new_bone.name in POSE mode
    new_bone_name = new_bone.name

    bpy.ops.object.mode_set(mode='POSE')

    # new bone will copy rotation from bone_to_dup
    crc = rig_obj.pose.bones[new_bone_name].constraints.new('COPY_ROTATION')
    crc.target = rig_obj
    crc.subtarget = bone_to_dup_trans
    crc.target_space = 'LOCAL'
    crc.owner_space = 'LOCAL'
    crc.use_offset = True
    # new bone will also copy location from bone_to_dup (user can turn off / remove if needed)
    clc = rig_obj.pose.bones[new_bone_name].constraints.new('COPY_LOCATION')
    clc.target = rig_obj
    clc.subtarget = bone_to_dup_trans
    clc.target_space = 'LOCAL'
    clc.owner_space = 'LOCAL'
    clc.use_offset = True

    bpy.ops.object.mode_set(mode='EDIT')

def batch_do_move_bones(self, rig_obj, stitch_datapack, bone_name_trans):
    # TORSO
    if self.torso_stitch_enum == 'YES':
        inner_batch_do_move(rig_obj, stitch_datapack.get("blist_move_torso"), bone_name_trans)

    # ARM LEFT
    if self.arm_left_stitch_enum == 'FORWARDK':
        inner_batch_do_move(rig_obj, stitch_datapack.get("blist_move_arm_L_fk"), bone_name_trans)
    elif self.arm_left_stitch_enum == 'INVERSEK':
        inner_batch_do_move(rig_obj, stitch_datapack.get("blist_move_arm_L_ik"), bone_name_trans)
    elif self.arm_left_stitch_enum == 'BOTH':
        inner_batch_do_move(rig_obj, stitchdata_concat_3(stitch_datapack.get("blist_move_arm_L_fk"), stitch_datapack.get("blist_move_arm_L_ik")), bone_name_trans)

    # ARM RIGHT
    if self.arm_right_stitch_enum == 'FORWARDK':
        inner_batch_do_move(rig_obj, stitch_datapack.get("blist_move_arm_R_fk"), bone_name_trans)
    elif self.arm_right_stitch_enum == 'INVERSEK':
        inner_batch_do_move(rig_obj, stitch_datapack.get("blist_move_arm_R_ik"), bone_name_trans)
    elif self.arm_right_stitch_enum == 'BOTH':
        inner_batch_do_move(rig_obj, stitchdata_concat_3(stitch_datapack.get("blist_move_arm_R_fk"), stitch_datapack.get("blist_move_arm_R_ik")), bone_name_trans)

    # LEG LEFT
    if self.leg_left_stitch_enum == 'FORWARDK':
        inner_batch_do_move(rig_obj, stitch_datapack.get("blist_move_leg_L_fk"), bone_name_trans)
    elif self.leg_left_stitch_enum == 'INVERSEK':
        inner_batch_do_move(rig_obj, stitch_datapack.get("blist_move_leg_L_ik"), bone_name_trans)
    elif self.leg_left_stitch_enum == 'BOTH':
        inner_batch_do_move(rig_obj, stitchdata_concat_3(stitch_datapack.get("blist_move_leg_L_fk"), stitch_datapack.get("blist_move_leg_L_ik")), bone_name_trans)

    # LEG right
    if self.leg_right_stitch_enum == 'FORWARDK':
        inner_batch_do_move(rig_obj, stitch_datapack.get("blist_move_leg_R_fk"), bone_name_trans)
    elif self.leg_right_stitch_enum == 'INVERSEK':
        inner_batch_do_move(rig_obj, stitch_datapack.get("blist_move_leg_R_ik"), bone_name_trans)
    elif self.leg_right_stitch_enum == 'BOTH':
        inner_batch_do_move(rig_obj, stitchdata_concat_3(stitch_datapack.get("blist_move_leg_R_fk"), stitch_datapack.get("blist_move_leg_R_ik")), bone_name_trans)

def inner_batch_do_move(rig_obj, stitch_list, bone_name_trans):
    if stitch_list is not None:
        for bone_to_move, ref_bone, dist_on_move, dist_on_ref in stitch_list:
            do_move_bone(rig_obj, bone_to_move, ref_bone, dist_on_move, dist_on_ref, bone_name_trans)

def do_move_bone(rig_obj, bone_to_move, ref_bone, dist_on_move, dist_on_ref, bone_name_trans):
    bone_to_move_trans = bone_name_trans.get(bone_to_move)
    ref_bone_trans = bone_name_trans.get(ref_bone)
    if bone_to_move_trans is None or ref_bone_trans is None:
        return

    # set parenting type to Offset to prevent warping when moving bone
    rig_obj.data.edit_bones[bone_to_move_trans].use_connect = False

    t_vec = get_translation_vec(rig_obj.data.edit_bones[bone_to_move_trans], rig_obj.data.edit_bones[ref_bone_trans], dist_on_move, dist_on_ref)

    rig_obj.data.edit_bones[bone_to_move_trans].head.x += t_vec[0]
    rig_obj.data.edit_bones[bone_to_move_trans].head.y += t_vec[1]
    rig_obj.data.edit_bones[bone_to_move_trans].head.z += t_vec[2]
    rig_obj.data.edit_bones[bone_to_move_trans].tail.x += t_vec[0]
    rig_obj.data.edit_bones[bone_to_move_trans].tail.y += t_vec[1]
    rig_obj.data.edit_bones[bone_to_move_trans].tail.z += t_vec[2]

def batch_do_set_parents(self, rig_obj, stitch_datapack, bone_name_trans):
    # TORSO
    if self.torso_stitch_enum == 'YES':
        inner_batch_do_set_parent(rig_obj, stitch_datapack.get("blist_setparent_torso"), bone_name_trans)

    # ARM LEFT
    if self.arm_left_stitch_enum == 'FORWARDK':
        inner_batch_do_set_parent(rig_obj, stitch_datapack.get("blist_setparent_arm_L_fk"), bone_name_trans)
    elif self.arm_left_stitch_enum == 'INVERSEK':
        inner_batch_do_set_parent(rig_obj, stitch_datapack.get("blist_setparent_arm_L_ik"), bone_name_trans)
    elif self.arm_left_stitch_enum == 'BOTH':
        inner_batch_do_set_parent(rig_obj, stitchdata_concat_4(stitch_datapack.get("blist_setparent_arm_L_fk"), stitch_datapack.get("blist_setparent_arm_L_ik")), bone_name_trans)

    # ARM RIGHT
    if self.arm_right_stitch_enum == 'FORWARDK':
        inner_batch_do_set_parent(rig_obj, stitch_datapack.get("blist_setparent_arm_R_fk"), bone_name_trans)
    elif self.arm_right_stitch_enum == 'INVERSEK':
        inner_batch_do_set_parent(rig_obj, stitch_datapack.get("blist_setparent_arm_R_ik"), bone_name_trans)
    elif self.arm_right_stitch_enum == 'BOTH':
        inner_batch_do_set_parent(rig_obj, stitchdata_concat_4(stitch_datapack.get("blist_setparent_arm_R_fk"), stitch_datapack.get("blist_setparent_arm_R_ik")), bone_name_trans)

    # LEG LEFT
    if self.leg_left_stitch_enum == 'FORWARDK':
        inner_batch_do_set_parent(rig_obj, stitch_datapack.get("blist_setparent_leg_L_fk"), bone_name_trans)
    elif self.leg_left_stitch_enum == 'INVERSEK':
        inner_batch_do_set_parent(rig_obj, stitch_datapack.get("blist_setparent_leg_L_ik"), bone_name_trans)
    elif self.leg_left_stitch_enum == 'BOTH':
        inner_batch_do_set_parent(rig_obj, stitchdata_concat_4(stitch_datapack.get("blist_setparent_leg_L_fk"), stitch_datapack.get("blist_setparent_leg_L_ik")), bone_name_trans)

    # LEG RIGHT
    if self.leg_right_stitch_enum == 'FORWARDK':
        inner_batch_do_set_parent(rig_obj, stitch_datapack.get("blist_setparent_leg_R_fk"), bone_name_trans)
    elif self.leg_right_stitch_enum == 'INVERSEK':
        inner_batch_do_set_parent(rig_obj, stitch_datapack.get("blist_setparent_leg_R_ik"), bone_name_trans)
    elif self.leg_right_stitch_enum == 'BOTH':
        inner_batch_do_set_parent(rig_obj, stitchdata_concat_4(stitch_datapack.get("blist_setparent_leg_R_fk"), stitch_datapack.get("blist_setparent_leg_R_ik")), bone_name_trans)

def inner_batch_do_set_parent(rig_obj, stitch_list, bone_name_trans):
    if stitch_list is not None:
        for stitch_from, stitch_to in stitch_list:
            stitch_set_parent_bone(rig_obj, stitch_from, stitch_to, bone_name_trans)

def stitch_set_parent_bone(rig_obj, stitch_from, stitch_to, bone_name_trans):
    stitch_from_trans = bone_name_trans.get(stitch_from)
    stitch_to_trans = bone_name_trans.get(stitch_to)
    if stitch_from_trans is None or stitch_to_trans is None:
        return

    # either bone can be warped by the re-parenting, so set parent type to Offset for both
    rig_obj.data.edit_bones[stitch_from_trans].use_connect = False
    rig_obj.data.edit_bones[stitch_to_trans].use_connect = False

    rig_obj.data.edit_bones[stitch_from_trans].parent = rig_obj.data.edit_bones[stitch_to_trans]

def detect_and_bridge_rigs(self, mhx_rig_obj, other_rig_obj):
    # destination rig type
    mhx_rig_type = "import_mhx"

    # get source rig type, automatically detecting as needed
    if self.src_rig_type_enum == 'I_MIXAMO_NATIVE_FBX':
        other_rig_type = "mixamo_native_fbx"
    elif self.src_rig_type_enum == 'I_MAKEHUMAN_CMU_MB':
        other_rig_type = "makehuman_cmu_mb"
    else:
        # auto-detect is last option, if nothing else matched
        other_rig_type = detect_rig_type(other_rig_obj)

    mhx_rig_bone_names = []
    for bone in mhx_rig_obj.data.bones:
        mhx_rig_bone_names.append(bone.name)
    other_rig_bone_names = []
    for bone in other_rig_obj.data.bones:
        other_rig_bone_names.append(bone.name)
    bone_name_trans = get_bone_name_translations(amh2b_rig_type_bone_names.get(mhx_rig_type), mhx_rig_bone_names, "")
    extra_name_trans = get_bone_name_translations(amh2b_rig_type_bone_names.get(other_rig_type), other_rig_bone_names, "")
    bone_name_trans.update(extra_name_trans)

    do_bridge_rigs(self, mhx_rig_obj, mhx_rig_type, other_rig_obj, other_rig_type, bone_name_trans)

# compare bone names to detect rig type
def detect_rig_type(given_rig):
    # create list of all bone names in given rig
    given_bone_names = []
    for bone in given_rig.data.bones:
        given_bone_names.append(bone.name)

    # find a rig type with matching bone names
    for test_typename, test_bone_names in amh2b_rig_type_bone_names.items():
        if get_bone_name_match_count(test_bone_names, given_bone_names) >= amh2b_min_bones_for_rig_match:
            return test_typename

    return ""

def get_bone_name_translations(bone_name_list_A, bone_name_list_B, postfix):
    trans = {}
    for bname in bone_name_list_A:
        foundNames = fnmatch.filter(bone_name_list_B, bname)
        if foundNames is not None and len(foundNames) > 0:
            trans[bname + postfix] = foundNames[0] + postfix
    return trans

# Find number of matches between list A and list B,
# where we are searching for A (which can include wildcards in the strings) within B.
def get_bone_name_match_count(bone_name_list_A, bone_name_list_B):
    m = 0   # zero matches at start
    # find matching bone names, names with wildcards allowed
    for bname in bone_name_list_A:
        if fnmatch.filter(bone_name_list_B, bname):
            m = m + 1
    return m

def do_bone_woven(self, dest_rig_obj, src_rig_obj):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    detect_and_bridge_rigs(self, dest_rig_obj, src_rig_obj)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_BoneWoven(AMH2B_BoneWovenInner, bpy.types.Operator):
    """Join two rigs, with bone stitching, to re-target MHX rig to another rig.\nSelect animated rig first and select MHX rig last, then use this function"""
    bl_idname = "amh2b.arm_bone_woven"
    bl_label = "Bone Woven"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "src_rig_type_enum")
        layout.prop(self, "torso_stitch_enum")
        layout.prop(self, "arm_left_stitch_enum")
        layout.prop(self, "arm_right_stitch_enum")
        layout.prop(self, "leg_left_stitch_enum")
        layout.prop(self, "leg_right_stitch_enum")
        layout.prop(self, "fingers_left_stitch_enum")
        layout.prop(self, "fingers_right_stitch_enum")

    def execute(self, context):
        act_ob = context.active_object
        sel_obs = context.selected_objects
        if act_ob is None or len(sel_obs) != 2 or sel_obs[0].type != 'ARMATURE' or sel_obs[1].type != 'ARMATURE':
            self.report({'ERROR'}, "Select exactly 2 ARMATURES and try again")
            return {'CANCELLED'}

        dest_rig_obj = act_ob
        src_rig_obj = None
        if sel_obs[0] != act_ob:
            src_rig_obj = sel_obs[0]
        else:
            src_rig_obj = sel_obs[1]

        do_bone_woven(self, dest_rig_obj, src_rig_obj)

        return {'FINISHED'}

#####################################################
#     Lucky
# One button to do all the work, or at least as much as possible, i.e.
# Automatically apply location/rotation/scale to animated armature,
# repose MHX armature and it"s parented objects (e.g. clothes, hair),
# apply Bone Woven.
#
#   Instructions for use:
# Select all meshes attached to the MHX Armature, and the Animated Armature, and the MHX Armature.
# The MHX Armature must be selected last so that it is the Active Object.

def do_lucky(self, mhx_arm_obj, other_armature_obj, sel_obj_list):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # since MHX armature is already the active object, do repose first
    if self.repose_rig_enum == 'YES':
        do_bridge_repose_rig(mhx_arm_obj, sel_obj_list)

    # de-select all objects
    bpy.ops.object.select_all(action='DESELECT')

    # select secondary armature (the animated armature), and make it the active object
    select_object(other_armature_obj)
    set_active_object(other_armature_obj)

    # use Blender to apply location and rotation to animated armature
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    # use custom apply scale to animated armature
    do_apply_scale(other_armature_obj)

    # other_armature_obj will still be selected and the active_object, so just add the MHX armature
    # to the selected list and make it the active object
    select_object(mhx_arm_obj)
    set_active_object(mhx_arm_obj)

    # do bone woven
    do_bone_woven(self, mhx_arm_obj, other_armature_obj)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

# TODO: Use BoneWoven as the base class instead of Operator,
# to get rid of doubling of code for user options input.
class AMH2B_Lucky(AMH2B_LuckyInner, bpy.types.Operator):
    """Given user selected MHX armature, animated source armature, and objects attached to MHX armature: do RePose, then Apply Scale, then BoneWoven: so the result is a correctly animated MHX armature - with working finger rig, face rig, etc"""
    bl_idname = "amh2b.arm_lucky"
    bl_label = "Lucky"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "repose_rig_enum")
        layout.prop(self, "src_rig_type_enum")
        layout.prop(self, "torso_stitch_enum")
        layout.prop(self, "arm_left_stitch_enum")
        layout.prop(self, "arm_right_stitch_enum")
        layout.prop(self, "leg_left_stitch_enum")
        layout.prop(self, "leg_right_stitch_enum")
        layout.prop(self, "fingers_left_stitch_enum")
        layout.prop(self, "fingers_right_stitch_enum")

    def execute(self, context):
        mhx_arm_obj = context.active_object

        # quit if no MHX rig selected or active object is wrong type
        if mhx_arm_obj is None or mhx_arm_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}

        # get the animated armature (other_armature_obj) from the list of selected objects
        # (other_armature_obj will be joined to the MHX armature)
        other_armature_obj = None
        for ob in context.selected_objects:
            if ob.name != mhx_arm_obj.name:
                if ob.type == 'ARMATURE':
                    other_armature_obj = ob
                    break

        # quit if no secondary armature is selected
        if other_armature_obj == None:
            self.report({'ERROR'}, "Could not find other armature to join with MHX armature")
            return {'CANCELLED'}

        do_lucky(self, mhx_arm_obj, other_armature_obj, context.selected_objects)
        return {'FINISHED'}

def do_toggle_preserve_volume(new_state, sel_obj_list):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    for ob in sel_obj_list:
        if ob.type != 'MESH':
            continue
        for mod in ob.modifiers:
            if mod.type == 'ARMATURE':
                mod.use_deform_preserve_volume = new_state

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_EnableModPreserveVolume(bpy.types.Operator):
    """Enable 'Preserve Volume' in all Armature modifiers attached to all selected MESH type objects"""
    bl_idname = "amh2b.arm_enable_preserve_volume"
    bl_label = "Enable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_toggle_preserve_volume(True, context.selected_objects)
        return {'FINISHED'}

class AMH2B_DisableModPreserveVolume(bpy.types.Operator):
    """Disable 'Preserve Volume' in all Armature modifiers attached to all selected MESH type objects"""
    bl_idname = "amh2b.arm_disable_preserve_volume"
    bl_label = "Disable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_toggle_preserve_volume(False, context.selected_objects)
        return {'FINISHED'}

def get_generic_bone_name(bone_name, generic_prefix):
    if bone_name.rfind(":") != -1:
        return generic_prefix + bone_name[ bone_name.rfind(":") : len(bone_name) ]
    else:
        return generic_prefix + ":" + bone_name

def rename_bones_generic(new_generic_prefix, include_mhx, rig_obj):
    mhx_bone_names = amh2b_rig_type_bone_names["import_mhx"]

    for ebone in rig_obj.data.edit_bones.data.bones:
        old_name = ebone.name
        if not include_mhx and old_name in mhx_bone_names:
            continue

        # change name of bone
        ebone.name = get_generic_bone_name(old_name, new_generic_prefix)

def do_rename_generic(new_generic_prefix, include_mhx, sel_obj_list):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    for ob in sel_obj_list:
        if ob.type != 'ARMATURE':
            continue

        rename_bones_generic(new_generic_prefix, include_mhx, ob)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_RenameGeneric(bpy.types.Operator):
    """Rename armature bones to match the format 'aaaa:bbbb', where 'aaaa' is the generic prefix"""
    bl_idname = "amh2b.arm_rename_generic"
    bl_label = "Rename Generic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_rename_generic(context.scene.Amh2bPropArmGenericPrefix, context.scene.Amh2bPropArmGenericMHX, context.selected_objects)
        return {'FINISHED'}

def get_non_generic_bone_name(bone_name):
    if bone_name.rfind(":") != -1:
        return bone_name[ bone_name.rfind(":")+1 : len(bone_name) ]
    else:
        return bone_name

def un_name_bones_generic(include_mhx, rig_obj):
    mhx_bone_names = amh2b_rig_type_bone_names["import_mhx"]

    for ebone in rig_obj.data.edit_bones.data.bones:
        old_name = ebone.name
        if not include_mhx and old_name in mhx_bone_names:
            continue

        # change name of bone, if needed
        new_name = get_non_generic_bone_name(old_name)
        if new_name != old_name:
            ebone.name = new_name

def do_un_name_generic(include_mhx, sel_obj_list):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    for ob in sel_obj_list:
        if ob.type != 'ARMATURE':
            continue

        un_name_bones_generic(include_mhx, ob)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_UnNameGeneric(bpy.types.Operator):
    """Rename bones to remove any formating like 'aaaa:bbbb', where 'aaaa' is removed and the bones name becomes 'bbbb'"""
    bl_idname = "amh2b.arm_un_name_generic"
    bl_label = "Un-name Generic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_un_name_generic(context.scene.Amh2bPropArmGenericMHX, context.selected_objects)
        return {'FINISHED'}
