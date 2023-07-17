{
    "label": "CMU MotionBuilder2 to Rigify Human",
    "data": [
        { "op": "join_armatures" },
        { "op": "dup_swap_stitch", "data": [
                # hips to head
                ("target", "Neck", "neck", 0, 0),
                ("target", "Head", "head", 0, 0),
                # left arm
                ("target", "LeftShoulder", "shoulder.L", 0, 0),
                ("target", "LeftArm", "upper_arm_ik.L", 0, 0),
                # left leg
                ("target", "LeftUpLeg", "thigh_ik.L", 0, 0),
                ("target", "LeftToeBase", "toe.L", 0, 0),
                # right arm
                ("target", "RightShoulder", "shoulder.R", 0, 0),
                ("target", "RightArm", "upper_arm_ik.R", 0, 0),
                # right leg
                ("target", "RightUpLeg", "thigh_ik.R", 0, 0),
                ("target", "RightToeBase", "toe.R", 0, 0),
                 ]
             },
        { "op": "set_parent_bone", "data": [
                # hips to head
                ("target", "torso", "Hips"),
                # left arm
                ("target", "hand_ik.L", "LeftHand"),
                # left leg
                ("target", "foot_ik.L", "LeftFoot"),
                # right arm
                ("target", "hand_ik.R", "RightHand"),
                # right leg
                ("target", "foot_ik.R", "RightFoot"),
                ]
            }
        ]
    }
