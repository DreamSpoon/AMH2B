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

import bpy
from bpy.types import Operator

from .func import (ratchet_point, animate_ratchet_hold)

class AMH2B_OT_RatchetPoint(Operator):
    """With active object Armature, create Ratchet Point (Empty type object) to be used with Ratchet Hold """ \
        """function. This creates an Empty type object parented to active Bone of active object Armature"""
    bl_idname = "amh2b.anim_ratchet_point"
    bl_label = "Ratchet Point"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and context.active_object.type == 'ARMATURE' \
            and context.active_bone != None

    def execute(self, context):
        if context.active_object is None or context.active_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not Armature type, select Armature object and try again")
            return {'CANCELLED'}
        if context.active_bone is None:
            self.report({'ERROR'}, "Active bone is None, select a bone and try again")
            return {'CANCELLED'}
        ratchet_point(context)
        return {'FINISHED'}

class AMH2B_OT_RatchetHold(Operator):
    """Active object's location is offset and keyframed to make Ratchet Point object motionless (in World """ \
        """coordinates), or optionally motionless relative to Ratchet Target (in World coordinates)"""
    bl_idname = "amh2b.anim_ratchet_hold"
    bl_label = "Ratchet Hold"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        a = context.scene.amh2b
        return context.active_object != None and bpy.data.objects.get(a.anim_ratchet_point_object) != None

    def execute(self, context):
        a = context.scene.amh2b
        if context.active_object is None:
            self.report({'ERROR'}, "Active object is None")
            return {'CANCELLED'}
        ratchet_point_ob = bpy.data.objects.get(a.anim_ratchet_point_object)
        if ratchet_point_ob is None:
            self.report({'ERROR'}, "Select a Ratchet Point object and try again")
            return {'CANCELLED'}
        ratchet_target_ob = bpy.data.objects.get(a.anim_ratchet_target_object)
        animate_ratchet_hold(a.anim_ratchet_frames, context.active_object, ratchet_point_ob, ratchet_target_ob)
        return {'FINISHED'}
