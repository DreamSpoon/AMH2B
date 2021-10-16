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
import mathutils
from mathutils import Vector
import re

from .imp_all import *
from .imp_string_const import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

# Deform Shape Keys match distance
FC_MATCH_DIST = 0.00001
SC_DSKEY = "DSKey"

def do_copy_with_mesh_deform():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_copy_with_mesh_deform() error: Active Object must be a mesh.")
        return
    mesh_obj = bpy.context.active_object
    original_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    select_object(mesh_obj)
    set_active_object(mesh_obj)
    dup_mesh_obj = dup_selected()

    mod = mesh_obj.modifiers.new("ClothSimDeform", 'MESH_DEFORM')
    if mod is None:
        print("do_copy_with_mesh_deform() error: Unable to add MESH_DEFORM modifier to object" + mesh_obj.name)
        return

    mod.object = dup_mesh_obj
    mod.use_dynamic_bind = True
    vert_grp = mesh_obj.vertex_groups.get(SC_VGRP_CUTS)
    if vert_grp is not None:
        mod.vertex_group = vert_grp.name
        mod.invert_vertex_group = True

    bpy.ops.object.mode_set(mode=original_mode)

class AMH2B_CopyWithMeshDeform(bpy.types.Operator):
    """Copy active object (must be MESH type), adding Mesh Deform Modifier to active object, and deform target set to copied object"""
    bl_idname = "amh2b.copy_with_mesh_deform"
    bl_label = "Copy with Deform"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_copy_with_mesh_deform()
        return {'FINISHED'}

def do_add_cloth_sim():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_add_cloth_sim() error: Active Object must be a mesh.")
        return
    mesh_obj = bpy.context.active_object
    original_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    mod = mesh_obj.modifiers.new("Cloth", 'CLOTH')
    if mod is None:
        print("do_add_cloth_sim() error: Unable to add CLOTH modifier to object" + mesh_obj.name)
        return

    mod.settings.use_pin_cloth = True
    vert_grp = mesh_obj.vertex_groups.get(SC_VGRP_PINS)
    if vert_grp is not None:
        mod.settings.vertex_group_mass = vert_grp.name

    vert_grp = mesh_obj.vertex_groups.get(SC_VGRP_TSEWN)
    if vert_grp is not None:
        mod.settings.use_sewing_springs = True
        mod.settings.vertex_group_shrink = vert_grp.name

    bpy.ops.object.mode_set(mode=original_mode)

class AMH2B_AddClothSim(bpy.types.Operator):
    """Add CLOTH modifer to active object with settings auto-filled for Pinning and Sewing Springs"""
    bl_idname = "amh2b.add_cloth_sim"
    bl_label = "Add Cloth Sim"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_add_cloth_sim()
        return {'FINISHED'}

def get_mod_verts_edges(obj):
    obj_data = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
    verts = [v.co for v in obj_data.vertices]
    edges = obj_data.edge_keys
    bpy.data.meshes.remove(obj_data)
    return verts, edges

def get_mod_verts(obj):
    obj_data = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
    verts = [Vector([v.co.x, v.co.y, v.co.z]) for v in obj_data.vertices]
    #verts = [Vector(matrix_vector_mult(obj.matrix_world, v.co)) for v in obj_data.vertices]
    bpy.data.meshes.remove(obj_data)
    return verts

def get_vert_matches(obj):
    # create a KDTree of the base vertices, to efficiently search for overlapping verts
    base_verts = obj.data.vertices
    kd = mathutils.kdtree.KDTree(len(base_verts))
    for v in base_verts:
        kd.insert((v.co.x, v.co.y, v.co.z), v.index)
        #kd.insert(matrix_vector_mult(obj.matrix_world, v.co), v.index)

    kd.balance()

    # search the modified vertices for overlapping verts and build the "matches" list
    mod_verts = get_mod_verts(obj)
    matches = []
    i = -1
    for vco in mod_verts:
        i = i + 1
        found_list = kd.find_range(vco, FC_MATCH_DIST)
        # if none found within match distance then goto next iteration
        if len(found_list) < 1:
            continue

        # append match tuple [base_mesh_vert_index, modified_mesh_vert_index]
        matches.append([found_list[0][1], i])

    return matches

def check_create_basis_shape_key(obj):
    if obj.data.shape_keys is None:
        sk_basis = obj.shape_key_add('Basis')
        sk_basis.interpolation = 'KEY_LINEAR'

def create_single_deform_shape_key(obj, vert_matches, mod_verts):
    check_create_basis_shape_key(obj)

    # create a shape key
    sk = obj.shape_key_add(SC_DSKEY)
    sk.interpolation = 'KEY_LINEAR'
    # modify shape key vertex positions to match modified (deformed) mesh
    for base_v_index, mod_v_index in vert_matches:
        sk.data[base_v_index].co.x = mod_verts[mod_v_index].x
        sk.data[base_v_index].co.y = mod_verts[mod_v_index].y
        sk.data[base_v_index].co.z = mod_verts[mod_v_index].z

    return sk

def create_deform_shapekeys(obj, bind_frame_num, start_frame_num, end_frame_num, animate_keys):
    old_current_frame = bpy.context.scene.frame_current

    # get "bind" vert matches in the bind frame
    bpy.context.scene.frame_set(bind_frame_num)
    vert_matches = get_vert_matches(obj)

    # create shape keys in the "deform" frames
    for f in range(start_frame_num, end_frame_num+1):
        bpy.context.scene.frame_set(f)
        mod_verts = get_mod_verts(obj)
        sk = create_single_deform_shape_key(obj, vert_matches, mod_verts)
        if animate_keys:
            sk.value = 0
            sk.keyframe_insert(data_path='value', frame=f-1)
            sk.keyframe_insert(data_path='value', frame=f+1)
            sk.value = 1
            sk.keyframe_insert(data_path='value', frame=f)

    bpy.context.scene.frame_set(old_current_frame)

def do_bake_deform_shape_keys(bind_frame_num, start_frame_num, end_frame_num, animate_keys):
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_bake_deform_shape_keys() error: Active Object must be a mesh.")
        return

    create_deform_shapekeys(bpy.context.active_object, bind_frame_num, start_frame_num, end_frame_num, animate_keys)

class AMH2B_BakeDeformShapeKeys(bpy.types.Operator):
    """Bake active object's mesh deformations to shape keys"""
    bl_idname = "amh2b.bake_deform_shape_keys"
    bl_label = "Bake Deform Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_bake_deform_shape_keys(bpy.context.scene.Amh2bPropDSK_BindFrame, bpy.context.scene.Amh2bPropDSK_StartFrame, bpy.context.scene.Amh2bPropDSK_EndFrame, bpy.context.scene.Amh2bPropDSK_AnimateSK)
        return {'FINISHED'}

def is_dsk_name(name):
    if name == SC_DSKEY or re.match(SC_DSKEY + "\.\w*", name):
        return True
    else:
        return False

def delete_deform_shapekeys(obj):
    for sk in obj.data.shape_keys.key_blocks:
        if is_dsk_name(sk.name):
            obj.shape_key_remove(sk)

def do_delete_deform_shape_keys():
    if bpy.context.active_object is None or bpy.context.active_object.type != 'MESH':
        print("do_delete_deform_shape_keys() error: Active Object must be a mesh.")
        return

    delete_deform_shapekeys(bpy.context.active_object)

class AMH2B_DeleteDeformShapeKeys(bpy.types.Operator):
    """Delete mesh deformations shape keys from active object"""
    bl_idname = "amh2b.delete_deform_shape_keys"
    bl_label = "Delete Deform Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        do_delete_deform_shape_keys()
        return {'FINISHED'}
