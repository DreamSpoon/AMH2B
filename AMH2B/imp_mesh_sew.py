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
from bpy_extras.io_utils import ImportHelper

from .imp_all import *
from .imp_string_const import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

###############################################
# Sewing and Patterning, Cutting and Sizing

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
    make_mesh_line(SC_MN_ASTITCH, vert_pos_a, vert_pos_b)
    make_cloth_stitch_vert_grp(mesh_obj, SC_VGRP_ASTITCH, vert_a, vert_b)

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
    """Add AStitch vertex group to the current mesh from exactly two selected vertexes.\nSelect exactly two vertexes before using this function"""
    bl_idname = "amh2b.pattern_add_stitch"
    bl_label = "Add Stitch"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_draw_cloth_stitch()
        return {'FINISHED'}

def get_vert_group_indexes(mesh_obj, vert_group_index):
    return [ v.index for v in mesh_obj.data.vertices if vert_group_index in [ vg.group for vg in v.groups ] ]

def add_vertex_group(mesh_obj, grp_name, vert_indexes):
    # create new vertex group
    new_vert_grp = mesh_obj.vertex_groups.new(name=grp_name)
    # add vertex indexes at weight = 1.0
    new_vert_grp.add(vert_indexes, 1.0, 'ADD')
    return new_vert_grp

#def add_replace_vertex_grp(mesh_obj, vert_grp_name):
#    delete_vertex_group(mesh_obj, vert_grp_name)
#    add_vertex_group(mesh_obj, vert_grp_name, [])
def add_ifnot_vertex_grp(mesh_obj, vert_grp_name):
    if mesh_obj.vertex_groups.get(vert_grp_name) is None:
        return add_vertex_group(mesh_obj, vert_grp_name, [])

def add_vertex_group_weighted(mesh_obj, grp_name, vert_index_weights):
    # create new vertex group
    new_vert_grp = mesh_obj.vertex_groups.new(name=grp_name)
    # transfer vertex group, with weights
    for viw in vert_index_weights:
        new_vert_grp.add([viw[0]], viw[1], 'REPLACE')

def copy_vertex_group(from_mesh_obj, to_mesh_obj, vert_grp_name):
    from_vert_grp = from_mesh_obj.vertex_groups.get(vert_grp_name)
    if from_vert_grp is None:
        return
    # get vertex indexes in group given by from_vert_grp.index
    vi_list = get_vert_group_indexes(from_mesh_obj, from_vert_grp.index)
    # create new vertex group
    add_vertex_group(to_mesh_obj, from_vert_grp.name, vi_list)

def copy_vertex_group_weighted(from_mesh_obj, to_mesh_obj, vert_grp_name):
    from_vert_grp = from_mesh_obj.vertex_groups.get(vert_grp_name)
    if from_vert_grp is None:
        return
    # get vertex indexes in group given by from_vert_grp.index
    vi_list = get_vert_group_indexes(from_mesh_obj, from_vert_grp.index)
    # create list with weights
    viw_list = []
    for vi in vi_list:
        viw_list.append([vi, from_vert_grp.weight(vi)])
    # create new vertex group
    add_vertex_group_weighted(to_mesh_obj, from_vert_grp.name, viw_list)

def copy_replace_vertex_group(from_mesh_obj, to_mesh_obj, vert_grp_name):
    from_vert_grp = from_mesh_obj.vertex_groups.get(vert_grp_name)
    if from_vert_grp is None:
        return
    delete_vertex_group(to_mesh_obj, vert_grp_name)
    copy_vertex_group(from_mesh_obj, to_mesh_obj, vert_grp_name)

def copy_replace_vertex_group_weighted(from_mesh_obj, to_mesh_obj, vert_grp_name):
    from_vert_grp = from_mesh_obj.vertex_groups.get(vert_grp_name)
    if from_vert_grp is None:
        return
    delete_vertex_group(to_mesh_obj, vert_grp_name)
    copy_vertex_group_weighted(from_mesh_obj, to_mesh_obj, vert_grp_name)

def delete_vertex_group(mesh_obj, vert_grp_name):
    vg = mesh_obj.vertex_groups.get(vert_grp_name)
    if vg is not None:
        mesh_obj.vertex_groups.remove(vg)

def is_vert_grp_sew(grp_name):
    return grp_name.lower() == SC_VGRP_ASTITCH.lower() or re.match(SC_VGRP_ASTITCH + "\.\w*", grp_name, re.IGNORECASE)

def do_inner_copy_sew_pattern(from_mesh_obj, selection_list):
    original_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    for sel in selection_list:
        if sel == from_mesh_obj or sel.type != 'MESH':
            continue
        # find vertex groups with names that match the sew group pattern, and copy the groups
        for vert_grp in from_mesh_obj.vertex_groups:
            if is_vert_grp_sew(vert_grp.name):
                copy_replace_vertex_group(from_mesh_obj, sel, vert_grp.name)

    bpy.ops.object.mode_set(mode=original_mode)

# takes two selected meshes as input, the active_object must be the mesh that is copied from
def do_copy_sew_pattern():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_copy_sew_pattern() error: Active Object was not a mesh. Select exactly two meshes and try again.")
        return
    if len(bpy.context.selected_objects) < 2:
        print("do_copy_sew_pattern() error: less then 2 objects selected. Select another mesh and try again.")
        return

    do_inner_copy_sew_pattern(bpy.context.active_object, bpy.context.selected_objects)


class AMH2B_PatternCopy(bpy.types.Operator):
    """Copy AStitch vertex groups from the active mesh object (last selected object) to all other selected mesh objects"""
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

def do_make_sew_pattern():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_make_sew_pattern() error: Active Object was not a mesh. Select a mesh as the Active Object and try again.")
        return

    active_obj = bpy.context.active_object

    original_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='EDIT')

    v_all_group_indexes = []
    # combine all Sew vertex groups and add edges in one pass
    for vert_grp in active_obj.vertex_groups:
        if is_vert_grp_sew(vert_grp.name):
            vi_list = get_vert_group_indexes(active_obj, vert_grp.index)
            v_all_group_indexes.extend(vi_list)    # add to total indexes
            make_mesh_edge(active_obj, vi_list)

    # if any stitch vertex groups were found then...
    if len(v_all_group_indexes) > 0:
        bpy.ops.object.mode_set(mode='OBJECT')
        # create total vertex group
        add_vertex_group(active_obj, SC_VGRP_TSEWN, v_all_group_indexes)

        # delete the individual stitch vertex groups
        for vert_grp in active_obj.vertex_groups:
            if is_vert_grp_sew(vert_grp.name):
                delete_vertex_group(active_obj, vert_grp.name)

    bpy.ops.object.mode_set(mode=original_mode)

class AMH2B_PatternSew(bpy.types.Operator):
    """Sew the stitch pattern on the active object.\nThis will delete all AStitch vertex groups on active object"""
    bl_idname = "amh2b.pattern_sew"
    bl_label = "Sew Stitches"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_make_sew_pattern()
        return {'FINISHED'}

def do_add_cuts_mask():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_add_cuts_mask() error: Active Object is not a MESH. Select a MESH object and try again.")
        return

    active_obj = bpy.context.active_object

    # add the TotalCuts vertex group if it does not exist
    add_ifnot_vertex_grp(active_obj, SC_VGRP_CUTS)
    v_grp = active_obj.vertex_groups.get(SC_VGRP_CUTS)

    # prevent duplicate masks: check for cuts mask in modifiers stack and quit if found
    for mod in active_obj.modifiers:
        if mod.type == 'MASK' and mod.vertex_group == SC_VGRP_CUTS:
            return

    # add mask modifier and set it
    mod = active_obj.modifiers.new("TotalCuts Mask", 'MASK')
    if mod is None:
        print("do_add_cuts_mask() error: Unable to add MASK modifier to object" + active_obj.name)
        return
    mod.vertex_group = v_grp.name
    mod.invert_vertex_group = True
    # move modifier to top of stack
    while active_obj.modifiers.find(mod.name) != 0:
        bpy.ops.object.modifier_move_up({"object": active_obj}, modifier=mod.name)

class AMH2B_AddCutsMask(bpy.types.Operator):
    """Add Mask modifier to implement TotalCuts, if active object has TotalCuts vertex group"""
    bl_idname = "amh2b.add_cuts_mask"
    bl_label = "Add Cuts Mask"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_add_cuts_mask()
        return {'FINISHED'}

def do_toggle_view_cuts_mask():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_toggle_view_cuts_mask() error: Active Object is not a MESH. Select a MESH object and try again.")
        return

    active_obj = bpy.context.active_object

    # find the cuts mask in the stack
    for mod in active_obj.modifiers:
        if mod.type == 'MASK' and mod.vertex_group == SC_VGRP_CUTS:
            # toggle and ensure that viewport and render visibility are the same
            mod.show_viewport = not mod.show_viewport
            mod.show_render = mod.show_viewport
            return

class AMH2B_ToggleViewCutsMask(bpy.types.Operator):
    """Toggle the visibility of the Cuts mask modifier, in viewport and render"""
    bl_idname = "amh2b.toggle_view_cuts_mask"
    bl_label = "Toggle View Cuts Mask"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_toggle_view_cuts_mask()
        return {'FINISHED'}

def do_inner_copy_tailor_vgroups(from_mesh_obj, selection_list):
    # iterate over selected 'MESH' type objects that are not the active object
    for to_mesh_obj in (x for x in selection_list if x.type == 'MESH' and x != from_mesh_obj):
        copy_replace_vertex_group(from_mesh_obj, to_mesh_obj, SC_VGRP_CUTS)
        copy_replace_vertex_group_weighted(from_mesh_obj, to_mesh_obj, SC_VGRP_PINS)

def do_copy_tailor_vgroups():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_copy_tailor_vgroups() error: active object was not a MESH. Select a MESH and try again.")
        return
    if len(bpy.context.selected_objects) < 2:
        print("do_copy_tailor_vgroups() error: less then 2 objects selected. Select another mesh and try again.")
        return

    do_inner_copy_tailor_vgroups(bpy.context.active_object, bpy.context.selected_objects)

class AMH2B_CopyTailorGroups(bpy.types.Operator):
    """Copy vertex groups TotalCuts and TotalPins from the active object (selected last) to all other selected mesh objects"""
    bl_idname = "amh2b.copy_tailor_groups"
    bl_label = "Copy Cut & Pin Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_copy_tailor_vgroups()
        return {'FINISHED'}

def do_make_tailor_vgroups():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_make_tailor_vgroups() error: active object was not a MESH. Select a MESH and try again.")
        return

    active_obj = bpy.context.active_object
    add_ifnot_vertex_grp(active_obj, SC_VGRP_CUTS)
    add_ifnot_vertex_grp(active_obj, SC_VGRP_PINS)

class AMH2B_MakeTailorGroups(bpy.types.Operator):
    """Add TotalCuts and TotalPins vertex groups to the active object, replacing these groups if they already exist"""
    bl_idname = "amh2b.make_tailor_groups"
    bl_label = "Make Cut & Pin Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_make_tailor_vgroups()
        return {'FINISHED'}

def do_create_size_rig(unlock_y):
    if bpy.context.active_object is None or bpy.context.active_object.type != 'ARMATURE':
        print("do_create_size_rig() error: no active object. Select exactly one ARMATURE and select meshes attached to the armature, and try again.")
        return

    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # copy ref to active object
    selection_active_obj = bpy.context.active_object
    # copy list of selected objects, minus the active object
    selection_list = []
    for ob in bpy.context.selected_objects:
        if ob.name != selection_active_obj.name and ob.type == 'MESH':
            selection_list.append(bpy.data.objects[ob.name])

    # de-select all objects
    bpy.ops.object.select_all(action='DESELECT')

    # select the old active_object in the 3D viewport
    select_object(selection_active_obj)
    # make it the active selected object
    set_active_object(selection_active_obj)

    # duplicate the original armature
    new_arm = dup_selected()
    # parent the duplicated armature to the original armature, to prevent mesh tearing if the armatures move apart
    new_arm.parent = selection_active_obj

    # add modifiers to the other selected objects (meshes), so the meshes will use the new armature
    if len(selection_list) > 0:
        add_armature_to_objects(new_arm, selection_list)

    # ensure new armature is selected
    select_object(new_arm)
    # make new armature is the active object
    set_active_object(new_arm)

    # unlock scale values for all pose bones - except for Y axis, unless allowed
    bpy.ops.object.mode_set(mode='POSE')
    for b in new_arm.pose.bones:
        b.lock_scale[0] = False
        if unlock_y:
            b.lock_scale[1] = False
        b.lock_scale[2] = False

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_CreateSizeRig(AMH2B_CreateSizeRigInner, bpy.types.Operator):
    """Copy armature and unlock pose scale values for resizing selected clothing meshes with copied armature.\nSelect mesh objects first and select armature object last"""
    bl_idname = "amh2b.create_size_rig"
    bl_label = "Create Size Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_create_size_rig(self.unlock_y_scale)
        return {'FINISHED'}

def get_tailor_object_name(object_name):
    if object_name.rfind(":") != -1:
        return object_name[object_name.rfind(":")+1 : len(object_name)]
    else:
        return object_name

def do_rename_tailor_object_to_searchable():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_rename_tailor_object_to_searchable() error: Active Object is not MESH type. Select only one MESH object and try again.")
        return
    bpy.context.active_object.name = get_tailor_object_name(bpy.context.active_object.name)

class AMH2B_MakeTailorObjectSearchable(bpy.types.Operator):
    """Rename active object, if needed, to make it searchable re: search file for Stitch, Cut, and Pin VGroups"""
    bl_idname = "amh2b.make_tailor_object_searchable"
    bl_label = "Make Object Searchable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_rename_tailor_object_to_searchable()
        return {'FINISHED'}

# Returns True if material was successfully appended.
# Checks if the material already exists in this file, if it does exist then rename the
# current material, and then append the new material.
def append_object_from_blend_file(mat_filepath, obj_name):
    # path inside of file (i.e. like opening the "Append" window; see Action, Armature, Brush, Camera, ...)
    inner_path = "Object"

    try:
        bpy.ops.wm.append(
            filepath=os.path.join(mat_filepath, inner_path, obj_name),
            directory=os.path.join(mat_filepath, inner_path),
            filename=obj_name
            )
    except:
        return False

    if bpy.data.objects.get(obj_name) is None:
        return False

    return True

def do_search_file_for_tailor_vgroups(chosen_blend_file):
    # copy list of selected objects, minus the active object
    selection_list = []
    for ob in bpy.context.selected_objects:
        if ob.type == 'MESH':
            selection_list.append(bpy.data.objects[ob.name])

    for sel in selection_list:
        search_name = get_tailor_object_name(sel.name)
        # if the desired VGroups mesh object name is already used then rename it before appending from file,
        # and rename later after the appended object is deleted
        test_obj = bpy.data.objects.get(search_name)
        if test_obj is not None:
            test_obj.name = "TempRenameName"

        # if cannot load mesh object from file...
        append_object_from_blend_file(chosen_blend_file, search_name)
        appended_obj = bpy.data.objects.get(search_name)
        if appended_obj is None:
            # if rename occurred, then undo rename
            if test_obj is not None:
                test_obj.name = search_name

            continue

        do_inner_copy_sew_pattern(appended_obj, [sel])
        do_inner_copy_tailor_vgroups(appended_obj, [sel])

        # select only the appended object and delete it
        bpy.ops.object.select_all(action='DESELECT')
        select_object(appended_obj)
        bpy.ops.object.delete()

        # if an object was named in order to do appending then fix name
        if test_obj is not None:
            test_obj.name = search_name

class AMH2B_SearchFileForTailorVGroups(AMH2B_SearchFileForTailorVGroupsInner, bpy.types.Operator, ImportHelper):
    """Try to add Cut and Pin VGroups for the selected MESH object(s) with a lookup from file based on object name.\nHint: the object name from Import MHX process is used to search for the correct object in the user selected file"""
    bl_idname = "amh2b.search_file_for_tailor_vgroups"
    bl_label = "From File"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        do_search_file_for_tailor_vgroups(self.filepath)
        return {'FINISHED'}
