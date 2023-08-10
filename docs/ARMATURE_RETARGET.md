# Armature Retarget Workflow
Transfer animations from Mixamo, CMU mocap, etc. to MHX or Rigify armatures.
Simplify MakeHuman rig animation process re: Mixamo et al. via a bridge that connects imported animation rigs to imported MHX2 rigs - leaving face panel and visemes intact, while allowing for great functionality e.g. finger movements.

This involves pose matching, joining armatures, and transferring animation from joined armature to a duplicate of original armature.

This is a multi-step process, explained by example below:

## Example: Mixamo to MHX
Transfer animation from Mixamo import (.fbx file) to MHX import (.mhx2 file).

1) Pose Matching
MHX default pose does not match Mixamo default pose, so adjustments are needed:
- select MHX armature, and use Armature -> Retarget -> Script Pose
  - this opens menu with options to automatically match MHX armature to Mixamo armature
  - select 'Mixamo 5 Finger to Import MHX FK', and press OK
  - MHX armature should now match Mixamo armature (T-pose)
- next, MHX armature pose must be applied, but MHX mesh ShapeKeys cause problems, so
- with all meshes attached to MHX armature:
  - disable in Viewport all Object modifiers *except Armature* modifier
    - e.g. disable Mask modifiers in Viewport, because mesh needs same vertex count before and after modifiers are applied
- select all meshes attached to MHX armature, and use ShapeKey -> Apply Modifier -> Apply Modifier
  - meshes will initially look distorted, but
- select MHX armature, and change to Pose mode
  - in Pose menu at top of window (only available in Pose mode)
  - choose Apply -> Apply Pose as Rest Pose
  - meshes attached to MHX armature should now appear normal
  - switch back to Object mode for next steps

2) *Snap IK to FK*
This step is easy to forget, so make note to do this or there will be problems later with IK pose bone locations.
Go to 'MHX2 Runtime' tab in Tools menu of 3D Viewport context.
Open 'FK/IK Switch' panel, and look down to the 'Snap Arm Bones' section:
- use 'Snap L IK Arm' and 'Snap R IK Arm'
- use 'Snap L IK Leg' and 'Snap R IK Leg'

The IK bones of the MHX armature should now be visible in Pose mode. Usually the elbow 'IK poles' are at incorrect locations, and the character's arms may look twisted.

Solution:
- use 'Pose' mode
- select elbow 'IK poles', named:
  - elbow.pt.ik.L and elbow.pt.ik.R
- grab (move) above named bones to locations behind character, i.e. on the +Y axis
- 'IK poles' should be horizontal behind elbows of character's mesh

3) Apply Armature Object Modifer and Apply Armature Pose
The current pose of the MHX armature needs to be 'applied', with 'Apply Pose as Rest Pose', before applying 'Stitch Armature' (in later steps).

To 'Apply Pose as Rest Pose' to the MHX armature, and keep attached meshes working correctly, each mesh attached to MHX armature needs to have its Armature modifier applied.

When trying to apply Armature object modifier to MHX meshes, the operation fails because some MHX meshes have ShapeKeys.

To fix this problem, use the ShapeKey -> Apply Modifier -> Apply Modifiers function.
- using this function will apply the Armature object modifier to all ShapeKeys of a mesh, as well as the base vertex locations
- the object's Armature modifier is unchanged - it is still needed

What to do:
- *disable Mask and Subdivision object modifiers on all meshes attached to MHX armature*
  - *un-modified* mesh must have the same number of vertices as *modified* mesh
  - to prevent problems later, it is a good idea to disable (in Viewport) all object modifiers except Armature modifiers
- select all meshes attached to MHX armature and use 'Apply Modifiers' function
  - meshes may look distorted at this point, but that is ok
- switch to 'Pose' mode, then use a function in Pose menu:
  - Pose mode -> Pose menu -> Apply -> Apply Pose as Rest Pose
- MHX armature's 'Rest Pose' will now match Mixamo armature's 'Rest Pose'

4) Duplicate MHX Armature
This step is only necessary if the final animated armature needs to be an unmodified MHX armature, i.e. no extra bones from the Stitch Armature process.

Duplicate (not linked) the MHX armature, and hide it.
- it will be used later for transferring animation from a modified MHX armature, to this un-modified MHX armature

5) Stitch Armature
This function joins the Mixamo armature with the MHX armature to retarget animation.

Afterwards, using Armature -> Retarget -> Copy Transforms, the animation can be transferred to the original armature (the duplicate from earlier).

Next steps:
- select Mixamo armature first, and MHX armature last, so that MHX armature is active object
- use Armature -> Retarget -> Stitch Armature
- result is a joined armature with Mixamo pose bones moving MHX pose bones, but no animation of pose bones

6) Animate Joined Armature
- go to Dope Sheet context and change UI mode from 'Dope Sheet' to 'Action Editor'

In about the middle of the Action Editor area, use 'Browse Action to be linked' to see list of animations available.
- see button just to left of '+    New' button

- choose animation from dropdown list of animations (Mixamo .fbx import animations)
  - e.g. Armature|mixamo.com|Layer0
- play animation in 3D Viewport to check results - the joined armature, and its attached meshes, should be animating correctly
  - if it is not animating correctly (e.g. problems in IK Mode)
    - then undo a few steps and redo the Snap IK to FK steps (just after Pose Matching)

This may be enough, because the MHX armature is animating correctly. The next step is optional, but it will reduce 'clutter' by removing extra bones from armature.

7) Copy Animation to Duplicate Armature
The following steps will copy the current animation from the modified MHX armature (joined armature), to a unmodified MHX armature.

- un-hide the duplicated MHX armature that was created in step 4)
  - this unmodified MHX armature will be animated to match the joined armature
- set scene Timeline's 'Start Frame' and 'End Frame' to match the imported Mixamo animation start and end frame
  - or use start and end frame of total animation of armature, e.g. if using NLA tracks and mixing multiple animations
- select the joined armature (MHX + Mixamo) first, and the unmodified MHX armature last (MHX armature from step 4)
- use Armature -> Retarget - > Copy Transforms to copy animation from joined armature to old MHX armature
- with each mesh attached to the joined armature, change its Armature object modifier 'Object' to old MHX armature

Now, all meshes that were animated by the joind armature are instead animated by the unmodified MHX armature.
- delete the joined armature (modified MHX armature), because it has been replaced by the animated unmodified MHX armature
