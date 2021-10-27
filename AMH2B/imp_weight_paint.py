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

import bpy
import numpy

SC_TEMP_VGRP_NAME = "TempVGroup"

def do_grow_paint(paint_object, paint_vg_index, iterations, start_weight, end_weight, tail_fill, tail_fill_value,
    only_connected):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='EDIT')

    #mesh = paint_object.data
    #paint_vertex_group = paint_object.vertex_groups[paint_vg_index]

    # create a temp vertex group containing only current selection
    temp_vgrp_a = paint_object.vertex_groups.new(name=SC_TEMP_VGRP_NAME)
    paint_object.vertex_groups.active_index = temp_vgrp_a.index
    bpy.context.scene.tool_settings.vertex_group_weight = 1.0
    bpy.ops.object.vertex_group_assign()

    # create a second group, to allow for "leap-frogging" of new selection
    temp_vgrp_b = paint_object.vertex_groups.new(name=SC_TEMP_VGRP_NAME)

    # apply starting weihgt paint to only initial selection
    paint_object.vertex_groups.active_index = paint_vg_index
    bpy.context.scene.tool_settings.vertex_group_weight = start_weight
    bpy.ops.object.vertex_group_assign()

    # switch back to temp group
    paint_object.vertex_groups.active_index = temp_vgrp_a.index
    temp_flip = False
    for iter in range(iterations):
        # grow selection
        bpy.ops.mesh.select_more()

        # assign grown selection to vertex group X
        if temp_flip:
            paint_object.vertex_groups.active_index = temp_vgrp_a.index
        else:
            paint_object.vertex_groups.active_index = temp_vgrp_b.index
        bpy.context.scene.tool_settings.vertex_group_weight = 1.0
        bpy.ops.object.vertex_group_assign()

        # deselect group Y, so total selection will contain only extra vertexes from "select more" operation
        if temp_flip:
            paint_object.vertex_groups.active_index = temp_vgrp_b.index
        else:
            paint_object.vertex_groups.active_index = temp_vgrp_a.index
        bpy.ops.object.vertex_group_deselect()

        # assign the blended weight paint to only the extra selected vertexes
        paint_object.vertex_groups.active_index = paint_vg_index
        vw = (end_weight - start_weight) * (iter+1) / iterations + start_weight
        bpy.context.scene.tool_settings.vertex_group_weight = vw
        bpy.ops.object.vertex_group_assign()

        # return to larger selection
        if temp_flip:
            paint_object.vertex_groups.active_index = temp_vgrp_a.index
        else:
            paint_object.vertex_groups.active_index = temp_vgrp_b.index
        bpy.ops.object.vertex_group_select()

        temp_flip = not temp_flip

    # if tail fill enabled then set certain remaining vertexes (vertexes not selected yet) to
    # tail fill weight paint value
    if tail_fill:
        if only_connected:
            # from previous code, selection will be at the largest, so keep a copy of selection, ...
            paint_object.vertex_groups.active_index = temp_vgrp_a.index
            bpy.context.scene.tool_settings.vertex_group_weight = 1.0
            bpy.ops.object.vertex_group_assign()
            # select all connect verts, ...
            bpy.ops.mesh.select_linked(delimit=set())
            # and deselect the previous largest selection to assign paint to verts that are linked, and not yet painted
            bpy.ops.object.vertex_group_deselect()
        else:
            bpy.ops.mesh.select_all(action='INVERT')

        paint_object.vertex_groups.active_index = paint_vg_index
        bpy.context.scene.tool_settings.vertex_group_weight = tail_fill_value
        bpy.ops.object.vertex_group_assign()

    paint_object.vertex_groups.active_index = paint_vg_index
    paint_object.vertex_groups.remove(temp_vgrp_a)
    paint_object.vertex_groups.remove(temp_vgrp_b)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_GrowPaint(bpy.types.Operator):
    """With active object, starting with currently selected vertexes, set weight paint in successive 'rings' by using 'select more' and weight painting only the newly selected vertexes - blending weight paint value by 'select more' iteration"""
    bl_idname = "amh2b.grow_paint"
    bl_label = "Grow Paint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob_act = context.active_object
        if ob_act is None or ob_act.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}
        vg_ai = context.active_object.vertex_groups.active_index
        if vg_ai < 0:
            self.report({'ERROR'}, "Active object does not have a vertex group")
            return {'CANCELLED'}

        scn = context.scene
        do_grow_paint(ob_act, vg_ai, scn.Amh2bPropGrowPaintIterations, scn.Amh2bPropGrowPaintStartWeight,
            scn.Amh2bPropGrowPaintEndWeight, scn.Amh2bPropTailFill, scn.Amh2bPropTailFillValue, scn.Amh2bPropTailFillConnected)
        return {'FINISHED'}
