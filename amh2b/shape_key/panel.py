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

from .operator import (AMH2B_OT_SearchFileForAutoShapeKeys, AMH2B_OT_ApplyModifierSK, AMH2B_OT_BakeDeformShapeKeys,
    AMH2B_OT_CopyOtherSK, AMH2B_OT_SKFuncDelete)
from .func import (SK_FUNC_APPLY_MOD, SK_FUNC_BAKE, SK_FUNC_COPY, SK_FUNC_DELETE)

def draw_panel_shape_key(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    act_ob = context.active_object
    func_grp_box.prop(scn.amh2b, "sk_active_function", text="")
    layout.separator()
    if scn.amh2b.sk_active_function == SK_FUNC_APPLY_MOD:
        layout.operator(AMH2B_OT_ApplyModifierSK.bl_idname)
    elif scn.amh2b.sk_active_function == SK_FUNC_BAKE:
        layout.operator(AMH2B_OT_BakeDeformShapeKeys.bl_idname)
        row = layout.row(align=True)
        if act_ob is None or not hasattr(act_ob, "vertex_groups"):
            row.prop(scn.amh2b, "sk_mask_vgroup_name", text="Mask")
        else:
            row.prop_search(scn.amh2b, "sk_mask_vgroup_name", act_ob, "vertex_groups", text="Mask")
        row.prop(scn.amh2b, "sk_mask_invert", icon="ARROW_LEFTRIGHT", text="")
        layout.prop(scn.amh2b, "sk_deform_name_prefix")
        layout.prop(scn.amh2b, "sk_bind_frame")
        layout.prop(scn.amh2b, "sk_start_frame")
        layout.prop(scn.amh2b, "sk_end_frame")
        layout.prop(scn.amh2b, "sk_animate")
        layout.prop(scn.amh2b, "sk_add_frame_to_name")
        layout.prop(scn.amh2b, "sk_dynamic")
        sub = layout.column()
        sub.active = scn.amh2b.sk_dynamic
        sub.label(text="Extra Accuracy")
        sub.prop(scn.amh2b, "sk_extra_accuracy")
    elif scn.amh2b.sk_active_function == SK_FUNC_COPY:
        layout.operator(AMH2B_OT_SearchFileForAutoShapeKeys.bl_idname)
        layout.operator(AMH2B_OT_CopyOtherSK.bl_idname)
        layout.prop(scn.amh2b, "sk_adapt_size")
        layout.prop(scn.amh2b, "sk_swap_autoname_ext")
        layout.prop(scn.amh2b, "sk_function_prefix")
    elif scn.amh2b.sk_active_function == SK_FUNC_DELETE:
        layout.operator(AMH2B_OT_SKFuncDelete.bl_idname)
        layout.prop(scn.amh2b, "sk_function_prefix")
