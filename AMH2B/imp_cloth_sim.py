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

from .imp_all import *
from .imp_string_const import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

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
