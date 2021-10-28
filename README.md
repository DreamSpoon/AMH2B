# Automate MakeHuman 2 Blender (AMH2B)

Addon for Blender 2.7x through Blender 2.93

Automate as much as possible of the MakeHuman to Blender workflow, e.g. materials, rig, cloth sim, animation

The addon is centred around the **MakeHuman MHX2 export format with MHX armature**, which offers fine control over animation with face and finger bones. **To get the correct rig from the import process, the 'MHX' format must be selected when using the MakeHuman Import MHX to Blender plugin/addon.**

Also includes convenience functions for use with any armature type, e.g. Ratchet Hold, Re-Size Clothes Rig.

Brief Overview:
- Name lookup to **auto swap materials, and cloth sim vertex groups (with weight paint),** from any Blender file
- **Re-target MakeHuman MHX rig to CMU or Mixamo rigs** to get accurate animation - including fingers
- Transition between different animations easily with **Ratchet Hold**
  - e.g. Keyframe rig movements to hold a foot in place while transitioning from standing to walk animations
- Easily adjust clothing size, before cloth sim, with **Create Size Rig** - temporary copy of MHX rig attached only to selected clothes
  - Re-size with rig, apply re-size rig modifier, delete re-size rig - or keep re-size rig for non-destructive cloth re-sizing
- Simplify cloth sim process with **Bake Deform Shape Keys**
  - Use vertex masking to reduce simulation time, without delicate modifiers like Surface Deform and Mesh Deform
    - Surface Deform and Mesh Deform are a nightmare to use with armatures and cloth/soft-body sims
    - Bake deform to shape keys is flexible re: binding mesh for calculating deform shape keys
    - Avoid wasting time manually creating mesh cages to run cloth/soft-body sims - just use vertex mask with original mesh
  - Simulations can be baked to shape keys, and the simulation can be run again!
    - Shape keys from first simulation can be used to guide the re-simulation, or add fine details

## Install Addon in Blender
1) Start Blender
2) Go to User Preferences -> Addons -> Install addon from file
3) Choose the AMH2B zip file you downloaded (available for download from the 'Releases' section of this website)

## Use Addon in Blender
- Look for 'AMH2B' button in View 3D:
  - Blender 2.7x: Tools menu (left-side of View 3D)
  - Blender 2.8x, 2.9x: Transforms menu (right-side of View 3D)

## Function List:
- Mesh Material
  - Swap material - From file (user chooses another file)
  - Swap material - Internal single (swapped with materials in current file only)
  - Swap material - Internal multiple (swapped with materials in current file only)
  - Setup material swap - Rename single
  - Setup material swap - Rename multiple
- Mesh Size
  - Create size rig
- Cloth Sim
  - Vertex group copy - From file
  - Vertex group copy - Make object searchable
  - Copy vertex groups by prefix
  - Make cut and pin groups
  - Add cuts mask
  - Toggle view cuts mask
  - Add cloth sim
  - Bake deform shape keys
  - Deform SK view toggle
  - Delete deform shape keys
- Armature
  - Adjust pose
  - Apply scale to rig
  - Bridge re-pose
  - Bone woven
  - Lucky
- Animation
  - Ratchet hold

## Mesh Material
### Swap Material - From File
Automatically swap materials from another Blend file. Other functions in this addon (see Setup Material Swap -> Rename Single / Rename Multi) are used to make materials "searchable" by this function. Custom materials for clothing can be maintained in one folder/file and easily re-used. Before usig this function, the user needs to find or create a materials dictionary file. Creation of said file will be explained elsewhere in this readme.

The script will do:
- User chooses source file with source materials
- Materials are appended from source file by name, and the names are "guessed" by trimming names of materials and trying to append said materials from the blend file chosen by the user
  - e.g. Material named 'Mass0010:Uniform_jacket:Uniform_jacket' will be swapped with the material named 'Uniform_jacket:Uniform_jacket' from the user selected file (material dictionary file)

#### Instructions to use the script:
Select all objects with materials that need to be swapped. Select meshes, armature objects, curves, etc. - the meshes will have their materials swapped and any objects without materials (e.g. armatures) will be ignored.

Press button AMH2B -> Mesh Material -> Swap Material - From File

File selection window will be shown, and user selects one file with preferred materials in it. Run this command multiple times if materials are located across many files:
  - e.g. Run Swap Materials from File and choose the file with clothes materials to swap only clothes materials (other materials will be ignored), then re-run this command and choose the file with hair materials to swap only hair materials, etc.

Result: All selected object's material slots will be swapped, if possible, with the materials in the user selected file.

### Swap Material - Internal Single
Try to swap material in object's active material slot with replacement material within this Blend file.

### Swap Material - Internal Multiple
Try to swap all materials of selected objects with replacement materials within this Blend file.

### Setup Material Swap - Rename Single
Rename active material slot of active object to make the material searchable re: swap material from file.

### Setup Material Swap - Rename Multiple
Rename all materials on all selected objects to make them searchable re: swap material from file.

### Notes re: creating materials dictionary file:
Export a MakeHuman model to MHX2 format (does not need to be MHX rig, or even have a rig, this works with any rig type - and no rig).

Modify the materials setup, i.e. shader nodes. Finally, use the Rename Materials Single / Multi to change the names of the materials like so:

'Mass0010:Uniform_jacket:Uniform_jacket'

would become

'Uniform_jacket:Uniform_jacket'

Renaming materials in this way lets the Swap Materials script find the materials in the materials library file that we're creating.
Now the material name will be found when the script is run.

For reference, the naming convention of the MakeHuman materials seems to be:

'HumanName:PartName:PartMaterialName'

e.g.

'Mass0010:Uniform_jacket:Uniform_jacket'

'Shelagh:Uniform_jacket:Uniform_jacket'

'Mass0002:High-poly:Eye_deepblue'

'Floopy:High-poly:Eye_brown'

## Mesh Size
### Clothing Size - Create Size Rig
Copy armature and unlock pose scale values for resizing selected clothing meshes with copied armature. Select mesh objects first and select armature object last.

## Weight Paint
### Vertex Select by Weight
With active object, deselect all vertices (optional), then select only vertices with weights between min_weight and max_weight, inclusive.
'Deselect all first' is enabled by default, if enabled then all mesh vertexes are deselected before the Select by Weight operation is applied.

### Grow Selection Paint
With active object, starting with currently selected vertexes, set weight paint in successive 'rings' by using 'select more' and weight painting only the newly selected vertexes - blending weight paint value by 'select more' iteration. Very useful, e.g. on dresses, to weight paint 1.0 at the waist and blend to 0.0 at the edge of the dress.

'Iterations' controls the amount of growth, it is the number of times 'Select More' is applied.

'Start Weight' is applied to the currently selected vertexes, and used as the beginning blend value.

'End Weight' is applied to the vertexes in the last 'Select More' iteration.

'Tail Fill' is disabled by default, if enabled then 'Tail Value' is weight painted to any vertexes that remain unselected after the 'Iterations' weight paint is applied. Basically, an 'Invert Selection' operation is applied after all growth weight paint is appplied.

'Fill Only Linked' is enabled by default, if enabled then 'Tail fill' is applied only to the vertexes that are linked - i.e. can be selected by 'Select Linked' operation.

## Cloth Sim
### Vertex Group Copy - From File
For each selected mesh object: Search another file automatically and try to copy vertex groups based on user given prefix and object name.

Note: Name of object from MHX import process is used to search for object in user selected file.

### Vertex Group Copy - Make Object Searchable
Rename active object, if needed, to make it searchable re: automatic search of file for vertex groups by object name and vertex group name prefix.

### Vertex Group Copy - Copy Vertex Groups by Prefix
Copy vertex groups by name prefix (user text box) from the active object (must be selected last) to all other selected mesh objects. Object does not need to be "searchable".

### Cut and Pin VGroup Make - Make Cut and Pin Vertex Groups
Add AutoCuts and AutoPins vertex groups to the active object, replacing these groups if they already exist.

### Cut and Pin VGroup Make - Add Cuts Mask
Add Mask modifier to implement AutoCuts, adding AutoCuts vertex group to active object if needed.

### Cloth Sim - Toggle View Cuts Mask
Toggle the visibility of the Cuts mask modifier, in viewport and render.

### Cloth Sim - Add Cloth Sim
Add CLOTH modifer to active object with settings auto-filled for Pinning.

### Cloth Sim - Bake Deform Shape Keys
Bake active object's mesh deformations to shape keys.

'Bind frame' - the frame when the object's vertexes must be in the same position as the 'deformation'.
Hint: the vertexes should be in the same position in 'Edit Mode' as they are in 'Object Mode' - zero deformation.

'Start frame' - the first frame for which shape keys are baked.

'End frame' - the last frame for which shape keys are baked.

Shape keys are baked Start Frame to End Frame **inclusive**.

'Animate Shape Keys' - add keyframes to baked shape keys so that they are active only on the frame when they were baked.

'Dynamic' - respect armature transformations when calculating deform shape keys - Dynamic is slower to run than not-Dynamic

Hint: use 'Dynamic' if you have an ARMATURE modifier on the object that needs shape keys baked

'Extra Accuracy' - increase accuracy of 'Dynamic' bake at the cost of extra computation time, use 0 to start and increase as needed

### Cloth Sim - Deform SK View Toggle
Toggle visibility between shape keys and cloth/soft body sims on active object.
Deform SK View Toggle - **only available if 'Dynamic' is disabled** - a convenience function to:
- if toggling on:
  - make CLOTH and SOFTBODY sims not visible
  - disable influence of ARMATURE modifier on vertexes that have baked shape keys, so that shape key verts are not "double-Armature-modified"
    - this step is unnecessary if 'Dynamic' bake is used, since shape keys are baked with armature influence accounted for
- if toggling off:
  - make CLOTH and SOFTBODY sims visible
  - undo disabling of influence of ARMATURE modifier on vertexes that have baked shape keys

## Shape Key
### Delete Prefixed Keys
Delete mesh deformation shape keys from active object, by prefix. Shape keys can be any kind, not limited to just deformation shape keys.

### Copy Prefixed Keys
With active object, copy shape keys by prefix to all other selected objects.

## Armature
### Retarget - Adjust Pose
Background: Time is wasted doing repetitive rotations of pose-bones to match imported animated rigs, in preparation for the AMH2B 'Lucky' function.

This script takes a user-created Comma Separated Variable (CSV) script and rotates pose-bones automatically.

In other words, script a series of pose-bone rotations so that an imported MakeHuman MHX rig aligns to an imported animated rig (Mixamo or CMU, only Mixamo supported presently) to simplify the process of animating mass amounts of MakeHuman MHX rigs.

**If using Blender 2.79 then press 'Reload Trusted' button in a loaded Blend file, or click 'Trusted Source' in the 'Load Blend' window, to enable MHX scripts before using adjust pose - or the result will be a pose adjustment that is unpredictable for FK and IK bones.**

#### Instructions to use the script:
- Open the Text Editor and create a text. The default name is "Text". Copy-and-Paste text from a file in the [ref_data folder](https://github.com/DreamSpoon/AMH2B/tree/main/ref_data) that matches your desired rig types and poses. Or make a custom CSV text, type rotations in Comma Separated Variable (CSV) format like this:

clavicle.L, y, -15

clavicle.L, z, 5

upper_arm.fk.L, y, -34

- See the AMH2B menu, the Armature panel, Text Editor Script Name - this is where you enter the name of the CSV text you just created, or leave it as default "Text"
- Select the armature that needs it's pose-bones adjusted
- Press button AMH2B -> Armature -> Retarget - AdjustPose
- Result: The pose bones in the selected armature will be rotated according to the script

### Retarget - Apply Scale to Rig
Correctly apply scale to animated armature, by adjusting its pose bone location animation f-curve values to match the scaling.

Background: Blender applies scale to non-animated rigs correctly, but the animations attached to the rig (i.e. the f-curves) are not scaled. The result is usually the animated rig moves violently around the scene, or the animation seems to hover in place and not move when it should move. Blender applies scale only to the bone lengths and bone locations in the current frame, but no scaling applied to animations (f-curves).

#### Instructions to use the script:

Select the armature that needs 'apply scale'.

Press button AMH2B -> Armature -> Retarget - Apply Scale to Rig

Result: The scale of the selected armature is 1.0 in X/Y/Z axes. Also, the keyframed animation on the rig is scaled correctly.

### Retarget - Bridge Re-Pose
Re-pose original rig (which has shape keys, hence the need for this work-around) by way of a duplicate "bridge" of original rig that moves mesh to desired pose, then original rig can animate from there on.

Basically, a duplicate rig moves the underlying mesh to the place where the re-posed original rig should be.

#### Instructions to use the script:
Select only the armature (the MHX armature, although this script will work with any armature) that needs its current pose to be set as the 'rest pose'.

Press button AMH2B -> Armature -> Retarget - Bridge Re-Pose

Result: Extra armature is created, and selected meshes will have an Armature modifier applied which uses this extra armature.

### Retarget - Bone Woven
Simplify the MakeHuman rig animation process re: Mixamo et al. via a bridge that connects imported animation rigs to imported MHX2 rigs - leaving face panel and visemes intact, while allowing for great functionality e.g. finger movements.

In a perfect world, Blender and MakeHuman would work seamlessly with any and all motion capture data, and any motion capture sharing website (including body, facial, etc. rig). The real world includes problems with bone names, 'bone roll', vertex groups, etc. This script bridges some real world gaps between different rigs, and re-targeting animations.

Basically, bones from Rig B (this could be a downloaded rig from a mocap sharing website, etc.) are mapped to Rig A so that Rig B acts like "marionettist" to the Rig A "marionette". Rig B controls Rig A, allowing the user to tweak the final animation by animating Rig A.

Caveat: Rig A and Rig B should be in the same pose.

Side-note: Ugly, But Works

#### Instructions to use the script:
Select the animated source rig and the MHX destination rig, so that the MHX rig is the active object.

Press button AMH2B -> Armature -> Retarget - Bone Woven

Result: Animated rig is joined to MHX rig, and a 'stitching' process will copy-swap-and-parent animated bones into the MHX rig's bone setup.

Important! Make sure your MHX rig has scale 1 in x/y/z, zero location, zero rotation - basically all transforms equal default. If your MHX rig already has location/rotation/scale, then re-locate/rotate/apply scale (with Apply Scale to Rig (!)) to set everything back to defaults. If the MHX rig has non-default location/rotation/scale then results are undefined.

It's a good idea to edit the bone groups after Bone Woven is applied. Select a visibility group that has the "new" bones from the animated rig, and very few bones from the original MHX rig, e.g. bone visility layer 0 (zero). Enter EDIT or POSE mode, select all, then deselect the MHX bones (only 2 bones in bone vis layer 0!), and move remaining bones to desired (empty) bone visibility layer. This way it's easier to select only the "new" bones, or just the regular MHX bones.

### Retarget Multi-Function - Lucky
One button press to:
1) Bridge Re-pose Rig (optional)
2) Scale incoming rig
3) BoneWoven the two rigs together

Go to the Dope Sheet -> Action Editor and add the original animation to your new rig.
If all works correctly then the old rig is animating inside your MHX rig, and this controls the original MHX rig's bones.

#### Instructions to use the script:
Before pressing this button, select all of:
1) Rig with the animation you want transferred to MHX rig
2) Objects attached to MHX rig with 'Armature' modifier (e.g. clothes, skin, hair, eyebrows)
3) MHX rig (select the MHX rig last)

Press button AMH2B -> Armature -> Retarget Multi - Lucky

Result: This will Re-Pose the MHX rig, apply location/rotation and Apply Scale to the animated rig, and finish with Bone Woven joining the two rigs.

One click success, if lucky.

## Animation
### Object Location - Ratchet Hold
Idea of script:

Easily keyframe movement of a walking/moving rig, by letting user select part of armature that should appear motionless (e.g. left leg stationary) while the rest of the armature moves about that part (e.g. right leg moving).

Re-calculate location data for an object (typically armature) given:
1) A single "Empty" type object, that is parented to a part of the armature object
  - i.e. Parented to a bone in the armature object
2) The location of the original object (armature) should be offset, and keyframed, to make the "Empty" type object appear to be motionless

#### Instructions to use the script:
- Select exactly two objects:
  - Object A - the "Empty" type object that we want to appear motionless (the empty is parented to B)
  - Object B - the parent object (typically armature that has walking animation)
- Object B must be selected last so that it is the active object.
- Before using this script, make sure that object A is parented to object B.
- Press button AMH2B -> Animation -> Ratchet Hold

Important: Ensure your that objects A and B have their scale applied (i.e. have scale = 1 in x/y/z) before running the script. If the scale is not 1, then movements will be calculated incorrectly.

Also important: This function does not work if Object A (the "Empty") is animated - the result is undefined if the Empty is animated.

The script will do:
1) Insert a location keyframe on object B.
2) Get the location of object A in the current frame.
3) Change to the next frame (increment frame).
4) Get the new location of object A, then calculate the offset to keep it motionless.
5) Apply location offset to object B, then insert location keyframe on B.

Result: Two keyframes created on object B, such that object A appears motionless over the two frames.

Repeat the operation a number of times to get an animation, e.g. of a person walking.

# Congratulations! You read me to the end.
