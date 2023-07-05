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

import bpy

from .geo_nodes import (REFLECT_PROXIMITY_GEO_NG_NAME, SB_WEIGHT_GEO_NG_NAME, SPRING_CONNECT_VERT_GEO_NG_NAME,
    create_geo_ng_weight_sb, create_weight_sb_mod_geo_node_group, create_spring_connect_mod_geo_node_group,
    create_geo_ng_spring_connect_vert)
from .mat_nodes import create_weight_test_mat_nodes
from ..node_other import ensure_node_group

SB_FUNCTION_WEIGHT = "SB_WEIGHT"
SB_FUNCTION_DATA_TRANSFER = "SB_DATA_TRANSFER"
SB_FUNCTION_SPRING = "SB_SPRING"
SB_FUNCTION_MODIFIER = "SB_MODIFIER"
SB_FUNCTION_ITEMS = [
    (SB_FUNCTION_WEIGHT, "Weight", "Calculate Soft Body vertex group weights"),
    (SB_FUNCTION_DATA_TRANSFER, "Data Transfer", "Transfer Soft Body vertex group weights between Mesh Objects"),
    (SB_FUNCTION_SPRING, "Spring", "Add springs (vertices/edges) to Mesh Object"),
    (SB_FUNCTION_MODIFIER, "Modifier", "Add Soft Body modifier with settings auto-filled"),
    ]

# each element of 'input_list' is dictionary type, using format:
# {
#     "value": x,
#     "use_attribute": True/False,
#     "attribute_name": y,
#     }
def set_geo_nodes_mod_inputs(gn_mod, input_list):
    val_key = None
    use_attr_key = None
    attr_name_key = None
    index = 0
    for mod_key in gn_mod.keys():
        if index >= len(input_list):
            return
        elif not mod_key.lower().startswith('input'):
            if val_key is None and use_attr_key is None and attr_name_key is None:
                continue
        elif mod_key.lower().endswith('_attribute_name'):
            if attr_name_key is None:
                attr_name_key = mod_key
                continue
        elif mod_key.lower().endswith('_use_attribute'):
            if use_attr_key is None:
                use_attr_key = mod_key
                continue
        elif val_key is None:
            val_key = mod_key
            continue
        # set values of inputs to given values from 'input_list', if available
        inp_dict = input_list[index]
        if val_key != None and val_key in gn_mod.keys() and "value" in inp_dict.keys():
            gn_mod[val_key] = inp_dict["value"]
        if use_attr_key != None and use_attr_key in gn_mod.keys() and "use_attribute" in inp_dict.keys():
            gn_mod[use_attr_key] = inp_dict["use_attribute"]
        if attr_name_key != None and attr_name_key in gn_mod.keys() and "attribute_name" in inp_dict.keys():
            gn_mod[attr_name_key] = inp_dict["attribute_name"]
        # increment input element index, and get input thing, if available
        index += 1
        val_key = None
        use_attr_key = None
        attr_name_key = None
        if not mod_key.lower().startswith('input'):
            continue
        elif mod_key.lower().endswith('_attribute_name'):
            attr_name_key = mod_key
        elif mod_key.lower().endswith('_use_attribute'):
            use_attr_key = mod_key
        else:
            val_key = mod_key
    if index >= len(input_list):
        return
    # set values of inputs to given values from 'input_list', if available
    inp_dict = input_list[index]
    if val_key != None and val_key in gn_mod.keys() and "value" in inp_dict.keys():
        gn_mod[val_key] = inp_dict["value"]
    if use_attr_key != None and use_attr_key in gn_mod.keys() and "use_attribute" in inp_dict.keys():
        gn_mod[use_attr_key] = inp_dict["use_attribute"]
    if attr_name_key != None and attr_name_key in gn_mod.keys() and "attribute_name" in inp_dict.keys():
        gn_mod[attr_name_key] = inp_dict["attribute_name"]

def set_geo_nodes_mod_outputs(gn_mod, output_list):
    index = 0
    for outp_key in gn_mod.keys():
        if not outp_key.lower().startswith('output'):
            continue
        try:
            gn_mod[outp_key] = output_list[index]
        except:
            pass
        index += 1

def create_prereq_sb_node_group(node_group_name, node_tree_type):
    if node_tree_type == 'GeometryNodeTree':
        if node_group_name == REFLECT_PROXIMITY_GEO_NG_NAME:
            return create_geo_ng_weight_sb()
        elif node_group_name == SPRING_CONNECT_VERT_GEO_NG_NAME:
            return create_geo_ng_spring_connect_vert()
    # error
    print("Unknown name passed to create_prereq_sb_node_group: " + str(node_group_name))
    return None

def apply_weight_sb_mod_geo_nodes(override_create, recv_ob, send_ob, goal_vg_name, mask_vg_name, mass_vg_name,
                                  spring_vg_name):
    geo_nodes_mod = recv_ob.modifiers.new(name=SB_WEIGHT_GEO_NG_NAME, type='NODES')
    if geo_nodes_mod.node_group is None:
        node_group = bpy.data.node_groups.new(name="WeightSoftBodyGeoNodes", type='GeometryNodeTree')
    else:
        # copy ref to node_group, and remove modifier's ref to node_group, so that default values can be
        # populated
        node_group = geo_nodes_mod.node_group
        geo_nodes_mod.node_group = None

    ensure_node_group(override_create, REFLECT_PROXIMITY_GEO_NG_NAME, 'GeometryNodeTree',
                      create_prereq_sb_node_group)
    create_weight_sb_mod_geo_node_group(node_group)
    # assign node_group to Geometry Nodes modifier, which will populate modifier's default input
    # values from node_group's default input values
    geo_nodes_mod.node_group = node_group
    # set Geometry Nodes modifier input/output values
    gr = 0.61803399
    gr_d20 = gr / 20.0
    gr_d200 = gr / 200.0
    set_geo_nodes_mod_inputs(geo_nodes_mod,
        ({ "value": send_ob }, { "value": gr_d200 }, { "value": gr_d20 }, { "value": 1.0 }, { "value": 0.0 },
         { "value": send_ob }, { "value": 0.0 }, { "value": gr_d200 },
         { "value": send_ob }, { "value": gr_d200 }, { "value": gr_d20 }, { "value": gr }, { "value": 1.0 },
         { "value": send_ob }, { "value": gr_d200 }, { "value": gr_d20 }, { "value": 1.0 }, { "value": gr }) )
    set_geo_nodes_mod_outputs(geo_nodes_mod, (goal_vg_name+"-test", mask_vg_name+"-test", mass_vg_name+"-test",
                                              spring_vg_name+"-test") )

def get_sbw_geo_nodes_mod(ob, sb_weight_geo_modifier):
    mods = [ m for m in ob.modifiers if m.name == sb_weight_geo_modifier and m.type == 'NODES' ]
    if len(mods) > 0:
        return mods[0]

def create_weighting_object(context, override_create, recv_ob, send_ob, goal_vg_name, mask_vg_name, mass_vg_name,
                            spring_vg_name):
    # duplicate 'receiver' object
    bpy.ops.object.select_all(action='DESELECT')
    recv_ob.select_set(True)
    context.view_layer.objects.active = recv_ob
    bpy.ops.object.duplicate()
    dup_recv_ob = context.active_object
    # create geo nodes modifier and node group
    apply_weight_sb_mod_geo_nodes(override_create, dup_recv_ob, send_ob, goal_vg_name, mask_vg_name, mass_vg_name,
                                  spring_vg_name)
    # add rainbow test material to dup_recv_ob, in new material slot, blue is 0 and red is 1
    bpy.ops.object.material_slot_add()
    weight_test_mat = bpy.data.materials.new(name="WeightTestMat")
    weight_test_mat.use_nodes = True
    create_weight_test_mat_nodes(weight_test_mat, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name)
    dup_recv_ob.material_slots[len(dup_recv_ob.material_slots)-1].material = weight_test_mat
    # hide previous objects
    recv_ob.hide_set(True)
    send_ob.hide_set(True)

def create_dup_geo_nodes_mod(ob, gn_mod):
    # get mod list before, so new modifier can be found - because modifier_copy does not return a ref to new modifier
    mod_list_before = [ m for m in ob.modifiers ]
    bpy.ops.object.modifier_copy(modifier=gn_mod.name)
    # compare mod list after to mod list before to get new geo nodes modifier, and return
    mod_diff_list = [ m for m in ob.modifiers if m not in mod_list_before ]
    return mod_diff_list[0] if len(mod_diff_list) > 0 else None

def finish_weighting_object(context, dup_recv_ob, gn_mod, apply_mix, goal_vg_name, mask_vg_name, mass_vg_name,
                            spring_vg_name):
    # select 'duplicate receiver' object
    bpy.ops.object.select_all(action='DESELECT')
    dup_recv_ob.select_set(True)
    context.view_layer.objects.active = dup_recv_ob
    # remove any existing shape_keys on dup_recv_object
    if dup_recv_ob.data.shape_keys != None:
        bpy.ops.object.shape_key_remove(all=True, apply_mix=apply_mix)
    # remove named attributes, if those attributes will be replaced by 'apply geometry nodes'
    remove_attrs = [ dup_recv_ob.data.attributes.get(goal_vg_name+"-test"),
                    dup_recv_ob.data.attributes.get(mask_vg_name+"-test"),
                    dup_recv_ob.data.attributes.get(mass_vg_name+"-test"),
                    dup_recv_ob.data.attributes.get(spring_vg_name+"-test"), ]
    [ dup_recv_ob.data.attributes.remove(named_attr) for named_attr in remove_attrs if named_attr != None ]
    # apply weight calc geo nodes modifier, creating attributes
    dup_geo_nodes_mod = create_dup_geo_nodes_mod(dup_recv_ob, gn_mod)
    if dup_geo_nodes_mod is None:
        return None
    bpy.ops.object.modifier_apply(modifier=dup_geo_nodes_mod.name)
    # remove previous vertex groups that will be replaced by conversion of attributes
    remove_vgroups = [ dup_recv_ob.vertex_groups.get(goal_vg_name),
                      dup_recv_ob.vertex_groups.get(mask_vg_name),
                      dup_recv_ob.vertex_groups.get(mass_vg_name),
                      dup_recv_ob.vertex_groups.get(spring_vg_name), ]
    [ dup_recv_ob.vertex_groups.remove(vg) for vg in remove_vgroups if vg != None ]
    # convert attributes (from geometry nodes) to vertex groups
    dup_recv_ob.data.attributes.active = dup_recv_ob.data.attributes[goal_vg_name+"-test"]
    bpy.ops.geometry.attribute_convert(mode='VERTEX_GROUP')
    dup_recv_ob.data.attributes.active = dup_recv_ob.data.attributes[mask_vg_name+"-test"]
    bpy.ops.geometry.attribute_convert(mode='VERTEX_GROUP')
    dup_recv_ob.data.attributes.active = dup_recv_ob.data.attributes[mass_vg_name+"-test"]
    bpy.ops.geometry.attribute_convert(mode='VERTEX_GROUP')
    dup_recv_ob.data.attributes.active = dup_recv_ob.data.attributes[spring_vg_name+"-test"]
    bpy.ops.geometry.attribute_convert(mode='VERTEX_GROUP')
    # rename vertex groups to final names to be used by Soft Body sim
    dup_recv_ob.vertex_groups[goal_vg_name+"-test"].name = goal_vg_name
    dup_recv_ob.vertex_groups[mask_vg_name+"-test"].name = mask_vg_name
    dup_recv_ob.vertex_groups[mass_vg_name+"-test"].name = mass_vg_name
    dup_recv_ob.vertex_groups[spring_vg_name+"-test"].name = spring_vg_name

def setup_dt_modifier(context, ob, other_ob, vert_mapping, apply_mod, vg_name=None):
    dt_mod = ob.modifiers.new(name="WeightSoftBody Data Transfer", type='DATA_TRANSFER')
    dt_mod.object = other_ob
    dt_mod.use_vert_data = True
    dt_mod.data_types_verts = {'VGROUP_WEIGHTS'}
    dt_mod.vert_mapping = vert_mapping
    dt_mod.layers_vgroup_select_dst = 'NAME'
    if vg_name is None:
        dt_mod.layers_vgroup_select_src = 'ALL'
    else:
        dt_mod.layers_vgroup_select_src = vg_name
    # apply modifier if needed
    if apply_mod:
        context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=dt_mod.name)

def data_transfer_sb_weights(context, ob, other_ob, gen_data_layers, vert_mapping, individual, apply_mod, include_goal,
        include_mask, include_mass, include_spring, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name):
    if individual:
        mod_created = False
        if include_goal and other_ob.vertex_groups.get(goal_vg_name) != None:
            setup_dt_modifier(context, ob, other_ob, vert_mapping, apply_mod, goal_vg_name)
            mod_created = True
        if include_mask and other_ob.vertex_groups.get(mask_vg_name) != None:
            setup_dt_modifier(context, ob, other_ob, vert_mapping, apply_mod, mask_vg_name)
            mod_created = True
        if include_mass and other_ob.vertex_groups.get(mass_vg_name) != None:
            setup_dt_modifier(context, ob, other_ob, vert_mapping, apply_mod, mass_vg_name)
            mod_created = True
        if include_spring and other_ob.vertex_groups.get(spring_vg_name) != None:
            setup_dt_modifier(context, ob, other_ob, vert_mapping, apply_mod, spring_vg_name)
            mod_created = True
        if not mod_created:
            return
    else:
        setup_dt_modifier(context, ob, other_ob, vert_mapping, apply_mod)
    # generate vertex groups on other_ob, if necessary
    if gen_data_layers:
        if ob.vertex_groups.get(goal_vg_name) is None:
            ob.vertex_groups.new(name=goal_vg_name)
        if ob.vertex_groups.get(mask_vg_name) is None:
            ob.vertex_groups.new(name=mask_vg_name)
        if ob.vertex_groups.get(mass_vg_name) is None:
            ob.vertex_groups.new(name=mass_vg_name)
        if ob.vertex_groups.get(spring_vg_name) is None:
            ob.vertex_groups.new(name=spring_vg_name)

def preset_soft_body(ob, goal_vg_name, mass_vg_name, spring_vg_name):
    existing_mods = [ m for m in ob.modifiers if m.type == 'SOFT_BODY' ]
    # if no soft body modifier exists object then add one
    if len(existing_mods) == 0:
        sb_mod = ob.modifiers.new(name="Softbody", type='SOFT_BODY')
    else:
        sb_mod = existing_mods[0]
    sb_mod.settings.vertex_group_mass = mass_vg_name
    sb_mod.settings.vertex_group_goal = goal_vg_name
    sb_mod.settings.vertex_group_spring = spring_vg_name
    sb_mod.settings.mass = 1.61803399
    sb_mod.settings.speed = 1.0
    sb_mod.settings.use_goal = True
    sb_mod.settings.goal_spring = 0.61803399 + 0.061803399
    sb_mod.settings.goal_friction = 50 * 0.61803399
    sb_mod.settings.goal_default = 1.0
    sb_mod.settings.goal_min = 0.0
    sb_mod.settings.goal_max = 1.0
    sb_mod.settings.use_edges = True
    sb_mod.settings.pull = 0.61803399
    sb_mod.settings.push = 0.61803399
    sb_mod.settings.damping = 50 * 0.61803399
    sb_mod.settings.plastic = 0
    sb_mod.settings.bend = 1.61803399 * 1.61803399 * 1.61803399
    sb_mod.settings.spring_length = 95
    sb_mod.settings.use_stiff_quads = False

def add_soft_body_spring(override_create, recv_ob, vertex_attrib_name):
    geo_nodes_mod = recv_ob.modifiers.new(name="SpringConnectVert Geometry Nodes", type='NODES')
    if geo_nodes_mod.node_group is None:
        node_group = bpy.data.node_groups.new(name="SpringConnectGeoNodes", type='GeometryNodeTree')
    else:
        # copy ref to node_group, and remove modifier's ref to node_group, so that default values can be
        # populated
        node_group = geo_nodes_mod.node_group
        geo_nodes_mod.node_group = None

    ensure_node_group(override_create, SPRING_CONNECT_VERT_GEO_NG_NAME, 'GeometryNodeTree',
                      create_prereq_sb_node_group)
    create_spring_connect_mod_geo_node_group(node_group)
    # assign node_group to Geometry Nodes modifier, which will populate modifier's default input
    # values from node_group's default input values
    geo_nodes_mod.node_group = node_group
    connect_d = { "use_attribute": True }
    if vertex_attrib_name != None and vertex_attrib_name != "":
        connect_d["attribute_name"] = vertex_attrib_name
    set_geo_nodes_mod_inputs(geo_nodes_mod, ({}, {}, connect_d ) )
