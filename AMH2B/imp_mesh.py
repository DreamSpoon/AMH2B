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
import bmesh
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
def swapmat_append_from_file(mat_filepath, mat_name):
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
            if not swapmat_append_from_file(shaderswap_blendfile, swatch_mat_name):
                # if rename occurred, then undo rename
                if test_swap_mat is not None:
                    test_swap_mat.name = old_name
                continue

            # include the newly loaded material in the list of loaded materials
            mats_loaded_from_file.append(swatch_mat_name)

            # swap material
            print("Swapping material on object " + obj.name + ", oldMat = " + mat_slot.material.name + ", newMat = " + swatch_mat_name)
            mat_slot.material = bpy.data.materials[swatch_mat_name]

class AMH2B_SwapMatWithFile(AMH2B_SwapMaterialsInner, bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Swap all materials on selected objects with swap materials from Source Blend File"""
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
    """Swap material in object's active material slot with appropriate swap material in this Blend file"""
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
    """Swap all materials of selected objects with appropriate swap materials in this Blend file"""
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
    """Swap material in object's active material slot with appropriate swap material in this Blend file"""
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
    """Swap all materials of selected objects with appropriate swap materials in this Blend file"""
    bl_idname = "amh2b.setup_mat_swap_multi"
    bl_label = "Rename Multi"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_setup_mat_swap_multi()
        return {'FINISHED'}

###############################################
# Sewing and Patterning

SC_ASTITCH = "AStitch"
SC_AUTO_STITCH = "AutoStitch"

def make_mesh_line(mesh_name, vert_pos_a, vert_pos_b):
    mesh_m = bpy.data.meshes.new("mesh")
    mesh_obj = bpy.data.objects.new(mesh_name, mesh_m)

    link_object(mesh_obj)
    set_active_object(mesh_obj)
    select_object(mesh_obj)

    bm = bmesh.new()

    # add the vertices and create an edge between them
    new_v_a = bm.verts.new(vert_pos_a)
    new_v_b = bm.verts.new(vert_pos_b)
    bm.edges.new((new_v_a, new_v_b))

    # finish up, write the bmesh back to the mesh
    bm.to_mesh(mesh_m)  
    # free and prevent further access
    bm.free()

    deselect_object(mesh_obj)

    return (new_v_a, new_v_b)

def make_cloth_stitch_vert_grp(mesh_obj, grp_name, vert_a, vert_b):
    new_vert_grp = mesh_obj.vertex_groups.new(name=grp_name)
    new_vert_grp.add([vert_a.index, vert_b.index], 1.0, 'ADD')

def make_cloth_stitch_grp(mesh_obj, vert_a, vert_b, vert_pos_a, vert_pos_b):
    make_mesh_line(SC_AUTO_STITCH, vert_pos_a, vert_pos_b)
    make_cloth_stitch_vert_grp(mesh_obj, SC_ASTITCH, vert_a, vert_b)

def do_draw_cloth_stitch():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_draw_cloth_stitch() error: Active Object must be a mesh.")
        return

    original_mode = bpy.context.object.mode
    mesh_obj = bpy.context.active_object
    mesh_world_matrix = mesh_obj.matrix_world

    # must switch to OBJECT mode to get selected vertexes, because does not work in EDIT mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # get selected vertexes
    selected_verts = list(filter(lambda v: v.select, mesh_obj.data.vertices))
    num_verts = len(selected_verts)
    if num_verts != 2:
        bpy.ops.object.mode_set(mode=original_mode)
        print("do_draw_cloth_stitch() error: number of selected vertexes to sew must be 2, instead was " + str(num_verts))
        return

    vert_pos_a = matrix_vector_mult(mesh_world_matrix, selected_verts[0].co)
    vert_pos_b = matrix_vector_mult(mesh_world_matrix, selected_verts[1].co)
    make_cloth_stitch_grp(mesh_obj, selected_verts[0], selected_verts[1], vert_pos_a, vert_pos_b)

    set_active_object(mesh_obj)

    bpy.ops.object.mode_set(mode=original_mode)

class AMH2B_PatternAddStitch(bpy.types.Operator):
    """Add a pattern stitch to the current mesh with exactly two selected vertexes"""
    bl_idname = "amh2b.pattern_add_stitch"
    bl_label = "Add Stitch"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_draw_cloth_stitch()
        return {'FINISHED'}

def get_vert_group_indexes(mesh_obj, vert_group_index):
    return [ v.index for v in mesh_obj.data.vertices if vert_group_index in [ vg.group for vg in v.groups ] ]

def make_vertex_group(mesh_obj, group_name, vert_indexes):
    # create new vertex group
    new_vert_grp = mesh_obj.vertex_groups.new(name=group_name)
    new_vert_grp.add(vert_indexes, 1.0, 'ADD')

def copy_vertex_group(from_mesh_obj, to_mesh_obj, from_vert_grp):
    # get vertex indexes in group given by from_vert_grp.index
    #vi = [ v.index for v in from_mesh_obj.data.vertices if from_vert_grp.index in [ vg.group for vg in v.groups ] ]
    vi = get_vert_group_indexes(from_mesh_obj, from_vert_grp.index)
    # create new vertex group
    #new_vert_grp = to_mesh_obj.vertex_groups.new(name=from_vert_grp.name)
    #new_vert_grp.add(vi, 1.0, 'ADD')
    make_vertex_group(to_mesh_obj, from_vert_grp.name, vi)

def is_vert_grp_sew(group_name):
    return group_name.lower() == SC_ASTITCH.lower() or re.match(SC_ASTITCH + "\.\w*", group_name, re.IGNORECASE)

# takes two selected meshes as input, the active_object must be the mesh that is copied from
def do_copy_sew_pattern():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_copy_sew_pattern() error: Active Object was not a mesh. Select exactly two meshes and try again.")
        return

    selection_list = bpy.context.selected_objects
    if len(selection_list) < 2:
        print("do_copy_sew_pattern() error: less then 2 objects selected. Select another mesh and try again.")
        return

    original_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    from_mesh_obj = bpy.context.active_object
    to_mesh_obj = None
    for sel in selection_list:
        if sel == from_mesh_obj or sel.type != 'MESH':
            continue
        # find vertex groups with names that match the sew group pattern, and copy the groups
        for vert_grp in from_mesh_obj.vertex_groups:
            if is_vert_grp_sew(vert_grp.name):
                copy_vertex_group(from_mesh_obj, sel, vert_grp)

    bpy.ops.object.mode_set(mode=original_mode)

class AMH2B_PatternCopy(bpy.types.Operator):
    """Copy pattern from the active object to all other selected mesh objects"""
    bl_idname = "amh2b.pattern_copy"
    bl_label = "Copy Stitches"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_copy_sew_pattern()
        return {'FINISHED'}

def make_mesh_edge(mesh_obj, vert_indexes):
    if len(vert_indexes) != 2:
        print("do_make_sew_pattern() error: stitch must be between 2 vertexes, not " + str(len(vert_indexes)))
        return

    bm = bmesh.from_edit_mesh(mesh_obj.data)
    if hasattr(bm.verts, "ensure_lookup_table"): 
        bm.verts.ensure_lookup_table()

    bm.edges.new((bm.verts[vert_indexes[0]], bm.verts[vert_indexes[1]]))

def delete_vertex_group(mesh_obj, group_name):
    vg = mesh_obj.vertex_groups.get(group_name)
    if vg is not None:
        mesh_obj.vertex_groups.remove(vg)

def do_make_sew_pattern():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_make_sew_pattern() error: Active Object was not a mesh. Select a mesh as the Active Object and try again.")
        return

    active_mesh_obj = bpy.context.active_object

    original_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='EDIT')

    v_all_group_indexes = []
    # combine all Sew vertex groups and add edges in one pass
    for vert_grp in active_mesh_obj.vertex_groups:
        if is_vert_grp_sew(vert_grp.name):
            vi = get_vert_group_indexes(active_mesh_obj, vert_grp.index)
            v_all_group_indexes.extend(vi)    # add to total indexes
            make_mesh_edge(active_mesh_obj, vi)

    # if any stitch vertex groups were found then...
    if len(v_all_group_indexes) > 0:
        bpy.ops.object.mode_set(mode='OBJECT')
        # create total vertex group
        make_vertex_group(active_mesh_obj, "TotalSewn", v_all_group_indexes)

        # delete the individual stitch vertex groups
        for vert_grp in active_mesh_obj.vertex_groups:
            if is_vert_grp_sew(vert_grp.name):
                delete_vertex_group(active_mesh_obj, vert_grp.name)

    bpy.ops.object.mode_set(mode=original_mode)

class AMH2B_PatternSew(bpy.types.Operator):
    """Sew the pattern on the active object"""
    bl_idname = "amh2b.pattern_sew"
    bl_label = "Sew Stitches"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_make_sew_pattern()
        return {'FINISHED'}
