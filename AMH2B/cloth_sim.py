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

import bpy

from .const import *

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"

def do_add_cloth_sim(mesh_obj):
    original_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    mod = mesh_obj.modifiers.new("Cloth", 'CLOTH')
    if mod is None:
        return "Unable to add CLOTH modifier to object" + mesh_obj.name

    mod.settings.use_dynamic_mesh = True

    vert_grp = mesh_obj.vertex_groups.get(SC_VGRP_CLOTH_PIN)
    if vert_grp is not None:
        cloth_sim_use_pin_group(mod, vert_grp.name)

    vert_grp = mesh_obj.vertex_groups.get(SC_VGRP_TSEWN)
    if vert_grp is not None:
        cloth_sim_use_sew_group(mod, vert_grp.name)

    bpy.ops.object.mode_set(mode=original_mode)

    return None

class AMH2B_AddClothSim(bpy.types.Operator):
    """Add CLOTH modifer to active object with settings auto-filled for Pinning"""
    bl_idname = "amh2b.csim_add_sim"
    bl_label = "Add Cloth Sim"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if act_ob is None or act_ob.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}

        err_str = do_add_cloth_sim(act_ob)
        if err_str is None:
            return {'FINISHED'}

        self.report({'ERROR'}, err_str)
        return {'CANCELLED'}
