{
    "label": "Mixamo 65 Bone to MHX Import",
    "data": [
        { "op": "create_transfer_armature" },
        { "op": "transfer_transforms", "data": [ ("*:Hips", "root", 0.0, 0.0, 1.0),
                ("*:LeftHand", "hand.ik.L", 0.0, 0.0, 1.0), ("*:LeftForeArm", "elbow.pt.ik.L", 0.0, 0.0, 1.0),
                ("*:LeftForeArm", "elbow.link.L", 0.0, 0.0, 1.0),
                ("*:RightHand", "hand.ik.R", 0.0, 0.0, 1.0), ("*:RightForeArm", "elbow.pt.ik.R", 0.0, 0.0, 1.0),
                ("*:RightForeArm", "elbow.link.R", 0.0, 0.0, 1.0), ("*:LeftLeg", "knee.pt.ik.L", 0.0, 0.0, 1.0),
                ("*:LeftLeg", "knee.link.L", 0.0, 0.0, 1.0), ("*:LeftFoot", "foot.ik.L", 0.0, 0.0, 1.0),
                ("*:RightLeg", "knee.pt.ik.R", 0.0, 0.0, 1.0), ("knee.link.R", "*:RightLeg", 0.0, 0.0, 1.0),
                ("foot.ik.R", "*:RightFoot", 0.0, 0.0, 1.0), ] },
        { "op": "transfer_rotation", "data": [ ("*:Spine", "spine-1"), ("*:Spine1", "chest"), ("*:Spine2", "chest-1"),
                ("*:Neck", "neck"), ("*:Head", "head"),
                ("*:LeftShoulder", "clavicle.L"), ("*:LeftArm", "arm_base.L"), ("*:LeftForeArm", "forearm.fk.L"),
                ("*:LeftHand", "hand.fk.L"),
                ("*:RightShoulder", "clavicle.R"), ("*:RightArm", "arm_base.R"), ("*:RightForeArm", "forearm.fk.R"),
                ("*:RightHand", "hand.fk.R"),
                ("*:LeftUpLeg", "thigh.fk.L"), ("*:LeftLeg", "shin.fk.L"), ("*:LeftFoot", "foot.fk.L"),
                ("*:LeftToeBase", "toe.fk.L"),
                ("*:RightUpLeg", "thigh.fk.R"), ("*:RightLeg", "shin.fk.R"), ("*:RightFoot", "foot.fk.R"),
                ("*:RightToeBase", "toe.fk.R"),
                ("*:LeftHandThumb1", "thumb.01.L"), ("*:LeftHandThumb2", "thumb.02.L"),
                ("*:LeftHandThumb3", "thumb.03.L"), ("*:LeftHandIndex1", "f_index.01.L"),
                ("*:LeftHandIndex2", "f_index.02.L"), ("*:LeftHandIndex3", "f_index.03.L"),
                ("*:LeftHandMiddle1", "f_middle.01.L"), ("*:LeftHandMiddle2", "f_middle.02.L"),
                ("*:LeftHandMiddle3", "f_middle.03.L"), ("*:LeftHandRing1", "f_ring.01.L"),
                ("*:LeftHandRing2", "f_ring.02.L"), ("*:LeftHandRing3", "f_ring.03.L"),
                ("*:LeftHandPinky1", "f_pinky.01.L"), ("*:LeftHandPinky2", "f_pinky.02.L"),
                ("*:LeftHandPinky3", "f_pinky.03.L"),
                ("*:RightHandThumb1", "thumb.01.R"), ("*:RightHandThumb2", "thumb.02.R"),
                ("*:RightHandThumb3", "thumb.03.R"), ("*:RightHandIndex1", "f_index.01.R"),
                ("*:RightHandIndex2", "f_index.02.R"), ("*:RightHandIndex3", "f_index.03.R"),
                ("*:RightHandMiddle1", "f_middle.01.R"), ("*:RightHandMiddle2", "f_middle.02.R"),
                ("*:RightHandMiddle3", "f_middle.03.R"), ("*:RightHandRing1", "f_ring.01.R"),
                ("*:RightHandRing2", "f_ring.02.R"), ("*:RightHandRing3", "f_ring.03.R"),
                ("*:RightHandPinky1", "f_pinky.01.R"), ("*:RightHandPinky2", "f_pinky.02.R"),
                ("*:RightHandPinky3", "f_pinky.03.R"),
            ] },
        ]
    }
