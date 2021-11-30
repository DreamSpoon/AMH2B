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

SC_LL_COPY_ROT_CONST_NAME = "LidLookCopyRot"
SC_LL_LIMIT_ROT_CONST_NAME = "LidLookLimitRot"

def add_lid_look(arm_list, bone_lidlook_data):
    for arm_obj in arm_list:
        for bone_name, subtarget_name, influence, min_x, max_x in bone_lidlook_data:
            bone = arm_obj.pose.bones.get(bone_name)
            if bone is None:
                continue
            con_copy = bone.constraints.new(type="COPY_ROTATION")
            con_copy.name = SC_LL_COPY_ROT_CONST_NAME
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
            con_limit.name = SC_LL_LIMIT_ROT_CONST_NAME
            con_limit.use_limit_x = True
            con_limit.min_x = min_x
            con_limit.max_x = max_x
            con_limit.owner_space = 'LOCAL'

class AMH2B_AddLidLook(bpy.types.Operator):
    """With all selected ARMATURE objects (including active object), add bone constraints to eye bones so eyelids move when eye gaze direction changes upwards and downwards"""
    bl_idname = "amh2b.eyelid_add_lidlook"
    bl_label = "Add Lid Look"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # create list of all selected objects and active object, without duplicates
        o_bunch = bpy.context.selected_objects.copy()
        if bpy.context.active_object not in o_bunch:
            o_bunch.append(bpy.context.active_object)
        # check selected objects, and active object, for ARMATURE
        arm_list = []
        for obj in o_bunch:
            if obj.type == 'ARMATURE':
                arm_list.append(obj)
        # exit if zero objects to work with
        if len(arm_list) == 0:
            self.report({'ERROR'}, "No ARMATURE selected to add Lid Look")
            return {'CANCELLED'}
        # get settings data and pass to add lid look
        scn = context.scene
        bone_lidlook_data = [
            (scn.Amh2bPropEyelidNameLeftLower, scn.Amh2bPropEyelidNameLeftEye, scn.Amh2bPropEyelidInfluenceLower, scn.Amh2bPropEyelidMinXLower, scn.Amh2bPropEyelidMaxXLower),
            (scn.Amh2bPropEyelidNameLeftUpper, scn.Amh2bPropEyelidNameLeftEye, scn.Amh2bPropEyelidInfluenceUpper, scn.Amh2bPropEyelidMinXUpper, scn.Amh2bPropEyelidMaxXUpper),
            (scn.Amh2bPropEyelidNameRightLower, scn.Amh2bPropEyelidNameRightEye, scn.Amh2bPropEyelidInfluenceLower, scn.Amh2bPropEyelidMinXLower, scn.Amh2bPropEyelidMaxXLower),
            (scn.Amh2bPropEyelidNameRightUpper, scn.Amh2bPropEyelidNameRightEye, scn.Amh2bPropEyelidInfluenceUpper, scn.Amh2bPropEyelidMinXUpper, scn.Amh2bPropEyelidMaxXUpper),
        ]
        add_lid_look(arm_list, bone_lidlook_data)

        return {'FINISHED'}

def remove_lid_look(arm_list, bone_remove_lidlook_data):
    for arm_obj in arm_list:
        for bone_name in bone_remove_lidlook_data:
            bone = arm_obj.pose.bones.get(bone_name)
            if bone is None:
                continue
            # get list of bone constraints needing removal
            constraints_to_remove = []
            for con in bone.constraints:
                if con.type == 'COPY_ROTATION' and con.name.startswith(SC_LL_COPY_ROT_CONST_NAME):
                    constraints_to_remove.append(con)
                elif con.type == 'LIMIT_ROTATION' and con.name.startswith(SC_LL_LIMIT_ROT_CONST_NAME):
                    constraints_to_remove.append(con)
            # remove bone constraints
            for con in constraints_to_remove:
                bone.constraints.remove(con)

class AMH2B_RemoveLidLook(bpy.types.Operator):
    """With all selected ARMATURE objects (including active object), remove Lid Look bone constraints from eye bones"""
    bl_idname = "amh2b.eyelid_remove_lidlook"
    bl_label = "Remove Lid Look"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # create list of all selected objects and active object, without duplicates
        o_bunch = bpy.context.selected_objects.copy()
        if bpy.context.active_object not in o_bunch:
            o_bunch.append(bpy.context.active_object)
        # check selected objects, and active object, for ARMATURE
        arm_list = []
        for obj in o_bunch:
            if obj.type == 'ARMATURE':
                arm_list.append(obj)
        # exit if zero objects to work with
        if len(arm_list) == 0:
            self.report({'ERROR'}, "No ARMATURE selected to remove Lid Look")
            return {'CANCELLED'}
        # get settings data and pass to remove lid look
        scn = context.scene
        bone_remove_lidlook_data = (scn.Amh2bPropEyelidNameLeftLower, scn.Amh2bPropEyelidNameLeftUpper,
                                    scn.Amh2bPropEyelidNameRightLower, scn.Amh2bPropEyelidNameRightUpper)
        remove_lid_look(arm_list, bone_remove_lidlook_data)

        return {'FINISHED'}
