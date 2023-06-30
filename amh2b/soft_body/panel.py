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

from bpy.types import Panel

from .operator import (AMH2B_OT_AddSoftBodyWeightTestCalc, AMH2B_OT_FinishSoftBodyWeightCalc,
    AMH2B_OT_DataTransferSBWeight, AMH2B_OT_PresetSoftBody, AMH2B_OT_AddSoftBodySpring)
from .func import (SB_FUNCTION_WEIGHT, SB_FUNCTION_MODIFIER, SB_FUNCTION_DATA_TRANSFER, SB_FUNCTION_SPRING)

class AMH2B_PT_SoftBodyWeight(Panel):
    bl_label = "Soft Body"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scn = context.scene
        a = scn.amh2b
        layout = self.layout
        box = layout.box()
        box.label(text="Function group")
        box.prop(a, "sb_function", text="")
        layout.separator(factor=2)

        if a.sb_function == SB_FUNCTION_WEIGHT:
            layout.operator(AMH2B_OT_AddSoftBodyWeightTestCalc.bl_idname)
            layout.operator(AMH2B_OT_FinishSoftBodyWeightCalc.bl_idname)
            layout.prop(a, "sb_apply_sk_mix")
        elif a.sb_function == SB_FUNCTION_DATA_TRANSFER:
            layout.operator(AMH2B_OT_DataTransferSBWeight.bl_idname)
            layout.prop(a, "sb_dt_gen_data_layers")
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
            layout.prop(a, "sb_add_mask_modifier")
        elif a.sb_function == SB_FUNCTION_SPRING:
            layout.operator(AMH2B_OT_AddSoftBodySpring.bl_idname)

        layout.separator()
        layout.label(text="Vertex Group Name")
        col = layout.box().column()
        col.prop(a, "sb_dt_goal_vg_name")
        col.prop(a, "sb_dt_mask_vg_name")
        col.prop(a, "sb_dt_mass_vg_name")
        col.prop(a, "sb_dt_spring_vg_name")
