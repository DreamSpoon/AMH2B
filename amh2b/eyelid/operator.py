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

from .func import (add_lid_look, remove_lid_look)

class AMH2B_OT_AddLidLook(Operator):
    """With all selected ARMATURE objects, add bone constraints to eye bones so """ \
        """eyelids move when eye gaze direction changes upwards and downwards"""
    bl_idname = "amh2b.eyelid_add_lidlook"
    bl_label = "Add Lid Look"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        return act_ob != None and act_ob.type == 'ARMATURE'

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            return {'CANCELLED'}
        # get settings data and pass to add lid look
        add_count = add_lid_look(act_ob, context.scene.amh2b.elid_rig_type)
        self.report({'INFO'}, "Added Lid Look constraints to %d bones" % add_count)
        return {'FINISHED'}

class AMH2B_OT_RemoveLidLook(bpy.types.Operator):
    """With active object ARMATURE, remove Lid Look bone constraints from eye bones"""
    bl_idname = "amh2b.eyelid_remove_lidlook"
    bl_label = "Remove Lid Look"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None:
            return {'CANCELLED'}
        remove_count = remove_lid_look(act_ob, context.scene.amh2b.elid_rig_type)
        self.report({'INFO'}, "Removed Lid Look constraints from %d bones" % remove_count)
        return {'FINISHED'}
