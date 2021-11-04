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

bl_info = {
    "name": "Automate MakeHuman 2 Blender (AMH2B)",
    "description": "Automate process of importing and animating MakeHuman models.",
    "author": "Dave",
    "version": (1, 2, 3),
    "blender": (2, 80, 0),
    "location": "View 3D -> Tools -> AMH2B",
    "wiki_url": "https://github.com/DreamSpoon/AMH2B#readme",
    "category": "Import MakeHuman Automation",
}

import bpy

from .imp_mesh_mat import *
from .imp_mesh_size import *
from .imp_vgroup import *
from .imp_weight_paint import *
from .imp_cloth_sim import *
from .imp_shape_key import *
from .imp_armature import *
from .imp_animation import *
from .imp_const import *

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

        box = layout.box()
        box.label(text="Swap Material")
        box.operator("amh2b.mat_swap_from_file")
        box.operator("amh2b.mat_swap_int_single")
        box.operator("amh2b.mat_swap_int_multi")

class AMH2B_MeshSize(bpy.types.Panel):
    bl_label = "Mesh Size"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

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

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Functions")
        box.operator("amh2b.vg_copy_from_file")
        box.operator("amh2b.vg_copy_by_prefix")
        box.operator("amh2b.vg_delete_by_prefix")
        box.prop(scn, "Amh2bPropVG_FunctionNamePrefix")
        box = layout.box()
        box.label(text="Auto Mask & Pin Group")
        box.operator("amh2b.vg_make_auto_vgroups")
        box.operator("amh2b.vg_add_maskout_modifier")
        box.operator("amh2b.vg_toggle_auto_maskout")

class AMH2B_WeightPaint(bpy.types.Panel):
    bl_label = "Weight Paint"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

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

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.label(text="ShapeKey Functions")
        box.operator("amh2b.sk_search_file_for_auto_sk")
        box.operator("amh2b.sk_func_copy")
        box.prop(scn, "Amh2bPropSK_AdaptSize")
        box.operator("amh2b.sk_func_delete")
        box.prop(scn, "Amh2bPropSK_FunctionPrefix")
        box = layout.box()
        box.label(text="Bake Deform ShapeKey")
        box.operator("amh2b.sk_bake_deform_shape_keys")
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

class AMH2B_Animation(bpy.types.Panel):
    bl_label = "Animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.label(text="Object Location")
        box.operator("amh2b.anim_ratchet_hold")
        box.prop(scn, "Amh2bPropAnimRatchetFrameCount")

class AMH2B_Template(bpy.types.Panel):
    bl_label = "Template"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Material")
        box.operator("amh2b.temp_setup_mat_swap_single")
        box.operator("amh2b.temp_setup_mat_swap_multi")
        box = layout.box()
        box.label(text="Vertex Group and ShapeKey")
        box.operator("amh2b.temp_make_tailor_object_searchable")

classes = [
    AMH2B_SwapMatWithFile,
    AMH2B_SwapMatIntSingle,
    AMH2B_SwapMatIntMulti,
    AMH2B_SetupMatSwapSingle,
    AMH2B_SetupMatSwapMulti,
    AMH2B_AddCutsMask,
    AMH2B_ToggleViewCutsMask,
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
    AMH2B_RatchetHold,
    AMH2B_MeshMat,
    AMH2B_MeshSize,
    AMH2B_VertexGroup,
    AMH2B_WeightPaint,
    AMH2B_Simulation,
    AMH2B_ShapeKey,
    AMH2B_Armature,
    AMH2B_Animation,
    AMH2B_Template,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bts = bpy.types.Scene
    bp = bpy.props
    bts.Amh2bPropArmTextBlockName = bp.StringProperty(name="Text Editor Script Name",
        description="Script data-block name in text editor", default="Text")
    bts.Amh2bPropSK_BindFrame = bp.IntProperty(name="Bind frame",
        description="Bind vertices in this frame. Choose a frame when mesh vertexes haven't moved from original locations.\nHint: vertex locations in OBJECT mode should be the same as in EDIT mode.", default=0, min=0)
    bts.Amh2bPropSK_StartFrame = bp.IntProperty(name="Start frame",
        description="Choose first frame of mesh animation to convert to Shape Key", default=1, min=0)
    bts.Amh2bPropSK_EndFrame = bp.IntProperty(name="End frame",
        description="Choose last frame of mesh animation to convert to Shape Key", default=2, min=0)
    bts.Amh2bPropSK_Animate = bp.BoolProperty(name="Animate Shape Keys",
        description="Keyframe shape key values to animate frames when Shape Keys were created", default=True)
    bts.Amh2bPropSK_AddFrameToName = bp.BoolProperty(name="Add Frame to Name",
        description="Append frame number to key name (e.g. DSKey005, DSKey006)", default=True)
    bts.Amh2bPropSK_Dynamic = bp.BoolProperty(name="Dynamic",
        description="Respect armature transformations when calculating deform shape keys. Dynamic is slower to run than not-Dynamic", default=True)
    bts.Amh2bPropSK_ExtraAccuracy = bp.IntProperty(name="",
        description="Extra accuracy iterations when baking shape keys with dynamic enabled", default=0, min=0)
    bts.Amh2bPropSK_DeformShapeKeyPrefix = bp.StringProperty(name="Prefix",
        description="Prefix for naming mesh deform shape keys. Default value is "+SC_DSKEY, default=SC_DSKEY)
    bts.Amh2bPropSK_AdaptSize = bp.BoolProperty(name="Adapt Size",
        description="Adapt size of shape key to size of mesh, per vertex, by ratio of sums of connected edge lengths", default=True)
    bts.Amh2bPropSK_FunctionPrefix = bp.StringProperty(name="Prefix",
        description="Prefix use in shape key functions. Default value is "+SC_DSKEY, default=SC_DSKEY)
    bts.Amh2bPropVG_FunctionNamePrefix = bp.StringProperty(name="Prefix",
        description="Perform functions on selected MESH type objects, but only vertex groups with names beginning with this prefix. Default value is "+SC_VGRP_AUTO_PREFIX, default=SC_VGRP_AUTO_PREFIX)
    bts.Amh2bPropWP_SelectVertexMinW = bp.FloatProperty(name="Min Weight",
        description="Minimum weight of vertex to select", default=0.0, min=0.0, max=1.0)
    bts.Amh2bPropWP_SelectVertexMaxW = bp.FloatProperty(name="Max Weight",
        description="Maximum weight of vertex to select", default=1.0, min=0.0, max=1.0)
    bts.Amh2bPropWP_SelectVertexDeselect = bp.BoolProperty(name="Deselect All First",
        description="Deselect all vertexes before selecting by weight", default=True)
    bts.Amh2bPropWP_GrowPaintIterations = bp.IntProperty(name="Iterations",
        description="Number of growth iterations - 'select more' is used each iteration to select more vertexes before applying weight paint", default=1, min=1)
    bts.Amh2bPropWP_GrowPaintStartWeight = bp.FloatProperty(name="Start Weight",
        description="Weight paint value applied to currently selected vertexes", default=1.0, min=0.0, max=1.0)
    bts.Amh2bPropWP_GrowPaintEndWeight = bp.FloatProperty(name="End Weight",
        description="Weight paint value applied to vertexes selected last, in the final iteration", default=0.0, min=0.0, max=1.0)
    bts.Amh2bPropWP_PaintInitialSelection = bp.BoolProperty(name="Paint Initial Selection",
        description="Initial selection will be included when applying weight paints", default=True)
    bts.Amh2bPropWP_TailFill = bp.BoolProperty(name="Tail Fill",
        description="All remaining non-hidden vertexes will have their vertex weight paint values set to tail fill value, after applying weights to vertexes during 'select more' iterations", default=False)
    bts.Amh2bPropWP_TailFillValue = bp.FloatProperty(name="Tail Value",
        description="Weight paint value applied to tail fill vertexes", default=0.0, min=0.0, max=1.0)
    bts.Amh2bPropWP_TailFillConnected = bp.BoolProperty(name="Fill only linked",
        description="Only linked vertexes will be included in the tail fill process", default=True)
    bts.Amh2bPropAnimRatchetFrameCount = bp.IntProperty(name="Frame Count",
        description="Number of times to apply Ratchet Hold, i.e. number of frames to Ratchet Hold", default=1, min=1)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
