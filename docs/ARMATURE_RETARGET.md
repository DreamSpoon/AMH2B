# Armature Retarget Workflow
Transfer animations from Mixamo, CMU mocap, etc. to MHX or Rigify armatures.
Simplify MakeHuman rig animation process re: Mixamo et al. via a bridge that connects imported animation rigs to imported MHX2 rigs - leaving face panel and visemes intact, while allowing for great functionality e.g. finger movements.

This involves pose matching, joining armatures, and transferring animation from joined armature to a duplicate of original armature.

This is a multi-step process, explained by example below:

## Example: Mixamo to MHX
Transfer animation from Mixamo import (.fbx file) to MHX import (.mhx2 file).
The following steps assume:
- MHX armature has been imported using File -> Import -> MakeHuman (.mhx2)
  - enable Override Exported Data, and set Rigging -> Rig Type to 'MHX'
- Mixamo armature has been imported using File -> Import -> FBX (.fbx)
  - enable Armature -> Ignore Leaf Bones

1) Pose Matching
MHX default pose does not match Mixamo default pose, so adjustments are needed:
- select MHX armature, and use Armature -> Retarget -> Script Pose
  - this opens menu with options to automatically match MHX armature to Mixamo armature
  - select 'Mixamo 5 Finger to Import MHX FK', and press OK
  - MHX armature should now match Mixamo armature (T-pose)
- next, MHX armature pose must be applied, but MHX mesh ShapeKeys cause problems, so
- with all meshes attached to MHX armature:
  - disable (in Viewport) all Object modifiers *except Armature* modifier
    - e.g. disable Mask modifiers in Viewport, because mesh needs same vertex count before and after modifiers are applied
- select all meshes attached to MHX armature, and use ShapeKey -> Apply Modifier -> Apply Modifier
  - meshes will initially look distorted, but
- select MHX armature, and change to Pose mode
  - in Pose menu at top of window (only available in Pose mode)
  - choose Apply -> Apply Pose as Rest Pose
  - meshes attached to MHX armature should now appear normal
  - switch back to Object mode for next steps

2) Snap IK to FK
This will snap the IK bones to the FK bone positions, so IK will work later.
Note: Snap MHX IK will also reset 'elbow IK pole' pose positions, to fix a common problem.
- select imported MHX armature, then use Armature -> Retarget -> Snap MHX IK

3) Apply Armature Object Modifer and Apply Armature Pose
The MHX armature pose needs to be 'applied' before applying 'Stitch Armature' (in later steps). This happens in two parts:
  i) with all MHX meshes, apply Armature object modifiers
  ii) with MHX armature, use Pose mode -> Pose menu -> Apply Pose as Rest Pose

MHX meshes with ShapeKeys will cause part a) to fail. There is a workaround, next steps:
- disable Mask and Subdivision object modifiers on all meshes attached to MHX armature
  - *un-modified* mesh must have the same number of vertices as *modified* mesh
  - to prevent problems later, it is a good idea to disable (in Viewport) all object modifiers except Armature modifiers
- select all meshes attached to MHX armature, then use ShapeKey -> Apply Modifier -> Apply Modifiers
  - this function will apply Armature object modifier to mesh vertices and to all mesh ShapeKeys
  - object's Armature modifier is unchanged - keep this modifier for later steps
  - meshes may look distorted at this point, but that is ok
- select MHX armature, then switch to 'Pose' mode
  - use Pose menu -> Apply -> Apply Pose as Rest Pose
- now, MHX armature's 'Rest Pose' will closely match Mixamo armature's 'Rest Pose'

4) Duplicate MHX Armature
This step is only necessary if the final animated armature needs to be an unmodified MHX armature, i.e. no extra bones from Stitch Armature process.
- duplicate (not linked) the MHX armature, and hide this duplicate
  - this duplicate will be used later for receiving animation from a modified MHX armature

5) Stitch Armature
This function joins the Mixamo armature with the MHX armature to retarget animation.

Afterwards, using Armature -> Retarget -> Copy Transforms, animation can be transferred to a unmodified copy of the MHX armature (from step 4).

Next steps:
- select Mixamo armature first, and MHX armature last, so that MHX armature is active object
- use Armature -> Retarget -> Stitch Armature
- result is a joined armature with Mixamo pose bones moving MHX pose bones
  - pose bones are not animated yet

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

7) Copy Animation to Unmodified Armature
The following steps will copy current animation from the modified MHX armature (joined armature), to a unmodified MHX armature.

- un-hide the unmodified MHX armature that was created in step 4)
  - this unmodified MHX armature will be animated to match the joined armature
- set scene Timeline's 'Start Frame' and 'End Frame' to match the imported Mixamo animation start and end frame
  - or use start and end frame of total animation of armature, e.g. if using NLA tracks and mixing multiple animations
- select the joined armature (MHX + Mixamo) first, and the unmodified MHX armature last (MHX armature from step 4)
- use Armature -> Retarget - > Copy Transforms to copy animation from joined armature to old MHX armature
- with each mesh attached to the joined armature, change its Armature object modifier 'Object' to old MHX armature

Now, all meshes that were animated by the joined armature are instead animated by the unmodified MHX armature.
- delete the modified MHX armature (joined armature), because it has been replaced by the unmodified MHX armature
