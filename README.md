# Automate MakeHuman 2 Blender (AMH2B)

Automate as much as possible of MakeHuman to Blender workflow, e.g. materials, rig, cloth sim, animation, templates

Addon for Blender 2.7x through Blender 3.0

YouTube video demo of addon:
https://youtu.be/XkOtsTrHRPg

Armature section of addon is centred around **MakeHuman MHX2 export format with MHX armature**, which offers fine control over animation with face and finger bones. **To get correct rig from import process, 'MHX' format must be selected when using MakeHuman Import MHX to Blender plugin/addon.**

Note: The words Rig and Armature are used interchangeably. Also, the words Material and Shader are used interchangeably.

Includes convenience functions for use with any armature type, e.g. Ratchet Hold, Re-Size Clothes Rig.

Brief Overview:
- Eye Blink track with one button
- Lid Look, so eyelids will move when eyes rotate to look up/down
- Auto swap Materials(Shaders), Vertex Groups (with Weight Paint), shape Keys from any Blender file
- Re-target MakeHuman MHX rig to CMU or Mixamo rigs to get accurate animation - including fingers
- Transition between different animations easily with Ratchet Hold
  - e.g. Keyframe rig movements to hold a foot in place while transitioning from standing to walk animations
- Bake cloth and soft-body sims to dynamic Shape Keys - with Bake Deform Shape Keys
  - Mask out vertexes to reduce simulation time, bake sim to Shape Keys, then remove mask and mesh looks perfect
    - avoids use of Surface Deform and Mesh Deform, which are difficult/delicate to use with armatures and cloth/soft-body sims
    - Avoid wasting time manually creating mesh cages to run cloth/soft-body sims - just use vertex mask with original mesh
  - Simulations can be baked to shape keys, and then
    - Slow-motion of cloth sim without wasting time calculating extra simulation frames - bake shape keys and adjust keyframe timing in dope sheet
    - Shape keys from first simulation can be used to guide re-simulation, or add fine details

## Install Addon in Blender
1) Start Blender
2) Go to User Preferences -> Addons -> Install addon from file
3) Choose AMH2B.zip file you downloaded (available for download from 'Releases' section of this website)

Done! The addon is now installed, but **you need to enable it by clicking the checkbox beside it's name**, in the addons window.

And **make sure you have the Import MHX2 addon with link given later** in the document.

## Use Addon in Blender
- Look for 'AMH2B' button in View 3D:
  - Blender 2.7x: Tools menu (left-side of View 3D)
  - Blender 2.8x, 3.x: Transforms menu (right-side of View 3D)

## Import MHX2 addon for Blender 2.8+ (with bug fixes to enable Moho, and make compatible with Blender 2.8+)

Download the following link for the fixed Import MHX Plugin, from author who did all the work to fix the bugs. This enables Moho support (text to mouth animation) in Blender version 2.83+. This github repo replaces the original Import MHX Plugin from the MakeHuman Community website. Fixed version:

https://github.com/helour/mhx2-makehuman-exchange

Blender installable zip file, just for convenience - this links to my repo, so use previous link and give repo traffic to original author, or use this and be lazy:

https://github.com/DreamSpoon/mhx2-makehuman-exchange/releases/download/v1.1.1/mhx2-makehuman-exchange-master.zip

## Original Import MHX2 Format plugin for Blender from MakeHuman community - use previous link instead

http://download.tuxfamily.org/makehuman/plugins/mhx-blender-latest.zip

Which is linked from this page:

http://www.makehumancommunity.org/content/plugins.html

## Function List:
- Mesh Material
  - Swap material
    - Search File
    - Search Internal
- Mesh Size
  - Create Size Rig
- Vertex Group
  - Functions
    - Copy from File
    - Copy Groups
    - Delete Groups
  - AutoMask and Pin Group
    - Add Groups
    - Add MaskOut Modifier
    - Toggle AutoMaskOut
- Weight Paint
  - Vertex Select
    - Select By Weight
  - Grow Selection Paint
    - Grow Paint
- Simulation
  - Add cloth sim
- ShapeKey
  - Functions
    - Copy from File
    - Copy Keys
    - Delete Keys
  - Bake Deform Shape Keys
    - Bake Deform Keys
    - Deform SK View Toggle
- Armature
  - Retarget
    - Adjust Pose
    - Apply Scale to Rig
    - Bridge Re-Pose
    - Bone Woven
  - Retarget Multi-Function
    - Lucky
  - Preserve Volume Toggle
    - Enable / Disable
  - Bone Names
    - Rename Generic
    - Un-name Generic
- Animation
  - Object Location
    - Ratchet hold
- Eyelid
  - Lid Look
- Eye Blink
  - Remove Blink Track
  - Add Blink Track
- Template
  - Material
    - Rename Single
    - Rename Multiple
  - Vertex Group and ShapeKey
    - Make Objects Searchable

## Mesh Material
### Swap Material - Search File
Automatically swap materials from another Blend file. See Template -> Rename Materials to make materials "searchable" by this function. Custom material templates for clothing can be maintained in one folder/file and easily re-used. Before applying this function, user needs to find or create a materials template file.

Script will do:
- User chooses source file with source materials
- Materials are appended from source file by name, and names are "guessed" by trimming names of materials and trying to append said materials from blend file chosen by user
  - e.g. Material named 'Mass0010:Uniform_jacket:Uniform_jacket' will be swapped with material named 'Uniform_jacket:Uniform_jacket' from user selected file (material dictionary file)

#### Instructions to use script:
Select all objects with materials that need to be swapped. Select meshes, armature objects, curves, etc. - meshes will have their materials swapped and any objects without materials (e.g. armatures) will be ignored.

Press button AMH2B -> Mesh Material -> Swap Material - Search File

File selection window will be shown, and user selects one file with preferred materials in it. Run this command multiple times if materials are located across many files:
  - e.g. Run Swap Material from File and choose file with clothes materials to swap only clothes materials (other materials will be ignored), then re-run this command and choose file with hair materials to swap only hair materials, etc.

Result: All selected object's material slots (or just Active Slot, depending) will be swapped, if possible, with materials in file selected by user.

### Swap Material - Search Internal
Try to swap material slot(s) of all selected objects with replacement materials contained within this Blend file.

## Mesh Size
### Clothing Size - Create Size Rig
Copy armature and unlock pose scale values for resizing selected clothing meshes with copied armature. Select mesh objects first and select armature object last.

Intended to be used to quickly up-size clothing, using MHX rig, before running cloth sim. i.e. begin with over-sized clothes so cloth sim can "shrink" clothing to body at start of simulation.

## Vertex Group
### Functions - Copy from File
For each selected MESH object: Search another file automatically and try to copy vertex groups based on Prefix and object name. Note: Name of object from MHX import process is used to search for object in other selected file.

### Functions - Copy Groups
Copy vertex groups by name prefix from active object (must be selected last) to all other selected mesh objects.

To **copy vertex groups between meshes with different numbers of vertexes**, enable 'Create Groups Only in Name' and set 'Prefix' = '', i.e. clear the 'Prefix' text box.
Or, set the Prefix value to only create the vertex groups with names beginning with Prefix.
Then add the 'Data Transfer' modifier to the destination mesh, so it automatically copies vertex weights for all vertex groups:
- "Data Transfer" modifier options:
  - With "Vertex Data" enabled, "Nearest Vertex" (or "Nearest Vertex Interpolated" for better quality)
  - Then select "Vertex Group(s)", "All Layers", "By Name"

Description of Swap Autoname Ext:
- if vertex group copy function is tried and fails, re-try swap with objects 'auto-name' extension removed
  - e.g. Object Mass0007:Eyebrow010.003 vertex groups may be copied from object Mass0007:Eyebrow010 vertex groups

### Functions - Delete Groups
With all selected objects, delete vertex groups by prefix.

### AutoMask and Pin Group - Add Groups
Add AutoMaskOut and AutoClothPin vertex groups to the active object, if these groups don't already exist.

### AutoMask and Pin Group - Add MaskOut Modifier
Add Mask modifier to implement AutoMaskOut, adding AutoMaskOut vertex group to active object if needed.

### AutoMask and Pin Group - Toggle AutoMaskOut
Toggle the visibility of the Auto Mask modifier, in viewport and render.

## Weight Paint
These functions make it easier to add realistic cloths sims to clothes and hair, with faster and better weight painting.

The Grow Selection Paint function creates a gradient from the selected vertexes outward (using the Grow Selection operation). E.g. top of a pair of pants would likely have weight = 1.0 for full strength pin, while the bottoms of the pant legs should have weight = 0.1 for minimal pinning. To use Grow Selection Paint in this case - select the top rows of pants' vertexes, estimate the number of "grow" operations to select the rest of the pants, and hit Grow Paint.

Result: Rainbow Pants (literally!)

### Vertex Select by Weight
With active object, deselect all vertices (optional), then select only vertices with weights between 'Min Weight' and 'Max Weight', inclusive.
'Deselect all first' is enabled by default, if enabled then all mesh vertexes are deselected before Select by Weight operation is applied.

### Grow Selection Paint
With active object, starting with currently selected vertexes, set weight paint in successive 'rings' by using 'select more' and weight painting only newly selected vertexes - blending weight paint value by 'select more' iteration. Very useful, e.g. on dresses, to weight paint 1.0 at waist and blend to 0.0 at edge of dress.

'Iterations' controls amount of growth, it is number of times 'Select More' is applied.

'Start Weight' is applied to currently selected vertexes, and used as beginning blend value.

'End Weight' is applied to vertexes in last 'Select More' iteration.

'Paint Initial Selection' (enabled by default)
  -enable so that vertexes selected before function is run will be painted
  -disable so that only 'growth' vertexes will be painted

'Tail Fill' (disabled by default)
  -if enabled then 'Tail Value' is weight painted to any vertexes that remain unselected after 'Iterations' weight paint is applied
  - basically, an 'Invert Selection' operation is applied after all growth weight paint is applied

'Fill Only Linked' (enabled by default)
  -if enabled then 'Tail fill' is applied only to vertexes that are 'linked' - i.e. connected by edges

## Simulation
### Cloth Sim - Add Cloth Sim
Add CLOTH modifer to active object with settings auto-filled for Pinning.

## ShapeKey
### Functions - Copy from File
For each selected MESH object: Search another file automatically and try to copy shape keys based on Prefix and object name. Note: Name of object from MHX import process is used to search for object in other selected file.

### Functions - Delete Prefixed Keys
With selected MESH type objects, delete shape keys by prefix.

### Functions - Copy Prefixed Keys
With active object, copy shape keys by prefix to all other selected objects

### Bake Deform Shape Key - Bake Deform Keys
Bake active object's mesh deformations to shape keys.

'Mask VGroup' - Name of vertex group to use as a mask when baking shapekeys. Optional: Use this feature for finer control over which vertexes are used to bake the shapekeys.

'Mask Include' - If vertex group is given, and 'Include' is enabled, then only mask vertex group vertexes are included when baking shapekey(s). If vertex group is given, and 'Include' is not enabled, then mask vertex group vertexes are excluded when baking shapekey(s).

'Bind frame' - frame when object's vertexes must be in same position as 'deformation'.
Hint: vertexes should be in same position in 'Edit Mode' as they are in 'Object Mode' - zero deformation.

'Start frame' - first frame for which shape keys are baked.

'End frame' - last frame for which shape keys are baked.

Shape keys are baked Start Frame to End Frame **inclusive**.

'Animate Shape Keys' - add keyframes to baked shape keys so that they are active only on frame when they were baked.

'Add Frame to Name' (enabled by default)
  - Append frame number to ShapeKey name
  - e.g. 'DSKey0005' at frame 5, 'DSKey0100' at frame 100, instead of Blender auto-naming to get 'DSKey.004' at frame 5, and 'DSKey.099' at frame 100
  - very helpful if baking multiple ShapeKeys for the same frame
    - e.g. combine multiple simulations run on separate parts of the same mesh object, with overlapping-frame ShapeKeys

'Dynamic' (enabled by default)
  - respect armature transformations when calculating deform shape keys
  - Dynamic is slower to run than not-Dynamic
  - Hint: use 'Dynamic' if you have an ARMATURE modifier on object that needs shape keys baked

'Extra Accuracy' (zero by default)
- increase accuracy of 'Dynamic' bake at cost of extra computation time, use 0 to start and increase as needed
- might only be needed in Blender v2.79, due to floating point accuracy error

### Bake Deform ShapeKey - Deform SK View Toggle
Toggle visibility between shape keys and cloth/soft body sims on active object. Intended only for non-Dynamic deform shape keys
Deform SK View Toggle - **only available if 'Dynamic' is disabled** - a convenience function to:
- if toggling on:
  - make CLOTH and SOFTBODY sims not visible
  - disable influence of ARMATURE modifier on vertexes that have baked shape keys, so that shape key verts are not "double-Armature-modified"
    - this step is unnecessary if 'Dynamic' bake is used, since shape keys are baked with armature influence accounted for
- if toggling off:
  - make CLOTH and SOFTBODY sims visible
  - undo disabling of influence of ARMATURE modifier on vertexes that have baked shape keys

## Armature
### Retarget - Adjust Pose
This script takes a user-created Comma Separated Variable (CSV) script and rotates pose-bones automatically.

Background: Time is wasted doing repetitive rotations of pose-bones to match imported animated rigs, in preparation for AMH2B 'Lucky' function.

In other words, script a series of pose-bone rotations so that an imported MakeHuman MHX rig aligns to an imported animated rig (Mixamo or CMU, only Mixamo supported presently) to simplify process of animating mass amounts of MakeHuman MHX rigs.

**If using Blender 2.79 then press 'Reload Trusted' button in a loaded Blend file, or click 'Trusted Source' in 'Load Blend' window, to enable MHX scripts before using adjust pose - or result will be a pose adjustment that is unpredictable for FK and IK bones.**

#### Instructions to use script:
- Open Text Editor and create a text. Default name is "Text". Copy-and-Paste text from a file in [ref_data folder](https://github.com/DreamSpoon/AMH2B/tree/main/ref_data) that matches your desired rig types and poses. Or make a custom CSV text, type rotations in Comma Separated Variable (CSV) format like this:

clavicle.L, y, -15

clavicle.L, z, 5

upper_arm.fk.L, y, -34

- See AMH2B menu, Armature panel, Text Editor Script Name - this is where you enter name of CSV text you just created, or leave it as default "Text"
- Select armature that needs it's pose-bones adjusted
- Press button AMH2B -> Armature -> Retarget - AdjustPose
- Result: Pose bones in selected armature will be rotated according to script

### Retarget - Apply Scale to Rig
Correctly apply scale to animated armature, by adjusting its pose bone location animation f-curve values to match scaling.

Background: Blender applies scale to non-animated rigs correctly, but animations attached to rig (i.e. f-curves) are not scaled. Result is usually animated rig moves violently around scene, or animation seems to hover in place and not move when it should move. Blender applies scale only to bone lengths and bone locations in current frame, but no scaling applied to animations (f-curves).

#### Instructions to use script:

Select armature that needs 'apply scale'.

Press button AMH2B -> Armature -> Retarget - Apply Scale to Rig

Result: Scale of selected armature is 1.0 in X/Y/Z axes. Also, keyframed animation on rig is scaled correctly.

### Retarget - Bridge Re-Pose
Re-pose original rig (which has shape keys, hence need for this work-around) by way of a duplicate "bridge" of original rig that moves mesh to desired pose, then original rig can animate from there on.

Basically, a duplicate rig moves underlying mesh to place where re-posed original rig should be.

#### Instructions to use script:
Select only armature (MHX armature, although this script will work with any armature) that needs its current pose to be set as 'rest pose'.

Press button AMH2B -> Armature -> Retarget - Bridge Re-Pose

Result: Extra armature is created, and selected meshes will have an Armature modifier applied which uses this extra armature.

### Retarget - Bone Woven
Simplify MakeHuman rig animation process re: Mixamo et al. via a bridge that connects imported animation rigs to imported MHX2 rigs - leaving face panel and visemes intact, while allowing for great functionality e.g. finger movements.

In a perfect world, Blender and MakeHuman would work seamlessly with any and all motion capture data, and any motion capture sharing website (including body, facial, etc. rig). Real world includes problems with bone names, 'bone roll', vertex groups, etc. This script bridges some real world gaps between different rigs, and re-targeting animations.

Basically, bones from Rig B (this could be a downloaded rig from a mocap sharing website, etc.) are mapped to Rig A so that Rig B acts like "marionettist" to Rig A "marionette". Rig B controls Rig A, allowing user to tweak final animation by animating Rig A.

Caveat: Rig A and Rig B should be in same pose.

Side-note: Ugly, But Works

#### Instructions to use script:
Select animated source rig and MHX destination rig, so that MHX rig is active object.

Press button AMH2B -> Armature -> Retarget - Bone Woven

Result: Animated rig is joined to MHX rig, and a 'stitching' process will copy-swap-and-parent animated bones into MHX rig's bone setup.

Important! Make sure your MHX rig has scale 1 in x/y/z, zero location, zero rotation - basically all transforms equal default. If your MHX rig already has location/rotation/scale, then re-locate/rotate/apply scale (with Apply Scale to Rig (!)) to set everything back to defaults. If MHX rig has non-default location/rotation/scale then results are undefined.

It's a good idea to edit bone groups after Bone Woven is applied. Select a visibility group that has "new" bones from animated rig, and very few bones from original MHX rig, e.g. bone visility layer 0 (zero). Enter EDIT or POSE mode, select all, then deselect MHX bones (only 2 bones in bone vis layer 0!), and move remaining bones to desired (empty) bone visibility layer. This way it's easier to select only "new" bones, or just regular MHX bones.

### Retarget Multi-Function - Lucky
One button press to:
1) Bridge Re-pose Rig (optional)
2) Scale incoming rig
3) BoneWoven two rigs together

Go to Dope Sheet -> Action Editor and add original animation to your new rig.
If all works correctly then old rig is animating inside your MHX rig, and this controls original MHX rig's bones.

#### Instructions to use script:
Before pressing this button, move the animated rig location to match the MHX rig as closely as possible - does not need to be exact, but don't have the rig 20 meters apart! **Move the animated rig to the MHX rig**, not the other way around.

Also, **scale the animated rig to closely match the MHX rig** - don't scale the MHX rig, change scale of animated rig instead.

Then, select all of:
1) Rig with animation you want transferred to MHX rig
2) Objects attached to MHX rig with 'Armature' modifier (e.g. clothes, skin, hair, eyebrows)
3) MHX rig (select MHX rig last)

Press button AMH2B -> Armature -> Retarget Multi - Lucky

Result: This will Re-Pose MHX rig, apply location/rotation and Apply Scale to animated rig, and finish with Bone Woven joining two rigs.

One click success, if lucky.

### Preserve Volume Toggle - Enable / Disable
For every Armature modifier on all selected objects, set Preserve Volume to Enabled or Disabled.

### Bone Names - Rename Generic
Rename armature bones to match the format 'aaaa:bbbb', where 'aaaa' is the generic prefix. 'G Prefix' is used, default value is 'G'.
- e.g. bone named 'aaaa:bbbb' would be renamed to 'G:bbbb'

Enable 'Include MHX Bones' to include bones with MHX bone names when renaming bones in the selected armature.

### Bone Names - Un-name Generic
Rename bones to remove any formating like 'aaaa:bbbb', where 'aaaa' is removed and the bones name becomes 'bbbb'.
- e.g. bone named 'aaaa:bbbb' would be renamed to 'bbbb'

## Animation
### Object Location - Ratchet Hold
Idea of script:

Easily keyframe movement of a walking/moving rig, by letting user select part of armature that should appear motionless (e.g. left leg stationary) while rest of armature moves about that part (e.g. right leg moving).

Re-calculate location data for an object (typically armature) given:
1) A single "Empty" type object, that is parented to a part of armature object
  - i.e. Parented to a bone in armature object
2) Location of original object (armature) should be offset, and keyframed, to make "Empty" type object appear to be motionless

#### Instructions to use script:
- Select exactly two objects:
  - Object A - "Empty" type object that we want to appear motionless (empty is parented to B)
  - Object B - parent object (typically armature that has walking animation)
- Object B must be selected last so that it is active object.
- Before using this script, make sure that object A is parented to object B.
- Press button AMH2B -> Animation -> Ratchet Hold

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

## Eyelid
### Add Lid Look
Use the settings given (e.g. eye bone names, rotation limits) to automatically add bone constraints to eyelids so that eyelids will move as eyes rotate up/down.

The MHX rig has a "gaze" bone, which lets the user easily adjust eye rotations to "look at" a point in space. "Copy Rotation" bone constraints are added to eyelid bones to copy some of the rotation from the eye bones, so eyelid movement matches eye movement.

## Eye Blink
### Remove Blink Track
Remove blink track from list of selected objects plus active object, based on EyeBlink and LidLook settings. Both eyeblink and "Lid Look" keyframes are removed.

Keyframes are removed from the bones with names given in the following tabs:
1) Eyelid tab -> Eyelid Bone Names
2) Eye Blink tab -> Template Bone Bames

Start and End Frames can be specified, so that certain sections of blink track can be kept while others are removed.

If no Start/End Frame is given then all Eye Blink and Lid Look keyframes are removed.

### Add Blink Track
Use the blink settings (timing, bone names, and bone positions/rotations) to add "blink track" to active object. If a second object is also selected (must be a MESH type object), then a Shapekey on the MESH object can be keyframed for the "blink track", in addition to eye bone blink keyframes.

The "closed" and "opened" states of the bones can be Set and Reset, independently.

Blink settings can also be written (saved) to a textblock (view with the Text Editor within Blender). Blink settings can also be read (loaded) from a textblock in the Text Editor.

#### Template Save/Load
Settings for eyeblink open/closed state and eyeblink timing can be saved in CSV format to text data-blocks in Blender's internal text editor.

Hint: Test this feature by pressing the "Write Settings" button, then open Blender's internal text editor and selecting the text block (default name is Text). Comma separated settings can be read and modified. Press the "Read Settings" button to read the settings back into the addon, then press the Add Blink Track Button to apply a blink track with the newly modifed settings. Eyeblink settings can be saved as templates for re-use later. e.g. eyeblink settings for each character in a series of scenes.

## Template
### Setup Material Swap - Rename Materials
Rename materials in material slot(s) on all selected objects to make them searchable re: swap material from file.

'Active Slot Only' - only the currently selected material slot (Active Slot) of each object will be swapped

### Notes re: creating materials template file:
Export a MakeHuman model to MHX2 format (does not need to be MHX rig, or even have a rig, this works with any rig type - and no rig).

Modify materials setup, i.e. shader nodes. Finally, use Rename Materials to change names of materials like so:

'Mass0010:Uniform_jacket:Uniform_jacket'

would become:

'Uniform_jacket:Uniform_jacket'

Renaming materials in this way lets Swap Materials functions find materials in materials template file.
Now material name will be found when Swap Material function is run.

For reference, naming convention of materials imported from MHX2 seems to be:

'HumanName:PartName:PartMaterialName'

e.g.

'Mass0010:Uniform_jacket:Uniform_jacket'

'Shelagh:Uniform_jacket:Uniform_jacket'

'Mass0002:High-poly:Eye_deepblue'

'Floopy:High-poly:Eye_brown'

### Vertex Group and ShapeKey - Make Objects Searchable
Rename active object, if needed, to make it searchable re: automatic search of file for vertex groups by object name and vertex group name prefix.

For reference, naming convention of objects imported from MHX2 seems to be:

'HumanName:PartName'

e.g.

'Mass0010:Uniform_jacket'

'Shelagh:Uniform_jacket'

'Mass0002:High-poly'

'Floopy:High-poly'

# Congratulations! You read me to the end.
