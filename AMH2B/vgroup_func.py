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

import re

def get_vert_group_indexes(mesh_obj, vert_group_index):
    return [ v.index for v in mesh_obj.data.vertices if vert_group_index in [ vg.group for vg in v.groups ] ]

def add_vertex_group(mesh_obj, grp_name, vert_indexes):
    # create new vertex group
    new_vert_grp = mesh_obj.vertex_groups.new(name=grp_name)
    # add vertex indexes at weight = 1.0
    new_vert_grp.add(vert_indexes, 1.0, 'REPLACE')
    return new_vert_grp

#def add_replace_vertex_grp(mesh_obj, vert_grp_name):
#    delete_vertex_group(mesh_obj, vert_grp_name)
#    add_vertex_group(mesh_obj, vert_grp_name, [])
def add_ifnot_vertex_grp(mesh_obj, vert_grp_name):
    if mesh_obj.vertex_groups.get(vert_grp_name) is None:
        return add_vertex_group(mesh_obj, vert_grp_name, [])

def add_vertex_group_weighted(mesh_obj, grp_name, vert_index_weights):
    # create new vertex group
    new_vert_grp = mesh_obj.vertex_groups.new(name=grp_name)
    # transfer vertex group, with weights
    for viw in vert_index_weights:
        new_vert_grp.add([viw[0]], viw[1], 'REPLACE')

def copy_vertex_group(from_mesh_obj, to_mesh_obj, vert_grp_name):
    from_vert_grp = from_mesh_obj.vertex_groups.get(vert_grp_name)
    if from_vert_grp is None:
        return
    # get vertex indexes in group given by from_vert_grp.index
    vi_list = get_vert_group_indexes(from_mesh_obj, from_vert_grp.index)
    # create new vertex group
    add_vertex_group(to_mesh_obj, from_vert_grp.name, vi_list)

def copy_vertex_group_weighted(from_mesh_obj, to_mesh_obj, vert_grp_name):
    from_vert_grp = from_mesh_obj.vertex_groups.get(vert_grp_name)
    if from_vert_grp is None:
        return
    # get vertex indexes in group given by from_vert_grp.index
    vi_list = get_vert_group_indexes(from_mesh_obj, from_vert_grp.index)
    # create list with weights
    viw_list = []
    for vi in vi_list:
        viw_list.append([vi, from_vert_grp.weight(vi)])
    # create new vertex group
    add_vertex_group_weighted(to_mesh_obj, from_vert_grp.name, viw_list)

def copy_replace_vertex_group(from_mesh_obj, to_mesh_obj, vert_grp_name):
    from_vert_grp = from_mesh_obj.vertex_groups.get(vert_grp_name)
    if from_vert_grp is None:
        return
    delete_vertex_group(to_mesh_obj, vert_grp_name)
    copy_vertex_group(from_mesh_obj, to_mesh_obj, vert_grp_name)

def copy_replace_vertex_group_weighted(from_mesh_obj, to_mesh_obj, vert_grp_name):
    from_vert_grp = from_mesh_obj.vertex_groups.get(vert_grp_name)
    if from_vert_grp is None:
        return
    delete_vertex_group(to_mesh_obj, vert_grp_name)
    copy_vertex_group_weighted(from_mesh_obj, to_mesh_obj, vert_grp_name)

def copy_vgroups_by_name_prefix(obj_src, obj_dest, name_prefix):
    for vgrp in obj_src.vertex_groups:
        if re.match(name_prefix + "\w*", vgrp.name):
            copy_replace_vertex_group_weighted(obj_src, obj_dest, vgrp.name)

def delete_vertex_group(mesh_obj, vert_grp_name):
    vg = mesh_obj.vertex_groups.get(vert_grp_name)
    if vg is not None:
        mesh_obj.vertex_groups.remove(vg)

def delete_vgroups_by_name_prefix(mesh_obj, name_prefix):
    for vgrp in mesh_obj.vertex_groups:
        if re.match(name_prefix + "\w*", vgrp.name):
            delete_vertex_group(mesh_obj, vgrp.name)
