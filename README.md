# Automate MakeHuman 2 Blender (AMH2B)

Addon for Blender 2.7x through Blender 2.93 (may work with later versions too).

Automate as much as possible of the MakeHuman to Blender workflow, e.g. materials, rig, and animation preparation.

Two flavors of addon: Blender 2.7x and Blender 2.8x

Blender 2.8x flavor is compatible with Blender 2.9x

To install this addon in Blender:

Copy the amh2b.py file (one of Blender 2.7x or Blender 2.8x flavor) into your Blender addons folder. Folder name depends on where you installed Blender, and which version of Blender was installed, like so:

e.g. Blender 2.79

C:\Program Files\blender-2.79b-windows64\2.79\scripts\addons

e.g. Blender 2.83

C:\Program Files\blender-2.83-windows64\2.83\scripts\addons

To use this addon in Blender:

The buttons to do the work are in the Object menu, in the 3D Viewport view.

3D Viewport -> Object -> AMH2B ...

## 5+1 menu options:
0) Lucky
1) Apply Scale to Rig
2) Bone Woven
3) Ratchet Hold
4) Repose Rig
5) Swap Materials

'Lucky' needs to be explained last because it is a compilation of the other functions.

## 1) Apply Scale to Rig
Correctly apply scale to animated armature, by adjusting its pose bone location animation f-curve values to match the scaling.

Background: Blender applies scale to non-animated rigs correctly, but the animations attached to the rig (i.e. the f-curves) are not scaled. The result is usually an animation that seems to move violently around the scene, or the animation seems to hover in place and not move when it should move. It seems that Blender applies scale only to the bone lengths and bone locations in the current frame, no scaling applied to animations (f-curves).

### Instructions to use the script:

Select the armature that needs 'apply scale'.

Press the 'AMH2B Apply Scale to Rig' button in the 3D Viewport -> Object menu.

## 2) Bone Woven
Simplify the MakeHuman rig animation process re: Mixamo et al. via a bridge that connects imported animation rigs to imported MHX2 rigs - leaving face panel and visemes intact, while allowing for great functionality e.g. finger movements.

In a perfect world, Blender and MakeHuman would work seamlessly with any and all motion capture data, and any motion capture sharing website (including body, facial, etc. rig). The real world includes problems with bone names, 'bone roll', vertex groups, etc. This script bridges some real world gaps between different rigs.

Basically, bones from Rig B (this could be a downloaded rig from a mocap sharing website, etc.) are mapped to Rig A so that Rig B acts like "marionettist" to the Rig A "marionette". Rig B controls Rig A, allowing the user to tweak the final animation by animating Rig A.

Caveat: Rig A and Rig B should be in the same pose.

Side-note: Ugly, But Works

### Instructions to use the script:

Important! Make sure your MHX rig has scale 1 in x/y/z, zero location, zero rotation - basically all transforms equal default. If your MHX rig already has location/rotation/scale, then re-locate/rotate/apply scale (with Apply Scale to Rig (!)) to set everything back to defaults. If the MHX rig has non-default location/rotation/scale then results are undefined.

Select the animated source rig and the MHX destination rig, so that the MHX rig is the active object.

Press the 'AMH2B Bone Woven' button in the 3D Viewport -> Object menu.

## 3) Ratchet Hold

Important: Ensure your 'Empty' objects have their scale applied (i.e. have scale = 1 in x/y/z), or the movements will be calculated incorrectly. Also it's a good idea to ensure the thing you want to move (usually your MHX rig) also has it's transforms applied  (apply rotation, location, and Apply Scale to Rig).

Idea of script:
Easily keyframe movement of a walking/moving rig, by letting user select part of armature that should appear motionless (e.g. left leg stationary) while the rest of the armature moves about that part (e.g. right leg moving).

Re-calculate location data for an object (typically armature), given:
  1) A single "Empty" type object, that is parented to a part of the armature object
       (i.e. parented to a bone in the armature object).
  2) The location of the original object (armature) should be offset, and keyframed, to make the "Empty"
     type object appear to be motionless.

### Instructions to use the script:

Select exactly two objects:

  Object A - the parent object (typically armature that has walking animation)

  Object B - the "Empty" type object that we want to appear motionless (the empty is parented to A)

Press the 'AMH2B Ratchet Hold' button in the 3D Viewport -> Object menu.

  The script will do:
1) Insert a location keyframe on object A.
2) Get the location of object B in the current frame.
3) Change to the next frame (increment frame).
4) Get the new location of object B, then calculate the offset to keep it motionless.
5) Apply location offset to object A, then insert location keyframe on A.

Result:

Two keyframes created on object A, such that object B appears motionless over the two frames.

Repeat the operation a number of times to get an animation, e.g. of a person walking.

## 4) Repose Rig
Re-pose original rig (which has shape keys, hence this work-around) by way of a duplicate of original that moves mesh to desired pose, then original rig is pose-apply'ed and takes over from duplicate rig.

Basically, a duplicate rig moves the underlying mesh to the place where the reposed original rig will be.

### Instructions to use the script:

Select only the armature (the MHX armature, although this script will work with any armature) that needs its current pose to be set as the 'rest pose'.

Press the 'AMH2B Repose Rig' button in the 3D Viewport -> Object menu.

## 5) Swap Materials
Swap Materials from Other Blend File, so custom materials for clothing can be maintained in one folder/file and easily used. For this to work, the user must already have set up a materials dictionary file. Read on for some hints on doing that.

The script will do:
  1) User chooses file with source materials.
  2) Materials are appended 'blindly', by trimming names of materials on selected objects and trying to append trimmed name materials from the blend file chosen by the user. e.g. the material named 'Mass0010:Uniform_jacket:Uniform_jacket' will be swapped with the material named 'Uniform_jacket:Uniform_jacket' from the user selected file (material dictionary file).

### Instructions to use the script:

Select all objects with materials that need to be swapped. It's okay to select armature objects, curves, etc. - these objects without materials will be ignored.

Press the 'AMH2B Swap Materials' button in the 3D Viewport -> Object menu.

A file selection window will show, and you can select one file that has your preferred materials in it. You can run this command multiple times if your materials are located across many files: e.g. run this command and choose the file with clothes materials, next run the command and choose the file with hair materials, etc.

Result:

All selected objects that have materials in their material slots will have their material slots swapped, if possible, with the materials in the user selected file.

### Hints for creating materials dictionary file:

Export your MakeHuman models like you normally would, and change the names of the materials like so:

'Mass0010:Uniform_jacket:Uniform_jacket'

would become

'Uniform_jacket:Uniform_jacket'

Just remove the first part of the material name, up to and including the first ':'

Now the material name will be found when the script is run. The script takes the default name of the material (after importing from MakeHuman to Blender), chops off the first part up to the ':', then looks for the result in the materials dictionary file.

For reference, the naming convention of the MakeHuman materials seems to be:

'HumanName:PartName:PartMaterialName'

e.g.

'Mass0010:Uniform_jacket:Uniform_jacket'

'Shelagh:Uniform_jacket:Uniform_jacket'

'Mass0002:High-poly:Eye_deepblue'

'Floopy:High-poly:Eye_brown'

## 0) Lucky

One button press to:
1) Re-Pose Rig (optional)
2) Scale incoming rig
3) BoneWoven the two rigs together

Go to the Dope Sheet -> Action Editor and add the original animation to your new rig.
If all works correctly then the old rig is animating inside your MHX rig, and this controls the original MHX rig's bones.

### Instructions to use the script:
Before pressing this button, select all of:
1) Rig with the animation you want transferred to MHX rig
2) Objects attached to MHX rig with 'Armature' modifier (e.g. clothes, skin, hair, eyebrows)
3) MHX rig (select the MHX rig last)

Press the Lucky button.

This will Re-Pose the MHX rig, apply location/rotation and Apply Scale to the animated rig, and finish with Bone Woven joining the two rigs.

One click success, if lucky.