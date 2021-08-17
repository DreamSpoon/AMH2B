# Automate MakeHuman 2 Blender (AMH2B)

Automate as much as possible of the MakeHuman to Blender import process, e.g. shader and rig preparation.

Two flavors of addon: Blender 2.7x and Blender 2.8x

Blender 2.8x flavor is compatible with Blender 2.9x

Addon with set of tools, accessible from Object menu in 3D Viewport.

3D Viewport -> Object -> AMH2B ...

## 5+1 menu options:
0) Lucky
1) Apply Scale to Rig
2) Bone Woven
3) Ratchet Hold
4) Repose
5) Swap Shaders

'Lucky' needs to be explained last because it is a compilation of other scripts.

## 1) Apply Scale to Rig
Apply scale to armature (this is only needed for armature scale apply), and adjust it's bone location animation f-curve values to match the scaling.

If this operation is not done, then the animated pose bones that have varying location values will appear to move incorrectly. It seems that Blender applies scale only to the bone lengths and bone locations in the current frame, no scaling applied to animations (f-curves).

Instructions to use the script:

Select the armature that needs 'apply scale', then press the AMH2B Apply Scale button.

## 2) Bone Woven
Simplify the MakeHuman rig animation process re: Mixamo et al. via a bridge that connects imported animation rigs to imported MHX2 rigs - leaving face panel and visemes intact, while allowing for great functionality e.g. finger movements.

In a perfect world, Blender and MakeHuman would work seamlessly with any and all motion capture data, and any motion capture sharing website (including body, facial, etc. rig). The real world includes problems with bone names, 'bone roll', vertex groups, etc. This script bridges some real world gaps between different rigs.

Basically, bones from Rig B (this could be a downloaded rig from a mocap sharing website, etc.) are mapped to Rig A so that Rig B acts like "marionettist" to the Rig A "marionette". Rig B controls Rig A, allowing the user to tweak the final animation by animating Rig A.

Caveat: Rig A and Rig B should be in the same pose.

Side-note: Ugly, But Works

Instructions to use the script:

Select the animated source rig and the MHX destination rig, so that the MHX rig is the active object.

Press the AMH2B Bone Woven button.

## 3) Ratchet Hold
Idea of script:

Re-calculate location data for an object (typically armature), given:
  1) A single "Empty" type object, that is parented to a part of the armature object
       (i.e. parented to a bone in the armature object).
  2) The location of the original object (armature) should be offset, and keyframed, to make the "Empty"
     type object appear to be motionless.

Instructions to use the script:

Select exactly two objects:

  Object A - the parent object (typically armature)

  Object B - the "Empty" type object, that is parented to A

Run the script:

  The script will do:
1) In the current frame, insert a location keyframe on object A.
2) Get the location of object B in the current frame.
3) Change to the next frame (increment frame).
4) Get the new location of object B, then calculate the offset to keep it motionless.
5) Apply location offset to object A, then insert location keyframe on A.

Result:

Two keyframes created on object A, such that object B appears motionless over the two frames.

Repeat the operation a number of times to get an animation, e.g. of a person walking.

## 4) Repose
Re-pose original rig (which has shape keys, hence this work-around) by way of a duplicate of original that moves mesh to desired pose, then original rig is pose-apply'ed and takes over from duplicate rig.

Basically, a duplicate rig moves the underlying mesh to the place where the reposed original rig will be.

Instructions to use the script:

Select only the armature (the MHX armature, although this script will work with any armature) that needs its current pose to be set as the 'rest pose'. Press the AMH2B RePose button.

## 5) Swap Shaders
Swap Materials from Other Blend File

Automate materials dictionary material swapping with a simple method:
  1) User chooses file with source materials.
  2) Materials are appended 'blindly', by trimming names of materials on selected objects and trying to append trimmed name materials from the blend file chosen by the user.

Instructions to use the script:

Select all objects with materials that need to be swapped. It's okay to select armature objects, curves, etc. - these objects without materials will be ignored. All selected objects that have materials in their material slots will have their material slots swapped, if possible, with the materials in the user selected file.

## 0) Lucky
Instructions to use the script:

  Before pressing this button, select all of:
	-rig with the animation you want transferred to MHX rig
	-objects attached to MHX rig with 'Armature' modifier (e.g. clothes, skin, hair, eyebrows)
	-MHX rig

Select the MHX rig last.

Press the Lucky button.

This will Re-Pose the MHX rig, apply location/rotation and Apply Scale to the animated rig, and finish with Bone Woven joining the two rigs.

One click success, if lucky.