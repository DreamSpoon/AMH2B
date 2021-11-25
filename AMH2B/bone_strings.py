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
    }
}
