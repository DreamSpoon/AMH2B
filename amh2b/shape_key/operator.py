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

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

from .func import (do_sk_func_delete, do_copy_shape_keys, do_search_file_for_auto_sk,
    do_bake_deform_shape_keys, apply_modifier_sk)

class AMH2B_OT_SKFuncDelete(Operator):
    """With selected MESH type objects, delete shape keys by prefix"""
    bl_idname = "amh2b.sk_func_delete"
    bl_label = "Delete Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        delete_prefix = context.scene.amh2b.sk_function_prefix
        do_sk_func_delete(context.selected_objects, delete_prefix)
        return {'FINISHED'}

# TODO copy animation keyframes too
class AMH2B_OT_CopyOtherSK(Operator):
    """With active object, copy shape keys by prefix to all other selected objects"""
    bl_idname = "amh2b.sk_copy_to_other"
    bl_label = "Copy Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        copy_prefix = context.scene.amh2b.sk_function_prefix
        ob_act = context.active_object
        if ob_act is None or ob_act.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        if ob_act.data.shape_keys is None or len(ob_act.data.shape_keys.key_blocks) < 2:
            self.report({'ERROR'}, "Active object does not have enough shape keys to be copied")
            return {'CANCELLED'}

        other_obj_list = [ob for ob in context.selected_editable_objects if ob.type == 'MESH' and ob != ob_act]
        if len(other_obj_list) < 1:
            self.report({'ERROR'}, "No meshes were selected to receive copied shape keys")
            return {'CANCELLED'}

        do_copy_shape_keys(context, ob_act, other_obj_list, copy_prefix, context.scene.amh2b.sk_adapt_size)
        return {'FINISHED'}

class AMH2B_OT_SearchFileForAutoShapeKeys(Operator, ImportHelper):
    """For each selected MESH object: Search another file automatically and try to copy shape keys based on Prefix and object name.\nNote: Name of object from MHX import process is used to search for object in other selected file"""
    bl_idname = "amh2b.sk_search_file_for_auto_sk"
    bl_label = "Copy from File"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob : StringProperty(default="*.blend", options={'HIDDEN'})

    def execute(self, context):
        scn = context.scene
        do_search_file_for_auto_sk(context.selected_objects, self.filepath, scn.amh2b.sk_function_prefix,
            scn.amh2b.sk_adapt_size, scn.amh2b.sk_swap_autoname_ext)
        return {'FINISHED'}

class AMH2B_OT_BakeDeformShapeKeys(Operator):
    """Bake active object's mesh deformations to shape keys"""
    bl_idname = "amh2b.sk_bake_deform_shape_keys"
    bl_label = "Bake Deform Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        scn = context.scene
        if scn.amh2b.sk_deform_name_prefix == '':
            self.report({'ERROR'}, "Shape key name prefix (add_prefix) is blank")
            return {'CANCELLED'}
        if scn.amh2b.sk_start_frame > scn.amh2b.sk_end_frame:
            self.report({'ERROR'}, "Start Frame number is higher than End Frame number")
            return {'CANCELLED'}

        do_bake_deform_shape_keys(context, act_ob, scn.amh2b.sk_deform_name_prefix, scn.amh2b.sk_bind_frame,
            scn.amh2b.sk_start_frame, scn.amh2b.sk_end_frame, scn.amh2b.sk_animate,
            scn.amh2b.sk_add_frame_to_name, scn.amh2b.sk_dynamic, scn.amh2b.sk_extra_accuracy,
            scn.amh2b.sk_mask_vgroup_name, scn.amh2b.sk_mask_invert)
        return {'FINISHED'}

class AMH2B_OT_ApplyModifierSK(Operator):
    """Apply active Object's active modifiers to its Mesh, with updates to Mesh's ShapeKeys. """ \
        """Object modifiers are not removed"""
    bl_idname = "amh2b.sk_apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        return act_ob != None and act_ob.type == 'MESH' and act_ob.mode == 'OBJECT'

    def execute(self, context):
        apply_modifier_sk(context, context.active_object)
        return {'FINISHED'}
