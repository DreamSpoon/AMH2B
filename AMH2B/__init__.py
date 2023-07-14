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
    "version": (2, 2, 0),
    "blender": (3, 30, 0),
    "location": "View 3D -> Tools -> AMH2B",
    "doc_url": "https://github.com/DreamSpoon/AMH2B#readme",
    "category": "Import MakeHuman Automation",
}

import bpy
from bpy.types import (Panel, PropertyGroup, Scene)
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty,
    StringProperty)

from .const import (SC_DSKEY, SC_VGRP_AUTO_PREFIX)

from .animation.operator import (AMH2B_OT_RatchetPoint, AMH2B_OT_RatchetHold)
from .animation.panel import draw_panel_animation
from .armature.func import (ARM_FUNC_ITEMS, script_pose_preset_items, stitch_armature_preset_items)
from .armature.operator import (AMH2B_OT_ScriptPose, AMH2B_OT_ApplyScale, AMH2B_OT_EnableModPreserveVolume,
    AMH2B_OT_DisableModPreserveVolume, AMH2B_OT_RenameGeneric, AMH2B_OT_UnNameGeneric, AMH2B_OT_CleanupGizmos,
    AMH2B_OT_StitchArmature, AMH2B_OT_CopyArmatureTransforms)
from .armature.panel import draw_panel_armature
from .attributes.panel import draw_panel_attributes
from .attributes.operator import AMH2B_OT_AttributeConvert
from .attributes.func import ATTR_CONV_FUNC_ITEMS
from .eyeblink import (AMH2B_OT_RemoveBlinkTrack, AMH2B_OT_AddBlinkTrack, AMH2B_OT_SaveBlinkCSV, AMH2B_OT_LoadBlinkCSV,
    AMH2B_OT_ResetEyeOpened, AMH2B_OT_ResetEyeClosed, AMH2B_OT_SetEyeOpened, AMH2B_OT_SetEyeClosed)
from .eyelid import (AMH2B_OT_AddLidLook, AMH2B_OT_RemoveLidLook)
from .material import (AMH2B_OT_SwapMatWithFile, AMH2B_OT_SwapMatInternal)
from .shape_key.func import SK_FUNC_ITEMS
from .shape_key.operator import (AMH2B_OT_BakeDeformShapeKeys, AMH2B_OT_SearchFileForAutoShapeKeys,
    AMH2B_OT_SKFuncDelete, AMH2B_OT_CopyOtherSK, AMH2B_OT_ApplyModifierSK)
from .shape_key.panel import draw_panel_shape_key
from .shrinkwrap import (AMH2B_OT_CreateGeoNodesDirectionalShrinkwrap,
    AMH2B_OT_CreateGeoNodesDirectionalThickShrinkwrap, AMH2B_OT_CreateGeoNodesShrinkwrap,
    AMH2B_OT_CreateGeoNodesThickShrinkwrap)
from .shrinkwrap_obj import (AMH2B_OT_CreateObjModDirectionalShrinkwrap,
    AMH2B_OT_CreateObjModDirectionalThickShrinkwrap, AMH2B_OT_CreateObjModShrinkwrap,
    AMH2B_OT_CreateObjModThickShrinkwrap)
from .soft_body.func import SB_FUNCTION_ITEMS
from .soft_body.geo_nodes import SB_WEIGHT_GEO_NG_NAME
from .soft_body.operator import (AMH2B_OT_AddSoftBodyWeightTestCalc, AMH2B_OT_FinishSoftBodyWeightCalc,
    AMH2B_OT_DataTransferSBWeight, AMH2B_OT_PresetSoftBody, AMH2B_OT_AddSoftBodySpring, AMH2B_OT_RemoveSoftBodySpring)
from .soft_body.panel import draw_panel_soft_body
from .template import (AMH2B_OT_MakeTailorObjectSearchable, AMH2B_OT_SetupMatSwap)
from .vgroup import (AMH2B_OT_CopyVertexGroupsByPrefix, AMH2B_OT_DeleteVertexGroupsByPrefix,
    AMH2B_OT_SearchFileForAutoVGroups)
from .weight_paint import (AMH2B_OT_GrowPaint, AMH2B_OT_SelectVertexByWeight)

def draw_panel_material(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    layout.separator()
    layout.operator(AMH2B_OT_SwapMatWithFile.bl_idname)
    col = layout.column()
    col.active = not scn.amh2b.mat_exact_name_only
    col.operator(AMH2B_OT_SwapMatInternal.bl_idname)
    layout.prop(scn.amh2b, "mat_active_slot_only")
    layout.prop(scn.amh2b, "mat_exact_name_only")
    col = layout.column()
    col.active = not scn.amh2b.mat_exact_name_only
    col.prop(scn.amh2b, "mat_ignore_autoname")
    col.prop(scn.amh2b, "mat_keep_original_name")
    col.prop(scn.amh2b, "mat_name_delimiter")
    col.prop(scn.amh2b, "mat_name_delimiter_count")

def draw_panel_vertex_group(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    layout.separator()
    layout.operator(AMH2B_OT_SearchFileForAutoVGroups.bl_idname)
    layout.operator(AMH2B_OT_CopyVertexGroupsByPrefix.bl_idname)
    layout.operator(AMH2B_OT_DeleteVertexGroupsByPrefix.bl_idname)
    layout.prop(scn.amh2b, "vg_func_name_prefix")
    layout.prop(scn.amh2b, "vg_swap_autoname_ext")
    layout.prop(scn.amh2b, "vg_create_name_only")

def draw_panel_weight_paint(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    layout.label(text="Vertex Select")
    layout.operator(AMH2B_OT_SelectVertexByWeight.bl_idname)
    box = layout.box()
    box.prop(scn.amh2b, "wp_select_vertex_min_w")
    box.prop(scn.amh2b, "wp_select_vertex_max_w")
    box.prop(scn.amh2b, "wp_select_vertex_deselect")
    layout.label(text="Grow Selection Paint")
    layout.operator(AMH2B_OT_GrowPaint.bl_idname)
    box = layout.box()
    box.prop(scn.amh2b, "wp_grow_paint_iterations")
    box.prop(scn.amh2b, "wp_grow_paint_start_weight")
    box.prop(scn.amh2b, "wp_grow_paint_end_weight")
    box.prop(scn.amh2b, "wp_paint_initial_selection")
    box.prop(scn.amh2b, "wp_tail_fill_enable")
    col = box.column()
    col.active = scn.amh2b.wp_tail_fill_enable
    col.prop(scn.amh2b, "wp_tail_fill_value")
    col.prop(scn.amh2b, "wp_tail_fill_connected")

def draw_panel_eye_lid(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    layout.separator()
    layout.operator(AMH2B_OT_RemoveLidLook.bl_idname)
    layout.operator(AMH2B_OT_AddLidLook.bl_idname)
    box = layout.box()
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

EBLINK_SUB_FUNC_ADD = "EBLINK_SUB_FUNC_ADD"
EBLINK_SUB_FUNC_REMOVE = "EBLINK_SUB_FUNC_REMOVE"
EBLINK_SUB_FUNC_TEMPLATE = "EBLINK_SUB_FUNC_TEMPLATE"
EBLINK_SUB_FUNC_ITEMS = [
    (EBLINK_SUB_FUNC_ADD, "Add", "Add eyeblink track to active object Armature"),
    (EBLINK_SUB_FUNC_REMOVE, "Remove", "Remove eyeblink track from active object Armature"),
    (EBLINK_SUB_FUNC_TEMPLATE, "Template", "Bone name templates, and read/write Eye Blink bone name templates"),
    ]
def draw_panel_eye_blink(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    a = scn.amh2b
    act_ob = context.active_object
    func_grp_box.prop(a, "eblink_sub_func", text="")
    layout.separator()
    if a.eblink_sub_func == EBLINK_SUB_FUNC_ADD:
        layout.operator(AMH2B_OT_AddBlinkTrack.bl_idname)
        box = layout.box()
        box.label(text="Add Options")
        box.prop(a, "eblink_framerate")
        box.prop(a, "eblink_start_frame")
        box.prop(a, "eblink_random_start_frame")
        box.prop(a, "eblink_allow_random_drift")
        box.prop(a, "eblink_frame_count")
        box.prop(a, "eblink_max_count_enable")
        sub = box.column()
        sub.active = a.eblink_max_count_enable
        sub.prop(a, "eblink_max_count")
        sub = box.column()
        sub.active = not a.eblink_blink_period_enable
        sub.prop(a, "eblink_blinks_per_min")
        box.prop(a, "eblink_blink_period_enable")
        sub = box.column()
        sub.active = a.eblink_blink_period_enable
        sub.prop(a, "eblink_blink_period")
        box.prop(a, "eblink_random_period_enable")
        box.prop(a, "eblink_eye_left_enable")
        box.prop(a, "eblink_eye_right_enable")
        if act_ob != None and act_ob.type == 'MESH' and act_ob.data.shape_keys != None:
            box.prop_search(a, "eblink_shapekey_name", act_ob.data.shape_keys, "key_blocks", text="")
        else:
            box.prop(a, "eblink_shapekey_name", text="")
        box = layout.box()
        box.label(text="Basis")
        box.prop(a, "eblink_closing_time")
        box.prop(a, "eblink_closed_time")
        box.prop(a, "eblink_opening_time")
        box = layout.box()
        box.label(text="Random")
        box.prop(a, "eblink_random_closing_time")
        box.prop(a, "eblink_random_closed_time")
        box.prop(a, "eblink_random_opening_time")
    elif a.eblink_sub_func == EBLINK_SUB_FUNC_REMOVE:
        layout.operator(AMH2B_OT_RemoveBlinkTrack.bl_idname)
        box = layout.box()
        box.label(text="Remove Options")
        box.prop(a, "eblink_remove_start_enable")
        sub = box.column()
        sub.active = a.eblink_remove_start_enable
        sub.prop(a, "eblink_remove_start_frame")
        box.prop(a, "eblink_remove_end_enable")
        sub = box.column()
        sub.active = a.eblink_remove_end_enable
        sub.prop(a, "eblink_remove_end_frame")
        box.prop(a, "eblink_remove_left")
        box.prop(a, "eblink_remove_right")
    elif a.eblink_sub_func == EBLINK_SUB_FUNC_TEMPLATE:
        layout.label(text="Template Set/Reset")
        layout.operator(AMH2B_OT_SetEyeOpened.bl_idname)
        layout.operator(AMH2B_OT_ResetEyeOpened.bl_idname)
        layout.operator(AMH2B_OT_SetEyeClosed.bl_idname)
        layout.operator(AMH2B_OT_ResetEyeClosed.bl_idname)
        box = layout.box()
        box.label(text="Template Bone Names")
        if act_ob != None and act_ob.type == 'ARMATURE':
            box.prop_search(a, "eblink_bone_name_left_lower", act_ob.data, "bones")
            box.prop_search(a, "eblink_bone_name_left_upper", act_ob.data, "bones")
            box.prop_search(a, "eblink_bone_name_right_lower", act_ob.data, "bones")
            box.prop_search(a, "eblink_bone_name_right_upper", act_ob.data, "bones")
        else:
            box.prop(a, "eblink_bone_name_left_lower")
            box.prop(a, "eblink_bone_name_left_upper")
            box.prop(a, "eblink_bone_name_right_lower")
            box.prop(a, "eblink_bone_name_right_upper")
        layout.label(text="Template Save/Load")
        layout.operator(AMH2B_OT_SaveBlinkCSV.bl_idname)
        layout.prop(a, "eblink_text_save_name")
        layout.operator(AMH2B_OT_LoadBlinkCSV.bl_idname)
        layout.prop_search(a, "eblink_text_load_name", bpy.data, "texts")

def draw_panel_template(self, context, func_grp_box):
    layout = self.layout
    scn = context.scene
    layout.label(text="Material")
    layout.operator(AMH2B_OT_SetupMatSwap.bl_idname)
    box = layout.box()
    box.prop(scn.amh2b, "temp_active_slot_only")
    box.prop(scn.amh2b, "temp_delimiter")
    box.prop(scn.amh2b, "temp_delim_count")
    layout.label(text="Vertex Group and ShapeKey")
    layout.operator(AMH2B_OT_MakeTailorObjectSearchable.bl_idname)

def draw_panel_shrinkwrap(self, context, func_grp_box):
    scn = context.scene
    layout = self.layout
    layout.operator(AMH2B_OT_CreateObjModDirectionalShrinkwrap.bl_idname)
    layout.operator(AMH2B_OT_CreateObjModDirectionalThickShrinkwrap.bl_idname)
    layout.operator(AMH2B_OT_CreateObjModShrinkwrap.bl_idname)
    layout.operator(AMH2B_OT_CreateObjModThickShrinkwrap.bl_idname)
    layout.prop(scn.amh2b, "nodes_override_create")

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

FUNC_GRP_ANIMATION = "FUNC_GRP_ANIMATION"
FUNC_GRP_ARMATURE = "FUNC_GRP_ARMATURE"
FUNC_GRP_ATTRIBUTES = "FUNC_GRP_ATTRIBUTES"
FUNC_GRP_EYE_BLINK = "FUNC_GRP_EYE_BLINK"
FUNC_GRP_EYE_LID = "FUNC_GRP_EYE_LID"
FUNC_GRP_MAT_SWAP = "FUNC_GRP_MAT_SWAP"
FUNC_GRP_SHAPE_KEY = "FUNC_GRP_SHAPE_KEY"
FUNC_GRP_SHRINKWRAP = "FUNC_GRP_SHRINKWRAP"
FUNC_GRP_SOFT_BODY = "FUNC_GRP_SOFT_BODY"
FUNC_GRP_TEMPLATE = "FUNC_GRP_TEMPLATE"
FUNC_GRP_VERTEX_GROUP = "FUNC_GRP_VERTEX_GROUP"
FUNC_GRP_WEIGHT_PAINT = "FUNC_GRP_WEIGHT_PAINT"
FUNC_GRP_ITEMS = [
    (FUNC_GRP_ANIMATION, "Animation", ""),
    (FUNC_GRP_ARMATURE, "Armature", ""),
    (FUNC_GRP_ATTRIBUTES, "Attributes", ""),
    (FUNC_GRP_EYE_BLINK, "Eye Blink", ""),
    (FUNC_GRP_EYE_LID, "Eye Lid", ""),
    (FUNC_GRP_MAT_SWAP, "Material Swap", ""),
    (FUNC_GRP_SHAPE_KEY, "Shape Key", ""),
    (FUNC_GRP_SHRINKWRAP, "Shrinkwrap", ""),
    (FUNC_GRP_SOFT_BODY, "Soft Body", ""),
    (FUNC_GRP_TEMPLATE, "Template", ""),
    (FUNC_GRP_VERTEX_GROUP, "Vertex Group", ""),
    (FUNC_GRP_WEIGHT_PAINT, "Weight Paint", ""),
    ]

function_group_draw = {
    FUNC_GRP_ANIMATION: draw_panel_animation,
    FUNC_GRP_ARMATURE: draw_panel_armature,
    FUNC_GRP_ATTRIBUTES: draw_panel_attributes,
    FUNC_GRP_EYE_BLINK: draw_panel_eye_blink,
    FUNC_GRP_EYE_LID: draw_panel_eye_lid,
    FUNC_GRP_MAT_SWAP: draw_panel_material,
    FUNC_GRP_SHAPE_KEY: draw_panel_shape_key,
    FUNC_GRP_SHRINKWRAP: draw_panel_shrinkwrap,
    FUNC_GRP_SOFT_BODY: draw_panel_soft_body,
    FUNC_GRP_TEMPLATE: draw_panel_template,
    FUNC_GRP_VERTEX_GROUP: draw_panel_vertex_group,
    FUNC_GRP_WEIGHT_PAINT: draw_panel_weight_paint,
    }
class AMH2B_PT_View3d(Panel):
    bl_label = "AMH2B"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AMH2B"

    def draw(self, context):
        scn = context.scene
        a = scn.amh2b
        layout = self.layout
        box = layout.box()
        box.label(text="Function Group")
        box.prop(a, "function_group", text="")
        func_grp_draw = function_group_draw.get(a.function_group)
        if func_grp_draw != None:
            func_grp_draw(self, context, box)

class AMH2B_PG_ScnAMH2B(PropertyGroup):
    function_group: EnumProperty(name="Function Group", items=FUNC_GRP_ITEMS, description="Type of function to " \
        "perform")
    nodes_override_create: BoolProperty(name="Override Create", description="Geometry Nodes and custom " +
        "Node Groups will be re-created if this option is enabled. When custom Node Groups are " +
        "override created, old Node Groups of the same name are renamed and deprecated", default=False)

    anim_ratchet_frames: IntProperty(name="Frame Count",
        description="Number of times to apply Ratchet Hold, i.e. number of frames to Ratchet Hold", default=1, min=1)
    anim_ratchet_point_object: StringProperty(name="Ratchet Point Object", description="Object which remains " \
        "motionless, in World coordinates, or optionally relative to Ratchet Target Object's location " \
        "(in World coordinates)")
    anim_ratchet_target_object: StringProperty(name="Ratchet Target Object", description="Object with location " \
        "(in World coordinates) which Ratchet Point will 'track' - i.e. Ratchet Point will remain motionless " \
        "relative to Ratchet Target")
    arm_function: EnumProperty(name="Sub-Function Group", description="Armature Sub-Function Group",
        items=ARM_FUNC_ITEMS)
    arm_copy_transforms_selected: BoolProperty(name="Copy Transforms Selected Only", description="Use only " \
        "selected bones, to Copy ALl Transforms")
    arm_copy_transforms_frame_start: IntProperty(name="Copy Transforms Frame Start", description="Add keyframes " \
        "bones starting this frame", min=0, default=1)
    arm_copy_transforms_frame_end: IntProperty(name="Copy Transforms Frame End", description="Add keyframes " \
        "bones ending this frame", min=0, default=250)
    arm_copy_transforms_frame_step: IntProperty(name="Copy Transforms Frame Step", description="Increment this " \
        "many frames between keyframes", min=1, default=1)
    arm_add_layer_index: IntProperty(name="Bone Layer Index", description="Index of Bone Layer assigned to bones " \
        "added to 'target' with Stitch Armature", default=24, min=0, max=31)
    arm_apply_transforms: BoolProperty(name="Apply Transforms", description="Apply all transforms to 'source' " \
        "Armature before joining with 'target' Armature", default=True)
    arm_textblock_name: StringProperty(name="Text Editor Script Name",
        description="Script data-block name in text editor", default="Text")
    arm_use_textblock: BoolProperty(name="Use Custom Text", default=False)
    arm_generic_prefix: StringProperty(name="G Prefix",
        description="Generic prefix for bone rename.\nDefault value is 'G'", default="G")
    arm_script_pose_preset: EnumProperty(name="Script Pose Preset", items=script_pose_preset_items)
    arm_script_pose_reverse: BoolProperty(name="Reverse Order", description="Run Pose Script in reverse order, " \
        "e.g. to undo previous use of Pose Script", default=False)
    arm_stitch_armature_preset: EnumProperty(name="Stitch Armature Preset", items=stitch_armature_preset_items)
    attr_conv_function: EnumProperty(items=ATTR_CONV_FUNC_ITEMS)
    attr_conv_shapekey: StringProperty(name="ShapeKey", description="ShapeKey to convert to Attribute")
    attr_conv_attribute: StringProperty(name="Attribute", description="Attribute to convert to other")
    eblink_sub_func: EnumProperty(name="Sub-Function Group", description="Eyeblink Sub-Function Group",
        items=EBLINK_SUB_FUNC_ITEMS)
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
        description="Instead of using Blinks Per Minute, use time (in seconds) between start of eyeblink and start " \
        "of next eyeblink", default=False)
    eblink_blink_period: FloatProperty(name="Blink Period",
        description="Time, in seconds, between the start of a eyeblink and the start of the next eyeblink",
        default=6, min=0.001)
    eblink_random_period_enable: FloatProperty(name="Period Random",
        description="Add random amount of time, in seconds, between start of one blink and start of next blink",
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
        description="Name of textblock in text editor where eyeblink settings will be written (saved)",
        default="Text")
    eblink_text_load_name: StringProperty(name="Read Text",
        description="Name of textblock in text editor from which eyeblink settings will be read (loaded)",
        default="Text")
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
        description="Ensure that the material name in each material slot is the same before and after swap",
        default=False)
    mat_name_delimiter: StringProperty(name="Delimiter", description="Delimiter between sections of material names " \
        "(MakeHuman uses the colon : )\n : is the default value", default=":")
    mat_name_delimiter_count: IntProperty(name="Delim. Count",
        description="Number of delimiters allowed in name search. Extra delimiters and related name sections will " +
        "be ignored.\nDefault value is 1", default=1, min=0)
    sb_function: EnumProperty(items=SB_FUNCTION_ITEMS, description="Soft Body Function group")
    sb_apply_sk_mix: BoolProperty(name="Apply SK Mix", description="Apply all ShapeKeys instead of deleting all " \
        "ShapeKeys - necessary before applying Geometry Nodes with 'Convert Test Weights' function", default=True)
    sb_add_spring_attrib: StringProperty(name="Connect Position Attribute", description="Name of Attribute with " \
        "Vertex -> Float Vector positions. e.g. Convert a ShapeKey to Attribute, in AMH2B -> Attributes panel")
    sb_weight_geo_modifier: StringProperty(name="Weight GeoNodes Modifier", description="Name of Geometry Nodes " \
        "modifier, from 'Create Weight Test' function, for use with 'Convert Test Weights' function",
        default=SB_WEIGHT_GEO_NG_NAME)
    sb_dt_individual: BoolProperty(name="Transfer Individually", description="Instead of creating a single Data " \
        "Transfer modifier to transfer all vertex groups, create multiple modifiers to transfer individual groups",
        default=False)
    sb_dt_vg_mask: BoolProperty(name="Include Mask", description="Include 'SB-mask' vertex group when creating " \
        "individual data transfer modifiers ", default=True)
    sb_dt_apply_mod: BoolProperty(name="Apply Modifier", description="Apply Data Transfer modifier to object",
        default=True)
    sb_dt_include_goal: BoolProperty(name="Goal", description="Include 'SB-goal'", default=True)
    sb_dt_include_mask: BoolProperty(name="Mask", description="Include 'SB-mask'", default=True)
    sb_dt_include_mass: BoolProperty(name="Mass", description="Include 'SB-mass'", default=True)
    sb_dt_include_spring: BoolProperty(name="Spring", description="Include 'SB-spring'", default=True)
    sb_dt_vert_mapping: bpy.props.EnumProperty(name="Vertex Data Mapping", description="Method used to map source " \
        "vertices to destination ones", items=[
            ("NEAREST", "Nearest Vertex", ""),
            ("TOPOLOGY", "Topology", ""),
            ("EDGE_NEAREST", "Nearest Edge Vertex", ""),
            ("EDGEINTERP_NEAREST", "Nearest Edge Interpolated", ""),
            ("POLY_NEAREST", "Nearest Face Vertex", ""),
            ("POLYINTERP_NEAREST", "Nearest Face Interpolated", ""),
            ("POLYINTERP_VNORPROJ", "Projected Face Interpolated", ""), ])
    sb_dt_goal_vg_name: StringProperty(name="Goal", description="Soft Body Goal vertex group name", default="SB-goal")
    sb_dt_mask_vg_name: StringProperty(name="Mask", description="Mask object modifier vertex group name",
        default="SB-mask")
    sb_dt_mass_vg_name: StringProperty(name="Mass", description="Soft Body Mass vertex group name", default="SB-mass")
    sb_dt_spring_vg_name: StringProperty(name="Spring", description="Soft Body Spring vertex group name",
        default="SB-spring")
    sk_active_function: EnumProperty(name="Function", description="ShapeKey menu active function",
        items=SK_FUNC_ITEMS)
    sk_bind_frame: IntProperty(name="Bind Frame", description="In this frame, modified (after viewport visible " \
        "modifiers are applied) mesh vertices must be in their original locations\nHint: vertex locations in " \
        "OBJECT mode must be same as in EDIT mode.", default=0, min=0)
    sk_start_frame: IntProperty(name="Start Frame", description="Choose first frame of mesh animation to convert " \
        "to Shape Key", default=1, min=0)
    sk_end_frame: IntProperty(name="End Frame", description="Choose last frame of mesh animation to convert to " \
        "Shape Key", default=2, min=0)
    sk_animate: BoolProperty(name="Animate Shape Keys", description="Animate baked Deform Shape Keys by adding " \
        "keyframes to ShapeKey 'Evaluation Time', from 'Start Frame' to 'End Frame'", default=True)
    sk_add_frame_to_name: BoolProperty(name="Add Frame to Name", description="Append frame number to key name " \
        "(e.g. DSKey005, DSKey006)", default=True)
    sk_dynamic: BoolProperty(name="Dynamic", description="Respect armature transformations when calculating " \
        "deform shape keys. Dynamic is slower to run than not-Dynamic", default=True)
    sk_extra_accuracy: IntProperty(name="",
        description="Extra accuracy iterations when baking shape keys with dynamic enabled", default=0, min=0)
    sk_deform_name_prefix: StringProperty(name="Prefix",
        description="Prefix for naming mesh deform shape keys. Default value is " + SC_DSKEY, default=SC_DSKEY)
    sk_adapt_size: BoolProperty(name="Adapt Size",
        description="Adapt size of shape key to size of mesh, per vertex, by ratio of sums of connected edge " +
        "lengths", default=True)
    sk_swap_autoname_ext: BoolProperty(name="Swap Autoname Ext", description="If shapekey copy function is tried " \
        "and fails, re-try swap with objects 'auto-name' extension removed.\ne.g. Object Mass0007:Eyebrow010.003 " \
        "shapekeys may be copied from object Mass0007:Eyebrow010 shapekeys", default=True)
    sk_function_prefix: StringProperty(name="Prefix",
        description="Prefix used in shape key functions. Default value is " + SC_DSKEY, default=SC_DSKEY)
    sk_mask_vgroup_name: StringProperty(name="Mask VGroup",
        description="Name of vertex group to use as a mask when baking shapekeys.\nOptional: Use this feature for " +
        "finer control over which vertexes are used to bake the shapekeys", default="")
    sk_mask_invert: BoolProperty(name="Mask Invert",
        description="If vertex group is given, and 'Invert' is enabled, then only mask vertex group vertexes " +
        "are included when baking shapekey(s).\nIf vertex group is given, and 'Invert' is not enabled, " +
        "then mask vertex group vertexes are excluded when baking shapekey(s)", default=False)
    temp_active_slot_only: BoolProperty(name="Active Slot Only",
        description="Rename only Active Slot material, instead of trying to rename all material slots",
        default=False)
    temp_delimiter: StringProperty(name="Delimiter",
        description="Delimiter between sections of material names (MakeHuman uses the colon : )", default=":")
    temp_delim_count: IntProperty(name="Delim. Count", description="Number of delimiters allowed in " +
        "name search. Extra delimiters and related name sections will be ignored", default=1, min=0)
    vg_func_name_prefix: StringProperty(name="Prefix",
        description="Perform functions on selected MESH type objects, but only vertex groups with names " +
        "beginning with this prefix. Default value is " + SC_VGRP_AUTO_PREFIX, default=SC_VGRP_AUTO_PREFIX)
    vg_swap_autoname_ext: BoolProperty(name="Swap Autoname Ext", description="If vertex group copy function is " \
        "tried and fails, re-try swap with objects 'auto-name' extension removed.\ne.g. Object " \
        "Mass0007:Eyebrow010.003 vertex groups may be copied from object Mass0007:Eyebrow010 vertex groups",
        default=True)
    vg_create_name_only: BoolProperty(name="Create Groups Only in Name",
        description="Create vertex groups 'in name only' when copying", default=False)
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

classes = [
    AMH2B_PG_ScnAMH2B,
    AMH2B_OT_SwapMatWithFile,
    AMH2B_OT_SwapMatInternal,
    AMH2B_OT_SetupMatSwap,
    AMH2B_OT_CopyVertexGroupsByPrefix,
    AMH2B_OT_DeleteVertexGroupsByPrefix,
    AMH2B_OT_MakeTailorObjectSearchable,
    AMH2B_OT_SearchFileForAutoVGroups,
    AMH2B_OT_GrowPaint,
    AMH2B_OT_SelectVertexByWeight,
    AMH2B_OT_BakeDeformShapeKeys,
    AMH2B_OT_ApplyModifierSK,
    AMH2B_OT_SearchFileForAutoShapeKeys,
    AMH2B_OT_SKFuncDelete,
    AMH2B_OT_CopyOtherSK,
    AMH2B_OT_CreateGeoNodesShrinkwrap,
    AMH2B_OT_CreateGeoNodesThickShrinkwrap,
    AMH2B_OT_CreateGeoNodesDirectionalShrinkwrap,
    AMH2B_OT_CreateGeoNodesDirectionalThickShrinkwrap,
    AMH2B_OT_CreateObjModDirectionalShrinkwrap,
    AMH2B_OT_CreateObjModDirectionalThickShrinkwrap,
    AMH2B_OT_CreateObjModShrinkwrap,
    AMH2B_OT_CreateObjModThickShrinkwrap,
    AMH2B_OT_ApplyScale,
    AMH2B_OT_ScriptPose,
    AMH2B_OT_EnableModPreserveVolume,
    AMH2B_OT_DisableModPreserveVolume,
    AMH2B_OT_RenameGeneric,
    AMH2B_OT_UnNameGeneric,
    AMH2B_OT_CleanupGizmos,
    AMH2B_OT_StitchArmature,
    AMH2B_OT_CopyArmatureTransforms,
    AMH2B_OT_RatchetPoint,
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
    AMH2B_OT_RemoveSoftBodySpring,
    AMH2B_OT_AttributeConvert,
    AMH2B_PT_NodeEditorShrinkwrap,
    AMH2B_PT_View3d,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.amh2b = PointerProperty(type=AMH2B_PG_ScnAMH2B)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.amh2b

if __name__ == "__main__":
    register()
