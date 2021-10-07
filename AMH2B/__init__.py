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
    "version": (1, 1, 9),
    "blender": (2, 80, 0),
    "location": "View 3D &gt; Tools &gt; AMH2B",
    "wiki_url": "https://github.com/DreamSpoon/AMH2B#readme",
    "category": "Import MakeHuman Automation",
}

import bpy

from .imp_mesh_mat import *
from .imp_mesh_sew import *
from .imp_armature import *
from .imp_animation import *

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
        box.operator("amh2b.swap_mat_from_file")
        box.operator("amh2b.swap_mat_int_single")
        box.operator("amh2b.swap_mat_int_multi")
        box = layout.box()
        box.label(text="Setup Material Swap")
        box.operator("amh2b.setup_mat_swap_single")
        box.operator("amh2b.setup_mat_swap_multi")

class AMH2B_MeshSew(bpy.types.Panel):
    bl_label = "Mesh Sew"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Pattern Utility")
        box.operator("amh2b.pattern_copy")
        box.operator("amh2b.pattern_sew")
        box = layout.box()
        box.label(text="Pattern Layout")
        box.operator("amh2b.pattern_add_stitch")
        box = layout.box()
        box.label(text="Cuts and Pins Groups")
        box.operator("amh2b.copy_tailor_groups")
        box.operator("amh2b.make_tailor_groups")

class AMH2B_Armature(bpy.types.Panel):
    bl_label = "Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.operator("amh2b.adjust_pose")
        box.prop(scn, "Amh2bPropTextBlockName")
        box = layout.box()
        box.operator("amh2b.apply_scale")
        box.operator("amh2b.bridge_repose")
        box.operator("amh2b.bone_woven")
        box.label(text="Multi-Function")
        box.operator("amh2b.lucky")

class AMH2B_Animation(bpy.types.Panel):
    bl_label = "Animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "AMH2B"

    def draw(self, context):
        layout = self.layout
        layout.operator("amh2b.ratchet_hold")

classes = [
    AMH2B_SwapMatWithFile,
    AMH2B_SwapMatIntSingle,
    AMH2B_SwapMatIntMulti,
    AMH2B_SetupMatSwapSingle,
    AMH2B_SetupMatSwapMulti,
    AMH2B_PatternAddStitch,
    AMH2B_PatternCopy,
    AMH2B_PatternSew,
    AMH2B_ApplyScale,
    AMH2B_AdjustPose,
    AMH2B_BridgeRepose,
    AMH2B_BoneWoven,
    AMH2B_Lucky,
    AMH2B_RatchetHold,
    AMH2B_MeshMat,
    AMH2B_MeshSew,
    AMH2B_CopyTailorGroups,
    AMH2B_MakeTailorGroups,
    AMH2B_Armature,
    AMH2B_Animation,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.Amh2bPropTextBlockName = bpy.props.StringProperty(name="Text Editor Script Name", description="Script data-block name in text editor", default="Text")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
