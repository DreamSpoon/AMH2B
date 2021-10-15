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

import bpy
from bpy_extras.io_utils import ImportHelper
import re
import os

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

# Returns True if material was successfully appended.
# Checks if the material already exists in this file, if it does exist then rename the
# current material, and then append the new material.
def append_material_from_blend_file(mat_filepath, mat_name):
    # path inside of file (i.e. like opening the "Append" window; see Action, Armature, Brush, Camera, ...)
    inner_path = "Material"

    try:
        bpy.ops.wm.append(
            filepath=os.path.join(mat_filepath, inner_path, mat_name),
            directory=os.path.join(mat_filepath, inner_path),
            filename=mat_name
            )
    except:
        return False

    if bpy.data.materials.get(mat_name) is None:
        return False

    return True

# trim string up to, and including, the first ":" character, and return trimmed string
def get_swatch_name_for_MH_name(mh_name):
    # if name is in MH format then return trimmed name
    # (remove first third, up to the ":", and return the remaining two-thirds)
    if len(mh_name.split(":", -1)) == 3:
        return mh_name.split(":", 1)[1]
    # otherwise return original name
    else:
        return mh_name

def do_swap_mats_with_file(shaderswap_blendfile):
    mats_loaded_from_file = []

    # get list of objects currently selected and fix materials on all selected objects,
    # swapping to correct materials
    selection_list = bpy.context.selected_objects

    # do the material swaps for each selected object
    for obj in selection_list:
        # iterate over the material slots and check/swap the materials
        for mat_slot in obj.material_slots:
            # skip material slots without an assigned material
            if mat_slot.material is None:
                continue

            swatch_mat_name = get_swatch_name_for_MH_name(mat_slot.material.name)

            # if material has already been loaded from file...
            if swatch_mat_name in mats_loaded_from_file:
                # swap material
                print("Swapping material on object " + obj.name + ", oldMat = " + mat_slot.material.name + ", newMat = " + swatch_mat_name)
                mat_slot.material = bpy.data.materials[swatch_mat_name]
                continue

            # if "swap material" already exists, then rename it so that a
            # newer version can be loaded from library file
            test_swap_mat = bpy.data.materials.get(swatch_mat_name)
            if test_swap_mat is not None:
                test_swap_mat.name = "A1:" + swatch_mat_name

            # if cannot load material from file...
            if not append_material_from_blend_file(shaderswap_blendfile, swatch_mat_name):
                # if rename occurred, then undo rename
                if test_swap_mat is not None:
                    test_swap_mat.name = swatch_mat_name
                continue

            # include the newly loaded material in the list of loaded materials
            mats_loaded_from_file.append(swatch_mat_name)

            # swap material
            print("Swapping material on object " + obj.name + ", oldMat = " + mat_slot.material.name + ", newMat = " + swatch_mat_name)
            mat_slot.material = bpy.data.materials[swatch_mat_name]

class AMH2B_SwapMatWithFile(AMH2B_SwapMaterialsInner, bpy.types.Operator, ImportHelper):
    """Try to swap all materials (based on material name) on all selected objects with replacement materials from another Blend File"""
    bl_idname = "amh2b.swap_mat_from_file"
    bl_label = "From File"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        do_swap_mats_with_file(self.filepath)
        return {'FINISHED'}

#####################################################
# Swap Materials Internal Single and Multi
# Search current Blend file for material that matches a "swappable" material based on name.
# E.g. given "SomeChar:HairMat1:HairMat1" is name of selected material, then
#      a "swappable" material based on that name would be "HairMat1:HairMat1".
#
#     Single
# Search and swap material only active material slot on active object.
#     Multi
# Search and swap materials for all material slots on all selected objects.

def is_mat_swappable_name(mat_name):
    if mat_name.count(':') == 1:
        return True
    return False

def is_mat_mhx_name(mat_name):
    if mat_name.count(':') == 2:
        return True
    return False

# this function is different from get_swatch_name_for_MH_name() because this function assumes
# proper MHX convention format of mat_name
def get_swappable_from_mhx_name(mat_name):
    return mat_name[ mat_name.find(":")+1 : len(mat_name) ]

def rename_material(old_mat_name, new_mat_name):
    got_mat = bpy.data.materials.get(old_mat_name)
    if got_mat is not None:
        got_mat.name = new_mat_name

def do_mat_swaps_internal_single():
    obj = bpy.context.active_object
    if obj is None:
        return
    mat_slot = obj.material_slots[obj.active_material_index]
    if mat_slot is None:
        return

    if not is_mat_mhx_name(mat_slot.material.name):
        return

    # get potential name of swap material and check for its existence
    swap_mat_name = get_swappable_from_mhx_name(mat_slot.material.name)
    sm = bpy.data.materials.get(swap_mat_name)
    if sm is None:
        return

    # swap material
    print("Swapping material on object " + obj.name + ", oldMat = " + mat_slot.material.name + ", newMat = " + swap_mat_name)
    mat_slot.material = sm

class AMH2B_SwapMatIntSingle(bpy.types.Operator):
    """Try to swap material in object's active material slot with replacement material within this Blend file"""
    bl_idname = "amh2b.swap_mat_int_single"
    bl_label = "Internal Single"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_mat_swaps_internal_single()
        return {'FINISHED'}

def do_mat_swaps_internal_multi():
    # fix materials on all selected objects, swapping to correct materials if available
    for obj in bpy.context.selected_objects:
        # iterate over the material slots and check/swap the materials
        for mat_slot in (s for s in obj.material_slots if s.material is not None):
            if not is_mat_mhx_name(mat_slot.material.name):
                continue

            # get potential name of swap material and check for its existence
            swap_mat_name = get_swappable_from_mhx_name(mat_slot.material.name)
            sm = bpy.data.materials.get(swap_mat_name)
            if sm is None:
                continue

            # swap material
            print("Swapping material on object " + obj.name + ", oldMat = " + mat_slot.material.name + ", newMat = " + swap_mat_name)
            mat_slot.material = sm

class AMH2B_SwapMatIntMulti(bpy.types.Operator):
    """Try to swap all materials of selected objects with replacement materials within this Blend file"""
    bl_idname = "amh2b.swap_mat_int_multi"
    bl_label = "Internal Multi"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_mat_swaps_internal_multi()
        return {'FINISHED'}

#####################################################
# Setup Swap Materials Single and Multi
# Rename material(s) to be searchable by the swap materials functions.
#    Single
# Rename only material in active slot on active object.
#    Multi
# Rename all materials in all slots on all selected objects.
#
# Note: Renames material only if it matches the Import MHX material name convention.

def do_setup_mat_swap_single():
    obj = bpy.context.active_object
    if obj is None:
        print("do_setup_mat_swap_single() error: no Active Object. Select an object and try again.")
        return
    if obj.material_slots[obj.active_material_index] is None:
        return

    active_mat_name = obj.material_slots[obj.active_material_index].name

    if is_mat_mhx_name(active_mat_name):
        new_mat_name = get_swappable_from_mhx_name(active_mat_name)
        rename_material(active_mat_name, new_mat_name)
        print("Renamed material " + active_mat_name + " to " + new_mat_name)

class AMH2B_SetupMatSwapSingle(bpy.types.Operator):
    """Rename active material slot of active object to make the material searchable re: swap material from file"""
    bl_idname = "amh2b.setup_mat_swap_single"
    bl_label = "Rename Single"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_setup_mat_swap_single()
        return {'FINISHED'}

def do_setup_mat_swap_multi():
    selection_list = bpy.context.selected_objects
    for obj in selection_list:
        # iterate over the material slots and check/rename the materials
        for mat_slot in obj.material_slots:
            if mat_slot.material is None:
                continue
            mat_name = mat_slot.material.name
            if is_mat_mhx_name(mat_name):
                new_mat_name = get_swappable_from_mhx_name(mat_name)
                rename_material(mat_name, new_mat_name)
                print("Renamed material " + mat_name + " to " + new_mat_name)

class AMH2B_SetupMatSwapMulti(bpy.types.Operator):
    """Rename all materials on all selected objects to make them searchable re: swap material from file"""
    bl_idname = "amh2b.setup_mat_swap_multi"
    bl_label = "Rename Multi"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_setup_mat_swap_multi()
        return {'FINISHED'}
