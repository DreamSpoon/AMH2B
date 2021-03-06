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
#   Blender 2.79 - 2.93 Addon
# A set of tools to automate the process of shading/texturing, and animating MakeHuman data imported in Blender.

import bpy
import math

from .items import *

def cloth_sim_use_sew_group(mod, vert_grp_name):
    mod.settings.use_sewing_springs = True

def cloth_sim_use_pin_group(mod, vert_grp_name):
    mod.settings.vertex_group_mass = vert_grp_name

def get_mesh_post_modifiers(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    object_eval = obj.evaluated_get(depsgraph)
    return bpy.data.meshes.new_from_object(object_eval)

def matrix_vector_mult(m, v):
    return m @ v

def set_active_object(ob):
    bpy.context.view_layer.objects.active = ob

def select_object(ob):
    ob.select_set(True)

def deselect_object(ob):
    ob.select_set(False)

def link_object(ob):
    bpy.context.scene.collection.objects.link(ob)

def set_object_hide(obj, hide_val):
    obj.hide_set(hide_val)

# https://blender.stackexchange.com/questions/144928/how-to-list-all-collections-and-their-objects
def get_all_objects_list():
    a_list = []
    for c in range(len(bpy.data.collections)):
        for i in range(len(bpy.data.collections[c].all_objects)):
            a_list.append(bpy.data.collections[c].all_objects[i])
    return a_list

def do_global_translate(tg):
    bpy.ops.transform.translate(value=tg, orient_type='GLOBAL')

def do_global_rotate(axis_name, rg):
    if axis_name == "x" or axis_name == "X":
        bpy.ops.transform.rotate(value=(math.pi * rg / 180), orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))
    elif axis_name == "y" or axis_name == "Y":
        bpy.ops.transform.rotate(value=(math.pi * rg / 180), orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False))
    elif axis_name == "z" or axis_name == "Z":
        bpy.ops.transform.rotate(value=(math.pi * rg / 180), orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True))
    else:
        print("do_global_rotate() Error: Unknown axis name = " + axis_name)

class AMH2B_SearchInFileInner:
    filter_glob : bpy.props.StringProperty(default="*.blend", options={'HIDDEN'})

class AMH2B_CreateSizeRigInner:
    unlock_y_scale : bpy.props.BoolProperty(name="Unlock Y Scale", description="Unlock Y scale, in addition onlocking X and Z axis scaling, on clothing size rig.", default=False)

class AMH2B_AdjustPoseInner:
    text_block_name_enum : bpy.props.StringProperty(name="Script TextBlock Name", description="Name of object, in Text Editor, that contains CSV script.", default="Text")

class AMH2B_BoneWovenInner:
    src_rig_type_enum : bpy.props.EnumProperty(name="Source Rig Type", description="Rig type that will be joined to MHX rig.", items=amh2b_src_rig_type_items)
    torso_stitch_enum : bpy.props.EnumProperty(name="Torso Stitches", description="Set torso stitches to yes/no.", items=amh2b_yes_no_items)
    arm_left_stitch_enum : bpy.props.EnumProperty(name="Left Arm Stitches", description="Set left arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    arm_right_stitch_enum : bpy.props.EnumProperty(name="Right Arm Stitches", description="Set right arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_left_stitch_enum : bpy.props.EnumProperty(name="Left Leg Stitches", description="Set left leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_right_stitch_enum : bpy.props.EnumProperty(name="Right Leg Stitches", description="Set right leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    fingers_left_stitch_enum : bpy.props.EnumProperty(name="Left Fingers Stitches", description="Set left fingers stitches to yes/no.", items=amh2b_yes_no_items)
    fingers_right_stitch_enum : bpy.props.EnumProperty(name="Right Fingers Stitches", description="Set right fingers stitches to yes/no.", items=amh2b_yes_no_items)

class AMH2B_LuckyInner:
    repose_rig_enum : bpy.props.EnumProperty(name="Re-Pose Rig", description="Apply Re-Pose to rig during lucky process yes/no.", items=amh2b_yes_no_items)
    src_rig_type_enum : bpy.props.EnumProperty(name="Source Rig Type", description="Rig type that will be joined to MHX rig.", items=amh2b_src_rig_type_items)
    torso_stitch_enum : bpy.props.EnumProperty(name="Torso Stitches", description="Set torso stitches to yes/no.", items=amh2b_yes_no_items)
    arm_left_stitch_enum : bpy.props.EnumProperty(name="Left Arm Stitches", description="Set left arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    arm_right_stitch_enum : bpy.props.EnumProperty(name="Right Arm Stitches", description="Set right arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_left_stitch_enum : bpy.props.EnumProperty(name="Left Leg Stitches", description="Set left leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_right_stitch_enum : bpy.props.EnumProperty(name="Right Leg Stitches", description="Set right leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    fingers_left_stitch_enum : bpy.props.EnumProperty(name="Left Fingers Stitches", description="Set left fingers stitches to yes/no.", items=amh2b_yes_no_items)
    fingers_right_stitch_enum : bpy.props.EnumProperty(name="Right Fingers Stitches", description="Set right fingers stitches to yes/no.", items=amh2b_yes_no_items)
