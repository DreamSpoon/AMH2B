{
    "label": "MPFB2 Mixamo to MPFB2 Default",
    "data": [
        { "op": "create_transfer_armature" },
        { "op": "transfer_transforms", "data": [ ("*:Hips", "root", 0.0, 0.0, 1.0) ] },
        { "op": "transfer_rotation", "data": [ ("*:Spine", "spine03"), ("*:Spine1", "spine02"), ("*:Spine2", "spine01"),
                                               ("*:Neck", "neck01"), ("*:Head", "neck02"), ("*:Head", "head") ]
            },
        { "op": "transfer_transforms", "data": [ ("*:LeftForeArm", "left_elbow_ik", 0.0, 0.0, 1.0),
            ("*:LeftHand", "left_hand_ik", 0.0, 0.0, 1.0), ("*:LeftLeg", "left_knee_ik", 0.0, 0.0, 1.0),
            ("*:LeftFoot", "left_foot_ik", 0.0, 0.0, 1.0)] },
        { "op": "transfer_rotation", "data": [ ("*:LeftShoulder", "clavicle.L"),
            ("*:LeftHandThumb2", "left_finger1_grip"), ("*:LeftHandIndex2", "left_finger2_grip"),
            ("*:LeftHandMiddle2", "left_finger3_grip"), ("*:LeftHandRing2", "left_finger4_grip"),
            ("*:LeftHandPinky2", "left_finger5_grip"), ("*:LeftToeBase", "toe1-1.L"), ("*:LeftToeBase", "toe2-1.L"),
            ("*:LeftToeBase", "toe3-1.L"), ("*:LeftToeBase", "toe4-1.L"), ("*:LeftToeBase", "toe5-1.L") ]
            },
        { "op": "transfer_transforms", "data": [ ("*:RightForeArm", "right_elbow_ik", 0.0, 0.0, 1.0),
            ("*:RightHand", "right_hand_ik", 0.0, 0.0, 1.0), ("*:RightLeg", "right_knee_ik", 0.0, 0.0, 1.0),
            ("*:RightFoot", "right_foot_ik", 0.0, 0.0, 1.0)] },
        { "op": "transfer_rotation", "data": [ ("*:RightShoulder", "clavicle.R"),
            ("*:RightHandThumb2", "right_finger1_grip"), ("*:RightHandIndex2", "right_finger2_grip"),
            ("*:RightHandMiddle2", "right_finger3_grip"), ("*:RightHandRing2", "right_finger4_grip"),
            ("*:RightHandPinky2", "right_finger5_grip"), ("*:RightToeBase", "toe1-1.R"), ("*:RightToeBase", "toe2-1.R"),
            ("*:RightToeBase", "toe3-1.R"), ("*:RightToeBase", "toe4-1.R"), ("*:RightToeBase", "toe5-1.R") ]
            },
        ]
    }
