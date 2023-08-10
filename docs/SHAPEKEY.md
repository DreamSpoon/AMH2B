# ShapeKey

## Apply Modifier -> Apply Modifiers
This function is intended to help with Pose Matching an MHX armature, so that animation retargetting can be used.
Retargetting an MHX armature to, e.g. Mixamo, for animation has a problem:
- the MHX armature needs to be re-posed, then use Pose Mode -> Pose menu -> Apply -> Apply Pose as Rest Pose
- the imported MHX meshes may have ShapeKeys with drivers, e.g. 'Face Panel' drivers
  - the Armature modifiers of these meshes cannot be applied because of ShapeKeys
This function solves the ShapeKey problem by *manually* applying modifiers to ShapeKeys, as well as base vertex positions.

### Usage
Select all meshes attached to MHX armature, then use this function.
It will apply all visible object modifiers (e.g. Armature modifier) to the base vertex locations, and all ShapeKeys - even ShapeKeys with drivers.

Object modifiers are not removed, meshes may look *deformed* after using this function, so to solve problem:
- with MHX armature active, use Pose Mode -> Pose menu -> Apply -> Apply Pose as Rest Pose
- armature should now be in new Pose and meshes will be in same pose

*Mesh must have the same number of vertices before and after modifiers are applied.*
- e.g. disable (in Viewport) all 'Mask' object modifiers on mesh

## Bake - Bake Deform Keys
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

## Bake Deform Keys - Deform SK View Toggle
Toggle visibility between shape keys and cloth/soft body sims on active object. Intended only for non-Dynamic deform shape keys
Deform SK View Toggle - **only available if 'Dynamic' is disabled** - a convenience function to:
- if toggling on:
  - make Cloth and Soft Body sims not visible
  - disable influence of ARMATURE modifier on vertexes that have baked shape keys, so that shape key verts are not "double-Armature-modified"
    - this step is unnecessary if 'Dynamic' bake is used, since shape keys are baked with armature influence accounted for
- if toggling off:
  - make Cloth and Soft Body sims visible
  - undo disabling of influence of Armature modifier on vertexes that have baked shape keys

## Copy - Copy from File
For each selected MESH object: Search another file automatically and try to copy shape keys based on Prefix and object name. Note: Name of object from MHX import process is used to search for object in other selected file.

## Copy - Copy Keys
With active object, copy shape keys by prefix to all other selected objects

## Delete - Delete Prefixed Keys
With selected MESH type objects, delete shape keys by prefix.
