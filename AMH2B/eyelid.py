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

# bpy.context.active_object.pose.bones[0].constraints.new(type="COPY_ROTATION")

class AMH2B_LidLook(bpy.types.Operator):
    """Add bone constraints to eye bones so eyelids move when eye gaze direction changes upwards and downwards, active object must be ARMATURE"""
    bl_idname = "amh2b.eyelid_lidlook"
    bl_label = "Add Lid Look"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        arm_obj = bpy.context.active_object
        if arm_obj is None or arm_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}
        # 20 degrees upper, and -14 lower
        upper_bone_names = [
            ("lolid.L", "eye_parent.L", 0.25, -0.244346, 0.087266),
            ("uplid.L", "eye_parent.L", 0.25, -0.087266, 0.349066),
            ("lolid.R", "eye_parent.R", 0.25, -0.244346, 0.087266),
            ("uplid.R", "eye_parent.R", 0.25, -0.087266, 0.349066),
        ]
        for bone_name, subtarget_name, influence, min_x, max_x in upper_bone_names:
            bone = arm_obj.pose.bones[bone_name]
            con_copy = bone.constraints.new(type="COPY_ROTATION")
            con_copy.target = arm_obj
            con_copy.subtarget = subtarget_name
            con_copy.use_x = True
            con_copy.use_y = False
            con_copy.use_z = False
            con_copy.invert_x = True
            con_copy.target_space = 'LOCAL'
            con_copy.owner_space = 'LOCAL'
            con_copy.influence = influence

            con_limit = bone.constraints.new(type="LIMIT_ROTATION")
            con_limit.use_limit_x = True
            con_limit.min_x = min_x
            con_limit.max_x = max_x
            con_limit.owner_space = 'LOCAL'

        return {'FINISHED'}
