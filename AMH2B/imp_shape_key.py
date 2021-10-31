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
import re

from .imp_object_func import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

def is_dsk_prefix_match(name, prefix):
    if name == prefix or re.match(prefix + "\w*", name):
        return True
    else:
        return False

def delete_deform_shapekeys(obj, delete_prefix):
    for sk in obj.data.shape_keys.key_blocks:
        if is_dsk_prefix_match(sk.name, delete_prefix):
            obj.shape_key_remove(sk)

class AMH2B_SKFuncDelete(bpy.types.Operator):
    """With active object, delete shape keys by prefix"""
    bl_idname = "amh2b.sk_func_delete"
    bl_label = "Delete Prefixed Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        delete_prefix = context.scene.Amh2bPropShapeKeyFunctionsPrefix
        if delete_prefix == '':
            self.report({'ERROR'}, "Shape key name prefix is blank")
            return {'CANCELLED'}
        ob_act = context.active_object
        if ob_act is None or ob_act.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        if ob_act.data.shape_keys is None or len(ob_act.data.shape_keys.key_blocks) < 2:
            self.report({'ERROR'}, "Active object has no shape keys available to delete")
            return {'CANCELLED'}

        delete_deform_shapekeys(ob_act, delete_prefix)
        return {'FINISHED'}

def copy_single_shapekey(src_obj, dest_obj, shape_key_index):
    check_create_basis_shape_key(dest_obj)

    src_obj.active_shape_key_index = shape_key_index
    set_active_object(dest_obj)
    src_obj.select = True
    dest_obj.select = True
    bpy.ops.object.shape_key_transfer()
    src_obj.select = False
    dest_obj.select = False

def copy_shapekeys(src_obj, dest_objects, copy_prefix):
    for dest_obj in dest_objects:
        show_temp = dest_obj.show_only_shape_key
        for sk in src_obj.data.shape_keys.key_blocks:
            if is_dsk_prefix_match(sk.name, copy_prefix):
                copy_single_shapekey(src_obj, dest_obj, src_obj.data.shape_keys.key_blocks.find(sk.name))

        # bpy.ops.object.shape_key_transfer will set show_only_shape_key to true, so reset to previous value
        dest_obj.show_only_shape_key = show_temp

def do_copy_shape_keys(src_object, dest_objects, copy_prefix):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # de-select all objects because copying shape keys requires bpy.ops.object.shape_key_transfer,
    # and this requires exactly two specific objects be selected per shape key copy
    bpy.ops.object.select_all(action='DESELECT')

    copy_shapekeys(src_object, dest_objects, copy_prefix)
    bpy.ops.object.mode_set(mode=old_3dview_mode)

# TODO copy animation keyframes too
class AMH2B_SKFuncCopy(bpy.types.Operator):
    """With active object, copy shape keys by prefix to all other selected objects"""
    bl_idname = "amh2b.sk_func_copy"
    bl_label = "Copy Prefixed Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        copy_prefix = context.scene.Amh2bPropShapeKeyFunctionsPrefix
        if copy_prefix == '':
            self.report({'ERROR'}, "Shape key name prefix is blank")
            return {'CANCELLED'}

        ob_act = context.active_object
        if ob_act is None or ob_act.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        if ob_act.data.shape_keys is None or len(ob_act.data.shape_keys.key_blocks) < 2:
            self.report({'ERROR'}, "Active object does not have enough shape keys to be copied")
            return {'CANCELLED'}

        objects = [ob for ob in context.selected_editable_objects if ob != ob_act]
        if len(objects) < 1:
            self.report({'ERROR'}, ("No meshes were selected to receive copied shape keys"))
            return {'CANCELLED'}

        do_copy_shape_keys(ob_act, objects, copy_prefix)
        return {'FINISHED'}
