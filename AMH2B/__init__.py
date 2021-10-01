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
#   Blender 2.xx Addon (tested and works with Blender 2.79b, 2.83, 2.93)
# A set of tools to automate the process of shading/texturing, and animating MakeHuman data imported in Blender.

bl_info = {
    "name": "Automate MakeHuman 2 Blender (AMH2B)",
    "description": "Automate process of importing and animating MakeHuman models.",
    "author": "Dave",
    "version": (1, 1, 9),
    "blender": (2, 80, 0),
    "location": "View 3D &gt; Tools &gt; AMH2B",
    "wiki_url": "https://github.com/DreamSpoon/AMH2B#readme",
    "category": "Import MakeHuman Automation",
}

import bpy
import os
import fnmatch
import numpy
import csv

from bpy.types import Operator

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

from .imp_items import *
from .imp_strings import *

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
amh2b_min_bones_for_rig_match = 10  # 10 is estimate, todo: check estimate


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

    tVec = get_translation_vec(rig_obj.data.edit_bones[bone_to_dup_trans], rig_obj.data.edit_bones[ref_bone_trans], dist_on_dup, dist_on_ref)

    # duplicate bone
    new_bone = rig_obj.data.edit_bones.new(rig_obj.data.edit_bones[bone_to_dup_trans].name)
    new_bone.head.x = rig_obj.data.edit_bones[bone_to_dup_trans].head.x + tVec[0]
    new_bone.head.y = rig_obj.data.edit_bones[bone_to_dup_trans].head.y + tVec[1]
    new_bone.head.z = rig_obj.data.edit_bones[bone_to_dup_trans].head.z + tVec[2]
    new_bone.tail.x = rig_obj.data.edit_bones[bone_to_dup_trans].tail.x + tVec[0]
    new_bone.tail.y = rig_obj.data.edit_bones[bone_to_dup_trans].tail.y + tVec[1]
    new_bone.tail.z = rig_obj.data.edit_bones[bone_to_dup_trans].tail.z + tVec[2]
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

    tVec = get_translation_vec(rig_obj.data.edit_bones[bone_to_move_trans], rig_obj.data.edit_bones[ref_bone_trans], dist_on_move, dist_on_ref)

    rig_obj.data.edit_bones[bone_to_move_trans].head.x += tVec[0]
    rig_obj.data.edit_bones[bone_to_move_trans].head.y += tVec[1]
    rig_obj.data.edit_bones[bone_to_move_trans].head.z += tVec[2]
    rig_obj.data.edit_bones[bone_to_move_trans].tail.x += tVec[0]
    rig_obj.data.edit_bones[bone_to_move_trans].tail.y += tVec[1]
    rig_obj.data.edit_bones[bone_to_move_trans].tail.z += tVec[2]


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


def do_bone_woven(self):
    print("boneWoven() begin.")
    selection_list = bpy.context.selected_objects
    if bpy.context.active_object is None or len(selection_list) < 1:
        print("No active object or selection is empty, no Bone Woven.")
        return {'FINISHED'}
    if not bpy.context.active_object in selection_list:
        print("Active object is not in selection list, no Bone Woven.")
        return {'FINISHED'}

    dest_rig_obj = bpy.context.active_object
    src_rig_obj = None
    # the Active Object must be the imported MHX2 rig (not animated - should not be animated, anyway...)
    # the other selected object must be the rig with the animation
    for i in selection_list:
        if i != bpy.context.active_object:
            src_rig_obj = i

    # fail if did not get two ARMATURE type objects
    if src_rig_obj is None:
        print("Only one object selected, but two are needed. No Bone Woven.")
        return {'FINISHED'}
    if dest_rig_obj.type != 'ARMATURE':
        print("Bone Woven failed because active object " + dest_rig_obj.name + " is not ARMATURE type.")
        return {'FINISHED'}
    if src_rig_obj.type != 'ARMATURE':
        print("Bone Woven failed because selected object " + src_rig_obj.name + " is not ARMATURE type.")
        return {'FINISHED'}

    detect_and_bridge_rigs(self, dest_rig_obj, src_rig_obj)
    print("boneWoven() end.")


class AMH2B_BoneWoven(AMH2B_BoneWovenInner, bpy.types.Operator):
    """MHX2 Rig to Rig Animation Bridge"""
    bl_idname = "amh2b.bone_woven"
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
        do_bone_woven(self)

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Swap Materials from Other Blend File
# Automate materials dictionary material swapping with a simple method:
#   1) User chooses file with source materials.
#   2) Materials are appended "blindly", by trimming names of materials on selected objects
#      and trying to append trimmed name materials from the blend file chosen by the user.

# Returns True if material was successfully appended.
# Checks if the material already exists in this file, if it does exist then rename the
# current material, and then append the new material.
def swapmat_append_from_file(mat_filepath, mat_name):
    # path inside of file (i.e. like opening the "Append" window; see Action, Armature, Brush, Camera, ...)
    inner_path = "Material"

    try:
        bpy.ops.wm.append(
            filepath=os.path.join(mat_filepath, inner_path, mat_name),
            directory=os.path.join(mat_filepath, inner_path),
            filename=mat_name
            )
    except:
        return False

    if bpy.data.materials.get(mat_name) is None:
        return False

    return True


# trim string up to, and including, the first ":" character, and return trimmed string
def get_swatch_name_for_MH_name(mh_name):
    # if name is in MH format then return trimmed name
    # (remove first third, up to the ":", and return the remaining two-thirds)
    if len(mh_name.split(":", -1)) == 3:
        return mh_name.split(":", 1)[1]
    # otherwise return original name
    else:
        return mh_name


def do_material_swaps(shaderswap_blendfile):
    mats_loaded_from_file = []

    # get list of objects currently selected and fix materials on all selected objects,
    # swapping to correct materials
    selection_list = bpy.context.selected_objects

    # do the material swaps for each selected object
    for obj in selection_list:
        # iterate over the material slots and check/swap the materials
        for mat_slot in obj.material_slots:
            swatch_mat_name = get_swatch_name_for_MH_name(mat_slot.material.name)

            # if material has already been loaded from file...
            if swatch_mat_name in mats_loaded_from_file:
                # swap material
                print("Swapping material on object " + obj.name + ", oldMat = " + obj.active_material.name + ", newMat = " + swatch_mat_name)
                mat_slot.material = bpy.data.materials[swatch_mat_name]
                continue

            # if "swap material" already exists, then rename it so that a
            # newer version can be loaded from library file
            test_swap_mat = bpy.data.materials.get(swatch_mat_name)
            if test_swap_mat is not None:
                old_name = test_swap_mat.name
                test_swap_mat.name = "A1:" + old_name

            # if cannot load material from file...
            if not swapmat_append_from_file(shaderswap_blendfile, swatch_mat_name):
                # if rename occurred, then undo rename
                if test_swap_mat is not None:
                    test_swap_mat.name = old_name
                continue

            # include the newly loaded material in the list of loaded materials
            mats_loaded_from_file.append(swatch_mat_name)

            # swap material
            print("Swapping material on object " + obj.name + ", oldMat = " + obj.active_material.name + ", newMat = " + swatch_mat_name)
            mat_slot.material = bpy.data.materials[swatch_mat_name]


class AMH2B_SwapMaterials(AMH2B_SwapMaterialsInner, Operator, ImportHelper):
    """Swap Materials from Source Blend File"""
    bl_idname = "amh2b.swap_materials"
    bl_label = "Swap Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        do_material_swaps(self.filepath)
        return {'FINISHED'}


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Apply Scale
# Apply scale to armature (this is only needed for armature scale apply),
# and adjust it"s bone location animation f-curve values to match the scaling.
# If this operation is not done, then the bones that have changing location values
# will appear to move incorrectly.
def do_apply_scale():
    if bpy.context.active_object is None:
        print("do_apply_scale() error: Active Object is None, should have an object selected as Active Object.")
        return
    if bpy.context.active_object.type != 'ARMATURE':
        print("do_apply_scale() error: Active Object is not ARMATURE type.")
        return

    # keep copy of old scale values
    old_scale = bpy.context.active_object.scale.copy()

    # do not apply scale if scale is already 1.0 in all dimensions!
    if old_scale.x == 1 and old_scale.y == 1 and old_scale.z == 1:
        print("do_apply_scale() avoided, active_object scale is already 1 in all dimensions.")
        return

    bpy.ops.object.mode_set(mode='OBJECT')

    print("do_apply_scale() to rig = " + bpy.context.active_object.name + "; old scale = " + str(old_scale))
    # apply scale to active object
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # scale only the location f-curves on active object
    obj = bpy.context.active_object
    if obj is None:
        return
    action = obj.animation_data.action
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


class AMH2B_ApplyScale(bpy.types.Operator):
    """Apply Scale to Rig without corrupting the bone pose data (e.g. location)."""
    bl_idname = "amh2b.apply_scale"
    bl_label = "Apply Scale to Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_apply_scale()
        return {'FINISHED'}


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Bridge Re-Pose Rig
# Re-pose original rig (which has shape keys, hence this work-around) by way of a duplicate of original
# that moves mesh to desired pose, then original rig is pose-apply"ed and takes over from duplicate rig.
# Basically, a duplicate rig moves the underlying mesh to the place where the reposed original rig will be.

# duplicate selected objects
def dup_selected():
    obj_to_dup = bpy.context.active_object
    bpy.ops.object.duplicate({"object" : obj_to_dup, "selected_objects" : [obj_to_dup]}, linked=False)
    # return ref to newly duped object
    return bpy.context.active_object


def add_armature_to_objects(arm_obj, objs_list):
    for dest_obj in objs_list:
        if dest_obj != arm_obj and dest_obj.type != 'ARMATURE':
            add_armature_to_obj(arm_obj, dest_obj)


def add_armature_to_obj(arm_obj, dest_obj):
    # create ARMATURE modifier and set refs, etc.
    mod = dest_obj.modifiers.new("ReposeArmature", 'ARMATURE')
    if mod is None:
        print("do_repose_rig() error: Unable to add armature to object" + dest_obj.name)
        return
    mod.object = arm_obj
    mod.use_deform_preserve_volume = True
    # Move modifier to top of stack, because this armature needs to move the mesh before
    # any other modifications occur, to match the re-posed main armature.
    while dest_obj.modifiers.find(mod.name) != 0:
        bpy.ops.object.modifier_move_up({"object": dest_obj}, modifier=mod.name)


def do_repose_rig():
    if bpy.context.active_object is None:
        print("do_repose_rig() error: Active object is None, cannot Re-Pose MHX rig.")
        return

    old_3dview_mode = bpy.context.object.mode

    # copy ref to active object
    selection_active_obj = bpy.context.active_object

    # copy list of selected objects, minus the active object
    # (0 selected objects is allowed, because armature can be re-posed independently)
    selection_list = []
    for ob in bpy.context.selected_objects:
        if ob.name != selection_active_obj.name:
            selection_list.append(bpy.data.objects[ob.name])

    # de-select all objects
    bpy.ops.object.select_all(action='DESELECT')

    # select the old active_object in the 3D viewport
    select_object(selection_active_obj)
    # make it the active selected object
    set_active_object(selection_active_obj)

    # duplicate the original armature
    new_arm = dup_selected()
    # parent the duplicated armature to the original armature, to prevent mesh tearing if the armatures move apart
    new_arm.parent = selection_active_obj

    # add modifiers to the other selected objects, so the other selected objects will use the new armature
    add_armature_to_objects(new_arm, selection_list)

    # ensure original armature is selected
    select_object(selection_active_obj)
    # make original armature the active object
    set_active_object(selection_active_obj) # debug 1 (delete this comment, and not the code)

    bpy.ops.object.mode_set(mode='POSE')
    # apply pose to original armature
    bpy.ops.pose.armature_apply()
    bpy.ops.object.mode_set(mode=old_3dview_mode)


class AMH2B_BridgeRepose(bpy.types.Operator):
    """Use a "bridge rig" to move a shape-keyed mesh into position with a "re-posed armature" (i.e. where the pose was changed and then applied as rest pose)."""
    bl_idname = "amh2b.bridge_repose"
    bl_label = "Bridge Re-Pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_repose_rig()
        return {'FINISHED'}


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Ratchet Hold
#
#   Idea of script:
# Re-calculate location data for an object (typically armature), given:
#   1) A single "Empty" type object, that is parented to a part of the armature object
#        (i.e. parented to a bone in the armature object).
#   2) The location of the original object (armature) should be offset, and keyframed, to make the "Empty"
#      type object appear to be motionless.
#   TODO: Use a second empty, parented to the first, which can be offset (keyframed or with a constraint),
#         to indicate motionless relative to the second empty. Thus motionless to a moving observer is possible.
#
# Instructions to use the script:
# Select exactly two objects:
#   Object A - the parent object (typically armature)
#   Object B - the "Empty" type object, that is parented to A
# Run the script:
#   The script will do:
# 1) In the current frame, insert a location keyframe on object A.
# 2) Get the location of object B in the current frame.
# 3) Change to the next frame (increment frame).
# 4) Get the new location of object B, then calculate the offset to keep it motionless.
# 5) Apply location offset to object A, then insert location keyframe on A.
#
# Result:
# Two keyframes created on object A, such that object B appears motionless over the two frames.
# Repeat the operation a number of times to get an animation, e.g. of a person walking.

def do_ratchet():
    if len(bpy.context.selected_objects) != 2:
        print("do_ratchet() error: Cannot Ratchet Hold, need to have exactly two objects selected.")
        return

    bpy.ops.object.mode_set(mode='OBJECT')

    # copy ref to active object
    obj_to_ratchet = bpy.context.active_object
    if obj_to_ratchet is None:
        print("do_ratchet() error: Active object is None, but must be the object to re-keyframe.")
        return

    # get ref to other object (presumably an "Empty" type object), the not active object
    hold_onto_obj = bpy.context.selected_objects[0]
    if hold_onto_obj.name == obj_to_ratchet.name:
        hold_onto_obj = bpy.context.selected_objects[1]

    # insert location keyframes on object to ratchet at old location
    obj_to_ratchet.keyframe_insert(data_path="location")

    # save old location
    hold_obj_old_loc = hold_onto_obj.matrix_world.to_translation()
    # increment current frame
    bpy.context.scene.frame_set(bpy.context.scene.frame_current+1)
    # save new location
    hold_obj_new_loc = hold_onto_obj.matrix_world.to_translation()
    # Calculate offset (in world coordinate system) for moving object to ratchet,
    # such that hold onto object remains stationary.
    deltaMove = numpy.subtract(hold_obj_old_loc, hold_obj_new_loc)
    # do move in (world coordinate system)
    doTranslateGlobal(deltaMove)
    # insert location keyframes on object to ratchet at new location
    obj_to_ratchet.keyframe_insert(data_path="location")


class AMH2B_RatchetHold(bpy.types.Operator):
    """Keyframe the movement of a parent object so that a child object appears motionless; the parent object"s location is offset to keep the child object"s location stationary."""
    bl_idname = "amh2b.ratchet_hold"
    bl_label = "Ratchet Hold"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_ratchet()
        return {'FINISHED'}


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Lucky
#
#   Idea of script:
# One button to do all the work, or at least as much as possible, i.e.
# Automatically apply location/rotation/scale to animated armature,
# repose MHX armature and it"s parented objects (e.g. clothes, hair),
# apply Bone Woven.
#
#   Instructions for use:
# Use selects first:
#   
# Use selects last:
#   MHX Armature last.
#
# So that:
#   MHX Armature is the active_object, and
#   selected_objects includes all objects parented to the MHX armature, and
#   selected_objects includes the animated armature.

def do_lucky(self):
    # copy ref to active object, the MHX armature
    mhx_arm_obj = bpy.context.active_object

    # quit if no MHX rig selected or active object is wrong type
    if mhx_arm_obj is None or mhx_arm_obj.type != 'ARMATURE':
        print("do_lucky() error: Active object is None or is not ARMATURE type, cannot Re-Pose MHX rig")
        return

    # get the animated armature (other_armature_obj) from the list of selected objects
    # (other_armature_obj will be joined to the MHX armature)
    other_armature_obj = None
    for ob in bpy.context.selected_objects:
        if ob.name != mhx_arm_obj.name:
            if ob.type == 'ARMATURE':
                other_armature_obj = ob
                break

    # quit if no secondary armature is selected
    if other_armature_obj == None:
        print("do_lucky() error: : missing other armature to join to MHX armature.")
        return

    # since MHX armature is already the active object, do repose first
    if self.repose_rig_enum == 'YES':
        do_repose_rig()

    # de-select all objects
    bpy.ops.object.select_all(action='DESELECT')

    # select secondary armature (the animated armature), and make it the active object
    select_object(other_armature_obj)
    set_active_object(other_armature_obj)

    # use Blender to apply location and rotation to animated armature
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    # use custom apply scale to animated armature
    do_apply_scale()

    # other_armature_obj will still be selected and the active_object, so just add the MHX armature
    # to the selected list and make it the active object
    select_object(mhx_arm_obj)
    set_active_object(mhx_arm_obj)

    # do bone woven
    do_bone_woven(self)


# TODO: Use BoneWoven as the base class instead of Operator,
# to get rid of doubling of code for user options input.
class AMH2B_Lucky(AMH2B_LuckyInner, bpy.types.Operator):
    """Given user selected MHX armature, animated source armature, and objects attached to MHX armature: do RePose, then Apply Scale to Deltas, then BoneWoven: so the result is a correctly animated MHX armature - with working finger rig, face rig, etc."""
    bl_idname = "amh2b.lucky"
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
        do_lucky(self)
        return {'FINISHED'}


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Adjust Pose
#
#   Idea of script:
# Script rotations of bones to reduce time waste. Input is from TextBlock named 'Text', in CSV format.
# Get the rotations correct once, type it up as a CSV file, then use the script repeatedly.

def rotBone(rig_object, bone_name, axis_name, offset_deg):
    the_bone = rig_object.pose.bones.get(bone_name)
    if the_bone is None:
        return
    the_bone.bone.select = True
    doRotationGlobal(axis_name, offset_deg)
    the_bone.bone.select = False


def runOffsets(rig_obj, offsets, datablock_textname):
    rec_count = 0
    try:
        for of_bone_name, of_axis, of_deg in offsets:
            rotBone(rig_obj, of_bone_name.strip(), of_axis.strip(), float(of_deg))
            rec_count = rec_count+1

    except ValueError:
        print("adjust_pose() error: ValueError while parsing CSV record #" + str(rec_count) + " in text block: " + datablock_textname)



def getScriptedOffsets(datablock_textname):
    bl = bpy.data.texts.get(datablock_textname)
    if bl is None:
        return

    bl_str = bl.as_string()
    if bl_str == '':
        return

    csv_lines = csv.reader(bl_str.splitlines())
    return list(csv_lines)


def do_adjustPose(self):
    # get CSV user data text block and convert to array of offsets data
    offsets = getScriptedOffsets(bpy.context.scene.Amh2bPropTextBlockName)
    if offsets is None:
        return

    # copy ref to active object, the MHX armature
    mhx_arm_obj = bpy.context.active_object
    # quit if Active Object is None or not an armature
    if mhx_arm_obj is None:
        print("adjust_pose() error: Active object is None, cannot adjust pose.")
        return
    if mhx_arm_obj.type != 'ARMATURE':
        print("adjust_pose() error: Active object is not Armature type, cannot adjust pose.")
        return

    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='POSE')

    bpy.ops.pose.select_all(action='DESELECT')
    runOffsets(mhx_arm_obj, offsets, bpy.context.scene.Amh2bPropTextBlockName)

    bpy.ops.object.mode_set(mode=old_3dview_mode)


class AMH2B_AdjustPose(AMH2B_AdjustPoseInner, bpy.types.Operator):
    """Add to rotations of pose by way of CSV script in Blender's Text Editor. Default script name is Text"""
    bl_idname = "amh2b.adjust_pose"
    bl_label = "AdjustPose"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        do_adjustPose(self)
        return {'FINISHED'}


#####################################################


class AMH2B_P_Setup(bpy.types.Panel):
    bl_label = "AMH2B Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        scn = context.scene

        layout.separator()
        box = layout.box()
        box.label(text="Material")
        box.operator("amh2b.swap_materials")

        layout.separator()
        box = layout.box()
        box.label(text="Armature")
        box.operator("amh2b.adjust_pose")
        box.prop(scn, "Amh2bPropTextBlockName")
        box.operator("amh2b.apply_scale")
        box.operator("amh2b.bridge_repose")
        box.operator("amh2b.bone_woven")

        layout.separator()
        box = layout.box()
        box.label(text="Movement")
        box.operator("amh2b.ratchet_hold")

        layout.separator()
        box = layout.box()
        box.label(text="Multi-Function")
        box.operator("amh2b.lucky")


classes = [
    AMH2B_BoneWoven,
    AMH2B_SwapMaterials,
    AMH2B_ApplyScale,
    AMH2B_BridgeRepose,
    AMH2B_RatchetHold,
    AMH2B_Lucky,
    AMH2B_AdjustPose,
    AMH2B_P_Setup,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.Amh2bPropTextBlockName = StringProperty(name="Text Editor Script Name", description="Script data-block name in text editor", default="Text")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
