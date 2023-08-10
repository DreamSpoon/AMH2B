# Animation

## Object Location - Ratchet Point
Create empty object for use with Ratchet Hold.

### Usage
- select armature that needs Ratchet Hold applied
- switch to 'Pose' mode, and select bone that should be stationary (e.g. foot bone, while foot is on ground)
- use Animation -> Ratchet Point to create an empty object, parented to selected pose bone, at selected pose bone's location

## Object Location - Ratchet Hold
Idea for function:

Easily keyframe movement of a walking/moving rig, between walk/run cycles, by keyframing an armature's location over two frames.

A 'ratchet point' is used: an empty attached to a pose bone that should appear stationary over two frames of animation.

Re-calculate location data for an object (typically armature) given:
1) A single "Empty" type object, that is parented to a part of armature object
  - i.e. Parented to a bone in armature object
2) Location of original object (armature) should be offset, and keyframed, to make "Empty" type object appear to be motionless

### Usage
- select exactly two objects:
  - Object A - "Empty" type object that we want to appear motionless (empty is parented to B)
  - Object B - parent object (typically armature that has walking animation)
- Object B must be selected last so that it is active object.
- before using this function, make sure that object A is parented to object B.
- use AMH2B -> Animation -> Ratchet Hold

Important: Ensure your that objects A and B have their scale applied (i.e. have scale = 1 in x/y/z) before running script. If scale is not 1, then movements will be calculated incorrectly.

Also important: This function does not work if Object A ("Empty") is animated - result is undefined if Empty is animated.

Script will do example (assuming Frame Count = 1):
1) Insert a location keyframe on object B.
2) Get location of object A in current frame.
3) Change to next frame (increment frame).
4) Get new location of object A, then calculate offset to keep it motionless.
5) Apply location offset to object B, then insert location keyframe on B.

Result: Two keyframes created on object B, such that object A appears motionless over two frames.

Repeat operation a number of times to get an animation, e.g. of a person walking.

'Frame Count' can be increased to automatically apply Ratchet Hold multiple times.
