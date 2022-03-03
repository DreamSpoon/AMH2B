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

amh2b_rig_type_bone_names = {
    "makehuman_cmu_mb": ["Hips", "LHipJoint", "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase", "LowerBack", "Spine", "Spine1", "LeftShoulder", "LeftArm", "LeftForeArm","LeftHand", "LThumb", "LeftFingerBase", "LeftHandFinger1", "Neck", "Neck1", "Head", "RightShoulder", "RightArm", "RightForeArm", "RightHand","RThumb", "RightFingerBase", "RightHandFinger1", "RHipJoint", "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"],

    "mixamo_native_fbx": ["*:Hips", "*:Spine", "*:Spine1", "*:Spine2", "*:Neck", "*:Head","*:LeftShoulder", "*:LeftArm", "*:LeftForeArm", "*:LeftHand", "*:LeftHandThumb1", "*:LeftHandThumb2", "*:LeftHandThumb3", "*:LeftHandIndex1", "*:LeftHandIndex2", "*:LeftHandIndex3", "*:LeftHandMiddle1", "*:LeftHandMiddle2", "*:LeftHandMiddle3", "*:LeftHandRing1", "*:LeftHandRing2", "*:LeftHandRing3", "*:LeftHandPinky1", "*:LeftHandPinky2", "*:LeftHandPinky3", "*:RightShoulder", "*:RightArm", "*:RightForeArm", "*:RightHand", "*:RightHandThumb1", "*:RightHandThumb2", "*:RightHandThumb3", "*:RightHandIndex1", "*:RightHandIndex2", "*:RightHandIndex3", "*:RightHandMiddle1", "*:RightHandMiddle2", "*:RightHandMiddle3", "*:RightHandRing1", "*:RightHandRing2", "*:RightHandRing3", "*:RightHandPinky1", "*:RightHandPinky2", "*:RightHandPinky3", "*:LeftUpLeg", "*:LeftLeg", "*:LeftFoot", "*:LeftToeBase", "*:RightUpLeg", "*:RightLeg", "*:RightFoot", "*:RightToeBase"],

    "import_mhx": ["master", "root", "spine", "spine-1", "chest", "DEF-serratus.L", "DEF-serratus.R", "DEF-pect.L", "breast.L", "DEF-breast.L", "DEF-pect.R", "breast.R", "DEF-breast.R", "chest-1", "neck", "neck-1", "head", "lolid.R", "lolid.L", "jaw", "tongue_base", "tongue_mid", "tongue_tip", "uplid.L", "uplid.R", "eyes", "eye_parent.L", "eye.L", "DEF-eye.L", "eye_parent.R", "eye.R", "DEF-eye.R", "DEF-uplid.L", "DEF-uplid.R", "DEF-lolid.L", "DEF-lolid.R", "DEF-jaw", "DEF-tongue_base", "DEF-tongue_mid", "DEF-tongue_tip", "DEF-neck-1", "DEF-head", "clavicle.L", "DEF-deltoid.L", "shoulder01.L", "arm_base.L", "elbow.pt.ik.L", "pectIk.L", "scap-parent.R", "DEF-scapula.R", "scap-parent.L", "DEF-scapula.L", "clavicle.R", "DEF-deltoid.R", "pectIk.R", "shoulder01.R", "arm_base.R", "elbow.pt.ik.R", "DEF-sternum", "DEF-clavicle.R", "DEF-chest", "DEF-chest-1", "DEF-clavicle.L", "DEF-neck", "hips", "pelvis.L", "leg_base.L", "DEF-hip.R", "DEF-gluteus.L", "DEF-hip.L", "DEF-gluteus.R", "pelvis.R", "leg_base.R", "arm_hinge.R", "arm_socket.R", "upper_arm.R","forearm.R", "hand.R", "palm_middle.R", "f_middle.01.R", "f_middle.02.R", "f_middle.03.R", "DEF-f_middle.02.R", "DEF-f_middle.03.R", "middle.R", "thumb.01.R", "thumb.02.R", "thumb.03.R", "DEF-thumb.03.R", "thumb.R", "DEF-thumb.02.R", "palm_index.R", "f_index.01.R", "f_index.02.R", "f_index.03.R", "DEF-f_index.03.R", "index.R", "DEF-f_index.01.R", "DEF-f_index.02.R", "palm_pinky.R", "f_pinky.01.R", "f_pinky.02.R", "f_pinky.03.R", "pinky.R", "palm_ring.R", "f_ring.01.R", "f_ring.02.R", "f_ring.03.R", "DEF-f_ring.03.R", "DEF-f_ring.02.R", "ring.R", "DEF-palm_ring.R", "DEF-f_ring.01.R", "DEF-thumb.01.R", "DEF-palm_middle.R", "DEF-f_middle.01.R", "DEF-palm_pinky.R", "DEF-f_pinky.01.R", "DEF-f_pinky.02.R", "DEF-f_pinky.03.R", "shoulderIk.R", "serratusIk.R", "DEF-elbow_fan.R", "DEF-forearm.01.R", "DEF-forearm.02.R", "DEF-forearm.03.R", "DEF-hand.R", "DEF-palm_index.R", "forearm_X120.R", "upper_arm.fk.R", "forearm.fk.R", "hand.fk.R", "upper_arm.ik.R", "elbow.link.R", "forearm.ik.R", "DEF-upper_arm.R", "leg_hinge.R", "leg_socket.R","thigh.R", "gluteusIk.R", "DEF-knee_fan.R", "hipIk.R", "shin.R", "foot.R", "toe.R", "DEF-shin.01.R", "DEF-shin.02.R", "DEF-shin.03.R", "DEF-foot.R", "DEF-toe.R", "shin_X150.R", "thigh.fk.R", "shin.fk.R", "foot.fk.R", "heel.marker.R", "ball.marker.R", "toe.fk.R", "toe.marker.R", "thigh.ik.R", "knee.link.R", "shin.ik.R", "DEF-thigh.R", "thigh_X-90.R", "leg_hinge.L", "leg_socket.L", "thigh.L", "hipIk.L", "DEF-knee_fan.L", "gluteusIk.L", "shin.L", "foot.L", "toe.L", "DEF-shin.01.L", "DEF-shin.02.L", "DEF-shin.03.L", "DEF-foot.L", "DEF-toe.L", "shin_X150.L","thigh.fk.L", "shin.fk.L", "foot.fk.L", "heel.marker.L", "ball.marker.L", "toe.fk.L", "toe.marker.L", "thigh.ik.L", "knee.link.L", "shin.ik.L", "DEF-thigh.L", "thigh_X-90.L", "arm_hinge.L", "arm_socket.L", "upper_arm.L", "serratusIk.L", "forearm.L", "hand.L", "palm_pinky.L", "f_pinky.01.L", "f_pinky.02.L", "f_pinky.03.L", "DEF-f_pinky.03.L", "DEF-f_pinky.02.L", "pinky.L", "DEF-f_pinky.01.L", "thumb.01.L", "thumb.02.L", "thumb.03.L", "thumb.L", "palm_index.L", "f_index.01.L","f_index.02.L", "f_index.03.L", "DEF-f_index.03.L", "index.L", "DEF-f_index.01.L", "DEF-f_index.02.L", "palm_ring.L", "f_ring.01.L", "f_ring.02.L", "f_ring.03.L", "ring.L", "DEF-f_ring.01.L", "DEF-f_ring.02.L", "DEF-f_ring.03.L", "palm_middle.L", "f_middle.01.L", "f_middle.02.L", "f_middle.03.L", "DEF-f_middle.02.L", "DEF-f_middle.03.L", "middle.L", "DEF-palm_middle.L", "DEF-f_middle.01.L", "DEF-thumb.01.L", "DEF-thumb.02.L", "DEF-thumb.03.L", "shoulderIk.L", "DEF-elbow_fan.L", "DEF-forearm.01.L", "DEF-forearm.02.L", "DEF-forearm.03.L", "DEF-hand.L", "DEF-palm_pinky.L", "DEF-palm_ring.L", "DEF-palm_index.L", "forearm_X120.L", "upper_arm.fk.L", "forearm.fk.L", "hand.fk.L", "upper_arm.ik.L", "elbow.link.L", "forearm.ik.L", "DEF-upper_arm.L", "DEF-spine", "DEF-spine-1", "DEF-hips", "DEF-pelvis.R", "DEF-pelvis.L", "p_face", "p_lo_lid.R", "p_mouth_in.L", "p_nose", "p_lo_lip.R", "p_lo_lid.L", "p_cheek.R", "p_tongue", "p_brow_in.R", "p_cheek.L", "p_lo_lip_mid", "p_face_display", "p_mouth_out.L", "p_up_lid.L", "p_up_lid.R", "p_mouth_out.R", "p_up_lip.R", "p_mouth_in.R", "p_up_lip.L", "p_brow_out.L", "p_jaw", "p_brow_mid", "p_brow_out.R", "p_brow_in.L", "p_mouth_mid", "p_lo_lip.L", "p_up_lip_mid", "gaze_parent", "gaze", "ankle.L", "ankle.R", "foot.ik.L", "toe.rev.L", "foot.rev.L", "ankle.ik.L", "knee.pt.ik.L", "foot.pt.ik.L", "foot.ik.R", "toe.rev.R", "foot.rev.R", "foot.pt.ik.R", "ankle.ik.R", "knee.pt.ik.R", "hand.ik.L", "hand.ik.R"],

    "rtbn_rigify": [ "root", "MCH-foot_ik_root.L", "MCH-foot_ik_root.R", "MCH-hand_ik_root.L", "MCH-hand_ik_root.R",
        "DEF-spine", "DEF-spine.001", "DEF-spine.002", "DEF-spine.003", "DEF-spine.004", "DEF-spine.005",
        "DEF-spine.006", "torso", "chest", "MCH-spine.002", "MCH-pivot", "tweak_spine.002", "ORG-spine.002", "MCH-spine.003",
        "MCH-ROT-neck", "neck", "MCH-STR-neck", "MCH-spine.005", "tweak_spine.005", "ORG-spine.005", "MCH-ROT-head", "head",
        "ORG-spine.006", "ORG-face", "ORG-lip.T.L", "ORG-lip.B.L", "ORG-ear.L", "ORG-ear.L.001", "ORG-ear.R", "ORG-ear.R.001",
        "ORG-lip.T.R", "ORG-lip.B.R", "ORG-forehead.L", "ORG-forehead.L.001", "ORG-forehead.L.002", "ORG-temple.L",
        "ORG-cheek.B.L", "ORG-forehead.R", "ORG-forehead.R.001", "ORG-forehead.R.002", "ORG-temple.R", "ORG-cheek.B.R",
        "ORG-cheek.T.L", "ORG-cheek.T.R", "ORG-teeth.T", "ORG-teeth.B", "DEF-forehead.L", "DEF-forehead.R",
        "DEF-forehead.L.001", "DEF-forehead.R.001", "DEF-forehead.L.002", "DEF-forehead.R.002", "DEF-temple.L", "DEF-temple.R",
        "master_eye.L", "brow.B.L", "ORG-brow.B.L", "DEF-brow.B.L", "brow.B.L.001", "ORG-brow.B.L.001", "DEF-brow.B.L.001",
        "brow.B.L.002", "ORG-brow.B.L.002", "DEF-brow.B.L.002", "brow.B.L.003", "ORG-brow.B.L.003", "DEF-brow.B.L.003",
        "brow.B.L.004", "lid.B.L", "ORG-lid.B.L", "lid.B.L.001", "ORG-lid.B.L.001", "lid.B.L.002", "ORG-lid.B.L.002",
        "lid.B.L.003", "ORG-lid.B.L.003", "lid.T.L", "ORG-lid.T.L", "lid.T.L.001", "ORG-lid.T.L.001", "lid.T.L.002",
        "ORG-lid.T.L.002", "lid.T.L.003", "ORG-lid.T.L.003", "MCH-eye.L", "ORG-eye.L", "MCH-eye.L.001", "MCH-lid.B.L",
        "DEF-lid.B.L", "MCH-lid.B.L.001", "DEF-lid.B.L.001", "MCH-lid.B.L.002", "DEF-lid.B.L.002", "MCH-lid.B.L.003",
        "DEF-lid.B.L.003", "MCH-lid.T.L", "DEF-lid.T.L", "MCH-lid.T.L.001", "DEF-lid.T.L.001", "MCH-lid.T.L.002",
        "DEF-lid.T.L.002", "MCH-lid.T.L.003", "DEF-lid.T.L.003", "master_eye.R", "brow.B.R", "ORG-brow.B.R", "DEF-brow.B.R",
        "brow.B.R.001", "ORG-brow.B.R.001", "DEF-brow.B.R.001", "brow.B.R.002", "ORG-brow.B.R.002", "DEF-brow.B.R.002",
        "brow.B.R.003", "ORG-brow.B.R.003", "DEF-brow.B.R.003", "brow.B.R.004", "lid.B.R", "ORG-lid.B.R", "lid.B.R.001",
        "ORG-lid.B.R.001", "lid.B.R.002", "ORG-lid.B.R.002", "lid.B.R.003", "ORG-lid.B.R.003", "lid.T.R", "ORG-lid.T.R",
        "lid.T.R.001", "ORG-lid.T.R.001", "lid.T.R.002", "ORG-lid.T.R.002", "lid.T.R.003", "ORG-lid.T.R.003", "MCH-eye.R",
        "ORG-eye.R", "MCH-eye.R.001", "MCH-lid.B.R", "DEF-lid.B.R", "MCH-lid.B.R.001", "DEF-lid.B.R.001", "MCH-lid.B.R.002",
        "DEF-lid.B.R.002", "MCH-lid.B.R.003", "DEF-lid.B.R.003", "MCH-lid.T.R", "DEF-lid.T.R", "MCH-lid.T.R.001",
        "DEF-lid.T.R.001", "MCH-lid.T.R.002", "DEF-lid.T.R.002", "MCH-lid.T.R.003", "DEF-lid.T.R.003", "ear.L", "DEF-ear.L",
        "DEF-ear.L.001", "ear.L.002", "ORG-ear.L.002", "DEF-ear.L.002", "ear.L.003", "ORG-ear.L.003", "DEF-ear.L.003",
        "ear.L.004", "ORG-ear.L.004", "DEF-ear.L.004", "ear.R", "DEF-ear.R", "DEF-ear.R.001", "ear.R.002", "ORG-ear.R.002",
        "DEF-ear.R.002", "ear.R.003", "ORG-ear.R.003", "DEF-ear.R.003", "ear.R.004", "ORG-ear.R.004", "DEF-ear.R.004",
        "jaw_master", "teeth.B", "tongue_master", "tongue", "ORG-tongue", "DEF-tongue", "chin", "ORG-chin", "DEF-chin",
        "chin.001", "ORG-chin.001", "DEF-chin.001", "chin.L", "ORG-chin.L", "DEF-chin.L", "chin.R", "ORG-chin.R", "DEF-chin.R",
        "jaw", "ORG-jaw", "DEF-jaw", "jaw.L.001", "ORG-jaw.L.001", "DEF-jaw.L.001", "jaw.R.001", "ORG-jaw.R.001",
        "DEF-jaw.R.001", "tongue.003", "MCH-tongue.001", "tongue.001", "ORG-tongue.001", "DEF-tongue.001", "MCH-tongue.002",
        "tongue.002", "ORG-tongue.002", "DEF-tongue.002", "teeth.T", "brow.T.L", "ORG-brow.T.L", "DEF-cheek.T.L",
        "DEF-brow.T.L", "brow.T.L.001", "ORG-brow.T.L.001", "DEF-brow.T.L.001", "brow.T.L.002", "ORG-brow.T.L.002",
        "DEF-brow.T.L.002", "brow.T.L.003", "ORG-brow.T.L.003", "DEF-brow.T.L.003", "brow.T.R", "ORG-brow.T.R",
        "DEF-cheek.T.R", "DEF-brow.T.R", "brow.T.R.001", "ORG-brow.T.R.001", "DEF-brow.T.R.001", "brow.T.R.002",
        "ORG-brow.T.R.002", "DEF-brow.T.R.002", "brow.T.R.003", "ORG-brow.T.R.003", "DEF-brow.T.R.003", "jaw.L", "ORG-jaw.L",
        "DEF-jaw.L", "jaw.R", "ORG-jaw.R", "DEF-jaw.R", "nose", "ORG-nose", "DEF-nose", "nose.L", "ORG-nose.L", "DEF-nose.L",
        "nose.R", "ORG-nose.R", "DEF-nose.R", "MCH-mouth_lock", "MCH-jaw_master", "lip.B", "DEF-lip.B.L", "DEF-lip.B.R",
        "chin.002", "MCH-jaw_master.001", "lip.B.L.001", "ORG-lip.B.L.001", "DEF-lip.B.L.001", "lip.B.R.001",
        "ORG-lip.B.R.001", "DEF-lip.B.R.001", "MCH-jaw_master.002", "cheek.B.L.001", "ORG-cheek.B.L.001", "DEF-cheek.B.L.001",
        "cheek.B.R.001", "ORG-cheek.B.R.001", "DEF-cheek.B.R.001", "lips.L", "DEF-cheek.B.L", "lips.R", "DEF-cheek.B.R",
        "MCH-jaw_master.003", "lip.T.L.001", "ORG-lip.T.L.001", "DEF-lip.T.L.001", "lip.T.R.001", "ORG-lip.T.R.001",
        "DEF-lip.T.R.001", "lip.T", "DEF-lip.T.L", "DEF-lip.T.R", "nose.005", "MCH-jaw_master.004", "nose_master", "nose.002",
        "ORG-nose.002", "DEF-nose.002", "nose.001", "ORG-nose.001", "DEF-nose.001", "nose.003", "ORG-nose.003", "DEF-nose.003",
        "nose.004", "ORG-nose.004", "DEF-nose.004", "nose.L.001", "ORG-nose.L.001", "DEF-nose.L.001", "nose.R.001",
        "ORG-nose.R.001", "DEF-nose.R.001", "cheek.T.L.001", "ORG-cheek.T.L.001", "DEF-cheek.T.L.001", "cheek.T.R.001",
        "ORG-cheek.T.R.001", "DEF-cheek.T.R.001", "tweak_spine.004", "ORG-spine.004", "MCH-WGT-chest", "tweak_spine.003",
        "ORG-spine.003", "ORG-shoulder.L", "ORG-upper_arm.L", "MCH-upper_arm_tweak.L", "upper_arm_tweak.L",
        "MCH-upper_arm_tweak.L.001", "upper_arm_tweak.L.001", "ORG-forearm.L", "MCH-forearm_tweak.L", "forearm_tweak.L",
        "MCH-forearm_tweak.L.001", "forearm_tweak.L.001", "ORG-hand.L", "MCH-hand_tweak.L", "hand_tweak.L", "DEF-shoulder.L",
        "MCH-upper_arm_parent.L", "upper_arm_ik.L", "MCH-upper_arm_ik.L", "MCH-upper_arm_ik_stretch.L", "upper_arm_fk.L",
        "forearm_fk.L", "MCH-hand_fk.L", "hand_fk.L", "MCH-upper_arm_parent_socket.L", "upper_arm_parent.L", "DEF-upper_arm.L",
        "DEF-upper_arm.L.001", "DEF-forearm.L", "DEF-forearm.L.001", "DEF-hand.L", "ORG-palm.01.L", "DEF-palm.01.L",
        "f_index.01.L", "f_index.02.L", "f_index.03.L", "tweak_f_index.03.L", "ORG-f_index.03.L", "tweak_f_index.03.L.001",
        "tweak_f_index.02.L", "ORG-f_index.02.L", "tweak_f_index.01.L", "ORG-f_index.01.L", "DEF-f_index.01.L",
        "DEF-f_index.02.L", "DEF-f_index.03.L","thumb.01.L", "thumb.02.L", "thumb.03.L", "tweak_thumb.03.L", "ORG-thumb.03.L",
        "tweak_thumb.03.L.001", "tweak_thumb.02.L", "ORG-thumb.02.L", "tweak_thumb.01.L", "ORG-thumb.01.L", "DEF-thumb.01.L",
        "DEF-thumb.02.L", "DEF-thumb.03.L", "ORG-palm.02.L", "DEF-palm.02.L", "f_middle.01.L", "f_middle.02.L",
        "f_middle.03.L", "tweak_f_middle.03.L", "ORG-f_middle.03.L", "tweak_f_middle.03.L.001", "tweak_f_middle.02.L",
        "ORG-f_middle.02.L", "tweak_f_middle.01.L", "ORG-f_middle.01.L", "DEF-f_middle.01.L", "DEF-f_middle.02.L",
        "DEF-f_middle.03.L", "ORG-palm.03.L", "DEF-palm.03.L", "f_ring.01.L", "f_ring.02.L", "f_ring.03.L",
        "tweak_f_ring.03.L", "ORG-f_ring.03.L", "tweak_f_ring.03.L.001", "tweak_f_ring.02.L", "ORG-f_ring.02.L",
        "tweak_f_ring.01.L", "ORG-f_ring.01.L", "DEF-f_ring.01.L", "DEF-f_ring.02.L", "DEF-f_ring.03.L", "ORG-palm.04.L",
        "DEF-palm.04.L", "f_pinky.01.L", "f_pinky.02.L", "f_pinky.03.L", "tweak_f_pinky.03.L", "ORG-f_pinky.03.L",
        "tweak_f_pinky.03.L.001", "tweak_f_pinky.02.L", "ORG-f_pinky.02.L", "tweak_f_pinky.01.L", "ORG-f_pinky.01.L",
        "DEF-f_pinky.01.L", "DEF-f_pinky.02.L", "DEF-f_pinky.03.L", "palm.L", "ORG-shoulder.R", "ORG-upper_arm.R",
        "MCH-upper_arm_tweak.R", "upper_arm_tweak.R", "MCH-upper_arm_tweak.R.001", "upper_arm_tweak.R.001", "ORG-forearm.R",
        "MCH-forearm_tweak.R", "forearm_tweak.R", "MCH-forearm_tweak.R.001", "forearm_tweak.R.001", "ORG-hand.R",
        "MCH-hand_tweak.R", "hand_tweak.R", "DEF-shoulder.R", "MCH-upper_arm_parent.R", "upper_arm_ik.R", "MCH-upper_arm_ik.R",
        "MCH-upper_arm_ik_stretch.R", "upper_arm_fk.R", "forearm_fk.R", "MCH-hand_fk.R", "hand_fk.R",
        "MCH-upper_arm_parent_socket.R", "upper_arm_parent.R", "DEF-upper_arm.R", "DEF-upper_arm.R.001", "DEF-forearm.R",
        "DEF-forearm.R.001", "DEF-hand.R", "ORG-palm.01.R", "DEF-palm.01.R", "f_index.01.R", "f_index.02.R",
        "f_index.03.R", "tweak_f_index.03.R", "ORG-f_index.03.R", "tweak_f_index.03.R.001", "tweak_f_index.02.R",
        "ORG-f_index.02.R", "tweak_f_index.01.R", "ORG-f_index.01.R", "DEF-f_index.01.R", "DEF-f_index.02.R",
        "DEF-f_index.03.R", "thumb.01.R", "thumb.02.R", "thumb.03.R", "tweak_thumb.03.R", "ORG-thumb.03.R",
        "tweak_thumb.03.R.001", "tweak_thumb.02.R", "ORG-thumb.02.R", "tweak_thumb.01.R", "ORG-thumb.01.R",
        "DEF-thumb.01.R", "DEF-thumb.02.R", "DEF-thumb.03.R", "ORG-palm.02.R", "DEF-palm.02.R", "f_middle.01.R",
        "f_middle.02.R", "f_middle.03.R", "tweak_f_middle.03.R", "ORG-f_middle.03.R", "tweak_f_middle.03.R.001",
        "tweak_f_middle.02.R", "ORG-f_middle.02.R", "tweak_f_middle.01.R", "ORG-f_middle.01.R", "DEF-f_middle.01.R",
        "DEF-f_middle.02.R", "DEF-f_middle.03.R", "ORG-palm.03.R", "DEF-palm.03.R", "f_ring.01.R", "f_ring.02.R",
        "f_ring.03.R", "tweak_f_ring.03.R", "ORG-f_ring.03.R", "tweak_f_ring.03.R.001", "tweak_f_ring.02.R", "ORG-f_ring.02.R",
        "tweak_f_ring.01.R", "ORG-f_ring.01.R", "DEF-f_ring.01.R", "DEF-f_ring.02.R", "DEF-f_ring.03.R", "ORG-palm.04.R",
        "DEF-palm.04.R", "f_pinky.01.R", "f_pinky.02.R", "f_pinky.03.R", "tweak_f_pinky.03.R", "ORG-f_pinky.03.R",
        "tweak_f_pinky.03.R.001", "tweak_f_pinky.02.R", "ORG-f_pinky.02.R", "tweak_f_pinky.01.R", "ORG-f_pinky.01.R",
        "DEF-f_pinky.01.R", "DEF-f_pinky.02.R", "DEF-f_pinky.03.R", "palm.R", "ORG-breast.L", "DEF-breast.L", "ORG-breast.R",
        "DEF-breast.R", "breast.L", "breast.R", "shoulder.L", "shoulder.R", "MCH-hand_ik_parent.R", "MCH-hand_ik_parent.L",
        "hips", "MCH-spine.001", "MCH-spine", "MCH-WGT-hips", "tweak_spine", "ORG-spine", "ORG-pelvis.L", "DEF-pelvis.L",
        "ORG-pelvis.R", "DEF-pelvis.R", "ORG-thigh.L", "MCH-thigh_tweak.L", "thigh_tweak.L", "MCH-thigh_tweak.L.001",
        "thigh_tweak.L.001", "ORG-shin.L", "MCH-shin_tweak.L", "shin_tweak.L", "MCH-shin_tweak.L.001", "shin_tweak.L.001",
        "ORG-foot.L", "ORG-heel.02.L", "MCH-foot_tweak.L", "foot_tweak.L", "MCH-toe.L", "ORG-toe.L", "toe.L", "ORG-thigh.R",
        "MCH-thigh_tweak.R", "thigh_tweak.R", "MCH-thigh_tweak.R.001", "thigh_tweak.R.001", "ORG-shin.R", "MCH-shin_tweak.R",
        "shin_tweak.R", "MCH-shin_tweak.R.001", "shin_tweak.R.001", "ORG-foot.R", "ORG-heel.02.R", "MCH-foot_tweak.R",
        "foot_tweak.R", "MCH-toe.R", "ORG-toe.R", "toe.R", "MCH-thigh_parent.L", "thigh_ik.L", "MCH-thigh_ik.L",
        "MCH-thigh_ik_stretch.L", "thigh_fk.L", "shin_fk.L", "MCH-foot_fk.L", "foot_fk.L", "MCH-thigh_parent_socket.L",
        "thigh_parent.L", "DEF-thigh.L", "DEF-thigh.L.001", "DEF-shin.L", "DEF-shin.L.001", "DEF-foot.L", "DEF-toe.L",
        "MCH-thigh_parent.R", "thigh_ik.R", "MCH-thigh_ik.R", "MCH-thigh_ik_stretch.R", "thigh_fk.R", "shin_fk.R",
        "MCH-foot_fk.R", "foot_fk.R", "MCH-thigh_parent_socket.R", "thigh_parent.R", "DEF-thigh.R", "DEF-thigh.R.001",
        "DEF-shin.R", "DEF-shin.R.001", "DEF-foot.R", "DEF-toe.R", "tweak_spine.001", "ORG-spine.001", "MCH-foot_ik_parent.R",
        "MCH-foot_ik_parent.L", "MCH-eyes_parent", "eyes", "eye.L", "eye.R", "VIS_thigh_ik_pole.L", "VIS_thigh_ik_pole.R",
        "VIS_upper_arm_ik_pole.L", "VIS_upper_arm_ik_pole.R", "MCH-hand_pole_ik_socket.R", "upper_arm_ik_target.R",
        "MCH-hand_ik_socket.R", "hand_ik.R", "MCH-upper_arm_ik_target.R", "MCH-hand_pole_ik_socket.L", "upper_arm_ik_target.L",
        "MCH-hand_ik_socket.L", "hand_ik.L", "MCH-upper_arm_ik_target.L", "MCH-foot_pole_ik_socket.R", "thigh_ik_target.R",
        "MCH-foot_ik_socket.R", "foot_ik.R", "MCH-heel.02_rock.R.001", "MCH-heel.02_rock.R", "MCH-heel.02_roll.R.001",
        "MCH-heel.02_roll.R", "foot_heel_ik.R", "MCH-thigh_ik_target.R", "MCH-foot_pole_ik_socket.L", "thigh_ik_target.L",
        "MCH-foot_ik_socket.L", "foot_ik.L", "MCH-heel.02_rock.L.001", "MCH-heel.02_rock.L", "MCH-heel.02_roll.L.001",
        "MCH-heel.02_roll.L", "foot_heel_ik.L", "MCH-thigh_ik_target.L"
    ],
}

amh2b_rig_stitch_dest_list = {
    "import_mhx": {
        "makehuman_cmu_mb": {
            "blist_dup_swap_stitch_torso": [("Hips", "root", 0, 0), ("LowerBack", "spine", 0, 0), ("Spine", "chest", 0, 0), ("Spine1", "chest-1", 0, 0), ("Neck", "neck", 0, 0), ("Neck1", "neck-1", 0, 0), ("Head", "head", 0, 0)],
            "blist_setparent_torso": [("Hips", "master")],
            "blist_dup_swap_stitch_arm_L_fk": [("LeftArm", "arm_base.L", 0.06, 0.35), ("LeftShoulder", "clavicle.L", 0, 0), ("LeftForeArm", "forearm.fk.L", 0, 0), ("LeftHand", "hand.fk.L", 0, 0)],
            "blist_dup_swap_stitch_arm_R_fk": [("RightArm", "arm_base.R", 0.06, 0.35), ("RightShoulder", "clavicle.R", 0, 0), ("RightForeArm", "forearm.fk.R", 0, 0), ("RightHand", "hand.fk.R", 0, 0)],
            "blist_setparent_arm_L_ik": [("elbow.pt.ik.L", "LeftForeArm"), ("elbow.link.L", "LeftForeArm"), ("hand.ik.L", "LeftHand")],
            "blist_setparent_arm_R_ik": [("elbow.pt.ik.R", "RightForeArm"), ("elbow.link.R", "RightForeArm"), ("hand.ik.R", "RightHand")],
            "blist_dup_swap_stitch_leg_L_fk": [("LHipJoint", "leg_socket.L", 0, 0), ("LeftUpLeg", "thigh.fk.L", 0, 0), ("LeftLeg", "shin.fk.L", 0, 0), ("LeftFoot", "foot.fk.L", 0, 0), ("LeftToeBase", "toe.fk.L", 0, 0)],
            "blist_dup_swap_stitch_leg_R_fk": [("RHipJoint", "leg_socket.R", 0, 0), ("RightUpLeg", "thigh.fk.R", 0, 0), ("RightLeg", "shin.fk.R", 0, 0), ("RightFoot", "foot.fk.R", 0, 0), ("RightToeBase", "toe.fk.R", 0, 0)],
            "blist_setparent_leg_L_ik": [("knee.pt.ik.L", "LeftLeg"), ("knee.link.L", "LeftLeg"), ("foot.ik.L", "LeftFoot")],
            "blist_setparent_leg_R_ik": [("knee.pt.ik.R", "RightLeg"), ("knee.link.R", "RightLeg"), ("foot.ik.R", "RightFoot")],
        },
        "mixamo_native_fbx": {
            "blist_dup_swap_stitch_torso": [("*:Hips", "root", 0, 0), ("*:Spine", "spine-1", 0, 0), ("*:Spine1", "chest", 0, 0), ("*:Spine2", "chest-1", 0, 0), ("*:Neck", "neck", 0, 0), ("*:Head", "head", 0, 0)],
            "blist_setparent_torso": [("*:Hips", "master")],
            "blist_dup_swap_stitch_arm_L_fk": [("*:LeftShoulder", "clavicle.L", 0, 0), ("*:LeftArm", "arm_base.L", 0.06, 0.35), ("*:LeftForeArm", "forearm.fk.L", 0, 0), ("*:LeftHand", "hand.fk.L", 0, 0)],
            "blist_dup_swap_stitch_arm_R_fk": [("*:RightShoulder", "clavicle.R", 0, 0), ("*:RightArm", "arm_base.R", 0.06, 0.35), ("*:RightForeArm", "forearm.fk.R", 0, 0), ("*:RightHand", "hand.fk.R", 0, 0)],
            "blist_setparent_arm_L_ik": [("hand.ik.L", "*:LeftHand"), ("elbow.pt.ik.L", "*:LeftForeArm"), ("elbow.link.L", "*:LeftForeArm")],
            "blist_setparent_arm_R_ik": [("hand.ik.R", "*:RightHand"), ("elbow.pt.ik.R", "*:RightForeArm"), ("elbow.link.R", "*:RightForeArm")],
            "blist_dup_swap_stitch_leg_L_fk": [("*:LeftUpLeg", "thigh.fk.L", 0, 0), ("*:LeftLeg", "shin.fk.L", 0, 0), ("*:LeftFoot", "foot.fk.L", 0, 0), ("*:LeftToeBase", "toe.fk.L", 0, 0)],
            "blist_dup_swap_stitch_leg_R_fk": [("*:RightUpLeg", "thigh.fk.R", 0, 0), ("*:RightLeg", "shin.fk.R", 0, 0), ("*:RightFoot", "foot.fk.R", 0, 0), ("*:RightToeBase", "toe.fk.R", 0, 0)],
            "blist_setparent_leg_L_ik": [("knee.pt.ik.L", "*:LeftLeg"), ("knee.link.L", "*:LeftLeg"), ("foot.ik.L", "*:LeftFoot")],
            "blist_setparent_leg_R_ik": [("knee.pt.ik.R", "*:RightLeg"), ("knee.link.R", "*:RightLeg"), ("foot.ik.R", "*:RightFoot")],
            "blist_dup_swap_stitch_fingers_L": [("*:LeftHandThumb1", "thumb.01.L", 0, 0), ("*:LeftHandThumb2", "thumb.02.L", 0, 0), ("*:LeftHandThumb3", "thumb.03.L", 0, 0), ("*:LeftHandIndex1", "f_index.01.L", 0, 0), ("*:LeftHandIndex2", "f_index.02.L", 0, 0), ("*:LeftHandIndex3", "f_index.03.L", 0, 0), ("*:LeftHandMiddle1", "f_middle.01.L", 0, 0), ("*:LeftHandMiddle2", "f_middle.02.L", 0, 0), ("*:LeftHandMiddle3", "f_middle.03.L", 0, 0), ("*:LeftHandRing1", "f_ring.01.L", 0, 0), ("*:LeftHandRing2", "f_ring.02.L", 0, 0), ("*:LeftHandRing3", "f_ring.03.L", 0, 0), ("*:LeftHandPinky1", "f_pinky.01.L", 0, 0), ("*:LeftHandPinky2", "f_pinky.02.L", 0, 0), ("*:LeftHandPinky3", "f_pinky.03.L", 0, 0)],
            "blist_dup_swap_stitch_fingers_R": [("*:RightHandThumb1", "thumb.01.R", 0, 0), ("*:RightHandThumb2", "thumb.02.R", 0, 0), ("*:RightHandThumb3", "thumb.03.R", 0, 0), ("*:RightHandIndex1", "f_index.01.R", 0, 0), ("*:RightHandIndex2", "f_index.02.R", 0, 0), ("*:RightHandIndex3", "f_index.03.R", 0, 0), ("*:RightHandMiddle1", "f_middle.01.R", 0, 0), ("*:RightHandMiddle2", "f_middle.02.R", 0, 0), ("*:RightHandMiddle3", "f_middle.03.R", 0, 0), ("*:RightHandRing1", "f_ring.01.R", 0, 0), ("*:RightHandRing2", "f_ring.02.R", 0, 0), ("*:RightHandRing3", "f_ring.03.R", 0, 0), ("*:RightHandPinky1", "f_pinky.01.R", 0, 0), ("*:RightHandPinky2", "f_pinky.02.R", 0, 0), ("*:RightHandPinky3", "f_pinky.03.R", 0, 0)],
        }
    },
    "rtbn_rigify": {
        "mixamo_native_fbx": {
            "blist_dup_swap_stitch_torso": [("*:LeftShoulder", "shoulder.L", 0, 0), ("*:RightShoulder", "shoulder.R", 0, 0),
                                            ("*:Neck", "neck", 0, 0), ("*:Head", "head", 0, 0),
            ],
            "blist_setparent_torso": [("*:Hips", "root"), ("torso", "*:Spine"), ("MCH-WGT-hips", "*:Hips"),
                                      ("MCH-spine.003", "*:Spine2")
            ],

            "blist_dup_swap_stitch_arm_L_ik": [("*:LeftArm", "upper_arm_ik.L", 0, 0),
            ],
            "blist_setparent_arm_L_ik": [("hand_ik.L", "*:LeftHand"),
            ],

            "blist_dup_swap_stitch_arm_R_ik": [("*:RightArm", "upper_arm_ik.R", 0, 0),
            ],
            "blist_setparent_arm_R_ik": [("hand_ik.R", "*:RightHand"),
            ],
        }
    }
}
