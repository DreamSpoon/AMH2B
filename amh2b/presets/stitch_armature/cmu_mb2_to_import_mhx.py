{
    "label": "CMU MotionBuilder2 to Import MHX",
    "data": [
        { "op": "join_armatures" },
        { "op": "dup_swap_stitch", "data": [
                ("target", "Hips", "root", 0, 0), ("target", "LowerBack", "spine", 0, 0), ("target", "Spine", "chest", 0, 0), ("target", "Spine1", "chest-1", 0, 0), ("target", "Neck", "neck", 0, 0), ("target", "Neck1", "neck-1", 0, 0), ("target", "Head", "head", 0, 0),
                ("target", "LeftArm", "arm_base.L", 0.06, 0.35), ("target", "LeftShoulder", "clavicle.L", 0, 0), ("target", "LeftForeArm", "forearm.fk.L", 0, 0), ("target", "LeftHand", "hand.fk.L", 0, 0),
                ("target", "RightArm", "arm_base.R", 0.06, 0.35), ("target", "RightShoulder", "clavicle.R", 0, 0), ("target", "RightForeArm", "forearm.fk.R", 0, 0), ("target", "RightHand", "hand.fk.R", 0, 0),
                ("target", "LHipJoint", "leg_socket.L", 0, 0), ("target", "LeftUpLeg", "thigh.fk.L", 0, 0), ("target", "LeftLeg", "shin.fk.L", 0, 0), ("target", "LeftFoot", "foot.fk.L", 0, 0), ("target", "LeftToeBase", "toe.fk.L", 0, 0),
                ("target", "RHipJoint", "leg_socket.R", 0, 0), ("target", "RightUpLeg", "thigh.fk.R", 0, 0), ("target", "RightLeg", "shin.fk.R", 0, 0), ("target", "RightFoot", "foot.fk.R", 0, 0), ("target", "RightToeBase", "toe.fk.R", 0, 0),
                ]
            },
        { "op": "set_parent_bone", "data": [
                ("target", "Hips", "master"),
                ("target", "elbow.pt.ik.L", "LeftForeArm"), ("target", "elbow.link.L", "LeftForeArm"), ("target", "hand.ik.L", "LeftHand"),
                ("target", "elbow.pt.ik.R", "RightForeArm"), ("target", "elbow.link.R", "RightForeArm"), ("target", "hand.ik.R", "RightHand"),
                ("target", "knee.pt.ik.L", "LeftLeg"), ("target", "knee.link.L", "LeftLeg"), ("target", "foot.ik.L", "LeftFoot"),
                ("target", "knee.pt.ik.R", "RightLeg"), ("target", "knee.link.R", "RightLeg"), ("target", "foot.ik.R", "RightFoot"),
                ]
            }
        ]
    }
