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
#   Blender 2.79 - 2.93 Addon
# A set of tools to automate the process of shading/texturing, and animating MakeHuman data imported in Blender.

bl_info = {
    "name": "Automate MakeHuman 2 Blender (AMH2B)",
    "description": "Automate process of importing and animating MakeHuman models.",
    "author": "Dave",
    "version": (1, 3, 3),
    "blender": (2, 80, 0),
    "location": "View 3D -> Tools -> AMH2B",
    "wiki_url": "https://github.com/DreamSpoon/AMH2B#readme",
    "category": "Import MakeHuman Automation",
}

import bpy

from .material import *
from .mesh_size import *
from .vgroup import *
from .weight_paint import *
from .cloth_sim import *
from .shape_key import *
from .armature import *
from .animation import AMH2B_RatchetHold
from .eyeblink import (AMH2B_RemoveBlinkTrack, AMH2B_AddBlinkTrack, AMH2B_SaveBlinkCSV, AMH2B_LoadBlinkCSV,
                       AMH2B_ResetEyeOpened, AMH2B_ResetEyeClosed, AMH2B_SetEyeOpened, AMH2B_SetEyeClosed)
from .eyelid import (AMH2B_AddLidLook, AMH2B_RemoveLidLook)
from .const import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

#####################################################

class AMH2B_MeshMat(bpy.types.Panel):
    bl_label = "Mesh Material"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Swap Material")
        box.operator("amh2b.mat_search_file")
        sub = box.column()
        sub.active = not scn.Amh2bPropMatExactNameOnly
        sub.operator("amh2b.mat_search_internal")
        box.prop(scn, "Amh2bPropMatActiveSlotOnly")
        box.prop(scn, "Amh2bPropMatExactNameOnly")
        sub = box.column()
        sub.active = not scn.Amh2bPropMatExactNameOnly
        sub.prop(scn, "Amh2bPropMatIgnoreAutoname")
        sub.prop(scn, "Amh2bPropMatKeepOriginalName")
        sub.prop(scn, "Amh2bPropMatDelimiter")
        sub.prop(scn, "Amh2bPropMatDelimCount")

class AMH2B_MeshSize(bpy.types.Panel):
    bl_label = "Mesh Size"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Clothing Size")
        box.operator("amh2b.mesh_create_size_rig")

class AMH2B_VertexGroup(bpy.types.Panel):
    bl_label = "Vertex Group"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Functions")
        box.operator("amh2b.vg_copy_from_file")
        box.operator("amh2b.vg_copy_by_prefix")
        box.operator("amh2b.vg_delete_by_prefix")
        box.prop(scn, "Amh2bPropVG_FunctionNamePrefix")
        box.prop(scn, "Amh2bPropVG_SwapAutonameExt")
        box.prop(scn, "Amh2bPropSK_CreateNameOnly")
        box = layout.box()
        box.label(text="AutoMask & Pin Group")
        box.operator("amh2b.vg_make_auto_vgroups")
        box.operator("amh2b.vg_add_maskout_modifier")
        box.operator("amh2b.vg_toggle_auto_maskout")

class AMH2B_WeightPaint(bpy.types.Panel):
    bl_label = "Weight Paint"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Vertex Select")
        box.operator("amh2b.wp_select_vertex_by_weight")
        box.prop(scn, "Amh2bPropWP_SelectVertexMinW")
        box.prop(scn, "Amh2bPropWP_SelectVertexMaxW")
        box.prop(scn, "Amh2bPropWP_SelectVertexDeselect")
        box = layout.box()
        box.label(text="Grow Selection Paint")
        box.operator("amh2b.wp_grow_paint")
        box.prop(scn, "Amh2bPropWP_GrowPaintIterations")
        box.prop(scn, "Amh2bPropWP_GrowPaintStartWeight")
        box.prop(scn, "Amh2bPropWP_GrowPaintEndWeight")
        box.prop(scn, "Amh2bPropWP_PaintInitialSelection")
        box.prop(scn, "Amh2bPropWP_TailFill")
        sub = box.column()
        sub.active = scn.Amh2bPropWP_TailFill
        sub.prop(scn, "Amh2bPropWP_TailFillValue")
        sub.prop(scn, "Amh2bPropWP_TailFillConnected")

class AMH2B_Simulation(bpy.types.Panel):
    bl_label = "Simulation"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Cloth Sim")
        box.operator("amh2b.csim_add_sim")

class AMH2B_ShapeKey(bpy.types.Panel):
    bl_label = "ShapeKey"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.label(text="Functions")
        box.operator("amh2b.sk_search_file_for_auto_sk")
        box.operator("amh2b.sk_func_copy")
        box.prop(scn, "Amh2bPropSK_AdaptSize")
        box.prop(scn, "Amh2bPropSK_SwapAutonameExt")
        box.operator("amh2b.sk_func_delete")
        box.prop(scn, "Amh2bPropSK_FunctionPrefix")
        box = layout.box()
        box.label(text="Bake Deform ShapeKey")
        box.operator("amh2b.sk_bake_deform_shape_keys")
        box.prop(scn, "Amh2bPropSK_MaskVGroupName")
        box.prop(scn, "Amh2bPropSK_MaskInclude")
        box.prop(scn, "Amh2bPropSK_DeformShapeKeyPrefix")
        box.prop(scn, "Amh2bPropSK_BindFrame")
        box.prop(scn, "Amh2bPropSK_StartFrame")
        box.prop(scn, "Amh2bPropSK_EndFrame")
        box.prop(scn, "Amh2bPropSK_Animate")
        box.prop(scn, "Amh2bPropSK_AddFrameToName")
        box.prop(scn, "Amh2bPropSK_Dynamic")
        sub = box.column()
        sub.active = scn.Amh2bPropSK_Dynamic
        sub.label(text="Extra Accuracy")
        sub.prop(scn, "Amh2bPropSK_ExtraAccuracy")
        sub = box.column()
        sub.active = not scn.Amh2bPropSK_Dynamic
        sub.operator("amh2b.sk_deform_sk_view_toggle")

class AMH2B_Armature(bpy.types.Panel):
    bl_label = "Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.label(text="Retarget")
        box.operator("amh2b.arm_adjust_pose")
        box.prop(scn, "Amh2bPropArmTextBlockName")
        box.operator("amh2b.arm_apply_scale")
        box.operator("amh2b.arm_bridge_repose")
        box.operator("amh2b.arm_bone_woven")
        box = layout.box()
        box.label(text="Retarget Multi-Function")
        box.operator("amh2b.arm_lucky")
        box = layout.box()
        box.label(text="Preserve Volume Toggle")
        box.operator("amh2b.arm_enable_preserve_volume")
        box.operator("amh2b.arm_disable_preserve_volume")
        box = layout.box()
        box.label(text="Bone Names")
        box.operator("amh2b.arm_rename_generic")
        box.prop(scn, "Amh2bPropArmGenericPrefix")
        box.prop(scn, "Amh2bPropArmGenericMHX")
        box.operator("amh2b.arm_un_name_generic")

class AMH2B_Animation(bpy.types.Panel):
    bl_label = "Animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.label(text="Object Location")
        box.operator("amh2b.anim_ratchet_hold")
        box.prop(scn, "Amh2bPropAnimRatchetFrameCount")

class AMH2B_Eyelid(bpy.types.Panel):
    bl_label = "Eyelid"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.operator("amh2b.eyelid_remove_lidlook")
        box.operator("amh2b.eyelid_add_lidlook")
        box.label(text="Eyelid Bone Names")
        box.prop(scn, "Amh2bPropEyelidNameLeftLower")
        box.prop(scn, "Amh2bPropEyelidNameLeftUpper")
        box.prop(scn, "Amh2bPropEyelidNameRightLower")
        box.prop(scn, "Amh2bPropEyelidNameRightUpper")
        box.label(text="Eye Bone Names")
        box.prop(scn, "Amh2bPropEyelidNameLeftEye")
        box.prop(scn, "Amh2bPropEyelidNameRightEye")
        box.label(text="Influence Amounts")
        box.prop(scn, "Amh2bPropEyelidInfluenceLower")
        box.prop(scn, "Amh2bPropEyelidInfluenceUpper")
        box.label(text="Min/Max Rotation Lower")
        box.prop(scn, "Amh2bPropEyelidMinXLower")
        box.prop(scn, "Amh2bPropEyelidMaxXLower")
        box.label(text="Min/Max Rotation Upper")
        box.prop(scn, "Amh2bPropEyelidMinXUpper")
        box.prop(scn, "Amh2bPropEyelidMaxXUpper")

class AMH2B_EyeBlink(bpy.types.Panel):
    bl_label = "Eye Blink"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.operator("amh2b.eblink_remove_blink_track")
        box.prop(scn, "Amh2bPropEBlinkRemoveStart")
        sub = box.column()
        sub.active = scn.Amh2bPropEBlinkRemoveStart
        sub.prop(scn, "Amh2bPropEBlinkRemoveStartFrame")
        box.prop(scn, "Amh2bPropEBlinkRemoveEnd")
        sub = box.column()
        sub.active = scn.Amh2bPropEBlinkRemoveEnd
        sub.prop(scn, "Amh2bPropEBlinkRemoveEndFrame")
        box.prop(scn, "Amh2bPropEBlinkRemoveLeft")
        box.prop(scn, "Amh2bPropEBlinkRemoveRight")
        box = layout.box()
        box.operator("amh2b.eblink_add_blink_track")
        box = layout.box()
        box.label(text="Options")
        box.prop(scn, "Amh2bPropEBlinkFrameRate")
        box.prop(scn, "Amh2bPropEBlinkStartFrame")
        box.prop(scn, "Amh2bPropEBlinkRndStartFrame")
        box.prop(scn, "Amh2bPropEBlinkAllowRndDrift")
        box.prop(scn, "Amh2bPropEBlinkFrameCount")
        box.prop(scn, "Amh2bPropEBlinkUseMaxCount")
        sub = box.column()
        sub.active = scn.Amh2bPropEBlinkUseMaxCount
        sub.prop(scn, "Amh2bPropEBlinkMaxCount")
        sub = box.column()
        sub.active = not scn.Amh2bPropEBlinkUseBlinkPeriod
        sub.prop(scn, "Amh2bPropEBlinkBlinksPerMinute")
        box.prop(scn, "Amh2bPropEBlinkUseBlinkPeriod")
        sub = box.column()
        sub.active = scn.Amh2bPropEBlinkUseBlinkPeriod
        sub.prop(scn, "Amh2bPropEBlinkPeriod")
        box.prop(scn, "Amh2bPropEBlinkRndPeriod")
        box.prop(scn, "Amh2bPropEBlinkEnableLeft")
        box.prop(scn, "Amh2bPropEBlinkEnableRight")
        box.prop(scn, "Amh2bPropEBlinkShapekeyName")
        box = layout.box()
        box.label(text="Basis")
        box.prop(scn, "Amh2bPropEBlinkClosingTime")
        box.prop(scn, "Amh2bPropEBlinkClosedTime")
        box.prop(scn, "Amh2bPropEBlinkOpeningTime")
        box = layout.box()
        box.label(text="Random")
        box.prop(scn, "Amh2bPropEBlinkRndClosingTime")
        box.prop(scn, "Amh2bPropEBlinkRndClosedTime")
        box.prop(scn, "Amh2bPropEBlinkRndOpeningTime")
        box = layout.box()
        box.label(text="Template Set/Reset")
        box.operator("amh2b.eblink_set_opened")
        box.operator("amh2b.eblink_reset_opened")
        box.operator("amh2b.eblink_set_closed")
        box.operator("amh2b.eblink_reset_closed")
        box = layout.box()
        box.label(text="Template Bone Names")
        box.prop(scn, "Amh2bPropEBlinkBNameLeftLower")
        box.prop(scn, "Amh2bPropEBlinkBNameLeftUpper")
        box.prop(scn, "Amh2bPropEBlinkBNameRightLower")
        box.prop(scn, "Amh2bPropEBlinkBNameRightUpper")
        box = layout.box()
        box.label(text="Template Save/Load")
        box.operator("amh2b.eblink_save_csv")
        box.prop(scn, "Amh2bPropEBlinkTextSaveName")
        box.operator("amh2b.eblink_load_csv")
        box.prop(scn, "Amh2bPropEBlinkTextLoadName")

class AMH2B_Template(bpy.types.Panel):
    bl_label = "Template"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.label(text="Material")
        box.operator("amh2b.temp_setup_mat_swap")
        box.prop(scn, "Amh2bPropTempActiveSlotOnly")
        box.prop(scn, "Amh2bPropTempDelimiter")
        box.prop(scn, "Amh2bPropTempDelimCount")
        box = layout.box()
        box.label(text="Vertex Group and ShapeKey")
        box.operator("amh2b.temp_make_tailor_object_searchable")

classes = [
    AMH2B_SwapMatWithFile,
    AMH2B_SwapMatInternal,
    AMH2B_SetupMatSwap,
    AMH2B_AddMaskOutMod,
    AMH2B_ToggleViewMaskoutMod,
    AMH2B_CopyVertexGroupsByPrefix,
    AMH2B_DeleteVertexGroupsByPrefix,
    AMH2B_MakeTailorGroups,
    AMH2B_MakeTailorObjectSearchable,
    AMH2B_SearchFileForAutoVGroups,
    AMH2B_CreateSizeRig,
    AMH2B_GrowPaint,
    AMH2B_SelectVertexByWeight,
    AMH2B_AddClothSim,
    AMH2B_BakeDeformShapeKeys,
    AMH2B_SearchFileForAutoShapeKeys,
    AMH2B_SKFuncDelete,
    AMH2B_SKFuncCopy,
    AMH2B_DeformSK_ViewToggle,
    AMH2B_ApplyScale,
    AMH2B_AdjustPose,
    AMH2B_BridgeRepose,
    AMH2B_BoneWoven,
    AMH2B_Lucky,
    AMH2B_EnableModPreserveVolume,
    AMH2B_DisableModPreserveVolume,
    AMH2B_RenameGeneric,
    AMH2B_UnNameGeneric,
    AMH2B_RatchetHold,
    AMH2B_RemoveBlinkTrack,
    AMH2B_AddBlinkTrack,
    AMH2B_SaveBlinkCSV,
    AMH2B_LoadBlinkCSV,
    AMH2B_ResetEyeOpened,
    AMH2B_ResetEyeClosed,
    AMH2B_SetEyeOpened,
    AMH2B_SetEyeClosed,
    AMH2B_AddLidLook,
    AMH2B_RemoveLidLook,
    AMH2B_MeshMat,
    AMH2B_MeshSize,
    AMH2B_VertexGroup,
    AMH2B_WeightPaint,
    AMH2B_Simulation,
    AMH2B_ShapeKey,
    AMH2B_Armature,
    AMH2B_Animation,
    AMH2B_Eyelid,
    AMH2B_EyeBlink,
    AMH2B_Template,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bts = bpy.types.Scene
    bp = bpy.props

    bts.Amh2bPropMatActiveSlotOnly = bp.BoolProperty(name="Active Slot Only",
        description="Try to swap only the Active Slot material, instead of trying to swap all material slots",
        default=False)
    bts.Amh2bPropMatExactNameOnly = bp.BoolProperty(name="Exact Name Only",
        description="Search for the exact same material name when trying to swap from another file", default=False)
    bts.Amh2bPropMatIgnoreAutoname = bp.BoolProperty(name="Ignore Autoname",
        description="If material swap function is tried and fails, re-try swap with material's 'auto-name' " +
        "extension removed.\ne.g. \"Mass0007:Eyebrow010:Eyebrow010.003\" material may be replaced " +
        "with \"Mass0007:Eyebrow010:Eyebrow010 material\"", default=True)
    bts.Amh2bPropMatKeepOriginalName = bp.BoolProperty(name="Keep Original Name",
        description="Ensure that the material name in each material slot is the same before and after swap", default=False)
    bts.Amh2bPropMatDelimiter = bp.StringProperty(name="Delimiter",
        description="Delimiter between sections of material names (MakeHuman uses the colon : )\n : is the default value", default=":")
    bts.Amh2bPropMatDelimCount = bp.IntProperty(name="Delim. Count",
        description="Number of delimiters allowed in name search. Extra delimiters and related name sections will " +
        "be ignored.\nDefault value is 1", default=1, min=0)
    bts.Amh2bPropArmTextBlockName = bp.StringProperty(name="Text Editor Script Name",
        description="Script data-block name in text editor", default="Text")
    bts.Amh2bPropArmGenericPrefix = bp.StringProperty(name="G Prefix",
        description="Generic prefix for bone rename.\nDefault value is 'G'", default="G")
    bts.Amh2bPropArmGenericMHX = bp.BoolProperty(name="Include MHX bones",
        description="Include MHX bones when renaming/un-naming", default=False)
    bts.Amh2bPropSK_BindFrame = bp.IntProperty(name="Bind frame",
        description="Bind vertices in this frame. Choose a frame when mesh vertexes haven't moved from original " +
        "locations.\nHint: vertex locations in OBJECT mode should be the same as in EDIT mode.", default=0, min=0)
    bts.Amh2bPropSK_StartFrame = bp.IntProperty(name="Start frame",
        description="Choose first frame of mesh animation to convert to Shape Key", default=1, min=0)
    bts.Amh2bPropSK_EndFrame = bp.IntProperty(name="End frame",
        description="Choose last frame of mesh animation to convert to Shape Key", default=2, min=0)
    bts.Amh2bPropSK_Animate = bp.BoolProperty(name="Animate Shape Keys",
        description="Keyframe shape key values to animate frames when Shape Keys were created", default=True)
    bts.Amh2bPropSK_AddFrameToName = bp.BoolProperty(name="Add Frame to Name",
        description="Append frame number to key name (e.g. DSKey005, DSKey006)", default=True)
    bts.Amh2bPropSK_Dynamic = bp.BoolProperty(name="Dynamic",
        description="Respect armature transformations when calculating deform shape keys. Dynamic is slower to " +
        "run than not-Dynamic", default=True)
    bts.Amh2bPropSK_ExtraAccuracy = bp.IntProperty(name="",
        description="Extra accuracy iterations when baking shape keys with dynamic enabled", default=0, min=0)
    bts.Amh2bPropSK_DeformShapeKeyPrefix = bp.StringProperty(name="Prefix",
        description="Prefix for naming mesh deform shape keys. Default value is " + SC_DSKEY, default=SC_DSKEY)
    bts.Amh2bPropSK_AdaptSize = bp.BoolProperty(name="Adapt Size",
        description="Adapt size of shape key to size of mesh, per vertex, by ratio of sums of connected edge " +
        "lengths", default=True)
    bts.Amh2bPropSK_SwapAutonameExt = bp.BoolProperty(name="Swap Autoname Ext",
        description="If shapekey copy function is tried and fails, re-try swap with objects 'auto-name' extension removed." +
        "\ne.g. Object Mass0007:Eyebrow010.003 shapekeys may be copied from object Mass0007:Eyebrow010 shapekeys", default=True)
    bts.Amh2bPropSK_CreateNameOnly = bp.BoolProperty(name="Create Groups Only in Name",
        description="Create vertex groups 'in name only' when copying.", default=False)
    bts.Amh2bPropSK_FunctionPrefix = bp.StringProperty(name="Prefix",
        description="Prefix used in shape key functions. Default value is " + SC_DSKEY, default=SC_DSKEY)
    bts.Amh2bPropSK_MaskVGroupName = bp.StringProperty(name="Mask VGroup",
        description="Name of vertex group to use as a mask when baking shapekeys.\nOptional: Use this feature for " +
        "finer control over which vertexes are used to bake the shapekeys", default="")
    bts.Amh2bPropSK_MaskInclude = bp.BoolProperty(name="Mask Include",
        description="If vertex group is given, and 'Include' is enabled, then only mask vertex group vertexes " +
        "are included when baking shapekey(s).\nIf vertex group is given, and 'Include' is not enabled, " +
        "then mask vertex group vertexes are excluded when baking shapekey(s)", default=False)
    bts.Amh2bPropVG_FunctionNamePrefix = bp.StringProperty(name="Prefix",
        description="Perform functions on selected MESH type objects, but only vertex groups with names " +
        "beginning with this prefix. Default value is " + SC_VGRP_AUTO_PREFIX, default=SC_VGRP_AUTO_PREFIX)
    bts.Amh2bPropVG_SwapAutonameExt = bp.BoolProperty(name="Swap Autoname Ext",
        description="If vertex group copy function is tried and fails, re-try swap with objects 'auto-name' extension removed." +
        "\ne.g. Object Mass0007:Eyebrow010.003 vertex groups may be copied from object Mass0007:Eyebrow010 vertex groups", default=True)
    bts.Amh2bPropWP_SelectVertexMinW = bp.FloatProperty(name="Min Weight",
        description="Minimum weight of vertex to select", default=0.0, min=0.0, max=1.0)
    bts.Amh2bPropWP_SelectVertexMaxW = bp.FloatProperty(name="Max Weight",
        description="Maximum weight of vertex to select", default=1.0, min=0.0, max=1.0)
    bts.Amh2bPropWP_SelectVertexDeselect = bp.BoolProperty(name="Deselect All First",
        description="Deselect all vertexes before selecting by weight", default=True)
    bts.Amh2bPropWP_GrowPaintIterations = bp.IntProperty(name="Iterations",
        description="Number of growth iterations - 'select more' is used each iteration to select more vertexes " +
        "before applying weight paint", default=1, min=1)
    bts.Amh2bPropWP_GrowPaintStartWeight = bp.FloatProperty(name="Start Weight",
        description="Weight paint value applied to currently selected vertexes", default=1.0, min=0.0, max=1.0)
    bts.Amh2bPropWP_GrowPaintEndWeight = bp.FloatProperty(name="End Weight",
        description="Weight paint value applied to vertexes selected last, in the final iteration", default=0.0,
        min=0.0, max=1.0)
    bts.Amh2bPropWP_PaintInitialSelection = bp.BoolProperty(name="Paint Initial Selection",
        description="Initial selection will be included when applying weight paints", default=True)
    bts.Amh2bPropWP_TailFill = bp.BoolProperty(name="Tail Fill",
        description="All remaining non-hidden vertexes will have their vertex weight paint values set to tail " +
        "fill value, after applying weights to vertexes during 'select more' iterations", default=False)
    bts.Amh2bPropWP_TailFillValue = bp.FloatProperty(name="Tail Value",
        description="Weight paint value applied to tail fill vertexes", default=0.0, min=0.0, max=1.0)
    bts.Amh2bPropWP_TailFillConnected = bp.BoolProperty(name="Fill Only Linked",
        description="Only linked vertexes will be included in the tail fill process", default=True)
    bts.Amh2bPropAnimRatchetFrameCount = bp.IntProperty(name="Frame Count",
        description="Number of times to apply Ratchet Hold, i.e. number of frames to Ratchet Hold", default=1, min=1)
    bts.Amh2bPropEBlinkRemoveStart = bp.BoolProperty(name="Remove Start",
        description="Enable removal of eyeblink keyframes starting at given frame number" +
        "\nKeyframes before the given frame number will not be affected by this operation", default=False)
    bts.Amh2bPropEBlinkRemoveStartFrame = bp.IntProperty(name="Start Frame",
        description="First frame to use in keyframe removal operation", default=1)
    bts.Amh2bPropEBlinkRemoveEnd = bp.BoolProperty(name="Remove End",
        description="Enable removal of eyeblink keyframes ending at given frame number" +
        "\nKeyframes after the given frame number will not be affected by this operation", default=False)
    bts.Amh2bPropEBlinkRemoveEndFrame = bp.IntProperty(name="End Frame",
        description="Last frame to use in keyframe removal operation", default=250)
    bts.Amh2bPropEBlinkRemoveLeft = bp.BoolProperty(name="Remove Left",
        description="Enable removal of eyeblink keyframes from left eye bones", default=True)
    bts.Amh2bPropEBlinkRemoveRight = bp.BoolProperty(name="Remove Right",
        description="Enable removal of eyeblink keyframes from right eye bones", default=True)
    bts.Amh2bPropEBlinkFrameRate = bp.FloatProperty(name="Frame Rate", description="Frames per second. " +
        "Input can be floating point, so e.g. the number 6.35 is allowed", default=30, min=0.001)
    bts.Amh2bPropEBlinkStartFrame = bp.IntProperty(name="Start Frame",
        description="First frame of first eyeblink, before any random timing is applied", default=1)
    bts.Amh2bPropEBlinkRndStartFrame = bp.FloatProperty(name="Random Start Frame",
        description="Max number of frames (not seconds) to add randomly to start frame. " +
        "Input can be floating point, so e.g. the number 6.35 is allowed", default=0, min=0)
    bts.Amh2bPropEBlinkAllowRndDrift = bp.BoolProperty(name="Allow Random Drift",
        description="Allow any random period timing difference to accumulate, instead of trying to maintain a " +
        "constant period with variation", default=True)
    bts.Amh2bPropEBlinkFrameCount = bp.IntProperty(name="Frame Count",
        description="Maximum number of frames to fill with blinking, final eyeblink may go over this count though " +
        "(debug this)", default=250)
    bts.Amh2bPropEBlinkUseMaxCount = bp.BoolProperty(name="Use Max Blink Count",
        description="Use maximum number of blinks to create the eyeblink track", default=False)
    bts.Amh2bPropEBlinkMaxCount = bp.IntProperty(name="Max Blink Count",
        description="Maximum number of blinks to keyframe", default=10)
    bts.Amh2bPropEBlinkBlinksPerMinute = bp.FloatProperty(name="Blinks Per Minute",
        description="Number of blinks per minute. Input can be floating point, so e.g. the number 6.35 is allowed",
        default=10, min=0)
    bts.Amh2bPropEBlinkUseBlinkPeriod = bp.BoolProperty(name="Use Blink Period",
        description="Instead of using Blinks Per Minute, use time (in seconds) between start of eyeblink and start of " +
        "next eyeblink", default=False)
    bts.Amh2bPropEBlinkPeriod = bp.FloatProperty(name="Blink Period",
        description="Time, in seconds, between the start of a eyeblink and the start of the next eyeblink",
        default=6, min=0.001)
    bts.Amh2bPropEBlinkRndPeriod = bp.FloatProperty(name="Period Random",
        description="Add a random amount of time, in seconds, between the start of a eyeblink and the start of the next eyeblink",
        default=0, min=0)
    bts.Amh2bPropEBlinkEnableLeft = bp.BoolProperty(name="Enable Left", description="Enable left eye eyeblink", default=True)
    bts.Amh2bPropEBlinkEnableRight = bp.BoolProperty(name="Enable Right", description="Enable right eye eyeblink", default=True)
    bts.Amh2bPropEBlinkShapekeyName = bp.StringProperty(name="Closed Shapekey",
        description="Name of shapekey for closed eyes (leave blank to ignore)", default="")
    bts.Amh2bPropEBlinkClosingTime = bp.FloatProperty(name="Closing Time",
        description="Time, in seconds, for eyelid to change from opened to closed", default=0.1, min=0.0001)
    bts.Amh2bPropEBlinkClosedTime = bp.FloatProperty(name="Closed Time",
        description="Time, in seconds, that eyelid remains closed", default=0, min=0)
    bts.Amh2bPropEBlinkOpeningTime = bp.FloatProperty(name="Opening Time",
        description="Time, in seconds, for eyelid to change from closed to opened", default=0.475, min=0.0001)
    bts.Amh2bPropEBlinkRndClosingTime = bp.FloatProperty(name="Closing Time",
        description="Add a random amount of time, in seconds, to eyelid closing time", default=0, min=0)
    bts.Amh2bPropEBlinkRndClosedTime = bp.FloatProperty(name="Closed Time",
        description="Add a random amount of time, in seconds, to eyelid closed time", default=0, min=0)
    bts.Amh2bPropEBlinkRndOpeningTime = bp.FloatProperty(name="Opening Time",
        description="Add a random amount of time, in seconds, to eyelid opening time", default=0, min=0)
    bts.Amh2bPropEBlinkBNameLeftLower = bp.StringProperty(name="Left Lower",
        description="Name of bone for left lower eyelid", default="lolid.L")
    bts.Amh2bPropEBlinkBNameLeftUpper = bp.StringProperty(name="Left Upper",
        description="Name of bone for left upper eyelid", default="uplid.L")
    bts.Amh2bPropEBlinkBNameRightLower = bp.StringProperty(name="Right Lower",
        description="Name of bone for right lower eyelid", default="lolid.R")
    bts.Amh2bPropEBlinkBNameRightUpper = bp.StringProperty(name="Right Upper",
        description="Name of bone for right upper eyelid", default="uplid.R")
    bts.Amh2bPropEBlinkTextSaveName = bp.StringProperty(name="Write Text",
        description="Name of textblock in text editor where eyeblink settings will be written (saved)", default="Text")
    bts.Amh2bPropEBlinkTextLoadName = bp.StringProperty(name="Read Text",
        description="Name of textblock in text editor from which eyeblink settings will be read (loaded)", default="Text")
    bts.Amh2bPropEyelidNameLeftLower = bp.StringProperty(name="Left Lower",
        description="Bone name for left lower eyelid", default="lolid.L")
    bts.Amh2bPropEyelidNameLeftUpper = bp.StringProperty(name="Left Upper",
        description="Bone name for left upper eyelid", default="uplid.L")
    bts.Amh2bPropEyelidNameRightLower = bp.StringProperty(name="Right Lower",
        description="Bone name for right lower eyelid", default="lolid.R")
    bts.Amh2bPropEyelidNameRightUpper = bp.StringProperty(name="Right Upper",
        description="Bone name for right upper eyelid", default="uplid.R")
    bts.Amh2bPropEyelidNameLeftEye = bp.StringProperty(name="Left Eye",
        description="Bone name for left eye (might need to use 'parent' of eye)", default="eye_parent.L")
    bts.Amh2bPropEyelidNameRightEye = bp.StringProperty(name="Right Eye",
        description="Bone name for right eye (might need to use 'parent' of eye)", default="eye_parent.R")
    bts.Amh2bPropEyelidInfluenceLower = bp.FloatProperty(name="Influence Lower",
        description="Lower eyelids bone constraint ('Copy Rotation') influence value", default=0.35, min=0, max=1)
    bts.Amh2bPropEyelidInfluenceUpper = bp.FloatProperty(name="Influence Upper",
        description="Upper eyelids bone constraint ('Copy Rotation') influence value", default=0.5, min=0, max=1)
    bts.Amh2bPropEyelidMinXLower = bp.FloatProperty(name="Lower Min X",
        description="Lower eyelids bone constraint ('Limit Rotation') minimum X rotation", subtype='ANGLE',
        default=-0.244346)
    bts.Amh2bPropEyelidMaxXLower = bp.FloatProperty(name="Lower Max X",
        description="Lower eyelids bone constraint ('Limit Rotation') maximum X rotation", subtype='ANGLE',
        default=0.087266)
    bts.Amh2bPropEyelidMinXUpper = bp.FloatProperty(name="Upper Min X",
        description="Upper eyelids bone constraint ('Limit Rotation') minimum X rotation", subtype='ANGLE',
        default=-0.087266)
    bts.Amh2bPropEyelidMaxXUpper = bp.FloatProperty(name="Upper Max X",
        description="Upper eyelids bone constraint ('Limit Rotation') maximum X rotation", subtype='ANGLE',
        default=0.349066)
    bts.Amh2bPropTempActiveSlotOnly = bp.BoolProperty(name="Active Slot Only",
        description="Rename only Active Slot material, instead of trying to rename all material slots",
        default=False)
    bts.Amh2bPropTempDelimiter = bp.StringProperty(name="Delimiter",
        description="Delimiter between sections of material names (MakeHuman uses the colon : )", default=":")
    bts.Amh2bPropTempDelimCount = bp.IntProperty(name="Delim. Count",
        description="Number of delimiters allowed in name search. Extra delimiters and related name sections will be ignored", default=1, min=0)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
