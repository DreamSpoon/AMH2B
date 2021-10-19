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

from .imp_const import *
from .imp_armature_func import *
from .imp_mesh_func import *
from .imp_object_func import *
from .imp_vgroup_func import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

###############################################
# Sewing and Patterning, Cutting and Sizing

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
