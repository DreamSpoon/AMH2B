# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#
# Automate MakeHuman 2 Blender (AMH2B)
#   Blender 2.xx Addon (tested and works with Blender 2.79b, 2.83, 2.93)
# A set of tools to automate the process of shading/texturing, and animating MakeHuman data imported in Blender.

import re
import bpy
from bpy_extras.io_utils import ImportHelper

from .append_from_file_func import *
from .material_func import *
from .template import get_mat_template_name

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

#####################################################
#     Swap Materials from Other Blend File
# Automate materials dictionary material swapping with a simple method:
#   1) User chooses file with source materials.
#   2) Materials are appended "blindly", by trimming names of materials on selected objects
#      and trying to append trimmed name materials from the blend file chosen by the user.

# Checks if the material already exists in this file, if it does exist then rename the
# current material, and then append the new material.

def do_swap_mats_with_file(shaderswap_blendfile, selection_list, active_slot_only, exact_name_only, ignore_autoname,
                           keep_original_name, delimiter, delimiter_count):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    mats_loaded_from_file = []

    # do the material swaps for each selected object
    for obj in selection_list:
        # iterate over the material slots and check/swap the materials
        for mat_slot in (s for s in obj.material_slots if s.material is not None):
            # skip this slot if 'active slot only' is enabled and if this is not the active slot
            if active_slot_only and mat_slot != obj.material_slots[obj.active_material_index]:
                continue
            original_mat_name = mat_slot.material.name
            if exact_name_only:
                swatch_mat_name = mat_slot.material.name
            else:
                swatch_mat_name = get_mat_template_name(mat_slot.material.name, delimiter, delimiter_count+1)

            # if material has already been loaded from file...
            if swatch_mat_name in mats_loaded_from_file:
                # swap material
                mat_slot.material = bpy.data.materials[swatch_mat_name]
                continue

            # if "swap material" already exists, then rename it so that a newer version
            # can be loaded from library file
            test_swap_mat = bpy.data.materials.get(swatch_mat_name)
            if test_swap_mat is not None:
                test_swap_mat.name = "A1:" + swatch_mat_name

            # if cannot load material from file...
            if not append_material_from_blend_file(shaderswap_blendfile, swatch_mat_name):
                # if "ignore autoname" is enabled then check material name, and if it follows the
                # '.001', '.002', etc. format, then try to swap again but with '.XYZ' extension removed
                if ignore_autoname and re.match(".*\.[0-9]{3}", swatch_mat_name) and append_material_from_blend_file(shaderswap_blendfile, swatch_mat_name[0:len(swatch_mat_name)-4]):
                    swatch_mat_name = swatch_mat_name[0:len(swatch_mat_name)-4]
                else:
                    # if rename occurred, then undo rename
                    if test_swap_mat is not None:
                        test_swap_mat.name = swatch_mat_name
                    continue

            # include the newly loaded material in the list of loaded materials
            mats_loaded_from_file.append(swatch_mat_name)

            # check original material name needs to be changed due to swap and keep original name
            if keep_original_name:
                mat_slot.material.name = "B1:" + mat_slot.material.name

            # swap material
            mat_slot.material = bpy.data.materials[swatch_mat_name]

            # check if rename to original material name
            if keep_original_name:
                mat_slot.material.name = original_mat_name

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_SwapMatWithFile(AMH2B_SearchInFileInner, bpy.types.Operator, ImportHelper):
    """Try to swap materials on all selected objects with replacement materials from another Blend File, based on following settings"""
    bl_idname = "amh2b.mat_search_file"
    bl_label = "Search File"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        do_swap_mats_with_file(self.filepath, context.selected_objects, scn.Amh2bPropMatActiveSlotOnly,
            scn.Amh2bPropMatExactNameOnly, scn.Amh2bPropMatIgnoreAutoname, scn.Amh2bPropMatKeepOriginalName,
            scn.Amh2bPropMatDelimiter, scn.Amh2bPropMatDelimCount)
        return {'FINISHED'}

#####################################################
# Swap Materials Internal
# Search current Blend file for material that matches a "swappable" material based on name.
# E.g. given "SomeChar:HairMat1:HairMat1" is name of selected material, then
#      a "swappable" material based on that name would be "HairMat1:HairMat1".
#
# Search and swap materials for all material slots on all selected objects, unless active slot only.

def do_mat_swaps_internal(sel_obj_list, active_slot_only, ignore_autoname, keep_original_name,
                          delimiter, delimiter_count):
    # fix materials on all selected objects, swapping to correct materials if available
    for obj in sel_obj_list:
        # iterate over the material slots and check/swap the materials
        for mat_slot in (s for s in obj.material_slots if s.material is not None):
            # skip this slot if 'active slot only' is enabled and if this is not the active slot
            if active_slot_only and mat_slot != obj.material_slots[obj.active_material_index]:
                continue

            original_mat_name = mat_slot.material.name
            # get potential name of swap material and check for its existence
            temp_mat_name = get_mat_template_name(mat_slot.material.name, delimiter, delimiter_count+1)
            sm = bpy.data.materials.get(temp_mat_name)
            if sm is None:
                # if "ignore autoname" is enabled then check material name, and if it follows the
                # '.001', '.002', etc. format, then try to swap again but with '.XYZ' extension removed
                if ignore_autoname and re.match(".*\.[0-9]{3}", temp_mat_name):
                    temp_mat_name = temp_mat_name[0:len(temp_mat_name)-4]
                    sm = bpy.data.materials.get(temp_mat_name)
                    if sm is None:
                        continue
                else:
                    continue

            # check original material name needs to be changed due to swap and keep original name
            if keep_original_name:
                mat_slot.material.name = "B1:" + mat_slot.material.name

            # swap material
            mat_slot.material = sm

            # check if rename to original material name
            if keep_original_name:
                mat_slot.material.name = original_mat_name

class AMH2B_SwapMatInternal(bpy.types.Operator):
    """Try to swap materials of all selected objects with replacement materials contained within this Blend file, based on following settings"""
    bl_idname = "amh2b.mat_search_internal"
    bl_label = "Search Internal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        # cannot search internally for swap because "exact name only" causes a contradiction:
        # replacing a material with itself!
        if scn.Amh2bPropMatExactNameOnly:
            return {'FINISHED'}
        do_mat_swaps_internal(context.selected_objects, scn.Amh2bPropMatActiveSlotOnly,
            scn.Amh2bPropMatIgnoreAutoname, scn.Amh2bPropMatKeepOriginalName, scn.Amh2bPropMatDelimiter,
            scn.Amh2bPropMatDelimCount)
        return {'FINISHED'}
