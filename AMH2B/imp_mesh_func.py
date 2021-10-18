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

def make_mesh_line(mesh_name, vert_pos_a, vert_pos_b):
    mesh_m = bpy.data.meshes.new("mesh")
    mesh_obj = bpy.data.objects.new(mesh_name, mesh_m)

    link_object(mesh_obj)
    set_active_object(mesh_obj)
    select_object(mesh_obj)

    bm = bmesh.new()

    # add the vertices and create an edge between them
    new_v_a = bm.verts.new(vert_pos_a)
    new_v_b = bm.verts.new(vert_pos_b)
    bm.edges.new((new_v_a, new_v_b))

    # finish up, write the bmesh back to the mesh
    bm.to_mesh(mesh_m)
    # free and prevent further access
    bm.free()

    deselect_object(mesh_obj)

    return (new_v_a, new_v_b)

def make_mesh_edge(mesh_obj, vert_indexes):
    if len(vert_indexes) != 2:
        print("do_make_sew_pattern() error: stitch must be between 2 vertexes, not " + str(len(vert_indexes)))
        return

    bm = bmesh.from_edit_mesh(mesh_obj.data)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()

    bm.edges.new((bm.verts[vert_indexes[0]], bm.verts[vert_indexes[1]]))
