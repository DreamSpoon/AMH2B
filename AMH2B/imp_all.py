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

# duplicate selected objects, return active object afterwards
def dup_selected():
    obj_to_dup = bpy.context.active_object
    bpy.ops.object.duplicate(linked=False)
    return bpy.context.active_object

def add_armature_to_objects(arm_obj, objs_list):
    for dest_obj in objs_list:
        if dest_obj != arm_obj and dest_obj.type != 'ARMATURE':
            add_armature_to_obj(arm_obj, dest_obj)

def add_armature_to_obj(arm_obj, dest_obj):
    # create ARMATURE modifier and set refs, etc.
    mod = dest_obj.modifiers.new("ReposeArmature", 'ARMATURE')
    if mod is None:
        print("do_repose_rig() error: Unable to add armature to object" + dest_obj.name)
        return
    mod.object = arm_obj
    mod.use_deform_preserve_volume = True
    # Move modifier to top of stack, because this armature needs to move the mesh before
    # any other modifications occur, to match the re-posed main armature.
    while dest_obj.modifiers.find(mod.name) != 0:
        bpy.ops.object.modifier_move_up({"object": dest_obj}, modifier=mod.name)
