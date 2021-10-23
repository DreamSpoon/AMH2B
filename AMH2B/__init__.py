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
    "version": (1, 2, 2),
    "blender": (2, 80, 0),
    "location": "View 3D -> Tools -> AMH2B",
    "wiki_url": "https://github.com/DreamSpoon/AMH2B#readme",
    "category": "Import MakeHuman Automation",
}

import bpy

from .imp_mesh_mat import *
from .imp_mesh_sew import *
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
        box.operator("amh2b.swap_mat_from_file")
        box.operator("amh2b.swap_mat_int_single")
        box.operator("amh2b.swap_mat_int_multi")
        box = layout.box()
        box.label(text="Setup Material Swap")
        box.operator("amh2b.setup_mat_swap_single")
        box.operator("amh2b.setup_mat_swap_multi")

class AMH2B_MeshSize(bpy.types.Panel):
    bl_label = "Mesh Size"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout

        #box = layout.box()
        #box.label(text="Pattern Utility")
        #box.operator("amh2b.pattern_copy")
        #box.operator("amh2b.pattern_sew")
        #box = layout.box()
        #box.label(text="Pattern Layout")
        #box.operator("amh2b.pattern_add_stitch")
        box = layout.box()
        box.label(text="Clothing Size")
        box.operator("amh2b.create_size_rig")

class AMH2B_ClothSim(bpy.types.Panel):
    bl_label = "Cloth Sim"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Vertex Group Copy")
        box.operator("amh2b.search_file_for_auto_vgroups")
        box.operator("amh2b.make_tailor_object_searchable")
        box.operator("amh2b.copy_vertex_groups_by_prefix")
        box.prop(scn, "Amh2bPropVGCopyNamePrefix")
        box = layout.box()
        box.label(text="Cut and Pin VGroup Make")
        box.operator("amh2b.make_tailor_groups")
        box.operator("amh2b.add_cuts_mask")
        box = layout.box()
        box.label(text="Cloth Sim")
        box.operator("amh2b.toggle_view_cuts_mask")
        box.operator("amh2b.add_cloth_sim")
        box.operator("amh2b.bake_deform_shape_keys")
        box.prop(scn, "Amh2bPropDeformShapeKeyAddPrefix")
        box.prop(scn, "Amh2bPropDSK_BindFrame")
        box.prop(scn, "Amh2bPropDSK_StartFrame")
        box.prop(scn, "Amh2bPropDSK_EndFrame")
        box.prop(scn, "Amh2bPropDSK_AnimateSK")
        box.operator("amh2b.deform_sk_view_toggle")

class AMH2B_ShapeKey(bpy.types.Panel):
    bl_label = "Shape Key"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Shape Key Functions")
        box.operator("amh2b.sk_func_delete")
        box.operator("amh2b.sk_func_copy")
        box.prop(scn, "Amh2bPropShapeKeyFunctionsPrefix")

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
        box.operator("amh2b.adjust_pose")
        box.prop(scn, "Amh2bPropTextBlockName")
        box.operator("amh2b.apply_scale")
        box.operator("amh2b.bridge_repose")
        box.operator("amh2b.bone_woven")
        box = layout.box()
        box.label(text="Retarget Multi-Function")
        box.operator("amh2b.lucky")

class AMH2B_Animation(bpy.types.Panel):
    bl_label = "Animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Object Location")
        box.operator("amh2b.ratchet_hold")

classes = [
    AMH2B_SwapMatWithFile,
    AMH2B_SwapMatIntSingle,
    AMH2B_SwapMatIntMulti,
    AMH2B_SetupMatSwapSingle,
    AMH2B_SetupMatSwapMulti,
    #AMH2B_PatternAddStitch,
    #AMH2B_PatternCopy,
    #AMH2B_PatternSew,
    AMH2B_AddCutsMask,
    AMH2B_ToggleViewCutsMask,
    AMH2B_CopyVertexGroupsByPrefix,
    AMH2B_MakeTailorGroups,
    AMH2B_MakeTailorObjectSearchable,
    AMH2B_SearchFileForAutoVGroups,
    AMH2B_CreateSizeRig,
    AMH2B_AddClothSim,
    AMH2B_BakeDeformShapeKeys,
    AMH2B_SKFuncDelete,
    AMH2B_SKFuncCopy,
    AMH2B_DeformSK_ViewToggle,
    AMH2B_ApplyScale,
    AMH2B_AdjustPose,
    AMH2B_BridgeRepose,
    AMH2B_BoneWoven,
    AMH2B_Lucky,
    AMH2B_RatchetHold,
    AMH2B_MeshMat,
    AMH2B_MeshSize,
    AMH2B_ClothSim,
    AMH2B_ShapeKey,
    AMH2B_Armature,
    AMH2B_Animation,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.Amh2bPropTextBlockName = bpy.props.StringProperty(name="Text Editor Script Name", description="Script data-block name in text editor", default="Text")
    bpy.types.Scene.Amh2bPropDSK_BindFrame = bpy.props.IntProperty(name="Bind frame", description="Bind vertices in this frame. Choose a frame when mesh vertexes haven't moved from original locations.\nHint: vertex locations in OBJECT mode should be the same as in EDIT mode.", default=0, min=0)
    bpy.types.Scene.Amh2bPropDSK_StartFrame = bpy.props.IntProperty(name="Start frame", description="Choose first frame of mesh animation to convert to Shape Key", default=1, min=0)
    bpy.types.Scene.Amh2bPropDSK_EndFrame = bpy.props.IntProperty(name="End frame", description="Choose last frame of mesh animation to convert to Shape Key", default=2, min=0)
    bpy.types.Scene.Amh2bPropDSK_AnimateSK = bpy.props.BoolProperty(name="Animate Shape Keys", description="Keyframe shape key values to match frames when Shape Keys were created", default=True)
    bpy.types.Scene.Amh2bPropDeformShapeKeyAddPrefix = bpy.props.StringProperty(name="Add Prefix", description="Prefix for naming mesh deform shape keys. Default value is "+SC_DSKEY, default=SC_DSKEY)
    bpy.types.Scene.Amh2bPropShapeKeyFunctionsPrefix = bpy.props.StringProperty(name="Delete Prefix", description="Prefix for shape key functions. Default value is "+SC_DSKEY, default=SC_DSKEY)
    bpy.types.Scene.Amh2bPropVGCopyNamePrefix = bpy.props.StringProperty(name="Prefix", description="Copy from active mesh object, only vertex groups with names beginning with this prefix, to other selected meshes. Default value is "+SC_VGRP_AUTO_PREFIX, default=SC_VGRP_AUTO_PREFIX)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
