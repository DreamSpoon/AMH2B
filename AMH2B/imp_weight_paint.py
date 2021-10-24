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

def do_grow_paint(paint_object, paint_vg_index, iterations, start_weight, end_weight, tail_fill, tail_fill_value):
    old_3dview_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # get and paint currently selected vertexes - ignore hidden verts
    mesh = paint_object.data
    v_list_size = len(mesh.vertices)
    v_selected = numpy.zeros(v_list_size, dtype=numpy.bool8)
    v_sel_indexes = []
    for i in range(v_list_size):
        if mesh.vertices[i].select and not mesh.vertices[i].hide:
            v_selected[i] = True
            v_sel_indexes.append(i)

    paint_vertex_group = paint_object.vertex_groups[paint_vg_index]
    paint_vertex_group.add(v_sel_indexes, start_weight, 'REPLACE')

    # grow selection in increments and apply paint only to the newly selected vertexes
    for iter in range(iterations):
        # grow selection
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_more()
        bpy.ops.object.mode_set(mode='OBJECT')

        # get newly selected verts - ignore hidden verts
        v_sel_indexes = []
        for i in range(v_list_size):
            if mesh.vertices[i].select and not mesh.vertices[i].hide and not v_selected[i]:
                v_selected[i] = True
                v_sel_indexes.append(i)
        # apply weight paint to newly selected verts
        vw = (end_weight - start_weight) * (iter+1) / iterations + start_weight
        paint_vertex_group.add(v_sel_indexes, vw, 'REPLACE')

    # if tail fill enabled then set remaining vertexes (vertexes not selected yet) to tail fill weight paint value
    if tail_fill:
        tail_vsel_indexes = [v.index for v in mesh.vertices if not v.select and not v.hide]
        paint_object.vertex_groups[paint_vg_index].add(tail_vsel_indexes, tail_fill_value, 'REPLACE')

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

        do_grow_paint(ob_act, vg_ai, context.scene.Amh2bPropGrowPaintIterations, context.scene.Amh2bPropGrowPaintStartWeight, context.scene.Amh2bPropGrowPaintEndWeight, context.scene.Amh2bPropTailFill, context.scene.Amh2bPropTailFillValue)
        return {'FINISHED'}
