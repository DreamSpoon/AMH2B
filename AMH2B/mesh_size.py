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

from .armature_func import *
from .object_func import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

def do_create_size_rig(act_ob, sel_obj_list, unlock_y):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # copy list of selected objects, minus the active object
    other_sel_list = []
    for ob in sel_obj_list:
        if ob.name != act_ob.name and ob.type == 'MESH':
            other_sel_list.append(ob)

    # de-select all objects
    bpy.ops.object.select_all(action='DESELECT')

    # select the old active_object in the 3D viewport
    select_object(act_ob)
    # make it the active selected object
    set_active_object(act_ob)

    # duplicate the original armature
    new_arm = dup_selected()
    # parent the duplicated armature to the original armature, to prevent mesh tearing if the armatures move apart
    new_arm.parent = act_ob
    # reset location/rotation of duplicate, relative to parent, to zero - and reset scale to 1
    new_arm.location = (0, 0, 0)
    if new_arm.rotation_mode == 'AXIS_ANGLE':
        new_arm.rotation_axis_angle = (0, 0, 1, 0)
    elif new_arm.rotation_mode == 'QUATERNION':
        new_arm.rotation_quaternion = (1, 0, 0, 0)
    else:
        new_arm.rotation_euler = (0, 0, 0)
    new_arm.scale = (1, 1, 1)

    # add modifiers to the other selected objects (meshes), so the meshes will use the new armature
    if len(other_sel_list) > 0:
        add_armature_to_objects(new_arm, other_sel_list)

    # ensure new armature is selected
    select_object(new_arm)
    # make new armature is the active object
    set_active_object(new_arm)

    # unlock scale values for all pose bones - except for Y axis, unless allowed
    bpy.ops.object.mode_set(mode='POSE')
    for b in new_arm.pose.bones:
        b.lock_scale[0] = False
        if unlock_y:
            b.lock_scale[1] = False
        b.lock_scale[2] = False

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_CreateSizeRig(AMH2B_CreateSizeRigInner, bpy.types.Operator):
    """Copy armature and unlock pose scale values for resizing selected clothing meshes with copied armature.\nSelect mesh objects first and select armature object last"""
    bl_idname = "amh2b.mesh_create_size_rig"
    bl_label = "Create Size Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}

        do_create_size_rig(act_ob, context.selected_objects, self.unlock_y_scale)
        return {'FINISHED'}
