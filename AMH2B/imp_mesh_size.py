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

from .imp_armature_func import *
from .imp_object_func import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

def do_create_size_rig(act_ob, unlock_y):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # copy list of selected objects, minus the active object
    selection_list = []
    for ob in bpy.context.selected_objects:
        if ob.name != act_ob.name and ob.type == 'MESH':
            selection_list.append(ob)

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

    # add modifiers to the other selected objects (meshes), so the meshes will use the new armature
    if len(selection_list) > 0:
        add_armature_to_objects(new_arm, selection_list)

    # ensure new armature is selected
    select_object(new_arm)
    # make new armature is the active object
    set_active_object(new_arm)

    # hack: ensure new armature has same location as original armature, because using CreateSizeRig with a rig
    # that has non-zero location will create a size rig in the wrong location (original rig location values x2)
    new_arm.location.x = act_ob.x
    new_arm.location.y = act_ob.y
    new_arm.location.z = act_ob.z

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
    bl_idname = "amh2b.create_size_rig"
    bl_label = "Create Size Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = bpy.context.active_object
        if act_ob is None or act_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not ARMATURE type")
            return {'CANCELLED'}

        do_create_size_rig(act_ob, self.unlock_y_scale)
        return {'FINISHED'}
