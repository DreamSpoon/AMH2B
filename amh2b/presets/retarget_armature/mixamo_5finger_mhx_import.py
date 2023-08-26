{
    "label": "Mixamo 5 Finger to MHX Import",
    "data": [
        { "op": "join_armatures" },
        { "op": "dup_swap_stitch", "data": [
                ("target", "*:Hips", "root", 0, 0), ("target", "*:Spine", "spine-1", 0, 0), ("target", "*:Spine1", "chest", 0, 0), ("target", "*:Spine2", "chest-1", 0, 0), ("target", "*:Neck", "neck", 0, 0), ("target", "*:Head", "head", 0, 0),
                ("target", "*:LeftShoulder", "clavicle.L", 0, 0), ("target", "*:LeftArm", "arm_base.L", 0.06, 0.35), ("target", "*:LeftForeArm", "forearm.fk.L", 0, 0), ("target", "*:LeftHand", "hand.fk.L", 0, 0),
                ("target", "*:RightShoulder", "clavicle.R", 0, 0), ("target", "*:RightArm", "arm_base.R", 0.06, 0.35), ("target", "*:RightForeArm", "forearm.fk.R", 0, 0), ("target", "*:RightHand", "hand.fk.R", 0, 0),
                ("target", "*:LeftUpLeg", "thigh.fk.L", 0, 0), ("target", "*:LeftLeg", "shin.fk.L", 0, 0), ("target", "*:LeftFoot", "foot.fk.L", 0, 0), ("target", "*:LeftToeBase", "toe.fk.L", 0, 0),
                ("target", "*:RightUpLeg", "thigh.fk.R", 0, 0), ("target", "*:RightLeg", "shin.fk.R", 0, 0), ("target", "*:RightFoot", "foot.fk.R", 0, 0), ("target", "*:RightToeBase", "toe.fk.R", 0, 0),
                ("target", "*:LeftHandThumb1", "thumb.01.L", 0, 0), ("target", "*:LeftHandThumb2", "thumb.02.L", 0, 0), ("target", "*:LeftHandThumb3", "thumb.03.L", 0, 0), ("target", "*:LeftHandIndex1", "f_index.01.L", 0, 0), ("target", "*:LeftHandIndex2", "f_index.02.L", 0, 0), ("target", "*:LeftHandIndex3", "f_index.03.L", 0, 0), ("target", "*:LeftHandMiddle1", "f_middle.01.L", 0, 0), ("target", "*:LeftHandMiddle2", "f_middle.02.L", 0, 0), ("target", "*:LeftHandMiddle3", "f_middle.03.L", 0, 0), ("target", "*:LeftHandRing1", "f_ring.01.L", 0, 0), ("target", "*:LeftHandRing2", "f_ring.02.L", 0, 0), ("target", "*:LeftHandRing3", "f_ring.03.L", 0, 0), ("target", "*:LeftHandPinky1", "f_pinky.01.L", 0, 0), ("target", "*:LeftHandPinky2", "f_pinky.02.L", 0, 0), ("target", "*:LeftHandPinky3", "f_pinky.03.L", 0, 0),
                ("target", "*:RightHandThumb1", "thumb.01.R", 0, 0), ("target", "*:RightHandThumb2", "thumb.02.R", 0, 0), ("target", "*:RightHandThumb3", "thumb.03.R", 0, 0), ("target", "*:RightHandIndex1", "f_index.01.R", 0, 0), ("target", "*:RightHandIndex2", "f_index.02.R", 0, 0), ("target", "*:RightHandIndex3", "f_index.03.R", 0, 0), ("target", "*:RightHandMiddle1", "f_middle.01.R", 0, 0), ("target", "*:RightHandMiddle2", "f_middle.02.R", 0, 0), ("target", "*:RightHandMiddle3", "f_middle.03.R", 0, 0), ("target", "*:RightHandRing1", "f_ring.01.R", 0, 0), ("target", "*:RightHandRing2", "f_ring.02.R", 0, 0), ("target", "*:RightHandRing3", "f_ring.03.R", 0, 0), ("target", "*:RightHandPinky1", "f_pinky.01.R", 0, 0), ("target", "*:RightHandPinky2", "f_pinky.02.R", 0, 0), ("target", "*:RightHandPinky3", "f_pinky.03.R", 0, 0),
                ]
            },
        { "op": "set_parent_bone", "data": [
                ("target", "*:Hips", "master"),
                ("target", "hand.ik.L", "*:LeftHand"), ("target", "elbow.pt.ik.L", "*:LeftForeArm"), ("target", "elbow.link.L", "*:LeftForeArm"),
                ("target", "hand.ik.R", "*:RightHand"), ("target", "elbow.pt.ik.R", "*:RightForeArm"), ("target", "elbow.link.R", "*:RightForeArm"),
                ("target", "knee.pt.ik.L", "*:LeftLeg"), ("target", "knee.link.L", "*:LeftLeg"), ("target", "foot.ik.L", "*:LeftFoot"),
                ("target", "knee.pt.ik.R", "*:RightLeg"), ("target", "knee.link.R", "*:RightLeg"), ("target", "foot.ik.R", "*:RightFoot"),
                ]
            }
        ]
    }
