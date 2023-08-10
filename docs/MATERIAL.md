# Mesh Material

## Material Swap - Search File
Select all mesh objects that need their materials swapped, then use Swap Material -> Search File.
This will automatically swap materials from another .blend file, by material name. Use Template -> Rename Materials to make materials "searchable" by this function. Custom material templates for clothing can be kept in one folder/file and used again quickly.
- Materials are appended from source file by name, and names are "guessed" by trimming names of materials and trying to append materials from blend file.
- e.g. Material named 'Mass0010:Uniform_jacket:Uniform_jacket' will be swapped with material named 'Uniform_jacket:Uniform_jacket' from user selected file (material dictionary file).
Select one file with preferred materials in it. Run this command multiple times for multiple materials. This will swap all material slots (or just Active), if possible, with materials in other .blend files.

## Material Swap - Search Internal
Select all mesh objects that need their materials swapped, then use Swap Material -> Search Internal.
Similar to Search File, this function will try to swap material slot(s) of all selected objects with replacement materials from same Blend file.
