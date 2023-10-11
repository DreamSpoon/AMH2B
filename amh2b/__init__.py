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
# Includes support for MPFB2.

bl_info = {
    "name": "Automate MakeHuman 2 Blender (AMH2B)",
    "description": "Automate process of importing and animating MakeHuman models.",
    "author": "Dave",
    "version": (2, 3, 3),
    "blender": (3, 30, 0),
    "location": "View 3D -> Tools -> AMH2B",
    "doc_url": "https://github.com/DreamSpoon/AMH2B#readme",
    "category": "Import MakeHuman Automation",
}

import bpy
from bpy.types import (Panel, PropertyGroup)
from bpy.props import (BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty)

from .const import (SC_DSKEY, SC_VGRP_AUTO_PREFIX)

from .anim_object.operator import (AMH2B_OT_RatchetPoint, AMH2B_OT_RatchetHold)
from .anim_object.panel import draw_panel_anim_object
from .armature.func import ARM_FUNC_ITEMS
from .armature.operator import (AMH2B_OT_ScriptPose, AMH2B_OT_ApplyScale, AMH2B_OT_EnableModPreserveVolume,
    AMH2B_OT_DisableModPreserveVolume, AMH2B_OT_RenameGeneric, AMH2B_OT_UnNameGeneric, AMH2B_OT_CleanupGizmos,
    AMH2B_OT_RetargetArmature, AMH2B_OT_SnapMHX_FK, AMH2B_OT_SnapMHX_IK, AMH2B_OT_RemoveRetargetConstraints,
    AMH2B_OT_SnapTransferTarget, AMH2B_OT_SelectRetargetBones)
from .armature.panel import draw_panel_armature
from .attributes.panel import draw_panel_attributes
from .attributes.operator import AMH2B_OT_AttributeConvert
from .attributes.func import ATTR_CONV_FUNC_ITEMS
from .eyeblink.panel import (EBLINK_SUB_FUNC_ITEMS, draw_panel_eye_blink)
from .eyeblink.operator import (AMH2B_OT_RemoveBlinkTrack, AMH2B_OT_AddBlinkTrack)
from .eyelid.func import elid_rig_type_items
from .eyelid.operator import (AMH2B_OT_AddLidLook, AMH2B_OT_RemoveLidLook)
from .eyelid.panel import draw_panel_eye_lid
from .shape_key.func import SK_FUNC_ITEMS
from .shape_key.operator import (AMH2B_OT_BakeDeformShapeKeys, AMH2B_OT_SearchFileForAutoShapeKeys,
    AMH2B_OT_SKFuncDelete, AMH2B_OT_CopyOtherSK, AMH2B_OT_ApplyModifierSK)
from .shape_key.panel import draw_panel_shape_key
from .geo_nodes.panel import (AMH2B_PT_NodeEditorGeoNodes, draw_panel_geometry_nodes)
from .geo_nodes.operator import (AMH2B_OT_CreateGeoNodesDirectionalShrinkwrap,
    AMH2B_OT_CreateGeoNodesDirectionalThickShrinkwrap, AMH2B_OT_CreateGeoNodesShrinkwrap,
    AMH2B_OT_CreateGeoNodesThickShrinkwrap, AMH2B_OT_CreateObjModDirectionalShrinkwrap,
    AMH2B_OT_CreateObjModDirectionalThickShrinkwrap, AMH2B_OT_CreateObjModShrinkwrap,
    AMH2B_OT_CreateObjModThickShrinkwrap)
from .soft_body.func import SB_FUNCTION_ITEMS
from .soft_body.geo_nodes import SB_WEIGHT_GEO_NG_NAME
from .soft_body.operator import (AMH2B_OT_AddSoftBodyWeightTestCalc, AMH2B_OT_FinishSoftBodyWeightCalc,
    AMH2B_OT_DataTransferSBWeight, AMH2B_OT_PresetSoftBody, AMH2B_OT_AddSoftBodySpring, AMH2B_OT_RemoveSoftBodySpring)
from .soft_body.panel import draw_panel_soft_body
from .template import AMH2B_OT_MakeObjectSearchable
from .vgroup import (AMH2B_OT_CopyVertexGroupsByPrefix, AMH2B_OT_DeleteVertexGroupsByPrefix,
    AMH2B_OT_SearchFileForAutoVGroups)
from .anim_pose.func import (POSE_FUNC_ITEMS, refresh_pose_action_frame_presets, pose_action_frame_preset_items)
from .anim_pose.list import AMH2B_UL_SelectAction
from .anim_pose.operator import (AMH2B_OT_ActionFrameSaveText, AMH2B_OT_ActionFrameLoadText,
    AMH2B_OT_ActionFrameLoadPreset, AMH2B_OT_ActionFrameSavePreset, AMH2B_OT_RefreshPosePresets,
    AMH2B_OT_ApplyActionFrame, AMH2B_OT_LoadActionScriptMOHO)
from .anim_pose.panel import draw_panel_anim_pose
from .weight_paint import (AMH2B_OT_GrowPaint, AMH2B_OT_SelectVertexByWeight)

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

def draw_panel_template(self, context, func_grp_box):
    layout = self.layout
    layout.label(text="Vertex Group and ShapeKey")
    layout.operator(AMH2B_OT_MakeObjectSearchable.bl_idname)

FUNC_GRP_ANIM_OBJECT = "FUNC_GRP_ANIM_OBJECT"
FUNC_GRP_ANIM_POSE = "FUNC_GRP_ANIM_POSE"
FUNC_GRP_ARMATURE = "FUNC_GRP_ARMATURE"
FUNC_GRP_ATTRIBUTES = "FUNC_GRP_ATTRIBUTES"
FUNC_GRP_EYE_BLINK = "FUNC_GRP_EYE_BLINK"
FUNC_GRP_EYE_LID = "FUNC_GRP_EYE_LID"
FUNC_GRP_GEO_NODES = "FUNC_GRP_GEO_NODES"
FUNC_GRP_SHAPE_KEY = "FUNC_GRP_SHAPE_KEY"
FUNC_GRP_SOFT_BODY = "FUNC_GRP_SOFT_BODY"
FUNC_GRP_TEMPLATE = "FUNC_GRP_TEMPLATE"
FUNC_GRP_VERTEX_GROUP = "FUNC_GRP_VERTEX_GROUP"
FUNC_GRP_WEIGHT_PAINT = "FUNC_GRP_WEIGHT_PAINT"
FUNC_GRP_ITEMS = [
    (FUNC_GRP_ANIM_OBJECT, "Animation - Object", ""),
    (FUNC_GRP_ANIM_POSE, "Animation - Pose", ""),
    (FUNC_GRP_ARMATURE, "Armature", ""),
    (FUNC_GRP_ATTRIBUTES, "Attributes", ""),
    (FUNC_GRP_EYE_BLINK, "Eye Blink", ""),
    (FUNC_GRP_EYE_LID, "Eye Lid", ""),
    (FUNC_GRP_GEO_NODES, "Geometry Nodes", ""),
    (FUNC_GRP_SHAPE_KEY, "Shape Key", ""),
    (FUNC_GRP_SOFT_BODY, "Soft Body", ""),
    (FUNC_GRP_TEMPLATE, "Template", ""),
    (FUNC_GRP_VERTEX_GROUP, "Vertex Group", ""),
    (FUNC_GRP_WEIGHT_PAINT, "Weight Paint", ""),
    ]

function_group_draw = {
    FUNC_GRP_ANIM_OBJECT: draw_panel_anim_object,
    FUNC_GRP_ARMATURE: draw_panel_armature,
    FUNC_GRP_ATTRIBUTES: draw_panel_attributes,
    FUNC_GRP_EYE_BLINK: draw_panel_eye_blink,
    FUNC_GRP_EYE_LID: draw_panel_eye_lid,
    FUNC_GRP_SHAPE_KEY: draw_panel_shape_key,
    FUNC_GRP_GEO_NODES: draw_panel_geometry_nodes,
    FUNC_GRP_SOFT_BODY: draw_panel_soft_body,
    FUNC_GRP_TEMPLATE: draw_panel_template,
    FUNC_GRP_VERTEX_GROUP: draw_panel_vertex_group,
    FUNC_GRP_ANIM_POSE: draw_panel_anim_pose,
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
        "motionless in World Coordinates, or optionally motionless relative to Ratchet Target Object")
    anim_ratchet_target_object: StringProperty(name="Ratchet Target Object (optional)", description="Ratchet Point " \
        "will remain motionless relative to Ratchet Target. Ratchet Target is optional")
    arm_function: EnumProperty(name="Sub-Function Group", description="Armature Sub-Function Group",
        items=ARM_FUNC_ITEMS)
    arm_generic_prefix: StringProperty(name="G Prefix",
        description="Generic prefix for bone rename.\nDefault value is 'G'", default="G")
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
    eblink_frame_rate: FloatProperty(name="Frame Rate", description="Frames per second. " +
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
    eblink_open_action: StringProperty(name="Open Action", description="")
    eblink_close_action: StringProperty(name="Close Action", description="")
    eblink_close_shapekey: StringProperty(name="Close Shapekey", description="")
    eblink_close_shapekey_off: FloatProperty(name="Close Shapekey Off", description="", default=0.0)
    eblink_close_shapekey_on: FloatProperty(name="Close Shapekey On", description="", default=1.0)
    elid_rig_type: EnumProperty(name="Lid Look Rig Type", description="Rig type that will receive Lid Look",
        items=elid_rig_type_items)
    pose_function: EnumProperty(name="Sub-Function Group", description="Pose Sub-Function Group",
        items=POSE_FUNC_ITEMS)
    pose_save_action_frame_text: StringProperty(name="Action Frame Save Text", description="Action F-Curve data " \
        "is saved to this Text, available in Blender's Text editor", default="pose_action")
    pose_load_action_frame_text: StringProperty(name="Action Frame Load Text", description="Action F-Curve data " \
        "is loaded from this Text, available in Blender's Text editor")
    pose_load_mark_asset: BoolProperty(name="Mark Asset", description="Each loaded Action is marked as a Pose " \
        "Asset, for use with Asset Browser", default=False)
    pose_select_action_index: IntProperty()
    pose_action_name_prepend: StringProperty(name="Action Name Prepend", description="This string will be " \
        "prepended to names of Actions. Leave blank to ignore")
    pose_shapekey_name_prepend: StringProperty(name="Shape Key Name Prepend", description="This string will be " \
        "prepended to names of Shape Keys. Leave blank to ignore")
    pose_action_frame_label: StringProperty(name="Pose Label", description="Display name in Pose Preset list",
        default="Pose")
    pose_preset: EnumProperty(name="Pose Preset", description="", items=pose_action_frame_preset_items)
    pose_apply_action: StringProperty(name="Apply Action", description="Name of Action that will be applied to " \
        "Pose of active Armature")
    pose_script_frame_offset: IntProperty(name="Frame Offset", description="Scripted Actions are offset in time by " \
        "'Frame Offset' frames", default=0)
    pose_script_frame_scale: FloatProperty(name="Frame Scale", description="Script frame times are scaled by this " \
        "value", default=1.0)
    pose_script_replace_unknown_action: StringProperty(name="Replace Unknown Action", description="Name of Action to " \
        "use when unknown named Action occurs in script. Leave blank to ignore")
    pose_script_replace_unknown_shapekey: StringProperty(name="Replace Unknown Shape Key", description="Name of " \
        "Shape Key to use when unknown named Shape Key occurs in script. Leave blank to ignore")
    pose_ref_bones_action: StringProperty(name="Size Reference Bones Action", description="'Head' locations for " \
        "Edit Bones in this Action will be saved with selected Actions, for auto-resize reference purposes")
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
    AMH2B_OT_CopyVertexGroupsByPrefix,
    AMH2B_OT_DeleteVertexGroupsByPrefix,
    AMH2B_OT_MakeObjectSearchable,
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
    AMH2B_OT_RetargetArmature,
    AMH2B_OT_SnapMHX_FK,
    AMH2B_OT_SnapMHX_IK,
    AMH2B_OT_RemoveRetargetConstraints,
    AMH2B_OT_SnapTransferTarget,
    AMH2B_OT_SelectRetargetBones,
    AMH2B_OT_RatchetPoint,
    AMH2B_OT_RatchetHold,
    AMH2B_OT_RemoveBlinkTrack,
    AMH2B_OT_AddBlinkTrack,
    AMH2B_OT_AddLidLook,
    AMH2B_OT_RemoveLidLook,
    AMH2B_OT_AddSoftBodyWeightTestCalc,
    AMH2B_OT_FinishSoftBodyWeightCalc,
    AMH2B_OT_DataTransferSBWeight,
    AMH2B_OT_PresetSoftBody,
    AMH2B_OT_AddSoftBodySpring,
    AMH2B_OT_RemoveSoftBodySpring,
    AMH2B_OT_AttributeConvert,
    AMH2B_PT_NodeEditorGeoNodes,
    AMH2B_OT_ActionFrameSaveText,
    AMH2B_OT_ActionFrameLoadText,
    AMH2B_OT_ActionFrameLoadPreset,
    AMH2B_OT_ActionFrameSavePreset,
    AMH2B_OT_RefreshPosePresets,
    AMH2B_OT_ApplyActionFrame,
    AMH2B_OT_LoadActionScriptMOHO,
    AMH2B_UL_SelectAction,
    AMH2B_PT_View3d,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.amh2b = PointerProperty(type=AMH2B_PG_ScnAMH2B)
    bpy.types.Action.select = BoolProperty(name="Select", description="Action selection state", default=False)
    refresh_pose_action_frame_presets()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Action.select
    del bpy.types.Scene.amh2b

if __name__ == "__main__":
    register()
