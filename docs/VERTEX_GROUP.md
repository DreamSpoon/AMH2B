# Vertex Group

## Functions - Copy from File
For each selected mesh object:
- search another file automatically and try to copy vertex groups based on Prefix and object name
- note: name of object from MHX import process is used to search for object in other selected file

## Functions - Copy Groups
Copy vertex groups (by name prefix) from active object to all other selected mesh objects.
Many uses for this function, including easy copy of Vertex Groups from character to clothes.
Character to clothes copying of vertex groups happens in two parts:
1) Copy the Vertex Group Names (AMH2B->Vertex Group->Copy Groups function)
2) Copy the Vertex Group Data (Data Transfer modifier)
How to do it:
1)
  - Go to the AMH2B panel in the 3DView window: AMH2B panel -> Vertex Group -> Copy Vertex Group
    - Enable the option "Create Groups Only in Name"
    - set the Prefix to blank (i.e. clear the "Prefix" box), so that all group names are copied
2)
  - Add a Data Transfer modifier to the clothes mesh object, and use these settings in the modifier:
    - enable Vertex Data
	- use 'Nearest Vertex' or better (better = higher quality)
	- select 'Vertex Group(s)', 'All Layers', 'By Name'
    - set Mix mode: 'Replace'
  - now look at the Vertex Groups in the "weight paint editing" mode of the 3DView, and check that the groups are transferring correctly
  - some adjustments to the clothes mesh may be needed to get best results
  - non-destructive changes to the character mesh are also possible
    - create a copy of the character mesh
	- modifying this new mesh to fix Vertex Group copying problems
    - Data Transfer to clothes from the new mesh
	- delete the copied-and-modified mesh
  - if everything looks good, then apply the Data Transfer modifier
  - **Data Transfer modifier must be applied before animating character/clothes, to prevent "tearing" / glitched vertex problems**
Following these two steps will copy all the Vertex Groups from character mesh to clothes mesh.

Description of Swap Autoname Ext option:
- enable this to solve a problem when making copies of character mesh objects, because Blender automatically renames the copied objects
  - when character's mesh objects are copied, Blender appends ".001", ".002", etc. to the name
  - copying an entire character's meshes (including teeth, eyes, etc.) will change the names of the copied meshes
  - e.g. Object Mass0007:Eyebrow010.003 vertex groups may be copied from object Mass0007:Eyebrow010 vertex groups
- this options solves the problem by ignoring the end of the name if name ends with ".001", ".002", etc.

## Functions - Delete Groups
With all selected objects, delete vertex groups by prefix.
