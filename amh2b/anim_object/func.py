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

def ratchet_point(context):
    original_mode = context.object.mode
    if original_mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.object.mode_set(mode='OBJECT')
    arm_ob = context.active_object
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='CURSOR')
    context.view_layer.objects.active = arm_ob
    arm_ob.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.object.parent_set(type='BONE')
    bpy.ops.object.mode_set(mode=original_mode)

#####################################################
#   Ratchet Hold
# Given 'Empty' type object, parented to bone of Armature object:
#   Offset location of original object, and keyframe, to make 'Empty' type object appear motionless.
#   Two keyframes created on object (e.g. Armature), such that 'Empty' object appears motionless over two frames.
# Ratchet Target (optional): Armature will remain motionless relative to Ratchet Target, which can be animated -
# Ratchet Point should not be animated.
# Example uses:
#   1) Walking cycle, and offset Armature location when walking cycle repeats.
#   2) Model's feet seem to 'slide' during transition from one animation to next, so lock foot to a location.
# In both of the above cases, use Ratchet Hold with Ratchet Point parented to foot bone of Armature,
# i.e. foot that is on ground during walk cycle repeat.
def ratchet_hold(ob_to_ratchet, point_ob, target_ob, original_target_loc):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    # insert location keyframes on object to ratchet at old location
    ob_to_ratchet.keyframe_insert(data_path="location")
    # save old location
    ratchet_point_old_loc = point_ob.matrix_world.to_translation()
    # increment current frame
    bpy.context.scene.frame_set(bpy.context.scene.frame_current+1)
    # save new location
    ratchet_point_new_loc = point_ob.matrix_world.to_translation()
    # Calculate offset (in world coordinate system) for moving object to ratchet,
    # such that hold onto object remains stationary.
    delta_move = np_subtract(ratchet_point_old_loc, ratchet_point_new_loc)
    # if Ratchet Target exists, then offset 'delta_move' by relative movement of Ratchet Target, so Ratchet Point
    # remains motionless relative to Ratchet Target, without needing to copy Ratchet Target's location to
    # Ratchet Point
    if target_ob != None and original_target_loc != None:
        delta_move += np_subtract(target_ob.matrix_world.to_translation(), original_target_loc)
    # do move, in World coordinate system
    bpy.ops.transform.translate(value=delta_move, orient_type='GLOBAL')
    # insert location keyframes on object to ratchet at new location
    ob_to_ratchet.keyframe_insert(data_path="location")
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def animate_ratchet_hold(ratchet_frames, ob_to_ratchet, point_ob, target_ob):
    original_target_loc = target_ob.matrix_world.to_translation() if target_ob != None else None
    for _ in range(0, ratchet_frames):
        ratchet_hold(ob_to_ratchet, point_ob, target_ob, original_target_loc)
