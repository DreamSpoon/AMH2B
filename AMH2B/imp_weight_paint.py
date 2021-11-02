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

SC_TEMP_VGRP_NAME = "TempVGroup"

# iterations must be >= 1
def do_grow_paint(paint_object, paint_vg_index, iterations, start_weight, end_weight, paint_initial_selection,
    tail_fill, tail_fill_value, only_connected):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')

    # apply starting weight paint to only initial selection, if needed
    if paint_initial_selection:
        # switch to group which needs weight paint
        paint_object.vertex_groups.active_index = paint_vg_index
        # paint the group with the "Start Weight"
        bpy.context.scene.tool_settings.vertex_group_weight = start_weight
        bpy.ops.object.vertex_group_assign()

    # create a temp vertex group containing only current selection
    temp_sel_vgrp = paint_object.vertex_groups.new(name=SC_TEMP_VGRP_NAME)
    paint_object.vertex_groups.active_index = temp_sel_vgrp.index
    bpy.context.scene.tool_settings.vertex_group_weight = 1.0
    bpy.ops.object.vertex_group_assign()

    for i in range(iterations):
        # grow selection
        bpy.ops.mesh.select_more()

        # deselect the previous selection, so only the 'select more' vertexes remain selected
        paint_object.vertex_groups.active_index = temp_sel_vgrp.index
        bpy.ops.object.vertex_group_deselect()

        # assign the blended weight paint to only the 'select more' vertexes
        paint_object.vertex_groups.active_index = paint_vg_index

        # if initial selection was painted with start_weight, then then offset weight blend by +1:
        # first iteration gets start_weight blended slightly to end_weight
        vw = start_weight
        if paint_initial_selection:
            vw = (end_weight - start_weight) * (i+1) / iterations + start_weight
        # otherwise, offset weight blend by zero:
        # first iteration gets start_weight
        elif iterations > 1:
            vw = (end_weight - start_weight) * i / (iterations-1) + start_weight

        bpy.context.scene.tool_settings.vertex_group_weight = vw
        bpy.ops.object.vertex_group_assign()

        # add back deselected vertexes, to resume 'grown' selection
        paint_object.vertex_groups.active_index = temp_sel_vgrp.index
        bpy.ops.object.vertex_group_select()
        # add re-selected 'select more' vertexes to the temp group
        bpy.context.scene.tool_settings.vertex_group_weight = 1.0
        bpy.ops.object.vertex_group_assign()

    # if tail fill enabled then set certain remaining vertexes (vertexes not selected yet) to
    # tail fill weight paint value
    if tail_fill:
        if only_connected:
            # from previous code, selection will be at the largest, so keep a copy of selection, ...
            paint_object.vertex_groups.active_index = temp_sel_vgrp.index
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
    paint_object.vertex_groups.remove(temp_sel_vgrp)

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_GrowPaint(bpy.types.Operator):
    """With active object, starting with currently selected vertexes, set weight paint in successive 'rings' by using 'select more' and weight painting only the newly selected vertexes - blending weight paint value by 'select more' iteration"""
    bl_idname = "amh2b.grow_paint"
    bl_label = "Grow Paint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob_act = context.active_object
        if ob_act is None or ob_act.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        vg_ai = context.active_object.vertex_groups.active_index
        if vg_ai < 0:
            self.report({'ERROR'}, "Active object does not have a vertex group")
            return {'CANCELLED'}

        scn = context.scene
        do_grow_paint(ob_act, vg_ai, scn.Amh2bPropGrowPaintIterations, scn.Amh2bPropGrowPaintStartWeight,
            scn.Amh2bPropGrowPaintEndWeight, scn.Amh2bPropPaintInitialSelection, scn.Amh2bPropTailFill,
            scn.Amh2bPropTailFillValue, scn.Amh2bPropTailFillConnected)
        return {'FINISHED'}

def do_select_vertex_by_weight(obj, vert_group_index, min_weight, max_weight, deselect_first):
    old_3dview_mode = bpy.context.object.mode

    if deselect_first:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.object.mode_set(mode='OBJECT')
    verts = [v for v in obj.data.vertices]
    for v in verts:
        actual_grp_list = [g for g in v.groups if g.group == vert_group_index]
        if len(actual_grp_list) < 1:
            continue
        actual_grp = actual_grp_list[0]
        vw = actual_grp.weight
        if vw <= max_weight and vw >= min_weight:
            v.select = True

    bpy.ops.object.mode_set(mode=old_3dview_mode)

class AMH2B_SelectVertexByWeight(bpy.types.Operator):
    """With active object, deselect all vertices (optional), then select only vertices with weights between min_weight and max_weight, inclusive"""
    bl_idname = "amh2b.select_vertex_by_weight"
    bl_label = "Select by Weight"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob_act = context.active_object
        if ob_act is None or ob_act.type != 'MESH':
            self.report({'ERROR'}, "Active object is not MESH type")
            return {'CANCELLED'}
        vg_ai = context.active_object.vertex_groups.active_index
        if vg_ai < 0:
            self.report({'ERROR'}, "Active object does not have a vertex group")
            return {'CANCELLED'}

        scn = context.scene
        do_select_vertex_by_weight(ob_act, vg_ai, scn.Amh2bPropSelectVertexMinW, scn.Amh2bPropSelectVertexMaxW, scn.Amh2bPropSelectVertexDeselect)
        return {'FINISHED'}
