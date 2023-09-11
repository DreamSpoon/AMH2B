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

from bpy.types import Operator

from .func import (remove_blink_track, generate_blink_track)

class AMH2B_OT_RemoveBlinkTrack(Operator):
    """Remove blink track from selected objects (including active object), based on EyeBlink and LidLook options"""
    bl_idname = "amh2b.eblink_remove_blink_track"
    bl_label = "Remove Blink Track"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None or len(context.selected_objects) > 0

    def execute(self, context):
        # check selected objects for ARMATURE or MESH
        arm_list = []
        mesh_list = []
        o_bunch = context.selected_objects.copy()
        if context.active_object not in o_bunch:
            o_bunch.append(context.active_object)
        for obj in o_bunch:
            if obj.type == 'ARMATURE':
                arm_list.append(obj)
            elif obj.type == 'MESH':
                mesh_list.append(obj)
        # exit if zero objects to work with
        if len(arm_list) == 0 and len(mesh_list) == 0:
            self.report({'ERROR'}, "No ARMATURE or MESH selected to remove Blink Track")
            return {'CANCELLED'}
        a = context.scene.amh2b
        shapekey_name = a.eblink_shapekey_name
        start_frame = None
        if a.eblink_remove_start_enable:
            start_frame = a.eblink_remove_start_frame
        end_frame = None
        if a.eblink_remove_end_enable:
            end_frame = a.eblink_remove_end_frame
        remove_blink_track(arm_list, mesh_list, a.eblink_rig_type, shapekey_name, start_frame, end_frame)
        return {'FINISHED'}

class AMH2B_OT_AddBlinkTrack(Operator):
    """With all selected objects (including active object), add blink track(s).\nMESH objects may receive """ \
        """Shapekey keyframes, ARMATURE objects may receive pose bone keyframes"""
    bl_idname = "amh2b.eblink_add_blink_track"
    bl_label = "Add Blink Track"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None or len(context.selected_objects) > 0

    def execute(self, context):
        # create list of all selected objects and active object, without duplicates
        o_bunch = context.selected_objects.copy()
        if context.active_object not in o_bunch:
            o_bunch.append(context.active_object)
        # check selected objects, and active object, for ARMATURE or MESH
        arm_list = []
        mesh_list = []
        for obj in o_bunch:
            if obj.type == 'ARMATURE':
                arm_list.append(obj)
            elif obj.type == 'MESH':
                mesh_list.append(obj)
        # exit if zero objects to work with
        if len(arm_list) == 0 and len(mesh_list) == 0:
            self.report({'ERROR'}, "No ARMATURE or MESH selected to add Blink Track")
            return {'CANCELLED'}
        # get settings from UI
        a = context.scene.amh2b
        max_blink_count = 0
        if a.eblink_max_count_enable:
            max_blink_count = a.eblink_max_count
        blink_settings = {
            "frame_rate": a.eblink_frame_rate,
            "start_frame": a.eblink_start_frame,
            "random_start_frame": a.eblink_random_start_frame,
            "frame_count": a.eblink_frame_count,
            "max_blink_count": max_blink_count,
            "closing_time": a.eblink_closing_time,
            "random_closing_time": a.eblink_random_closing_time,
            "closed_time": a.eblink_closed_time,
            "random_closed_time": a.eblink_random_closed_time,
            "opening_time": a.eblink_opening_time,
            "random_opening_time": a.eblink_random_opening_time,
            "blinks_per_minute": a.eblink_blinks_per_min,
            "use_period": a.eblink_blink_period_enable,
            "blink_period": a.eblink_blink_period,
            "random_blink_period": a.eblink_random_period_enable,
            "allow_random_drift": a.eblink_allow_random_drift,
            "shapekey_name": a.eblink_shapekey_name,
        }
        generate_blink_track(arm_list, mesh_list, a.eblink_rig_type, blink_settings)
        return {'FINISHED'}