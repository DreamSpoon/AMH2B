# Template

## Setup Material Swap - Rename Materials
Rename materials in material slot(s) on all selected objects to make them searchable re: swap material from file.

'Active Slot Only' - only the currently selected material slot (Active Slot) of each object will be swapped

## Notes re: creating materials template file:
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

## Vertex Group and ShapeKey - Make Objects Searchable
Rename active object, if needed, to make it searchable re: automatic search of file for vertex groups by object name and vertex group name prefix.

For reference, naming convention of objects imported from MHX2 seems to be:

'HumanName:PartName'

e.g.

'Mass0010:Uniform_jacket'

'Shelagh:Uniform_jacket'

'Mass0002:High-poly'

'Floopy:High-poly'
