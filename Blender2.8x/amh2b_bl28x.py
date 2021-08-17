#     Automate MakeHuman 2 Blender (AMH2B)

bl_info = {
    'name': 'Automate MakeHuman 2 Blender',
    'blender': (2, 79, 0),
    'description': 'Automate process of importing MakeHuman models, and animating these models.',
    'category': 'Object',
}

import bpy
import os
import fnmatch
import numpy

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


#####################################################
#     Bone Woven
# Simplify the MakeHuman rig animation process re: Mixamo et al. via a bridge that connects
# imported animation rigs to imported MHX2 rigs - leaving face panel and visemes intact, while allowing
# for great functionality e.g. finger movements.
# In a perfect world, Blender and MakeHuman would work seamlessly with any and all motion capture data,
# and any motion capture sharing website (including body, facial, etc. rig).
# The real world includes problems with bone names, 'bone roll', vertex groups, etc.
# This addon bridges some real world gaps between different rigs.
# Basically, bones from Rig B (this could be a downloaded rig from a mocap sharing website, etc.)
# are mapped to Rig A so that Rig B acts like "marionettist" to the Rig A "marionette".
# Rig B controls Rig A, allowing the user to tweak the final animation by animating Rig A.
# Caveat: Rig A and Rig B should be in the same pose.
# Side-note: Ugly, But Works

amh2b_fk_ik_both_none_items = [
    ('BOTH', 'Both', '', 1),
    ('FORWARDK', 'FK', '', 2),
    ('INVERSEK', 'IK', '', 3),
    ('NONE', 'None', '', 4),
]
amh2b_src_rig_type_items = [
    ('I_AUTOMATIC', 'Automatic', '', 1),
    ('I_MIXAMO_NATIVE_FBX', 'Mixamo Native FBX', '', 2),
    ('I_MAKEHUMAN_CMU_MB', 'MakeHuman CMU MB', '', 3),
]
amh2b_yes_no_items = [
    ('YES', 'Yes', '', 1),
    ('NO', 'No', '', 2),
]

# minimum number of bones matching by string to justify matching rig found = true
amh2b_min_bones_for_rig_match = 10  # 10 is estimate, todo: check estimate

amh2b_rig_type_bone_names = {
    'makehuman_cmu_mb': ['Hips', 'LHipJoint', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase', 'LowerBack', 'Spine', 'Spine1', 'LeftShoulder', 'LeftArm', 'LeftForeArm','LeftHand', 'LThumb', 'LeftFingerBase', 'LeftHandFinger1', 'Neck', 'Neck1', 'Head', 'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand','RThumb', 'RightFingerBase', 'RightHandFinger1', 'RHipJoint', 'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase'],

    'mixamo_native_fbx': ['*:Hips', '*:Spine', '*:Spine1', '*:Spine2', '*:Neck', '*:Head','*:LeftShoulder', '*:LeftArm', '*:LeftForeArm', '*:LeftHand', '*:LeftHandThumb1', '*:LeftHandThumb2', '*:LeftHandThumb3', '*:LeftHandIndex1', '*:LeftHandIndex2', '*:LeftHandIndex3', '*:LeftHandMiddle1', '*:LeftHandMiddle2', '*:LeftHandMiddle3', '*:LeftHandRing1', '*:LeftHandRing2', '*:LeftHandRing3', '*:LeftHandPinky1', '*:LeftHandPinky2', '*:LeftHandPinky3', '*:RightShoulder', '*:RightArm', '*:RightForeArm', '*:RightHand', '*:RightHandThumb1', '*:RightHandThumb2', '*:RightHandThumb3', '*:RightHandIndex1', '*:RightHandIndex2', '*:RightHandIndex3', '*:RightHandMiddle1', '*:RightHandMiddle2', '*:RightHandMiddle3', '*:RightHandRing1', '*:RightHandRing2', '*:RightHandRing3', '*:RightHandPinky1', '*:RightHandPinky2', '*:RightHandPinky3', '*:LeftUpLeg', '*:LeftLeg', '*:LeftFoot', '*:LeftToeBase', '*:RightUpLeg', '*:RightLeg', '*:RightFoot', '*:RightToeBase'],

    'import_mhx': ['master', 'root', 'spine', 'spine-1', 'chest', 'DEF-serratus.L', 'DEF-serratus.R', 'DEF-pect.L', 'breast.L', 'DEF-breast.L', 'DEF-pect.R', 'breast.R', 'DEF-breast.R', 'chest-1', 'neck', 'neck-1', 'head', 'lolid.R', 'lolid.L', 'jaw', 'tongue_base', 'tongue_mid', 'tongue_tip', 'uplid.L', 'uplid.R', 'eyes', 'eye_parent.L', 'eye.L', 'DEF-eye.L', 'eye_parent.R', 'eye.R', 'DEF-eye.R', 'DEF-uplid.L', 'DEF-uplid.R', 'DEF-lolid.L', 'DEF-lolid.R', 'DEF-jaw', 'DEF-tongue_base', 'DEF-tongue_mid', 'DEF-tongue_tip', 'DEF-neck-1', 'DEF-head', 'clavicle.L', 'DEF-deltoid.L', 'shoulder01.L', 'arm_base.L', 'elbow.pt.ik.L', 'pectIk.L', 'scap-parent.R', 'DEF-scapula.R', 'scap-parent.L', 'DEF-scapula.L', 'clavicle.R', 'DEF-deltoid.R', 'pectIk.R', 'shoulder01.R', 'arm_base.R', 'elbow.pt.ik.R', 'DEF-sternum', 'DEF-clavicle.R', 'DEF-chest', 'DEF-chest-1', 'DEF-clavicle.L', 'DEF-neck', 'hips', 'pelvis.L', 'leg_base.L', 'DEF-hip.R', 'DEF-gluteus.L', 'DEF-hip.L', 'DEF-gluteus.R', 'pelvis.R', 'leg_base.R', 'arm_hinge.R', 'arm_socket.R', 'upper_arm.R','forearm.R', 'hand.R', 'palm_middle.R', 'f_middle.01.R', 'f_middle.02.R', 'f_middle.03.R', 'DEF-f_middle.02.R', 'DEF-f_middle.03.R', 'middle.R', 'thumb.01.R', 'thumb.02.R', 'thumb.03.R', 'DEF-thumb.03.R', 'thumb.R', 'DEF-thumb.02.R', 'palm_index.R', 'f_index.01.R', 'f_index.02.R', 'f_index.03.R', 'DEF-f_index.03.R', 'index.R', 'DEF-f_index.01.R', 'DEF-f_index.02.R', 'palm_pinky.R', 'f_pinky.01.R', 'f_pinky.02.R', 'f_pinky.03.R', 'pinky.R', 'palm_ring.R', 'f_ring.01.R', 'f_ring.02.R', 'f_ring.03.R', 'DEF-f_ring.03.R', 'DEF-f_ring.02.R', 'ring.R', 'DEF-palm_ring.R', 'DEF-f_ring.01.R', 'DEF-thumb.01.R', 'DEF-palm_middle.R', 'DEF-f_middle.01.R', 'DEF-palm_pinky.R', 'DEF-f_pinky.01.R', 'DEF-f_pinky.02.R', 'DEF-f_pinky.03.R', 'shoulderIk.R', 'serratusIk.R', 'DEF-elbow_fan.R', 'DEF-forearm.01.R', 'DEF-forearm.02.R', 'DEF-forearm.03.R', 'DEF-hand.R', 'DEF-palm_index.R', 'forearm_X120.R', 'upper_arm.fk.R', 'forearm.fk.R', 'hand.fk.R', 'upper_arm.ik.R', 'elbow.link.R', 'forearm.ik.R', 'DEF-upper_arm.R', 'leg_hinge.R', 'leg_socket.R','thigh.R', 'gluteusIk.R', 'DEF-knee_fan.R', 'hipIk.R', 'shin.R', 'foot.R', 'toe.R', 'DEF-shin.01.R', 'DEF-shin.02.R', 'DEF-shin.03.R', 'DEF-foot.R', 'DEF-toe.R', 'shin_X150.R', 'thigh.fk.R', 'shin.fk.R', 'foot.fk.R', 'heel.marker.R', 'ball.marker.R', 'toe.fk.R', 'toe.marker.R', 'thigh.ik.R', 'knee.link.R', 'shin.ik.R', 'DEF-thigh.R', 'thigh_X-90.R', 'leg_hinge.L', 'leg_socket.L', 'thigh.L', 'hipIk.L', 'DEF-knee_fan.L', 'gluteusIk.L', 'shin.L', 'foot.L', 'toe.L', 'DEF-shin.01.L', 'DEF-shin.02.L', 'DEF-shin.03.L', 'DEF-foot.L', 'DEF-toe.L', 'shin_X150.L','thigh.fk.L', 'shin.fk.L', 'foot.fk.L', 'heel.marker.L', 'ball.marker.L', 'toe.fk.L', 'toe.marker.L', 'thigh.ik.L', 'knee.link.L', 'shin.ik.L', 'DEF-thigh.L', 'thigh_X-90.L', 'arm_hinge.L', 'arm_socket.L', 'upper_arm.L', 'serratusIk.L', 'forearm.L', 'hand.L', 'palm_pinky.L', 'f_pinky.01.L', 'f_pinky.02.L', 'f_pinky.03.L', 'DEF-f_pinky.03.L', 'DEF-f_pinky.02.L', 'pinky.L', 'DEF-f_pinky.01.L', 'thumb.01.L', 'thumb.02.L', 'thumb.03.L', 'thumb.L', 'palm_index.L', 'f_index.01.L','f_index.02.L', 'f_index.03.L', 'DEF-f_index.03.L', 'index.L', 'DEF-f_index.01.L', 'DEF-f_index.02.L', 'palm_ring.L', 'f_ring.01.L', 'f_ring.02.L', 'f_ring.03.L', 'ring.L', 'DEF-f_ring.01.L', 'DEF-f_ring.02.L', 'DEF-f_ring.03.L', 'palm_middle.L', 'f_middle.01.L', 'f_middle.02.L', 'f_middle.03.L', 'DEF-f_middle.02.L', 'DEF-f_middle.03.L', 'middle.L', 'DEF-palm_middle.L', 'DEF-f_middle.01.L', 'DEF-thumb.01.L', 'DEF-thumb.02.L', 'DEF-thumb.03.L', 'shoulderIk.L', 'DEF-elbow_fan.L', 'DEF-forearm.01.L', 'DEF-forearm.02.L', 'DEF-forearm.03.L', 'DEF-hand.L', 'DEF-palm_pinky.L', 'DEF-palm_ring.L', 'DEF-palm_index.L', 'forearm_X120.L', 'upper_arm.fk.L', 'forearm.fk.L', 'hand.fk.L', 'upper_arm.ik.L', 'elbow.link.L', 'forearm.ik.L', 'DEF-upper_arm.L', 'DEF-spine', 'DEF-spine-1', 'DEF-hips', 'DEF-pelvis.R', 'DEF-pelvis.L', 'p_face', 'p_lo_lid.R', 'p_mouth_in.L', 'p_nose', 'p_lo_lip.R', 'p_lo_lid.L', 'p_cheek.R', 'p_tongue', 'p_brow_in.R', 'p_cheek.L', 'p_lo_lip_mid', 'p_face_display', 'p_mouth_out.L', 'p_up_lid.L', 'p_up_lid.R', 'p_mouth_out.R', 'p_up_lip.R', 'p_mouth_in.R', 'p_up_lip.L', 'p_brow_out.L', 'p_jaw', 'p_brow_mid', 'p_brow_out.R', 'p_brow_in.L', 'p_mouth_mid', 'p_lo_lip.L', 'p_up_lip_mid', 'gaze_parent', 'gaze', 'ankle.L', 'ankle.R', 'foot.ik.L', 'toe.rev.L', 'foot.rev.L', 'ankle.ik.L', 'knee.pt.ik.L', 'foot.pt.ik.L', 'foot.ik.R', 'toe.rev.R', 'foot.rev.R', 'foot.pt.ik.R', 'ankle.ik.R', 'knee.pt.ik.R', 'hand.ik.L', 'hand.ik.R'],
}

amh2b_rig_stitch_dest_list = {
    'import_mhx': {
        'makehuman_cmu_mb': {
            'blist_dup_swap_stitch_torso': [('Hips', 'root', 0, 0), ('LowerBack', 'spine', 0, 0), ('Spine', 'chest', 0, 0), ('Spine1', 'chest-1', 0, 0), ('Neck', 'neck', 0, 0), ('Neck1', 'neck-1', 0, 0), ('Head', 'head', 0, 0)],
            'blist_setparent_torso': [('Hips', 'master')],
            'blist_dup_swap_stitch_arm_L_fk': [('LeftArm', 'arm_base.L', 0.06, 0.35), ('LeftShoulder', 'clavicle.L', 0, 0), ('LeftForeArm', 'forearm.fk.L', 0, 0), ('LeftHand', 'hand.fk.L', 0, 0)],
            'blist_dup_swap_stitch_arm_R_fk': [('RightArm', 'arm_base.R', 0.06, 0.35), ('RightShoulder', 'clavicle.R', 0, 0), ('RightForeArm', 'forearm.fk.R', 0, 0), ('RightHand', 'hand.fk.R', 0, 0)],
            'blist_setparent_arm_L_ik': [('elbow.pt.ik.L', 'LeftForeArm'), ('elbow.link.L', 'LeftForeArm'), ('hand.ik.L', 'LeftHand')],
            'blist_setparent_arm_R_ik': [('elbow.pt.ik.R', 'RightForeArm'), ('elbow.link.R', 'RightForeArm'), ('hand.ik.R', 'RightHand')],
            'blist_dup_swap_stitch_leg_L_fk': [('LHipJoint', 'leg_socket.L', 0, 0), ('LeftUpLeg', 'thigh.fk.L', 0, 0), ('LeftLeg', 'shin.fk.L', 0, 0), ('LeftFoot', 'foot.fk.L', 0, 0), ('LeftToeBase', 'toe.fk.L', 0, 0)],
            'blist_dup_swap_stitch_leg_R_fk': [('RHipJoint', 'leg_socket.R', 0, 0), ('RightUpLeg', 'thigh.fk.R', 0, 0), ('RightLeg', 'shin.fk.R', 0, 0), ('RightFoot', 'foot.fk.R', 0, 0), ('RightToeBase', 'toe.fk.R', 0, 0)],
            'blist_setparent_leg_L_ik': [('knee.pt.ik.L', 'LeftLeg'), ('knee.link.L', 'LeftLeg'), ('foot.ik.L', 'LeftFoot')],
            'blist_setparent_leg_R_ik': [('knee.pt.ik.R', 'RightLeg'), ('knee.link.R', 'RightLeg'), ('foot.ik.R', 'RightFoot')],
        },
        'mixamo_native_fbx': {
            'blist_dup_swap_stitch_torso': [('*:Hips', 'root', 0, 0), ('*:Spine', 'spine-1', 0, 0), ('*:Spine1', 'chest', 0, 0), ('*:Spine2', 'chest-1', 0, 0), ('*:Neck', 'neck', 0, 0), ('*:Head', 'head', 0, 0)],
            'blist_setparent_torso': [('*:Hips', 'master')],
            'blist_dup_swap_stitch_arm_L_fk': [('*:LeftShoulder', 'clavicle.L', 0, 0), ('*:LeftArm', 'arm_base.L', 0.06, 0.35), ('*:LeftForeArm', 'forearm.fk.L', 0, 0), ('*:LeftHand', 'hand.fk.L', 0, 0)],
            'blist_dup_swap_stitch_arm_R_fk': [('*:RightShoulder', 'clavicle.R', 0, 0), ('*:RightArm', 'arm_base.R', 0.06, 0.35), ('*:RightForeArm', 'forearm.fk.R', 0, 0), ('*:RightHand', 'hand.fk.R', 0, 0)],
            'blist_setparent_arm_L_ik': [('hand.ik.L', '*:LeftHand'), ('elbow.pt.ik.L', '*:LeftForeArm'), ('elbow.link.L', '*:LeftForeArm')],
            'blist_setparent_arm_R_ik': [('hand.ik.R', '*:RightHand'), ('elbow.pt.ik.R', '*:RightForeArm'), ('elbow.link.R', '*:RightForeArm')],
            'blist_dup_swap_stitch_leg_L_fk': [('*:LeftUpLeg', 'thigh.fk.L', 0, 0), ('*:LeftLeg', 'shin.fk.L', 0, 0), ('*:LeftFoot', 'foot.fk.L', 0, 0), ('*:LeftToeBase', 'toe.fk.L', 0, 0)],
            'blist_dup_swap_stitch_leg_R_fk': [('*:RightUpLeg', 'thigh.fk.R', 0, 0), ('*:RightLeg', 'shin.fk.R', 0, 0), ('*:RightFoot', 'foot.fk.R', 0, 0), ('*:RightToeBase', 'toe.fk.R', 0, 0)],
            'blist_setparent_leg_L_ik': [('knee.pt.ik.L', '*:LeftLeg'), ('knee.link.L', '*:LeftLeg'), ('foot.ik.L', '*:LeftFoot')],
            'blist_setparent_leg_R_ik': [('knee.pt.ik.R', '*:RightLeg'), ('knee.link.R', '*:RightLeg'), ('foot.ik.R', '*:RightFoot')],
            'blist_dup_swap_stitch_fingers_L': [('*:LeftHandThumb1', 'thumb.01.L', 0, 0), ('*:LeftHandThumb2', 'thumb.02.L', 0, 0), ('*:LeftHandThumb3', 'thumb.03.L', 0, 0), ('*:LeftHandIndex1', 'f_index.01.L', 0, 0), ('*:LeftHandIndex2', 'f_index.02.L', 0, 0), ('*:LeftHandIndex3', 'f_index.03.L', 0, 0), ('*:LeftHandMiddle1', 'f_middle.01.L', 0, 0), ('*:LeftHandMiddle2', 'f_middle.02.L', 0, 0), ('*:LeftHandMiddle3', 'f_middle.03.L', 0, 0), ('*:LeftHandRing1', 'f_ring.01.L', 0, 0), ('*:LeftHandRing2', 'f_ring.02.L', 0, 0), ('*:LeftHandRing3', 'f_ring.03.L', 0, 0), ('*:LeftHandPinky1', 'f_pinky.01.L', 0, 0), ('*:LeftHandPinky2', 'f_pinky.02.L', 0, 0), ('*:LeftHandPinky3', 'f_pinky.03.L', 0, 0)],
            'blist_dup_swap_stitch_fingers_R': [('*:RightHandThumb1', 'thumb.01.R', 0, 0), ('*:RightHandThumb2', 'thumb.02.R', 0, 0), ('*:RightHandThumb3', 'thumb.03.R', 0, 0), ('*:RightHandIndex1', 'f_index.01.R', 0, 0), ('*:RightHandIndex2', 'f_index.02.R', 0, 0), ('*:RightHandIndex3', 'f_index.03.R', 0, 0), ('*:RightHandMiddle1', 'f_middle.01.R', 0, 0), ('*:RightHandMiddle2', 'f_middle.02.R', 0, 0), ('*:RightHandMiddle3', 'f_middle.03.R', 0, 0), ('*:RightHandRing1', 'f_ring.01.R', 0, 0), ('*:RightHandRing2', 'f_ring.02.R', 0, 0), ('*:RightHandRing3', 'f_ring.03.R', 0, 0), ('*:RightHandPinky1', 'f_pinky.01.R', 0, 0), ('*:RightHandPinky2', 'f_pinky.02.R', 0, 0), ('*:RightHandPinky3', 'f_pinky.03.R', 0, 0)],
        }
    }
}


def getTranslationVec(bone_from, bone_to, from_dist, to_dist):
    deltaX_from = bone_from.tail.x - bone_from.head.x
    deltaY_from = bone_from.tail.y - bone_from.head.y
    deltaZ_from = bone_from.tail.z - bone_from.head.z
    deltaX_to = bone_to.tail.x - bone_to.head.x
    deltaY_to = bone_to.tail.y - bone_to.head.y
    deltaZ_to = bone_to.tail.z - bone_to.head.z

    # to
    tX = bone_to.head.x + deltaX_to * to_dist - bone_from.head.x
    tY = bone_to.head.y + deltaY_to * to_dist - bone_from.head.y
    tZ = bone_to.head.z + deltaZ_to * to_dist - bone_from.head.z
    # from
    tX = tX - deltaX_from * from_dist
    tY = tY - deltaY_from * from_dist
    tZ = tZ - deltaZ_from * from_dist

    # translation vector
    return (tX, tY, tZ)


def stitchDataConcatDbl(stitchData1, stitchData2):
    if stitchData1 is None:
        return stitchData2
    elif stitchData2 is None:
        return stitchData1
    else:
        data_concat = stitchData1.copy()
        for temp1, temp2 in stitchData2:
            data_concat.append((temp1, temp2))
        return data_concat


def stitchDataConcatTrpl(stitchData1, stitchData2):
    if stitchData1 is None:
        return stitchData2
    elif stitchData2 is None:
        return stitchData1
    else:
        data_concat = stitchData1.copy()
        for temp1, temp2, temp3 in stitchData2:
            data_concat.append((temp1, temp2, temp3))
        return data_concat


# otherRig is source, mhx2Rig is destination
def doBridgeRigs(self, mhx2Rig, mhx2RigType, otherRig, otherRigType, boneNameTranslations):
    dest_stitch = amh2b_rig_stitch_dest_list.get(mhx2RigType).get(otherRigType)

    bpy.ops.object.mode_set(mode='OBJECT')

    # *** Blender 2.7x
    #bpy.context.scene.objects.active = otherRig
    # *** Blender 2.8x and higher
    bpy.context.view_layer.objects.active = otherRig
    # ***

    bpy.ops.object.mode_set(mode='EDIT')
    # Rename before join so that animation is attached to correct bones, to prevent mismatches
    # from bones being auto-renamed when rigs are joined.
    renameBonesBeforeJoin(otherRig, dest_stitch.get('blist_rename'))

    bpy.ops.object.mode_set(mode='OBJECT')

    # *** Blender 2.7x
    #bpy.context.scene.objects.active = mhx2Rig
    # *** Blender 2.8x and higher
    bpy.context.view_layer.objects.active = mhx2Rig
    # ***

    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode='EDIT')
    stitchBones(self, mhx2Rig, dest_stitch, boneNameTranslations)
    bpy.ops.object.mode_set(mode='OBJECT')


def renameBonesBeforeJoin(rig, bone_rename_tuples):
    if bone_rename_tuples is not None:
        for old_bn, new_bn in bone_rename_tuples:
            rig.data.edit_bones[old_bn].name = new_bn


def stitchBones(self, rig, stitch_datapack, boneNameTrans):
    batchDoDupSwapStitches(self, rig, stitch_datapack, boneNameTrans)
    batchDoMoveBones(self, rig, stitch_datapack, boneNameTrans)
    batchDoSetParents(self, rig, stitch_datapack, boneNameTrans)


def batchDoDupSwapStitches(self, rig, stitch_datapack, boneNameTrans):
    # TORSO
    if self.torso_stitch_enum == 'YES':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_torso'), boneNameTrans)

    # ARM LEFT
    if self.arm_left_stitch_enum == 'FORWARDK':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_arm_L_fk'), boneNameTrans)
    elif self.arm_left_stitch_enum == 'INVERSEK':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_arm_L_ik'), boneNameTrans)
    elif self.arm_left_stitch_enum == 'BOTH':
        innerBatchDupSwapStitches(rig, stitchDataConcatDbl(stitch_datapack.get('blist_dup_swap_stitch_arm_L_fk'), stitch_datapack.get('blist_dup_swap_stitch_arm_L_ik')), boneNameTrans)

    # ARM RIGHT
    if self.arm_right_stitch_enum == 'FORWARDK':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_arm_R_fk'), boneNameTrans)
    elif self.arm_right_stitch_enum == 'INVERSEK':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_arm_R_ik'), boneNameTrans)
    elif self.arm_right_stitch_enum == 'BOTH':
        innerBatchDupSwapStitches(rig, stitchDataConcatDbl(stitch_datapack.get('blist_dup_swap_stitch_arm_R_fk'), stitch_datapack.get('blist_dup_swap_stitch_arm_R_ik')), boneNameTrans)

    # LEG LEFT
    if self.leg_left_stitch_enum == 'FORWARDK':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_leg_L_fk'), boneNameTrans)
    elif self.leg_left_stitch_enum == 'INVERSEK':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_leg_L_ik'), boneNameTrans)
    elif self.leg_left_stitch_enum == 'BOTH':
        innerBatchDupSwapStitches(rig, stitchDataConcatDbl(stitch_datapack.get('blist_dup_swap_stitch_leg_L_fk'), stitch_datapack.get('blist_dup_swap_stitch_leg_L_ik')), boneNameTrans)

    # LEG RIGHT
    if self.leg_right_stitch_enum == 'FORWARDK':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_leg_R_fk'), boneNameTrans)
    elif self.leg_right_stitch_enum == 'INVERSEK':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_leg_R_ik'), boneNameTrans)
    elif self.leg_right_stitch_enum == 'BOTH':
        innerBatchDupSwapStitches(rig, stitchDataConcatDbl(stitch_datapack.get('blist_dup_swap_stitch_leg_R_fk'), stitch_datapack.get('blist_dup_swap_stitch_leg_R_ik')), boneNameTrans)

    # FINGERS LEFT
    if self.fingers_left_stitch_enum == 'YES':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_fingers_L'), boneNameTrans)
    # FINGERS RIGHT
    if self.fingers_right_stitch_enum == 'YES':
        innerBatchDupSwapStitches(rig, stitch_datapack.get('blist_dup_swap_stitch_fingers_R'), boneNameTrans)


def innerBatchDupSwapStitches(rig, stitchList, boneNameTrans):
    if stitchList is not None:
        for bone_to_dup, ref_bone, dist_on_dup, dist_on_ref in stitchList:
            stitchDupSwap(rig, bone_to_dup, ref_bone, dist_on_dup, dist_on_ref, boneNameTrans)


def stitchDupSwap(rig, bone_to_dup, ref_bone, dist_on_dup, dist_on_ref, boneNameTrans):
    bone_to_dup_trans = boneNameTrans.get(bone_to_dup)
    ref_bone_trans = boneNameTrans.get(ref_bone)
    if bone_to_dup_trans is None or ref_bone_trans is None:
        return

    # set the parenting type to offset (connect=False), to prevent geometry being warped when re-parented
    rig.data.edit_bones[bone_to_dup_trans].use_connect = False
    rig.data.edit_bones[ref_bone_trans].use_connect = False

    tVec = getTranslationVec(rig.data.edit_bones[bone_to_dup_trans], rig.data.edit_bones[ref_bone_trans], dist_on_dup, dist_on_ref)

    # duplicate bone
    newBone = rig.data.edit_bones.new(rig.data.edit_bones[bone_to_dup_trans].name)
    newBone.head.x = rig.data.edit_bones[bone_to_dup_trans].head.x + tVec[0]
    newBone.head.y = rig.data.edit_bones[bone_to_dup_trans].head.y + tVec[1]
    newBone.head.z = rig.data.edit_bones[bone_to_dup_trans].head.z + tVec[2]
    newBone.tail.x = rig.data.edit_bones[bone_to_dup_trans].tail.x + tVec[0]
    newBone.tail.y = rig.data.edit_bones[bone_to_dup_trans].tail.y + tVec[1]
    newBone.tail.z = rig.data.edit_bones[bone_to_dup_trans].tail.z + tVec[2]
    newBone.roll = rig.data.edit_bones[bone_to_dup_trans].roll
    # swap new bone for ref_bone
    newBone.parent = rig.data.edit_bones[ref_bone_trans].parent
    rig.data.edit_bones[ref_bone_trans].parent = newBone

    # need to make copy of newBone.name because of mode_set change,
    # somehow cannot access newBone.name in POSE mode
    newBoneName = newBone.name

    bpy.ops.object.mode_set(mode='POSE')

    # new bone will copy rotation from bone_to_dup
    crc = rig.pose.bones[newBoneName].constraints.new('COPY_ROTATION')
    crc.target = rig
    crc.subtarget = bone_to_dup_trans
    crc.target_space = 'LOCAL'
    crc.owner_space = 'LOCAL'
    crc.use_offset = True
    # new bone will also copy location from bone_to_dup (user can turn off / remove if needed)
    clc = rig.pose.bones[newBoneName].constraints.new('COPY_LOCATION')
    clc.target = rig
    clc.subtarget = bone_to_dup_trans
    clc.target_space = 'LOCAL'
    clc.owner_space = 'LOCAL'
    clc.use_offset = True

    bpy.ops.object.mode_set(mode='EDIT')


def batchDoMoveBones(self, rig, stitch_datapack, boneNameTrans):
    # TORSO
    if self.torso_stitch_enum == 'YES':
        innerBatchDoMove(rig, stitch_datapack.get('blist_move_torso'), boneNameTrans)

    # ARM LEFT
    if self.arm_left_stitch_enum == 'FORWARDK':
        innerBatchDoMove(rig, stitch_datapack.get('blist_move_arm_L_fk'), boneNameTrans)
    elif self.arm_left_stitch_enum == 'INVERSEK':
        innerBatchDoMove(rig, stitch_datapack.get('blist_move_arm_L_ik'), boneNameTrans)
    elif self.arm_left_stitch_enum == 'BOTH':
        innerBatchDoMove(rig, stitchDataConcatTrpl(stitch_datapack.get('blist_move_arm_L_fk'), stitch_datapack.get('blist_move_arm_L_ik')), boneNameTrans)

    # ARM RIGHT
    if self.arm_right_stitch_enum == 'FORWARDK':
        innerBatchDoMove(rig, stitch_datapack.get('blist_move_arm_R_fk'), boneNameTrans)
    elif self.arm_right_stitch_enum == 'INVERSEK':
        innerBatchDoMove(rig, stitch_datapack.get('blist_move_arm_R_ik'), boneNameTrans)
    elif self.arm_right_stitch_enum == 'BOTH':
        innerBatchDoMove(rig, stitchDataConcatTrpl(stitch_datapack.get('blist_move_arm_R_fk'), stitch_datapack.get('blist_move_arm_R_ik')), boneNameTrans)

    # LEG LEFT
    if self.leg_left_stitch_enum == 'FORWARDK':
        innerBatchDoMove(rig, stitch_datapack.get('blist_move_leg_L_fk'), boneNameTrans)
    elif self.leg_left_stitch_enum == 'INVERSEK':
        innerBatchDoMove(rig, stitch_datapack.get('blist_move_leg_L_ik'), boneNameTrans)
    elif self.leg_left_stitch_enum == 'BOTH':
        innerBatchDoMove(rig, stitchDataConcatTrpl(stitch_datapack.get('blist_move_leg_L_fk'), stitch_datapack.get('blist_move_leg_L_ik')), boneNameTrans)

    # LEG right
    if self.leg_right_stitch_enum == 'FORWARDK':
        innerBatchDoMove(rig, stitch_datapack.get('blist_move_leg_R_fk'), boneNameTrans)
    elif self.leg_right_stitch_enum == 'INVERSEK':
        innerBatchDoMove(rig, stitch_datapack.get('blist_move_leg_R_ik'), boneNameTrans)
    elif self.leg_right_stitch_enum == 'BOTH':
        innerBatchDoMove(rig, stitchDataConcatTrpl(stitch_datapack.get('blist_move_leg_R_fk'), stitch_datapack.get('blist_move_leg_R_ik')), boneNameTrans)


def innerBatchDoMove(rig, stitch_list, boneNameTrans):
    if stitch_list is not None:
        for bone_to_move, ref_bone, dist_on_move, dist_on_ref in stitch_list:
            doMoveBone(rig, bone_to_move, ref_bone, dist_on_move, dist_on_ref, boneNameTrans)


def doMoveBone(rig, bone_to_move, ref_bone, dist_on_move, dist_on_ref, boneNameTrans):
    bone_to_move_trans = boneNameTrans.get(bone_to_move)
    ref_bone_trans = boneNameTrans.get(ref_bone)
    if bone_to_move_trans is None or ref_bone_trans is None:
        return

    # set parenting type to Offset to prevent warping when moving bone
    rig.data.edit_bones[bone_to_move_trans].use_connect = False

    tVec = getTranslationVec(rig.data.edit_bones[bone_to_move_trans], rig.data.edit_bones[ref_bone_trans], dist_on_move, dist_on_ref)

    rig.data.edit_bones[bone_to_move_trans].head.x += tVec[0]
    rig.data.edit_bones[bone_to_move_trans].head.y += tVec[1]
    rig.data.edit_bones[bone_to_move_trans].head.z += tVec[2]
    rig.data.edit_bones[bone_to_move_trans].tail.x += tVec[0]
    rig.data.edit_bones[bone_to_move_trans].tail.y += tVec[1]
    rig.data.edit_bones[bone_to_move_trans].tail.z += tVec[2]


def batchDoSetParents(self, rig, stitch_datapack, boneNameTrans):
    # TORSO
    if self.torso_stitch_enum == 'YES':
        innerBatchDoSetParent(rig, stitch_datapack.get('blist_setparent_torso'), boneNameTrans)

    # ARM LEFT
    if self.arm_left_stitch_enum == 'FORWARDK':
        innerBatchDoSetParent(rig, stitch_datapack.get('blist_setparent_arm_L_fk'), boneNameTrans)
    elif self.arm_left_stitch_enum == 'INVERSEK':
        innerBatchDoSetParent(rig, stitch_datapack.get('blist_setparent_arm_L_ik'), boneNameTrans)
    elif self.arm_left_stitch_enum == 'BOTH':
        innerBatchDoSetParent(rig, stitchDataConcatDbl(stitch_datapack.get('blist_setparent_arm_L_fk'), stitch_datapack.get('blist_setparent_arm_L_ik')), boneNameTrans)

    # ARM RIGHT
    if self.arm_right_stitch_enum == 'FORWARDK':
        innerBatchDoSetParent(rig, stitch_datapack.get('blist_setparent_arm_R_fk'), boneNameTrans)
    elif self.arm_right_stitch_enum == 'INVERSEK':
        innerBatchDoSetParent(rig, stitch_datapack.get('blist_setparent_arm_R_ik'), boneNameTrans)
    elif self.arm_right_stitch_enum == 'BOTH':
        innerBatchDoSetParent(rig, stitchDataConcatDbl(stitch_datapack.get('blist_setparent_arm_R_fk'), stitch_datapack.get('blist_setparent_arm_R_ik')), boneNameTrans)

    # LEG LEFT
    if self.leg_left_stitch_enum == 'FORWARDK':
        innerBatchDoSetParent(rig, stitch_datapack.get('blist_setparent_leg_L_fk'), boneNameTrans)
    elif self.leg_left_stitch_enum == 'INVERSEK':
        innerBatchDoSetParent(rig, stitch_datapack.get('blist_setparent_leg_L_ik'), boneNameTrans)
    elif self.leg_left_stitch_enum == 'BOTH':
        innerBatchDoSetParent(rig, stitchDataConcatDbl(stitch_datapack.get('blist_setparent_leg_L_fk'), stitch_datapack.get('blist_setparent_leg_L_ik')), boneNameTrans)

    # LEG RIGHT
    if self.leg_right_stitch_enum == 'FORWARDK':
        innerBatchDoSetParent(rig, stitch_datapack.get('blist_setparent_leg_R_fk'), boneNameTrans)
    elif self.leg_right_stitch_enum == 'INVERSEK':
        innerBatchDoSetParent(rig, stitch_datapack.get('blist_setparent_leg_R_ik'), boneNameTrans)
    elif self.leg_right_stitch_enum == 'BOTH':
        innerBatchDoSetParent(rig, stitchDataConcatDbl(stitch_datapack.get('blist_setparent_leg_R_fk'), stitch_datapack.get('blist_setparent_leg_R_ik')), boneNameTrans)


def innerBatchDoSetParent(rig, stitch_list, boneNameTrans):
    if stitch_list is not None:
        for stitch_from, stitch_to in stitch_list:
            stitchSetParentBone(rig, stitch_from, stitch_to, boneNameTrans)


def stitchSetParentBone(rig, stitch_from, stitch_to, boneNameTrans):
    stitch_from_trans = boneNameTrans.get(stitch_from)
    stitch_to_trans = boneNameTrans.get(stitch_to)
    if stitch_from_trans is None or stitch_to_trans is None:
        return

    # either bone can be warped by the re-parenting, so set parent type to Offset for both
    rig.data.edit_bones[stitch_from_trans].use_connect = False
    rig.data.edit_bones[stitch_to_trans].use_connect = False

    rig.data.edit_bones[stitch_from_trans].parent = rig.data.edit_bones[stitch_to_trans]


def detectAndbridgeRigs(self, mhx2Rig, otherRig):
    print('detectAndBridgeRigs function started')
    print('mhx2Rig.name = ' + mhx2Rig.name)
    print('otherRig.name = ' + otherRig.name)

    # destination rig type
    mhx2RigType = 'import_mhx'

    # get source rig type, automatically detecting as needed
    if self.src_rig_type_enum == 'I_MIXAMO_NATIVE_FBX':
        otherRigType = 'mixamo_native_fbx'
    elif self.src_rig_type_enum == 'I_MAKEHUMAN_CMU_MB':
        otherRigType = 'makehuman_cmu_mb'
    else:
        # auto-detect is last option, if nothing else matched
        otherRigType = detectRigType(otherRig)

    mhx2RigBoneNames = []
    for bone in mhx2Rig.data.bones:
        mhx2RigBoneNames.append(bone.name)
    otherRigBoneNames = []
    for bone in otherRig.data.bones:
        otherRigBoneNames.append(bone.name)
    boneNameTranslations = getBoneNameTranslations(amh2b_rig_type_bone_names.get(mhx2RigType), mhx2RigBoneNames, '')
    additionalNameTrans = getBoneNameTranslations(amh2b_rig_type_bone_names.get(otherRigType), otherRigBoneNames, '')
    boneNameTranslations.update(additionalNameTrans)

    print('mhx2RigType=' + mhx2RigType)
    print('otherRigType=' + otherRigType)

    doBridgeRigs(self, mhx2Rig, mhx2RigType, otherRig, otherRigType, boneNameTranslations)


# compare bone names to detect rig type
def detectRigType(given_rig):
    # create list of all bone names in given rig
    given_bone_names = []
    for bone in given_rig.data.bones:
        given_bone_names.append(bone.name)

    # find a rig type with matching bone names
    for test_typename, test_bone_names in amh2b_rig_type_bone_names.items():
        if getBoneNameMatchCount(test_bone_names, given_bone_names) >= amh2b_min_bones_for_rig_match:
            return test_typename

    return ''


def getBoneNameTranslations(boneNameListA, boneNameListB, postFix):
    trans = {}
    for bname in boneNameListA:
        foundNames = fnmatch.filter(boneNameListB, bname)
        if foundNames is not None and len(foundNames) > 0:
            trans[bname + postFix] = foundNames[0] + postFix
    return trans


# Find number of matches between list A and list B,
# where we are searching for A (which can include wildcards in the strings) within B.
def getBoneNameMatchCount(boneNameListA, boneNameListB):
    m = 0   # zero matches at start
    # find matching bone names, names with wildcards allowed
    for bname in boneNameListA:
        if fnmatch.filter(boneNameListB, bname):
            m = m + 1
    return m


def doBoneWoven(self):
    print('boneWoven() begin.')
    selection_list = bpy.context.selected_objects
    if bpy.context.active_object is None or len(selection_list) < 1:
        print('No active object or selection is empty, no Bone Woven.')
        return {'FINISHED'}
    if not bpy.context.active_object in selection_list:
        print('Active object is not in selection list, no Bone Woven.')
        return {'FINISHED'}

    mRig = bpy.context.active_object
    oRig = None
    # the Active Object must be the imported MHX2 rig (not animated - should not be animated, anyway...)
    # the other selected object must be the rig with the animation
    for i in selection_list:
        if i != bpy.context.active_object:
            oRig = i

    # fail if did not get two ARMATURE type objects
    if oRig is None:
        print('Only one object selected, but two are needed. No Bone Woven.')
        return {'FINISHED'}
    if mRig.type != 'ARMATURE':
        print('Bone Woven failed because active object ' + mRig.name + ' is not ARMATURE type.')
        return {'FINISHED'}
    if oRig.type != 'ARMATURE':
        print('Bone Woven failed because selected object ' + oRig.name + ' is not ARMATURE type.')
        return {'FINISHED'}

    detectAndbridgeRigs(self, mRig, oRig)
    print('boneWoven() end.')


class AMH2B_BoneWoven(bpy.types.Operator):
    """Automate MakeHuman 2 Blender - Bone Woven"""
    """MHX2 Rig to Rig Animation Bridge"""
    bl_idname = 'object.amh2b_bone_woven'
    bl_label = 'AMH2B Bone Woven'
    bl_options = {'REGISTER', 'UNDO'}

    # *** Blender 2.7x
    #src_rig_type_enum = bpy.props.EnumProperty(name='Source Rig Type', description='Rig type that will be joined to MHX rig.', items=amh2b_src_rig_type_items)
    #torso_stitch_enum = bpy.props.EnumProperty(name='Torso Stitches', description='Set torso stitches to yes/no.', items=amh2b_yes_no_items)
    #arm_left_stitch_enum = bpy.props.EnumProperty(name='Left Arm Stitches', description='Set left arm stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    #arm_right_stitch_enum = bpy.props.EnumProperty(name='Right Arm Stitches', description='Set right arm stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    #leg_left_stitch_enum = bpy.props.EnumProperty(name='Left Leg Stitches', description='Set left leg stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    #leg_right_stitch_enum = bpy.props.EnumProperty(name='Right Leg Stitches', description='Set right leg stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    #fingers_left_stitch_enum = bpy.props.EnumProperty(name='Left Fingers Stitches', description='Set left fingers stitches to yes/no.', items=amh2b_yes_no_items)
    #fingers_right_stitch_enum = bpy.props.EnumProperty(name='Right Fingers Stitches', description='Set right fingers stitches to yes/no.', items=amh2b_yes_no_items)
    # *** Blender 2.8x and higher
    src_rig_type_enum : bpy.props.EnumProperty(name='Source Rig Type', description='Rig type that will be joined to MHX rig.', items=amh2b_src_rig_type_items)
    torso_stitch_enum : bpy.props.EnumProperty(name='Torso Stitches', description='Set torso stitches to yes/no.', items=amh2b_yes_no_items)
    arm_left_stitch_enum : bpy.props.EnumProperty(name='Left Arm Stitches', description='Set left arm stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    arm_right_stitch_enum : bpy.props.EnumProperty(name='Right Arm Stitches', description='Set right arm stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    leg_left_stitch_enum : bpy.props.EnumProperty(name='Left Leg Stitches', description='Set left leg stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    leg_right_stitch_enum : bpy.props.EnumProperty(name='Right Leg Stitches', description='Set right leg stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    fingers_left_stitch_enum : bpy.props.EnumProperty(name='Left Fingers Stitches', description='Set left fingers stitches to yes/no.', items=amh2b_yes_no_items)
    fingers_right_stitch_enum : bpy.props.EnumProperty(name='Right Fingers Stitches', description='Set right fingers stitches to yes/no.', items=amh2b_yes_no_items)
    # ***

    def execute(self, context):
        doBoneWoven(self)

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Swap Materials from Other Blend File
# Automate materials dictionary material swapping with a simple method:
#   1) User chooses file with source materials.
#   2) Materials are appended 'blindly', by trimming names of materials on selected objects
#      and trying to append trimmed name materials from the blend file chosen by the user.
class AMH2B_SwapMaterials(Operator, ImportHelper):
    """Automate MakeHuman 2 Blender - Swap Materials"""
    """Swap Materials from Source Blend File"""
    bl_idname = 'object.amh2b_swap_materials'
    bl_label = 'AMH2B Swap Materials'
    bl_options = {'REGISTER', 'UNDO'}

    # *** Blender 2.7x
    #filter_glob = StringProperty(default='*.blend', options={'HIDDEN'})
    # *** Blender 2.8x
    filter_glob: StringProperty(default='*.blend', options={'HIDDEN'})
    # ***

    # returns True if material was successfully appended
    # TODO check if the material already exists in this file, if it does exist then rename
    #   the current material, and then append the new material
    def appendFromFile(self, mat_filepath, mat_name):
        # path inside of file (i.e. like opening the 'Append' window; see Action, Armature, Brush, Camera, ...)
        inner_path = 'Material'

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

    # Trim string up to, and including, the first ':' character, and return trimmed string.
    def getSwatchNameForMH_Name(self, mh_name):
        # if name is in MH format then return trimmed name
        # (remove first third, up to the ':', and return the remaining two-thirds)
        if len(mh_name.split(':', -1)) == 3:
            return mh_name.split(':', 1)[1]
        # otherwise return original name
        else:
            return mh_name


    # TODO swap more than one material (active material), if object has more than one material
    #   for mat in obj.material_slots:
    #       ...
    def doShaderSwaps(self, shaderswap_blendfile):
        # get list of objects currently selected and fix materials on all selected objects, swapping to correct materials
        selection_list = bpy.context.selected_objects

        # do the material swapping
        for obj in selection_list:
            # Iterate over the material slots and check/swap the materials
            for mat_slot in obj.material_slots:
                swatch_mat_name = self.getSwatchNameForMH_Name(mat_slot.material.name)

                # do not append/swap material if material already exists
                if bpy.data.materials.get(swatch_mat_name) is not None:
                    continue

                if not self.appendFromFile(shaderswap_blendfile, swatch_mat_name):
                    continue

                print('Swapping material on object ' + obj.name + ', oldMat = ' + obj.active_material.name + ', newMat = ' + swatch_mat_name)
                mat_slot.material = bpy.data.materials[swatch_mat_name]


    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        self.doShaderSwaps(self.filepath)
        return {'FINISHED'}


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Apply Scale
# Apply scale to armature (this is only needed for armature scale apply),
# and adjust it's bone location animation f-curve values to match the scaling.
# If this operation is not done, then the bones that have changing location values
# will appear to move incorrectly.
def doApplyScale():
    if bpy.context.active_object is None:
        print('doApplyScale() error: bpy.context.active_object is None, should have an object selected as active object.')
        return

    # keep copy of old scale values
    old_scale = bpy.context.active_object.scale.copy()

    # do not apply scale if scale is already 1.0 in all dimensions!
    if old_scale.x == 1 and old_scale.y == 1 and old_scale.z == 1:
        print('doApplyScale() avoided, active_object scale is already 1 in all dimensions.')
        return

    bpy.ops.object.mode_set(mode='OBJECT')

    print('doApplyScale() to rig = ' + bpy.context.active_object.name + '; old scale = ' + str(old_scale))
    # apply scale to active object
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # scale only the location f-curves on active object
    obj = bpy.context.active_object
    action = obj.animation_data.action

    # get only location f-curves
    fcurves = [fc for fc in action.fcurves if fc.data_path.endswith('location')]
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
    """Automate MakeHuman 2 Blender - Apply Scale to Rig"""
    """Apply Scale to Rig without corrupting the bone pose data (e.g. location)."""
    bl_idname = 'object.amh2b_apply_scale'
    bl_label = 'AMH2B Apply Scale to Rig'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        doApplyScale()
        return {'FINISHED'}


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Repose Rig
# Re-pose rig by way of a duplicate of original that moves mesh to desired pose,
# then original rig is pose-apply'ed and takes over from duplicate rig.
# Basically, a duplicate rig moves the underlying mesh to the place where the reposed original rig will be.

# duplicate selected objects
def dupSelected():
    obj_to_dup = bpy.context.active_object
    bpy.ops.object.duplicate({"object" : obj_to_dup, "selected_objects" : [obj_to_dup]}, linked=False)
    # return ref to newly duped object
    return bpy.context.active_object


def addArmatureToObjects(arm_obj, objs_list):
    for dest_obj in objs_list:
        if dest_obj != arm_obj:
            addArmatureToObj(arm_obj, dest_obj)


def addArmatureToObj(arm_obj, dest_obj):
    # create ARMATURE modifier and set refs, etc.
    mod = dest_obj.modifiers.new('ReposeArmature', 'ARMATURE')
    if mod is None:
        print('ReposeArmature: Unable to add armature to object' + dest_obj.name)
        return
    mod.object = arm_obj
    mod.use_deform_preserve_volume = True
    # Move modifier to top of stack, because this armature needs to move the mesh before
    # any other modifications occur, to match the re-posed main armature.
    while dest_obj.modifiers.find(mod.name) != 0:
        bpy.ops.object.modifier_move_up({'object': dest_obj}, modifier=mod.name)


def doReposeRig():
    if bpy.context.active_object is None:
        print('doReposeRig() error: Active object is None, cannot Re-Pose MHX rig.')
        return

    old_3dview_mode = bpy.context.object.mode

    # copy ref to active object
    selection_active_obj = bpy.context.active_object
    print('doReposeRig() applied to active object ' + bpy.context.active_object.name)

    # copy list of selected objects, minus the active object
    # (0 selected objects is allowed, because armature can be re-posed independently)
    selection_list = []
    for ob in bpy.context.selected_objects:
        if ob.name != selection_active_obj.name:
            selection_list.append(bpy.data.objects[ob.name])

    # de-select all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Blender 2.7x *** {
    # select the old active_object in the 3D viewport
    #selection_active_obj.select = True
    # make it the active selected object
    #bpy.context.scene.objects.active = selection_active_obj
    # Blender 2.7x *** }
    # Blender 2.8x *** {
    # select the old active_object in the 3D viewport
    selection_active_obj.select_set(True)
    # make it the active selected object
    bpy.context.view_layer.objects.active = selection_active_obj
    # Blender 2.8x *** }

    # duplicate the original armature
    new_arm = dupSelected()
    print('new_arm=')
    print(new_arm)
    print('selection_active=')
    print(selection_active_obj)
    # parent the duplicated armature to the original armature, to prevent mesh tearing if the armatures move apart
    new_arm.parent = selection_active_obj

    # add modifiers to the other selected objects, so the other selected objects will use the new armature
    addArmatureToObjects(new_arm, selection_list)

    # select original armature
    # Blender 2.7x *** {
    #bpy.context.scene.objects.active = selection_active_obj
    # Blender 2.7x *** }
    # Blender 2.8x *** {
    bpy.context.view_layer.objects.active = selection_active_obj
    # Blender 2.8x *** }

    bpy.ops.object.mode_set(mode='POSE')
    # apply pose to original armature
    bpy.ops.pose.armature_apply()
    bpy.ops.object.mode_set(mode=old_3dview_mode)


class AMH2B_ReposeRig(bpy.types.Operator):
    """Automate MakeHuman 2 Blender - Repose Rig"""
    """Use a 'bridge rig' to move a shape-keyed mesh into position with a 'reposed armature' (i.e. where the pose was changed and then applied as rest pose)."""
    bl_idname = 'object.amh2b_repose_rig'
    bl_label = 'AMH2B Repose Rig'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        doReposeRig()
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

def doRatchet():
    if len(bpy.context.selected_objects) != 2:
        print('doRatchet() error: Cannot Ratchet Hold, need to have exactly two objects selected.')
        return

    bpy.ops.object.mode_set(mode='OBJECT')

    # copy ref to active object
    obj_to_ratchet = bpy.context.active_object
    if obj_to_ratchet is None:
        print('doRatchet() error: Active object is None, but must be the object to re-keyframe.')
        return

    # get ref to other object (presumably an 'Empty' type object), the not active object
    hold_onto_obj = bpy.context.selected_objects[0]
    if hold_onto_obj.name == obj_to_ratchet.name:
        hold_onto_obj = bpy.context.selected_objects[1]

    # insert location keyframes on object to ratchet at old location
    obj_to_ratchet.keyframe_insert(data_path='location')

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
    bpy.ops.transform.translate(value=deltaMove, constraint_orientation='GLOBAL')
    # insert location keyframes on object to ratchet at new location
    obj_to_ratchet.keyframe_insert(data_path='location')


class AMH2B_RatchetHold(bpy.types.Operator):
    """Automate MakeHuman 2 Blender - Ratchet Hold"""
    """Keyframe the movement of a parent object so that a child object appears motionless; the parent object's location is offset to keep the child object's location stationary."""
    bl_idname = 'object.amh2b_ratchet_hold'
    bl_label = 'AMH2B Ratchet Hold'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        doRatchet()
        return {'FINISHED'}


#####################################################
#     Automate MakeHuman 2 Blender (AMH2B)
#     Lucky
#
#   Idea of script:
# One button to do all the work, or at least as much as possible, i.e.
# Automatically apply location/rotation/scale to animated armature,
# repose MHX armature and it's parented objects (e.g. clothes, hair),
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

def doLucky(self):
    # copy ref to active object, the MHX armature
    mhx_arm_obj = bpy.context.active_object
    if mhx_arm_obj is None:
        print('doLucky() error: Active object is None, cannot Re-Pose MHX rig')
        return

    # get the animated armature (otherArmature) from the list of selected objects
    # (otherArmature will be joined to the MHX armature)
    otherArmature = None
    for ob in bpy.context.selected_objects:
        if ob.name != mhx_arm_obj.name:
            if ob.type == 'ARMATURE':
                otherArmature = ob
                break

    if otherArmature == None:
        print('doLucky() error: : missing other armature to join to MHX armature.')
        return

    print('doLucky() debug info: +++')
    print('mhx_arm_obj=')
    print(mhx_arm_obj)
    print('otherArmature=')
    print(otherArmature)
    print('doLucky() debug info: ---')

    # since MHX armature is already the active object, do repose first
    if self.repose_rig_enum == 'YES':
        doReposeRig()

    # de-select all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Blender 2.7x *** {
    # select the other armature (the imported animated armature) in the 3D viewport
    #otherArmature.select = True
    # make it the active selected object
    #bpy.context.scene.objects.active = otherArmature
    # Blender 2.7x *** }
    # Blender 2.8x *** {
    # select the other armature (the imported animated armature) in the 3D viewport
    otherArmature.select_set(True)
    # make it the active selected object
    bpy.context.view_layer.objects.active = otherArmature
    # Blender 2.8x *** }

    # let Blender apply location and rotation to animated armature
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    # custom apply scale to animated armature
    doApplyScale()

    # otherArmature will still be selected and the active_object, so just add the MHX armature
    # to the selected list and make it the active object.

    # Blender 2.7x *** {
    # select the MHX armature (the armature that lacks animation) in the 3D viewport
    #mhx_arm_obj.select = True
    # make it the active selected object
    #bpy.context.scene.objects.active = mhx_arm_obj
    # Blender 2.7x *** }
    # Blender 2.8x *** {
    # select the MHX armature (the armature that lacks animation) in the 3D viewport
    mhx_arm_obj.select_set(True)
    # make it the active selected object
    bpy.context.view_layer.objects.active = mhx_arm_obj
    # Blender 2.8x *** }

    # do bone woven
    doBoneWoven(self)


# TODO: Use BoneWoven as the base class instead of Operator,
# to get rid of doubling of code for user options input.
class AMH2B_Lucky(bpy.types.Operator):
    """Automate MakeHuman 2 Blender - Lucky"""
    """Given user selected MHX armature, animated source armature, and objects attached to MHX armature: do RePose, then ApplyScale, then BoneWoven: so the result is a correctly animated MHX armature - with working finger rig, face rig, etc."""
    bl_idname = 'object.amh2b_lucky'
    bl_label = 'AMH2B Lucky'
    bl_options = {'REGISTER', 'UNDO'}

    # *** Blender 2.7x
    #repose_rig_enum = bpy.props.EnumProperty(name='Re-Pose Rig', description='Apply Re-Pose to rig during lucky process yes/no.', items=amh2b_yes_no_items)
    #src_rig_type_enum = bpy.props.EnumProperty(name='Source Rig Type', description='Rig type that will be joined to MHX rig.', items=amh2b_src_rig_type_items)
    #torso_stitch_enum = bpy.props.EnumProperty(name='Torso Stitches', description='Set torso stitches to yes/no.', items=amh2b_yes_no_items)
    #arm_left_stitch_enum = bpy.props.EnumProperty(name='Left Arm Stitches', description='Set left arm stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    #arm_right_stitch_enum = bpy.props.EnumProperty(name='Right Arm Stitches', description='Set right arm stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    #leg_left_stitch_enum = bpy.props.EnumProperty(name='Left Leg Stitches', description='Set left leg stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    #leg_right_stitch_enum = bpy.props.EnumProperty(name='Right Leg Stitches', description='Set right leg stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    #fingers_left_stitch_enum = bpy.props.EnumProperty(name='Left Fingers Stitches', description='Set left fingers stitches to yes/no.', items=amh2b_yes_no_items)
    #fingers_right_stitch_enum = bpy.props.EnumProperty(name='Right Fingers Stitches', description='Set right fingers stitches to yes/no.', items=amh2b_yes_no_items)
    # *** Blender 2.8x and higher
    repose_rig_enum : bpy.props.EnumProperty(name='Re-Pose Rig', description='Apply Re-Pose to rig during lucky process yes/no.', items=amh2b_yes_no_items)
    src_rig_type_enum : bpy.props.EnumProperty(name='Source Rig Type', description='Rig type that will be joined to MHX rig.', items=amh2b_src_rig_type_items)
    torso_stitch_enum : bpy.props.EnumProperty(name='Torso Stitches', description='Set torso stitches to yes/no.', items=amh2b_yes_no_items)
    arm_left_stitch_enum : bpy.props.EnumProperty(name='Left Arm Stitches', description='Set left arm stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    arm_right_stitch_enum : bpy.props.EnumProperty(name='Right Arm Stitches', description='Set right arm stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    leg_left_stitch_enum : bpy.props.EnumProperty(name='Left Leg Stitches', description='Set left leg stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    leg_right_stitch_enum : bpy.props.EnumProperty(name='Right Leg Stitches', description='Set right leg stitches to FK, or IK, or both, or none.', items=amh2b_fk_ik_both_none_items)
    fingers_left_stitch_enum : bpy.props.EnumProperty(name='Left Fingers Stitches', description='Set left fingers stitches to yes/no.', items=amh2b_yes_no_items)
    fingers_right_stitch_enum : bpy.props.EnumProperty(name='Right Fingers Stitches', description='Set right fingers stitches to yes/no.', items=amh2b_yes_no_items)
    # ***

    def execute(self, context):
        doLucky(self)
        return {'FINISHED'}


#####################################################


def amh2b_lucky_menu_func(self, context):
    self.layout.operator(AMH2B_Lucky.bl_idname)

def amh2b_apply_scale_menu_func(self, context):
    self.layout.operator(AMH2B_ApplyScale.bl_idname)

def amh2b_bone_woven_menu_func(self, context):
    self.layout.operator(AMH2B_BoneWoven.bl_idname)

def amh2b_ratchet_hold_menu_func(self, context):
    self.layout.operator(AMH2B_RatchetHold.bl_idname)

def amh2b_repose_rig_menu_func(self, context):
    self.layout.operator(AMH2B_ReposeRig.bl_idname)

def amh2b_swap_shaders_menu_func(self, context):
    self.layout.operator(AMH2B_SwapMaterials.bl_idname)

def register():
    bpy.utils.register_class(AMH2B_SwapMaterials)
    bpy.types.VIEW3D_MT_object.append(amh2b_swap_shaders_menu_func)
    bpy.utils.register_class(AMH2B_ReposeRig)
    bpy.types.VIEW3D_MT_object.append(amh2b_repose_rig_menu_func)
    bpy.utils.register_class(AMH2B_RatchetHold)
    bpy.types.VIEW3D_MT_object.append(amh2b_ratchet_hold_menu_func)
    bpy.utils.register_class(AMH2B_BoneWoven)
    bpy.types.VIEW3D_MT_object.append(amh2b_bone_woven_menu_func)
    bpy.utils.register_class(AMH2B_ApplyScale)
    bpy.types.VIEW3D_MT_object.append(amh2b_apply_scale_menu_func)
    bpy.utils.register_class(AMH2B_Lucky)
    bpy.types.VIEW3D_MT_object.append(amh2b_lucky_menu_func)

def unregister():
    bpy.types.VIEW3D_MT_object.remove(amh2b_lucky_menu_func)
    bpy.utils.unregister_class(AMH2B_Lucky)
    bpy.types.VIEW3D_MT_object.remove(amh2b_apply_scale_menu_func)
    bpy.utils.unregister_class(AMH2B_ApplyScale)
    bpy.types.VIEW3D_MT_object.remove(amh2b_bone_woven_menu_func)
    bpy.utils.unregister_class(AMH2B_BoneWoven)
    bpy.types.VIEW3D_MT_object.remove(amh2b_ratchet_hold_menu_func)
    bpy.utils.unregister_class(AMH2B_RatchetHold)
    bpy.types.VIEW3D_MT_object.remove(amh2b_repose_rig_menu_func)
    bpy.utils.unregister_class(AMH2B_ReposeRig)
    bpy.types.VIEW3D_MT_object.remove(amh2b_swap_shaders_menu_func)
    bpy.utils.unregister_class(AMH2B_SwapMaterials)

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == '__main__':
    register()