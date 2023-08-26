{
    "label": "Mixamo 5 Finger to MHX Rigify",
    "data": [
        { "op": "join_armatures" },
        { "op": "dup_swap_stitch", "data": [
                # hips to head
                ("target", "*:Neck", "neck", 0, 0),
                ("target", "*:Head", "head", 0, 0),
                # left arm
                ("target", "*:LeftShoulder", "shoulder.L", 0, 0),
                ("target", "*:LeftArm", "upper_arm_ik.L", 0, 0),
                ("target", "*:LeftHandThumb1", "thumb.01.L", 0, 0),
                ("target", "*:LeftHandThumb2", "thumb.02.L", 0, 0),
                ("target", "*:LeftHandThumb3", "thumb.03.L", 0, 0),
                ("target", "*:LeftHandIndex1", "f_index.01.L", 0, 0),
                ("target", "*:LeftHandIndex2", "f_index.02.L", 0, 0),
                ("target", "*:LeftHandIndex3", "f_index.03.L", 0, 0),
                ("target", "*:LeftHandMiddle1", "f_middle.01.L", 0, 0),
                ("target", "*:LeftHandMiddle2", "f_middle.02.L", 0, 0),
                ("target", "*:LeftHandMiddle3", "f_middle.03.L", 0, 0),
                ("target", "*:LeftHandRing1", "f_ring.01.L", 0, 0),
                ("target", "*:LeftHandRing2", "f_ring.02.L", 0, 0),
                ("target", "*:LeftHandRing3", "f_ring.03.L", 0, 0),
                ("target", "*:LeftHandPinky1", "f_pinky.01.L", 0, 0),
                ("target", "*:LeftHandPinky2", "f_pinky.02.L", 0, 0),
                ("target", "*:LeftHandPinky3", "f_pinky.03.L", 0, 0),
                # left leg
                ("target", "*:LeftUpLeg", "thigh_ik.L", 0, 0),
                ("target", "*:LeftToeBase", "toe.L", 0, 0),
                # right arm
                ("target", "*:RightShoulder", "shoulder.R", 0, 0),
                ("target", "*:RightArm", "upper_arm_ik.R", 0, 0),
                ("target", "*:RightHandThumb1", "thumb.01.R", 0, 0),
                ("target", "*:RightHandThumb2", "thumb.02.R", 0, 0),
                ("target", "*:RightHandThumb3", "thumb.03.R", 0, 0),
                ("target", "*:RightHandIndex1", "f_index.01.R", 0, 0),
                ("target", "*:RightHandIndex2", "f_index.02.R", 0, 0),
                ("target", "*:RightHandIndex3", "f_index.03.R", 0, 0),
                ("target", "*:RightHandMiddle1", "f_middle.01.R", 0, 0),
                ("target", "*:RightHandMiddle2", "f_middle.02.R", 0, 0),
                ("target", "*:RightHandMiddle3", "f_middle.03.R", 0, 0),
                ("target", "*:RightHandRing1", "f_ring.01.R", 0, 0),
                ("target", "*:RightHandRing2", "f_ring.02.R", 0, 0),
                ("target", "*:RightHandRing3", "f_ring.03.R", 0, 0),
                ("target", "*:RightHandPinky1", "f_pinky.01.R", 0, 0),
                ("target", "*:RightHandPinky2", "f_pinky.02.R", 0, 0),
                ("target", "*:RightHandPinky3", "f_pinky.03.R", 0, 0),
                # right leg
                ("target", "*:RightUpLeg", "thigh_ik.R", 0, 0),
                ("target", "*:RightToeBase", "toe.R", 0, 0),
                ]
            },
        { "op": "set_parent_bone", "data": [
                # hips to head
                ("target", "*:Hips", "root"),
                ("target", "torso", "*:Spine"),
                ("target", "MCH-WGT-hips", "*:Hips"),
                ("target", "MCH-spine.003", "*:Spine2"),
                # left arm
                ("target", "hand_ik.L", "*:LeftHand"),
                # left leg
                ("target", "foot_ik.L", "*:LeftFoot"),
                # right arm
                ("target", "hand_ik.R", "*:RightHand"),
                # right leg
                ("target", "foot_ik.R", "*:RightFoot"),
                ]
            }
        ]
    }
