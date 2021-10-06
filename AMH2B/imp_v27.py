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
import math

#from bpy.props import StringProperty
#from bpy_extras.io_utils import ImportHelper
#from bpy.types import Operator

from .imp_items import *

def matrix_vector_mult(m, v):
    return m * v

def set_active_object(ob):
    bpy.context.scene.objects.active = ob

def select_object(ob):
    ob.select = True

def deselect_object(ob):
    ob.select = False

def link_object(ob):
    bpy.context.scene.objects.link(ob)

def doTranslateGlobal(tg):
    bpy.ops.transform.translate(value=tg, constraint_orientation='GLOBAL')

def doRotationGlobal(axis_name, rg):
    if axis_name == "x" or axis_name == "X":
        bpy.ops.transform.rotate(value=(math.pi * rg / 180), axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL')
    elif axis_name == "y" or axis_name == "Y":
        bpy.ops.transform.rotate(value=(math.pi * rg / 180), axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL')
    elif axis_name == "z" or axis_name == "Z":
        bpy.ops.transform.rotate(value=(math.pi * rg / 180), axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL')
    else:
        print("doRotationGlobal Error: Unknown axis name = " + axis_name)

class AMH2B_BoneWovenInner:
    src_rig_type_enum = bpy.props.EnumProperty(name="Source Rig Type", description="Rig type that will be joined to MHX rig.", items=amh2b_src_rig_type_items)
    torso_stitch_enum = bpy.props.EnumProperty(name="Torso Stitches", description="Set torso stitches to yes/no.", items=amh2b_yes_no_items)
    arm_left_stitch_enum = bpy.props.EnumProperty(name="Left Arm Stitches", description="Set left arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    arm_right_stitch_enum = bpy.props.EnumProperty(name="Right Arm Stitches", description="Set right arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_left_stitch_enum = bpy.props.EnumProperty(name="Left Leg Stitches", description="Set left leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_right_stitch_enum = bpy.props.EnumProperty(name="Right Leg Stitches", description="Set right leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    fingers_left_stitch_enum = bpy.props.EnumProperty(name="Left Fingers Stitches", description="Set left fingers stitches to yes/no.", items=amh2b_yes_no_items)
    fingers_right_stitch_enum = bpy.props.EnumProperty(name="Right Fingers Stitches", description="Set right fingers stitches to yes/no.", items=amh2b_yes_no_items)

class AMH2B_SwapMaterialsInner:
    filter_glob = bpy.props.StringProperty(default="*.blend", options={'HIDDEN'})

class AMH2B_LuckyInner:
    repose_rig_enum = bpy.props.EnumProperty(name="Re-Pose Rig", description="Apply Re-Pose to rig during lucky process yes/no.", items=amh2b_yes_no_items)
    src_rig_type_enum = bpy.props.EnumProperty(name="Source Rig Type", description="Rig type that will be joined to MHX rig.", items=amh2b_src_rig_type_items)
    torso_stitch_enum = bpy.props.EnumProperty(name="Torso Stitches", description="Set torso stitches to yes/no.", items=amh2b_yes_no_items)
    arm_left_stitch_enum = bpy.props.EnumProperty(name="Left Arm Stitches", description="Set left arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    arm_right_stitch_enum = bpy.props.EnumProperty(name="Right Arm Stitches", description="Set right arm stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_left_stitch_enum = bpy.props.EnumProperty(name="Left Leg Stitches", description="Set left leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    leg_right_stitch_enum = bpy.props.EnumProperty(name="Right Leg Stitches", description="Set right leg stitches to FK, or IK, or both, or none.", items=amh2b_fk_ik_both_none_items)
    fingers_left_stitch_enum = bpy.props.EnumProperty(name="Left Fingers Stitches", description="Set left fingers stitches to yes/no.", items=amh2b_yes_no_items)
    fingers_right_stitch_enum = bpy.props.EnumProperty(name="Right Fingers Stitches", description="Set right fingers stitches to yes/no.", items=amh2b_yes_no_items)

class AMH2B_AdjustPoseInner:
    text_block_name_enum = bpy.props.StringProperty(name="Script TextBlock Name", description="Name of object, in Text Editor, that contains CSV script.", default="Text")
