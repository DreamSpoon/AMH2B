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
from numpy import subtract as np_subtract

#####################################################
#     Ratchet Hold
# Re-calculate location data for an object (typically armature), given:
#   1) A single "Empty" type object, that is parented to a part of the armature object
#        (i.e. parented to a bone in the armature object).
#   2) The location of the original object (armature) should be offset, and keyframed, to make the "Empty"
#      type object appear to be motionless.
#   TODO: Use a second empty, parented to the first, which can be offset (keyframed or with a constraint),
#         to indicate motionless relative to the second empty. Thus motionless to a moving observer is possible.
#
# Instructions to use the script:
# Select exactly two objects:
#   Object A - the parent object (typically armature)
#   Object B - the "Empty" type object, that is parented to A
# Run the script:
#   The script will do:
# 1) In the current frame, insert a location keyframe on object A.
# 2) Get the location of object B in the current frame.
# 3) Change to the next frame (increment frame).
# 4) Get the new location of object B, then calculate the offset to keep it motionless.
# 5) Apply location offset to object A, then insert location keyframe on A.
#
# Result:
# Two keyframes created on object A, such that object B appears motionless over the two frames.
# Repeat the operation a number of times to get an animation, e.g. of a person walking.

def do_ratchet_hold(obj_to_ratchet, sel_obj_list):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # get ref to other object (presumably an "Empty" type object), the not active object
    hold_onto_obj = sel_obj_list[0]
    if hold_onto_obj.name == obj_to_ratchet.name:
        hold_onto_obj = sel_obj_list[1]

    # insert location keyframes on object to ratchet at old location
    obj_to_ratchet.keyframe_insert(data_path="location")

    # save old location
    hold_obj_old_loc = hold_onto_obj.matrix_world.to_translation()
    # increment current frame
    bpy.context.scene.frame_set(bpy.context.scene.frame_current+1)
    # save new location
    hold_obj_new_loc = hold_onto_obj.matrix_world.to_translation()
    # Calculate offset (in world coordinate system) for moving object to ratchet,
    # such that hold onto object remains stationary.
    delta_move = np_subtract(hold_obj_old_loc, hold_obj_new_loc)
    # do move in (world coordinate system)
    bpy.ops.transform.translate(value=delta_move, orient_type='GLOBAL')
    # insert location keyframes on object to ratchet at new location
    obj_to_ratchet.keyframe_insert(data_path="location")

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_OT_RatchetHold(bpy.types.Operator):
    """Active object's location is offset and keyframed to make other selected object appear stationary.\nSelect first the intended stationary object, select last the object to be keyframed"""
    bl_idname = "amh2b.anim_ratchet_hold"
    bl_label = "Ratchet Hold"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.active_object is None:
            self.report({'ERROR'}, "Active object is None")
            return {'CANCELLED'}
        if len(context.selected_objects) != 2:
            self.report({'ERROR'}, "Select exactly 2 objects and try again")
            return {'CANCELLED'}

        for _ in range(0, context.scene.amh2b.anim_ratchet_frames):
            do_ratchet_hold(context.active_object, context.selected_objects)
        return {'FINISHED'}
