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

from .operator import (AMH2B_OT_AddSoftBodyWeightTestCalc, AMH2B_OT_FinishSoftBodyWeightCalc,
    AMH2B_OT_DataTransferSBWeight, AMH2B_OT_PresetSoftBody, AMH2B_OT_AddSoftBodySpring, AMH2B_OT_RemoveSoftBodySpring)
from .func import (SB_FUNCTION_WEIGHT, SB_FUNCTION_MODIFIER, SB_FUNCTION_DATA_TRANSFER, SB_FUNCTION_SPRING)

def draw_panel_soft_body(self, context, box):
    scn = context.scene
    act_ob = context.active_object
    a = scn.amh2b
    layout = self.layout
    box.prop(a, "sb_function", text="")
    layout.separator()

    if a.sb_function == SB_FUNCTION_SPRING:
        layout.operator(AMH2B_OT_RemoveSoftBodySpring.bl_idname)
        layout.operator(AMH2B_OT_AddSoftBodySpring.bl_idname)
        if act_ob.type != 'MESH' or act_ob.data is None:
            layout.prop(a, "sb_add_spring_attrib", text="")
        else:
            layout.prop_search(a, "sb_add_spring_attrib", act_ob.data, "attributes", text="")
        layout.prop(a, "nodes_override_create")
    elif a.sb_function == SB_FUNCTION_WEIGHT:
        layout.operator(AMH2B_OT_AddSoftBodyWeightTestCalc.bl_idname)
        layout.prop(a, "nodes_override_create")
        layout.separator()
        layout.operator(AMH2B_OT_FinishSoftBodyWeightCalc.bl_idname)
        layout.prop(a, "sb_apply_sk_mix")
        if act_ob.type != 'MESH' or act_ob.data is None:
            layout.prop(a, "sb_weight_geo_modifier", text="")
        else:
            layout.prop_search(a, "sb_weight_geo_modifier", act_ob, "modifiers", text="")
    elif a.sb_function == SB_FUNCTION_DATA_TRANSFER:
        layout.operator(AMH2B_OT_DataTransferSBWeight.bl_idname)
        layout.prop(a, "sb_dt_vert_mapping", text="")
        layout.prop(a, "sb_dt_apply_mod")
        layout.prop(a, "sb_dt_individual")
        col = layout.box().column()
        col.active = a.sb_dt_individual
        col.prop(a, "sb_dt_include_goal")
        col.prop(a, "sb_dt_include_mask")
        col.prop(a, "sb_dt_include_mass")
        col.prop(a, "sb_dt_include_spring")
    elif a.sb_function == SB_FUNCTION_MODIFIER:
        layout.operator(AMH2B_OT_PresetSoftBody.bl_idname)

    layout.separator()
    layout.label(text="Vertex Group Name")
    col = layout.box().column()
    col.prop(a, "sb_dt_goal_vg_name")
    col.prop(a, "sb_dt_mask_vg_name")
    col.prop(a, "sb_dt_mass_vg_name")
    col.prop(a, "sb_dt_spring_vg_name")
