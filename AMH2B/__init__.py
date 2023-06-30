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

# Automate MakeHuman 2 Blender (AMH2B)
# A set of tools to automate repetitive tasks after importing data from MakeHuman, and enhance imported data.

bl_info = {
    "name": "Automate MakeHuman 2 Blender (AMH2B)",
    "description": "Automate process of importing and animating MakeHuman models.",
    "author": "Dave",
    "version": (2, 0, 0),
    "blender": (3, 30, 0),
    "location": "View 3D -> Tools -> AMH2B",
    "doc_url": "https://github.com/DreamSpoon/AMH2B#readme",
    "category": "Import MakeHuman Automation",
}

import bpy
from bpy.types import (Panel, PropertyGroup, Scene)
from bpy.props import (BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty,
    StringProperty)
from .const import (SC_DSKEY, SC_VGRP_AUTO_PREFIX)
from .animation import AMH2B_OT_RatchetHold
from .armature import (AMH2B_OT_AdjustPose, AMH2B_OT_ApplyScale, AMH2B_OT_BridgeRepose, AMH2B_OT_BoneWoven,
    AMH2B_OT_Lucky, AMH2B_OT_EnableModPreserveVolume, AMH2B_OT_DisableModPreserveVolume, AMH2B_OT_RenameGeneric,
    AMH2B_OT_UnNameGeneric)
from .eyeblink import (AMH2B_OT_RemoveBlinkTrack, AMH2B_OT_AddBlinkTrack, AMH2B_OT_SaveBlinkCSV, AMH2B_OT_LoadBlinkCSV,
    AMH2B_OT_ResetEyeOpened, AMH2B_OT_ResetEyeClosed, AMH2B_OT_SetEyeOpened, AMH2B_OT_SetEyeClosed)
from .eyelid import (AMH2B_OT_AddLidLook, AMH2B_OT_RemoveLidLook)
from .material import (AMH2B_OT_SwapMatWithFile, AMH2B_OT_SwapMatInternal)
from .mesh_size import AMH2B_OT_CreateSizeRig
from .shape_key import (SK_MENU_FUNC_ITEMS, AMH2B_OT_BakeDeformShapeKeys, AMH2B_OT_SearchFileForAutoShapeKeys,
    AMH2B_OT_SKFuncDelete, AMH2B_OT_SKFuncCopy, AMH2B_OT_DeformSK_ViewToggle)
from .shrinkwrap import (AMH2B_OT_CreateGeoNodesDirectionalShrinkwrap, AMH2B_OT_CreateGeoNodesDirectionalThickShrinkwrap,
    AMH2B_OT_CreateGeoNodesShrinkwrap, AMH2B_OT_CreateGeoNodesThickShrinkwrap)
from .shrinkwrap_obj import (AMH2B_OT_CreateObjModDirectionalShrinkwrap, AMH2B_OT_CreateObjModDirectionalThickShrinkwrap,
    AMH2B_OT_CreateObjModShrinkwrap, AMH2B_OT_CreateObjModThickShrinkwrap)
from .template import (AMH2B_OT_MakeTailorObjectSearchable, AMH2B_OT_SetupMatSwap)
from .vgroup import (AMH2B_OT_AddMaskOutMod, AMH2B_OT_ToggleViewMaskoutMod, AMH2B_OT_CopyVertexGroupsByPrefix,
    AMH2B_OT_DeleteVertexGroupsByPrefix, AMH2B_OT_MakeTailorGroups, AMH2B_OT_SearchFileForAutoVGroups)
from .weight_paint import (AMH2B_OT_GrowPaint, AMH2B_OT_SelectVertexByWeight)
from .soft_body.func import SB_FUNCTION_ITEMS
from .soft_body.operator import (AMH2B_OT_AddSoftBodyWeightTestCalc, AMH2B_OT_FinishSoftBodyWeightCalc,
    AMH2B_OT_DataTransferSBWeight, AMH2B_OT_PresetSoftBody, AMH2B_OT_AddSoftBodySpring)
from .soft_body.panel import AMH2B_PT_SoftBodyWeight
from .attrib_convert.panel import AMH2B_PT_Attribs
from .attrib_convert.operator import AMH2B_OT_AttributeConvert
from .attrib_convert.func import ATTR_CONV_FUNC_ITEMS

class AMH2B_PT_MeshMat(Panel):
    bl_label = "Mesh Material"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Swap Material")
        box.operator(AMH2B_OT_SwapMatWithFile.bl_idname)
        sub = box.column()
        sub.active = not scn.amh2b.mat_exact_name_only
        sub.operator(AMH2B_OT_SwapMatInternal.bl_idname)
        box.prop(scn.amh2b, "mat_active_slot_only")
        box.prop(scn.amh2b, "mat_exact_name_only")
        sub = box.column()
        sub.active = not scn.amh2b.mat_exact_name_only
        sub.prop(scn.amh2b, "mat_ignore_autoname")
        sub.prop(scn.amh2b, "mat_keep_original_name")
        sub.prop(scn.amh2b, "mat_name_delimiter")
        sub.prop(scn.amh2b, "mat_name_delimiter_count")

class AMH2B_PT_MeshSize(Panel):
    bl_label = "Mesh Size"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Clothing Size")
        box.operator(AMH2B_OT_CreateSizeRig.bl_idname)

class AMH2B_PT_VertexGroup(Panel):
    bl_label = "Vertex Group"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Functions")
        box.operator(AMH2B_OT_SearchFileForAutoVGroups.bl_idname)
        box.operator(AMH2B_OT_CopyVertexGroupsByPrefix.bl_idname)
        box.operator(AMH2B_OT_DeleteVertexGroupsByPrefix.bl_idname)
        box.prop(scn.amh2b, "vg_func_name_prefix")
        box.prop(scn.amh2b, "vg_swap_autoname_ext")
        box.prop(scn.amh2b, "vg_create_name_only")
        box = layout.box()
        box.label(text="AutoMask & Pin Group")
        box.operator(AMH2B_OT_MakeTailorGroups.bl_idname)
        box.operator(AMH2B_OT_AddMaskOutMod.bl_idname)
        box.operator(AMH2B_OT_ToggleViewMaskoutMod.bl_idname)

class AMH2B_PT_WeightPaint(Panel):
    bl_label = "Weight Paint"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Vertex Select")
        box.operator(AMH2B_OT_SelectVertexByWeight.bl_idname)
        box.prop(scn.amh2b, "wp_select_vertex_min_w")
        box.prop(scn.amh2b, "wp_select_vertex_max_w")
        box.prop(scn.amh2b, "wp_select_vertex_deselect")
        box = layout.box()
        box.label(text="Grow Selection Paint")
        box.operator(AMH2B_OT_GrowPaint.bl_idname)
        box.prop(scn.amh2b, "wp_grow_paint_iterations")
        box.prop(scn.amh2b, "wp_grow_paint_start_weight")
        box.prop(scn.amh2b, "wp_grow_paint_end_weight")
        box.prop(scn.amh2b, "wp_paint_initial_selection")
        box.prop(scn.amh2b, "wp_tail_fill_enable")
        sub = box.column()
        sub.active = scn.amh2b.wp_tail_fill_enable
        sub.prop(scn.amh2b, "wp_tail_fill_value")
        sub.prop(scn.amh2b, "wp_tail_fill_connected")

class AMH2B_PT_ShapeKey(Panel):
    bl_label = "ShapeKey"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        act_ob = context.active_object
        box = layout.box()
        box.prop(scn.amh2b, "sk_active_function", text="")
        box = layout.box()
        if scn.amh2b.sk_active_function == "SK_FUNC_COPY":
            box.label(text="Functions")
            box.operator(AMH2B_OT_SearchFileForAutoShapeKeys.bl_idname)
            box.operator(AMH2B_OT_SKFuncCopy.bl_idname)
            box.prop(scn.amh2b, "sk_adapt_size")
            box.prop(scn.amh2b, "sk_swap_autoname_ext")
            box.prop(scn.amh2b, "sk_function_prefix")
        elif scn.amh2b.sk_active_function == "SK_FUNC_DELETE":
            box.operator(AMH2B_OT_SKFuncDelete.bl_idname)
            box.prop(scn.amh2b, "sk_function_prefix")
        elif scn.amh2b.sk_active_function == "SK_FUNC_BAKE":
            box.label(text="Bake Deform ShapeKey")
            box.operator(AMH2B_OT_BakeDeformShapeKeys.bl_idname)
            box.prop(scn.amh2b, "sk_mask_vgroup_name")
            box.prop(scn.amh2b, "sk_mask_include")
            box.prop(scn.amh2b, "sk_deform_name_prefix")
            box.prop(scn.amh2b, "sk_bind_frame")
            box.prop(scn.amh2b, "sk_start_frame")
            box.prop(scn.amh2b, "sk_end_frame")
            box.prop(scn.amh2b, "sk_animate")
            box.prop(scn.amh2b, "sk_add_frame_to_name")
            box.prop(scn.amh2b, "sk_dynamic")
            sub = box.column()
            sub.active = scn.amh2b.sk_dynamic
            sub.label(text="Extra Accuracy")
            sub.prop(scn.amh2b, "sk_extra_accuracy")
            sub = box.column()
            sub.active = not scn.amh2b.sk_dynamic
            sub.operator(AMH2B_OT_DeformSK_ViewToggle.bl_idname)

class AMH2B_PT_Armature(Panel):
    bl_label = "Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.label(text="Retarget")
        box.operator(AMH2B_OT_AdjustPose.bl_idname)
        box.prop(scn.amh2b, "arm_textblock_name")
        box.operator(AMH2B_OT_ApplyScale.bl_idname)
        box.operator(AMH2B_OT_BridgeRepose.bl_idname)
        box.operator(AMH2B_OT_BoneWoven.bl_idname)
        box = layout.box()
        box.label(text="Retarget Multi-Function")
        box.operator(AMH2B_OT_Lucky.bl_idname)
        box = layout.box()
        box.label(text="Preserve Volume Toggle")
        box.operator(AMH2B_OT_EnableModPreserveVolume.bl_idname)
        box.operator(AMH2B_OT_DisableModPreserveVolume.bl_idname)
        box = layout.box()
        box.label(text="Bone Names")
        box.operator(AMH2B_OT_RenameGeneric.bl_idname)
        box.prop(scn.amh2b, "arm_generic_prefix")
        box.prop(scn.amh2b, "arm_generic_mhx")
        box.operator(AMH2B_OT_UnNameGeneric.bl_idname)

class AMH2B_PT_Animation(Panel):
    bl_label = "Animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.label(text="Object Location")
        box.operator(AMH2B_OT_RatchetHold.bl_idname)
        box.prop(scn.amh2b, "anim_ratchet_frames")

class AMH2B_PT_Eyelid(Panel):
    bl_label = "Eyelid"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.operator(AMH2B_OT_RemoveLidLook.bl_idname)
        box.operator(AMH2B_OT_AddLidLook.bl_idname)
        box.label(text="Eyelid Bone Names")
        box.prop(scn.amh2b, "elid_name_left_lower")
        box.prop(scn.amh2b, "elid_name_left_upper")
        box.prop(scn.amh2b, "elid_name_right_lower")
        box.prop(scn.amh2b, "elid_name_right_upper")
        box.label(text="Eye Bone Names")
        box.prop(scn.amh2b, "elid_name_left_eye")
        box.prop(scn.amh2b, "elid_name_right_eye")
        box.label(text="Influence Amounts")
        box.prop(scn.amh2b, "elid_influence_lower")
        box.prop(scn.amh2b, "elid_influence_upper")
        box.label(text="Min/Max Rotation Lower")
        box.prop(scn.amh2b, "elid_min_x_lower")
        box.prop(scn.amh2b, "elid_max_x_lower")
        box.label(text="Min/Max Rotation Upper")
        box.prop(scn.amh2b, "elid_min_x_upper")
        box.prop(scn.amh2b, "elid_max_x_upper")

class AMH2B_PT_EyeBlink(Panel):
    bl_label = "Eye Blink"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.operator(AMH2B_OT_RemoveBlinkTrack.bl_idname)
        box.prop(scn.amh2b, "eblink_remove_start_enable")
        sub = box.column()
        sub.active = scn.amh2b.eblink_remove_start_enable
        sub.prop(scn.amh2b, "eblink_remove_start_frame")
        box.prop(scn.amh2b, "eblink_remove_end_enable")
        sub = box.column()
        sub.active = scn.amh2b.eblink_remove_end_enable
        sub.prop(scn.amh2b, "eblink_remove_end_frame")
        box.prop(scn.amh2b, "eblink_remove_left")
        box.prop(scn.amh2b, "eblink_remove_right")
        box = layout.box()
        box.operator(AMH2B_OT_AddBlinkTrack.bl_idname)
        box = layout.box()
        box.label(text="Options")
        box.prop(scn.amh2b, "eblink_framerate")
        box.prop(scn.amh2b, "eblink_start_frame")
        box.prop(scn.amh2b, "eblink_random_start_frame")
        box.prop(scn.amh2b, "eblink_allow_random_drift")
        box.prop(scn.amh2b, "eblink_frame_count")
        box.prop(scn.amh2b, "eblink_max_count_enable")
        sub = box.column()
        sub.active = scn.amh2b.eblink_max_count_enable
        sub.prop(scn.amh2b, "eblink_max_count")
        sub = box.column()
        sub.active = not scn.amh2b.eblink_blink_period_enable
        sub.prop(scn.amh2b, "eblink_blinks_per_min")
        box.prop(scn.amh2b, "eblink_blink_period_enable")
        sub = box.column()
        sub.active = scn.amh2b.eblink_blink_period_enable
        sub.prop(scn.amh2b, "eblink_blink_period")
        box.prop(scn.amh2b, "eblink_random_period_enable")
        box.prop(scn.amh2b, "eblink_eye_left_enable")
        box.prop(scn.amh2b, "eblink_eye_right_enable")
        box.prop(scn.amh2b, "eblink_shapekey_name")
        box = layout.box()
        box.label(text="Basis")
        box.prop(scn.amh2b, "eblink_closing_time")
        box.prop(scn.amh2b, "eblink_closed_time")
        box.prop(scn.amh2b, "eblink_opening_time")
        box = layout.box()
        box.label(text="Random")
        box.prop(scn.amh2b, "eblink_random_closing_time")
        box.prop(scn.amh2b, "eblink_random_closed_time")
        box.prop(scn.amh2b, "eblink_random_opening_time")
        box = layout.box()
        box.label(text="Template Set/Reset")
        box.operator(AMH2B_OT_SetEyeOpened.bl_idname)
        box.operator(AMH2B_OT_ResetEyeOpened.bl_idname)
        box.operator(AMH2B_OT_SetEyeClosed.bl_idname)
        box.operator(AMH2B_OT_ResetEyeClosed.bl_idname)
        box = layout.box()
        box.label(text="Template Bone Names")
        box.prop(scn.amh2b, "eblink_bone_name_left_lower")
        box.prop(scn.amh2b, "eblink_bone_name_left_upper")
        box.prop(scn.amh2b, "eblink_bone_name_right_lower")
        box.prop(scn.amh2b, "eblink_bone_name_right_upper")
        box = layout.box()
        box.label(text="Template Save/Load")
        box.operator(AMH2B_OT_SaveBlinkCSV.bl_idname)
        box.prop(scn.amh2b, "eblink_text_save_name")
        box.operator(AMH2B_OT_LoadBlinkCSV.bl_idname)
        box.prop(scn.amh2b, "eblink_text_load_name")

class AMH2B_PT_Template(Panel):
    bl_label = "Template"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.label(text="Material")
        box.operator(AMH2B_OT_SetupMatSwap.bl_idname)
        box.prop(scn.amh2b, "temp_active_slot_only")
        box.prop(scn.amh2b, "temp_delimiter")
        box.prop(scn.amh2b, "temp_delim_count")
        box = layout.box()
        box.label(text="Vertex Group and ShapeKey")
        box.operator(AMH2B_OT_MakeTailorObjectSearchable.bl_idname)

class AMH2B_PT_View3D_Shrinkwrap(Panel):
    bl_label = "Shrinkwrap"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scn = context.scene
        layout = self.layout

        box = layout.box()
        box.label(text="Shrinkwrap Mesh Modifiers")
        box.operator(AMH2B_OT_CreateObjModDirectionalShrinkwrap.bl_idname)
        box.operator(AMH2B_OT_CreateObjModDirectionalThickShrinkwrap.bl_idname)
        box.operator(AMH2B_OT_CreateObjModShrinkwrap.bl_idname)
        box.operator(AMH2B_OT_CreateObjModThickShrinkwrap.bl_idname)
        box.prop(scn.amh2b, "nodes_override_create")

class AMH2B_PT_NodeEditorShrinkwrap(Panel):
    bl_label = "Shrinkwrap"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "AMH2B"

    def draw(self, context):
        scn = context.scene
        layout = self.layout

        box = layout.box()
        box.label(text="Create Shrinkwrap Nodes")
        box.operator(AMH2B_OT_CreateGeoNodesShrinkwrap.bl_idname)
        box.operator(AMH2B_OT_CreateGeoNodesThickShrinkwrap.bl_idname)
        box.operator(AMH2B_OT_CreateGeoNodesDirectionalShrinkwrap.bl_idname)
        box.operator(AMH2B_OT_CreateGeoNodesDirectionalThickShrinkwrap.bl_idname)
        box.prop(scn.amh2b, "nodes_override_create")

def dt_vert_mapping_items(self, context):
    return [ ("NEAREST", "Nearest Vertex", ""),
            ("TOPOLOGY", "Topology", ""),
            ("EDGE_NEAREST", "Nearest Edge Vertex", ""),
            ("EDGEINTERP_NEAREST", "Nearest Edge Interpolated", ""),
            ("POLY_NEAREST", "Nearest Face Vertex", ""),
            ("POLYINTERP_NEAREST", "Nearest Face Interpolated", ""),
            ("POLYINTERP_VNORPROJ", "Projected Face Interpolated", ""),
    ]

class AMH2B_PG_Amh2b(PropertyGroup):
    mat_active_slot_only: BoolProperty(name="Active Slot Only",
        description="Try to swap only the Active Slot material, instead of trying to swap all material slots",
        default=False)
    mat_exact_name_only: BoolProperty(name="Exact Name Only",
        description="Search for the exact same material name when trying to swap from another file", default=False)
    mat_ignore_autoname: BoolProperty(name="Ignore Autoname",
        description="If material swap function is tried and fails, re-try swap with material's 'auto-name' " +
        "extension removed.\ne.g. \"Mass0007:Eyebrow010:Eyebrow010.003\" material may be replaced " +
        "with \"Mass0007:Eyebrow010:Eyebrow010 material\"", default=True)
    mat_keep_original_name: BoolProperty(name="Keep Original Name",
        description="Ensure that the material name in each material slot is the same before and after swap", default=False)
    mat_name_delimiter: StringProperty(name="Delimiter",
        description="Delimiter between sections of material names (MakeHuman uses the colon : )\n : is the default value", default=":")
    mat_name_delimiter_count: IntProperty(name="Delim. Count",
        description="Number of delimiters allowed in name search. Extra delimiters and related name sections will " +
        "be ignored.\nDefault value is 1", default=1, min=0)
    arm_textblock_name: StringProperty(name="Text Editor Script Name",
        description="Script data-block name in text editor", default="Text")
    arm_generic_prefix: StringProperty(name="G Prefix",
        description="Generic prefix for bone rename.\nDefault value is 'G'", default="G")
    arm_generic_mhx: BoolProperty(name="Include MHX bones",
        description="Include MHX bones when renaming/un-naming", default=False)
    sk_active_function: EnumProperty(name="Function", description="ShapeKey menu active function",
        items=SK_MENU_FUNC_ITEMS)
    sk_bind_frame: IntProperty(name="Bind frame",
        description="Bind vertices in this frame. Choose a frame when mesh vertexes haven't moved from original " +
        "locations.\nHint: vertex locations in OBJECT mode should be the same as in EDIT mode.", default=0, min=0)
    sk_start_frame: IntProperty(name="Start frame",
        description="Choose first frame of mesh animation to convert to Shape Key", default=1, min=0)
    sk_end_frame: IntProperty(name="End frame",
        description="Choose last frame of mesh animation to convert to Shape Key", default=2, min=0)
    sk_animate: BoolProperty(name="Animate Shape Keys", description="Animate Shape Keys with keyframes", default=True)
    sk_add_frame_to_name: BoolProperty(name="Add Frame to Name",
        description="Append frame number to key name (e.g. DSKey005, DSKey006)", default=True)
    sk_dynamic: BoolProperty(name="Dynamic",
        description="Respect armature transformations when calculating deform shape keys. Dynamic is slower to " +
        "run than not-Dynamic", default=True)
    sk_extra_accuracy: IntProperty(name="",
        description="Extra accuracy iterations when baking shape keys with dynamic enabled", default=0, min=0)
    sk_deform_name_prefix: StringProperty(name="Prefix",
        description="Prefix for naming mesh deform shape keys. Default value is " + SC_DSKEY, default=SC_DSKEY)
    sk_adapt_size: BoolProperty(name="Adapt Size",
        description="Adapt size of shape key to size of mesh, per vertex, by ratio of sums of connected edge " +
        "lengths", default=True)
    sk_swap_autoname_ext: BoolProperty(name="Swap Autoname Ext",
        description="If shapekey copy function is tried and fails, re-try swap with objects 'auto-name' extension removed." +
        "\ne.g. Object Mass0007:Eyebrow010.003 shapekeys may be copied from object Mass0007:Eyebrow010 shapekeys", default=True)
    sk_function_prefix: StringProperty(name="Prefix",
        description="Prefix used in shape key functions. Default value is " + SC_DSKEY, default=SC_DSKEY)
    sk_mask_vgroup_name: StringProperty(name="Mask VGroup",
        description="Name of vertex group to use as a mask when baking shapekeys.\nOptional: Use this feature for " +
        "finer control over which vertexes are used to bake the shapekeys", default="")
    sk_mask_include: BoolProperty(name="Mask Include",
        description="If vertex group is given, and 'Include' is enabled, then only mask vertex group vertexes " +
        "are included when baking shapekey(s).\nIf vertex group is given, and 'Include' is not enabled, " +
        "then mask vertex group vertexes are excluded when baking shapekey(s)", default=False)
    vg_func_name_prefix: StringProperty(name="Prefix",
        description="Perform functions on selected MESH type objects, but only vertex groups with names " +
        "beginning with this prefix. Default value is " + SC_VGRP_AUTO_PREFIX, default=SC_VGRP_AUTO_PREFIX)
    vg_swap_autoname_ext: BoolProperty(name="Swap Autoname Ext",
        description="If vertex group copy function is tried and fails, re-try swap with objects 'auto-name' extension removed." +
        "\ne.g. Object Mass0007:Eyebrow010.003 vertex groups may be copied from object Mass0007:Eyebrow010 vertex groups", default=True)
    vg_create_name_only: BoolProperty(name="Create Groups Only in Name",
        description="Create vertex groups 'in name only' when copying.", default=False)
    wp_select_vertex_min_w: FloatProperty(name="Min Weight",
        description="Minimum weight of vertex to select", default=0.0, min=0.0, max=1.0)
    wp_select_vertex_max_w: FloatProperty(name="Max Weight",
        description="Maximum weight of vertex to select", default=1.0, min=0.0, max=1.0)
    wp_select_vertex_deselect: BoolProperty(name="Deselect All First",
        description="Deselect all vertexes before selecting by weight", default=True)
    wp_grow_paint_iterations: IntProperty(name="Iterations",
        description="Number of growth iterations - 'select more' is used each iteration to select more vertexes " +
        "before applying weight paint", default=1, min=1)
    wp_grow_paint_start_weight: FloatProperty(name="Start Weight",
        description="Weight paint value applied to currently selected vertexes", default=1.0, min=0.0, max=1.0)
    wp_grow_paint_end_weight: FloatProperty(name="End Weight",
        description="Weight paint value applied to vertexes selected last, in the final iteration", default=0.0,
        min=0.0, max=1.0)
    wp_paint_initial_selection: BoolProperty(name="Paint Initial Selection",
        description="Initial selection will be included when applying weight paints", default=True)
    wp_tail_fill_enable: BoolProperty(name="Tail Fill",
        description="All remaining non-hidden vertexes will have their vertex weight paint values set to tail " +
        "fill value, after applying weights to vertexes during 'select more' iterations", default=False)
    wp_tail_fill_value: FloatProperty(name="Tail Value",
        description="Weight paint value applied to tail fill vertexes", default=0.0, min=0.0, max=1.0)
    wp_tail_fill_connected: BoolProperty(name="Fill Only Linked",
        description="Only linked vertexes will be included in the tail fill process", default=True)
    anim_ratchet_frames: IntProperty(name="Frame Count",
        description="Number of times to apply Ratchet Hold, i.e. number of frames to Ratchet Hold", default=1, min=1)
    eblink_remove_start_enable: BoolProperty(name="Remove Start",
        description="Enable removal of eyeblink keyframes starting at given frame number" +
        "\nKeyframes before the given frame number will not be affected by this operation", default=False)
    eblink_remove_start_frame: IntProperty(name="Start Frame",
        description="First frame to use in keyframe removal operation", default=1)
    eblink_remove_end_enable: BoolProperty(name="Remove End",
        description="Enable removal of eyeblink keyframes ending at given frame number" +
        "\nKeyframes after the given frame number will not be affected by this operation", default=False)
    eblink_remove_end_frame: IntProperty(name="End Frame",
        description="Last frame to use in keyframe removal operation", default=250)
    eblink_remove_left: BoolProperty(name="Remove Left",
        description="Enable removal of eyeblink keyframes from left eye bones", default=True)
    eblink_remove_right: BoolProperty(name="Remove Right",
        description="Enable removal of eyeblink keyframes from right eye bones", default=True)
    eblink_framerate: FloatProperty(name="Frame Rate", description="Frames per second. " +
        "Input can be floating point, so e.g. the number 6.35 is allowed", default=30, min=0.001)
    eblink_start_frame: IntProperty(name="Start Frame",
        description="First frame of first eyeblink, before any random timing is applied", default=1)
    eblink_random_start_frame: FloatProperty(name="Random Start Frame",
        description="Max number of frames (not seconds) to add randomly to start frame. " +
        "Input can be floating point, so e.g. the number 6.35 is allowed", default=0, min=0)
    eblink_allow_random_drift: BoolProperty(name="Allow Random Drift",
        description="Allow any random period timing difference to accumulate, instead of trying to maintain a " +
        "constant period with variation", default=True)
    eblink_frame_count: IntProperty(name="Frame Count",
        description="Maximum number of frames to fill with blinking, final eyeblink may go over this count though " +
        "(debug this)", default=250)
    eblink_max_count_enable: BoolProperty(name="Use Max Blink Count",
        description="Use maximum number of blinks to create the eyeblink track", default=False)
    eblink_max_count: IntProperty(name="Max Blink Count",
        description="Maximum number of blinks to keyframe", default=10)
    eblink_blinks_per_min: FloatProperty(name="Blinks Per Minute",
        description="Number of blinks per minute. Input can be floating point, so e.g. the number 6.35 is allowed",
        default=10, min=0)
    eblink_blink_period_enable: BoolProperty(name="Use Blink Period",
        description="Instead of using Blinks Per Minute, use time (in seconds) between start of eyeblink and start of " +
        "next eyeblink", default=False)
    eblink_blink_period: FloatProperty(name="Blink Period",
        description="Time, in seconds, between the start of a eyeblink and the start of the next eyeblink",
        default=6, min=0.001)
    eblink_random_period_enable: FloatProperty(name="Period Random",
        description="Add a random amount of time, in seconds, between the start of a eyeblink and the start of the next eyeblink",
        default=0, min=0)
    eblink_eye_left_enable: BoolProperty(name="Enable Left", description="Enable left eye eyeblink", default=True)
    eblink_eye_right_enable: BoolProperty(name="Enable Right", description="Enable right eye eyeblink", default=True)
    eblink_shapekey_name: StringProperty(name="Closed Shapekey",
        description="Name of shapekey for closed eyes (leave blank to ignore)", default="")
    eblink_closing_time: FloatProperty(name="Closing Time",
        description="Time, in seconds, for eyelid to change from opened to closed", default=0.1, min=0.0001)
    eblink_closed_time: FloatProperty(name="Closed Time",
        description="Time, in seconds, that eyelid remains closed", default=0, min=0)
    eblink_opening_time: FloatProperty(name="Opening Time",
        description="Time, in seconds, for eyelid to change from closed to opened", default=0.475, min=0.0001)
    eblink_random_closing_time: FloatProperty(name="Closing Time",
        description="Add a random amount of time, in seconds, to eyelid closing time", default=0, min=0)
    eblink_random_closed_time: FloatProperty(name="Closed Time",
        description="Add a random amount of time, in seconds, to eyelid closed time", default=0, min=0)
    eblink_random_opening_time: FloatProperty(name="Opening Time",
        description="Add a random amount of time, in seconds, to eyelid opening time", default=0, min=0)
    eblink_bone_name_left_lower: StringProperty(name="Left Lower",
        description="Name of bone for left lower eyelid", default="lolid.L")
    eblink_bone_name_left_upper: StringProperty(name="Left Upper",
        description="Name of bone for left upper eyelid", default="uplid.L")
    eblink_bone_name_right_lower: StringProperty(name="Right Lower",
        description="Name of bone for right lower eyelid", default="lolid.R")
    eblink_bone_name_right_upper: StringProperty(name="Right Upper",
        description="Name of bone for right upper eyelid", default="uplid.R")
    eblink_text_save_name: StringProperty(name="Write Text",
        description="Name of textblock in text editor where eyeblink settings will be written (saved)", default="Text")
    eblink_text_load_name: StringProperty(name="Read Text",
        description="Name of textblock in text editor from which eyeblink settings will be read (loaded)", default="Text")
    elid_name_left_lower: StringProperty(name="Left Lower",
        description="Bone name for left lower eyelid", default="lolid.L")
    elid_name_left_upper: StringProperty(name="Left Upper",
        description="Bone name for left upper eyelid", default="uplid.L")
    elid_name_right_lower: StringProperty(name="Right Lower",
        description="Bone name for right lower eyelid", default="lolid.R")
    elid_name_right_upper: StringProperty(name="Right Upper",
        description="Bone name for right upper eyelid", default="uplid.R")
    elid_name_left_eye: StringProperty(name="Left Eye",
        description="Bone name for left eye (might need to use 'parent' of eye)", default="eye_parent.L")
    elid_name_right_eye: StringProperty(name="Right Eye",
        description="Bone name for right eye (might need to use 'parent' of eye)", default="eye_parent.R")
    elid_influence_lower: FloatProperty(name="Influence Lower",
        description="Lower eyelids bone constraint ('Copy Rotation') influence value", default=0.35, min=0, max=1)
    elid_influence_upper: FloatProperty(name="Influence Upper",
        description="Upper eyelids bone constraint ('Copy Rotation') influence value", default=0.5, min=0, max=1)
    elid_min_x_lower: FloatProperty(name="Lower Min X",
        description="Lower eyelids bone constraint ('Limit Rotation') minimum X rotation", subtype='ANGLE',
        default=-0.244346)
    elid_max_x_lower: FloatProperty(name="Lower Max X",
        description="Lower eyelids bone constraint ('Limit Rotation') maximum X rotation", subtype='ANGLE',
        default=0.087266)
    elid_min_x_upper: FloatProperty(name="Upper Min X",
        description="Upper eyelids bone constraint ('Limit Rotation') minimum X rotation", subtype='ANGLE',
        default=-0.087266)
    elid_max_x_upper: FloatProperty(name="Upper Max X",
        description="Upper eyelids bone constraint ('Limit Rotation') maximum X rotation", subtype='ANGLE',
        default=0.349066)
    temp_active_slot_only: BoolProperty(name="Active Slot Only",
        description="Rename only Active Slot material, instead of trying to rename all material slots",
        default=False)
    temp_delimiter: StringProperty(name="Delimiter",
        description="Delimiter between sections of material names (MakeHuman uses the colon : )", default=":")
    temp_delim_count: IntProperty(name="Delim. Count", description="Number of delimiters allowed in " +
        "name search. Extra delimiters and related name sections will be ignored", default=1, min=0)
    nodes_override_create: BoolProperty(name="Override Create", description="Geometry Nodes and custom " +
        "Node Groups will be re-created if this option is enabled. When custom Node Groups are " +
        "override created, old Node Groups of the same name are renamed and deprecated", default=False)

    sb_function: EnumProperty(items=SB_FUNCTION_ITEMS, description="Soft Body Function group")
    sb_apply_sk_mix: BoolProperty(name="Apply SK Mix", description="Apply all ShapeKeys instead of deleting all " \
        "ShapeKeys - necessary before applying Geometry Nodes", default=True)
    sb_add_mask_modifier: BoolProperty(name="Add Mask Modifier", description="Add Mask modifier with settings " \
        "auto-filled", default=True)
    sb_dt_gen_data_layers: BoolProperty(name="Generate Groups", description="With active object, create Vertex " \
        "Groups for Soft Body weights if necessary", default=True)
    sb_dt_individual: BoolProperty(name="Transfer Individually", description="Instead of creating a single Data " \
        "Transfer modifier to transfer all vertex groups, create multiple modifiers to transfer individual groups",
        default=False)
    sb_dt_vg_mask: BoolProperty(name="Include Mask", description="Include 'SB-mask' vertex group when creating " \
        "individual data transfer modifiers ", default=True)
    sb_dt_apply_mod: BoolProperty(name="Apply Modifier(s)", description="Apply Data Transfer modifier(s) to object",
        default=True)
    sb_dt_include_goal: BoolProperty(name="Goal", description="Include 'SB-goal'", default=True)
    sb_dt_include_mask: BoolProperty(name="Mask", description="Include 'SB-mask'", default=True)
    sb_dt_include_mass: BoolProperty(name="Mass", description="Include 'SB-mass'", default=True)
    sb_dt_include_spring: BoolProperty(name="Spring", description="Include 'SB-spring'", default=True)
    sb_dt_vert_mapping: bpy.props.EnumProperty(name="Vertex Data Mapping", description="Method used to map source " \
        "vertices to destination ones", items=dt_vert_mapping_items)
    sb_dt_goal_vg_name: StringProperty(name="Goal", description="Goal vertex group name", default="SB-goal")
    sb_dt_mask_vg_name: StringProperty(name="Mask", description="Mask vertex group name", default="SB-mask")
    sb_dt_mass_vg_name: StringProperty(name="Mass", description="Mass vertex group name", default="SB-mass")
    sb_dt_spring_vg_name: StringProperty(name="Spring", description="Spring vertex group name", default="SB-spring")

    attr_conv_function: EnumProperty(items=ATTR_CONV_FUNC_ITEMS)
    attr_conv_shapekey: StringProperty(name="ShapeKey", description="ShapeKey to convert to Attribute")
    attr_conv_attribute: StringProperty(name="Attribute", description="Attribute to convert to other")

classes = [
    AMH2B_PG_Amh2b,
    AMH2B_OT_SwapMatWithFile,
    AMH2B_OT_SwapMatInternal,
    AMH2B_OT_SetupMatSwap,
    AMH2B_OT_AddMaskOutMod,
    AMH2B_OT_ToggleViewMaskoutMod,
    AMH2B_OT_CopyVertexGroupsByPrefix,
    AMH2B_OT_DeleteVertexGroupsByPrefix,
    AMH2B_OT_MakeTailorGroups,
    AMH2B_OT_MakeTailorObjectSearchable,
    AMH2B_OT_SearchFileForAutoVGroups,
    AMH2B_OT_CreateSizeRig,
    AMH2B_OT_GrowPaint,
    AMH2B_OT_SelectVertexByWeight,
    AMH2B_OT_BakeDeformShapeKeys,
    AMH2B_OT_SearchFileForAutoShapeKeys,
    AMH2B_OT_SKFuncDelete,
    AMH2B_OT_SKFuncCopy,
    AMH2B_OT_DeformSK_ViewToggle,
    AMH2B_OT_CreateGeoNodesShrinkwrap,
    AMH2B_OT_CreateGeoNodesThickShrinkwrap,
    AMH2B_OT_CreateGeoNodesDirectionalShrinkwrap,
    AMH2B_OT_CreateGeoNodesDirectionalThickShrinkwrap,
    AMH2B_OT_CreateObjModDirectionalShrinkwrap,
    AMH2B_OT_CreateObjModDirectionalThickShrinkwrap,
    AMH2B_OT_CreateObjModShrinkwrap,
    AMH2B_OT_CreateObjModThickShrinkwrap,
    AMH2B_OT_ApplyScale,
    AMH2B_OT_AdjustPose,
    AMH2B_OT_BridgeRepose,
    AMH2B_OT_BoneWoven,
    AMH2B_OT_Lucky,
    AMH2B_OT_EnableModPreserveVolume,
    AMH2B_OT_DisableModPreserveVolume,
    AMH2B_OT_RenameGeneric,
    AMH2B_OT_UnNameGeneric,
    AMH2B_OT_RatchetHold,
    AMH2B_OT_RemoveBlinkTrack,
    AMH2B_OT_AddBlinkTrack,
    AMH2B_OT_SaveBlinkCSV,
    AMH2B_OT_LoadBlinkCSV,
    AMH2B_OT_ResetEyeOpened,
    AMH2B_OT_ResetEyeClosed,
    AMH2B_OT_SetEyeOpened,
    AMH2B_OT_SetEyeClosed,
    AMH2B_OT_AddLidLook,
    AMH2B_OT_RemoveLidLook,
    AMH2B_OT_AddSoftBodyWeightTestCalc,
    AMH2B_OT_FinishSoftBodyWeightCalc,
    AMH2B_OT_DataTransferSBWeight,
    AMH2B_OT_PresetSoftBody,
    AMH2B_OT_AddSoftBodySpring,
    AMH2B_OT_AttributeConvert,
    AMH2B_PT_MeshMat,
    AMH2B_PT_MeshSize,
    AMH2B_PT_View3D_Shrinkwrap,
    AMH2B_PT_VertexGroup,
    AMH2B_PT_WeightPaint,
    AMH2B_PT_Attribs,
    AMH2B_PT_SoftBodyWeight,
    AMH2B_PT_ShapeKey,
    AMH2B_PT_Armature,
    AMH2B_PT_Animation,
    AMH2B_PT_Eyelid,
    AMH2B_PT_EyeBlink,
    AMH2B_PT_Template,
    AMH2B_PT_NodeEditorShrinkwrap,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.amh2b = PointerProperty(type=AMH2B_PG_Amh2b)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.amh2b

if __name__ == "__main__":
    register()
