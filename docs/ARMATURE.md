# Armature

## Utility - Preserve Volume Toggle - Enable / Disable
For every Armature modifier on all selected objects, set Preserve Volume to Enabled or Disabled.

## Utility - Apply Scale to Rig
If 'Apply Scale' is used on armatures with animated pose bones, the animation becomes distorted - because it is not scaled properly.
This function will correctly apply scale, by adjusting pose bone location animation f-curve values to match scaling.

### Usage
Select armature, and use AMH2B -> Armature -> Retarget - Apply Scale to Rig

Result: Scale of selected armature is 1.0 in X/Y/Z axes, and keyframed animation is correct.

## Utility - Bone Names - Rename Generic
Rename armature bones to match the format 'aaaa:bbbb', where 'aaaa' is the generic prefix. 'G Prefix' is used, default value is 'G'.
- e.g. bone named 'aaaa:bbbb' would be renamed to 'G:bbbb'

Enable 'Include MHX Bones' to include bones with MHX bone names when renaming bones in the selected armature.

## Utility - Bone Names - Un-name Generic
Rename bones to remove any formating like 'aaaa:bbbb', where 'aaaa' is removed and the bones name becomes 'bbbb'.
- e.g. bone named 'aaaa:bbbb' would be renamed to 'bbbb'
