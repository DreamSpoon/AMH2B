# Eye Blink

## Remove Blink Track
Remove blink track from list of selected objects plus active object, based on EyeBlink and LidLook settings. Both eyeblink and "Lid Look" keyframes are removed.

Keyframes are removed from the bones with names given in the following tabs:
1) Eyelid tab -> Eyelid Bone Names
2) Eye Blink tab -> Template Bone Bames

Start and End Frames can be specified, so that certain sections of blink track can be kept while others are removed.

If no Start/End Frame is given then all Eye Blink and Lid Look keyframes are removed.

## Add Blink Track
Use the blink settings (timing, bone names, and bone positions/rotations) to add "blink track" to active object. If a second object is also selected (must be a MESH type object), then a Shapekey on the MESH object can be keyframed for the "blink track", in addition to eye bone blink keyframes.

The "closed" and "opened" states of the bones can be Set and Reset, independently.

Blink settings can also be written (saved) to a textblock (view with the Text Editor within Blender). Blink settings can also be read (loaded) from a textblock in the Text Editor.

### Template Save/Load
Settings for eyeblink open/closed state and eyeblink timing can be saved in CSV format to text data-blocks in Blender's internal text editor.

Hint: Test this feature by pressing the "Write Settings" button, then open Blender's internal text editor and selecting the text block (default name is Text). Comma separated settings can be read and modified. Press the "Read Settings" button to read the settings back into the addon, then press the Add Blink Track Button to apply a blink track with the newly modifed settings. Eyeblink settings can be saved as templates for re-use later. e.g. eyeblink settings for each character in a series of scenes.
