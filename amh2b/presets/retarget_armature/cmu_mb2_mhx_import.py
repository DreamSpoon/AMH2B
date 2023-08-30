{
    "label": "CMU MotionBuilder2 to MHX Import",
    "data": [
        { "op": "create_transfer_armature" },
        { "op": "transfer_transforms", "data": [
                ("Hips", "root", 0.0, 0.0, 1.0),
                ("LeftForeArm""elbow.pt.ik.L", 0.0, 0.0, 1.0), ("LeftForeArm", "elbow.link.L", 0.0, 0.0, 1.0),
                ("LeftHand", "hand.ik.L", 0.0, 0.0, 1.0),
                ("LeftLeg", "knee.pt.ik.L", 0.0, 0.0, 1.0), ("LeftLeg", "knee.link.L", 0.0, 0.0, 1.0),
                ("LeftFoot", "foot.ik.L", 0.0, 0.0, 1.0),
                ("RightForeArm", "elbow.pt.ik.R", 0.0, 0.0, 1.0), ("RightForeArm", "elbow.link.R", 0.0, 0.0, 1.0),
                ("RightHand", "hand.ik.R", 0.0, 0.0, 1.0),
                ("RightLeg", "knee.pt.ik.R", 0.0, 0.0, 1.0), ("RightLeg", "knee.link.R", 0.0, 0.0, 1.0),
                ("RightFoot", "foot.ik.R", 0.0, 0.0, 1.0),
                ]
            },
        { "op": "transfer_rotation", "data": [ ("LowerBack", "spine"), ("Spine", "chest"), ("Spine1", "chest-1"),
                ("Neck", "neck"), ("Neck1", "neck-1"), ("Head", "head"),
                ("LeftArm", "arm_base.L"), ("LeftShoulder", "clavicle.L"), ("LeftForeArm", "forearm.fk.L"),
                ("LeftHand", "hand.fk.L"), ("LHipJoint", "leg_socket.L"), ("LeftUpLeg", "thigh.fk.L"),
                ("LeftLeg", "shin.fk.L"), ("LeftFoot", "foot.fk.L"), ("LeftToeBase", "toe.fk.L"),
                ("RightArm", "arm_base.R"), ("RightShoulder", "clavicle.R"), ("RightForeArm", "forearm.fk.R"),
                ("RightHand", "hand.fk.R"), ("RHipJoint", "leg_socket.R"), ("RightUpLeg", "thigh.fk.R"),
                ("RightLeg", "shin.fk.R"), ("RightFoot", "foot.fk.R"), ("RightToeBase", "toe.fk.R"),
                ("LeftHandFinger1", "index.L"), ("LeftHandFinger1", "middle.L"), ("LeftHandFinger1", "ring.L"),
                ("LeftHandFinger1", "pinky.L"), ("LThumb", "thumb.L"),
                ("RightHandFinger1", "index.R"), ("RightHandFinger1", "middle.R"), ("RightHandFinger1", "ring.R"),
                ("RightHandFinger1", "pinky.R"), ("LThumb", "thumb.R"),
                ]
            },
        ]
    }
