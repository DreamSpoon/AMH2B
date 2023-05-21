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

SB_WEIGHT_GEO_NG_NAME = "SoftBodyWeight Geometry Nodes"

def create_weight_sb_mod_geo_node_group(new_node_group, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name):
    # remove old group inputs and outputs
    new_node_group.inputs.clear()
    new_node_group.outputs.clear()
    # create new group inputs and outputs
    new_node_group.inputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.inputs.new(type='NodeSocketObject', name="Goal Object")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Goal From Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Goal From Max")
    new_input.default_value = 1.000000
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Goal To Min")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketFloat', name="Goal To Max")
    new_node_group.inputs.new(type='NodeSocketObject', name="Mask Object")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Mask From Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Mask From Max")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketObject', name="Mass Object")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Mass From Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Mass From Max")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketFloat', name="Mass To Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Mass To Max")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketObject', name="Spring Object")
    new_node_group.inputs.new(type='NodeSocketFloat', name="Spring From Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Spring From Max")
    new_input.default_value = 1.000000
    new_node_group.inputs.new(type='NodeSocketFloat', name="Spring To Min")
    new_input = new_node_group.inputs.new(type='NodeSocketFloat', name="Spring To Max")
    new_input.default_value = 1.000000
    new_node_group.outputs.new(type='NodeSocketGeometry', name="Geometry")
    new_node_group.outputs.new(type='NodeSocketFloat', name=goal_vg_name)
    new_node_group.outputs.new(type='NodeSocketFloat', name=mask_vg_name)
    new_node_group.outputs.new(type='NodeSocketFloat', name=mass_vg_name)
    new_node_group.outputs.new(type='NodeSocketFloat', name=spring_vg_name)
    tree_nodes = new_node_group.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.location = (529, -725)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Spring Map Range"
    node.location = (529, -470)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[8].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[9].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[10].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[11].default_value = (4.000000, 4.000000, 4.000000)
    new_nodes["Map Range"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Spring Object Info"
    node.location = (529, -882)
    node.transform_space = "ORIGINAL"
    node.inputs[1].default_value = False
    new_nodes["Object Info"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Spring Clamp"
    node.location = (529, -314)
    node.operation = "ADD"
    node.use_clamp = True
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Mass Map Range"
    node.location = (314, -431)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[8].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[9].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[10].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[11].default_value = (4.000000, 4.000000, 4.000000)
    new_nodes["Map Range.001"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.location = (314, -686)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.001"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Mass Object Info"
    node.location = (314, -843)
    node.transform_space = "ORIGINAL"
    node.inputs[1].default_value = False
    new_nodes["Object Info.001"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Mass Clamp"
    node.location = (314, -274)
    node.operation = "ADD"
    node.use_clamp = True
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.001"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.location = (98, -666)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.002"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Mask Object Info"
    node.location = (98, -823)
    node.transform_space = "ORIGINAL"
    node.inputs[1].default_value = False
    new_nodes["Object Info.002"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Mask Map Range"
    node.location = (98, -412)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    node.inputs[3].default_value = 0.000000
    node.inputs[4].default_value = 1.000000
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[8].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[9].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[10].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[11].default_value = (4.000000, 4.000000, 4.000000)
    new_nodes["Map Range.002"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Mask Clamp"
    node.location = (98, -235)
    node.operation = "GREATER_THAN"
    node.use_clamp = True
    node.inputs[1].default_value = 0.500000
    node.inputs[2].default_value = 1.120000
    new_nodes["Math.002"] = node
    # Geometry Proximity
    node = tree_nodes.new(type="GeometryNodeProximity")
    node.location = (-118, -608)
    node.target_element = "FACES"
    new_nodes["Geometry Proximity.003"] = node
    # Object Info
    node = tree_nodes.new(type="GeometryNodeObjectInfo")
    node.label = "Goal Object Info"
    node.location = (-118, -764)
    node.transform_space = "ORIGINAL"
    node.inputs[1].default_value = False
    new_nodes["Object Info.003"] = node
    # Map Range
    node = tree_nodes.new(type="ShaderNodeMapRange")
    node.label = "Goal Map Range"
    node.location = (-118, -353)
    node.clamp = True
    node.data_type = "FLOAT"
    node.interpolation_type = "LINEAR"
    node.inputs[5].default_value = 4.000000
    node.inputs[7].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[8].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[9].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[10].default_value = (1.000000, 1.000000, 1.000000)
    node.inputs[11].default_value = (4.000000, 4.000000, 4.000000)
    new_nodes["Map Range.003"] = node
    # Math
    node = tree_nodes.new(type="ShaderNodeMath")
    node.label = "Goal Clamp"
    node.location = (-118, -196)
    node.operation = "ADD"
    node.use_clamp = True
    node.inputs[1].default_value = 0.000000
    node.inputs[2].default_value = 0.500000
    new_nodes["Math.003"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Spring CapAttr"
    node.location = (529, -137)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Mass CapAttr"
    node.location = (314, -98)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute.001"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Mask CapAttr"
    node.location = (98, -59)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute.002"] = node
    # Capture Attribute
    node = tree_nodes.new(type="GeometryNodeCaptureAttribute")
    node.label = "Goal CapAttr"
    node.location = (-118, -20)
    node.data_type = "FLOAT"
    node.domain = "POINT"
    node.inputs[1].default_value = (0.000000, 0.000000, 0.000000)
    node.inputs[3].default_value = (0.000000, 0.000000, 0.000000, 0.000000)
    node.inputs[4].default_value = False
    node.inputs[5].default_value = 0
    new_nodes["Capture Attribute.003"] = node
    # Group Input
    node = tree_nodes.new(type="NodeGroupInput")
    node.location = (-372, -490)
    new_nodes["Group Input"] = node
    # Group Output
    node = tree_nodes.new(type="NodeGroupOutput")
    node.location = (745, -20)
    new_nodes["Group Output"] = node
    # create links
    tree_links = new_node_group.links
    tree_links.new(new_nodes["Object Info"].outputs[3], new_nodes["Geometry Proximity"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[10], new_nodes["Map Range.001"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[11], new_nodes["Map Range.001"].inputs[2])
    tree_links.new(new_nodes["Math.001"].outputs[0], new_nodes["Capture Attribute.001"].inputs[2])
    tree_links.new(new_nodes["Capture Attribute.001"].outputs[2], new_nodes["Group Output"].inputs[3])
    tree_links.new(new_nodes["Map Range.001"].outputs[0], new_nodes["Math.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[12], new_nodes["Map Range.001"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[13], new_nodes["Map Range.001"].inputs[4])
    tree_links.new(new_nodes["Math"].outputs[0], new_nodes["Capture Attribute"].inputs[2])
    tree_links.new(new_nodes["Geometry Proximity"].outputs[1], new_nodes["Map Range"].inputs[0])
    tree_links.new(new_nodes["Map Range"].outputs[0], new_nodes["Math"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute"].outputs[2], new_nodes["Group Output"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[9], new_nodes["Object Info.001"].inputs[0])
    tree_links.new(new_nodes["Object Info.001"].outputs[3], new_nodes["Geometry Proximity.001"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[14], new_nodes["Object Info"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[15], new_nodes["Map Range"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[16], new_nodes["Map Range"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[17], new_nodes["Map Range"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[18], new_nodes["Map Range"].inputs[4])
    tree_links.new(new_nodes["Geometry Proximity.001"].outputs[1], new_nodes["Map Range.001"].inputs[0])
    tree_links.new(new_nodes["Math.003"].outputs[0], new_nodes["Capture Attribute.003"].inputs[2])
    tree_links.new(new_nodes["Map Range.003"].outputs[0], new_nodes["Math.003"].inputs[0])
    tree_links.new(new_nodes["Object Info.003"].outputs[3], new_nodes["Geometry Proximity.003"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.003"].outputs[1], new_nodes["Map Range.003"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute.003"].outputs[2], new_nodes["Group Output"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[1], new_nodes["Object Info.003"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[2], new_nodes["Map Range.003"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[3], new_nodes["Map Range.003"].inputs[2])
    tree_links.new(new_nodes["Group Input"].outputs[4], new_nodes["Map Range.003"].inputs[3])
    tree_links.new(new_nodes["Group Input"].outputs[5], new_nodes["Map Range.003"].inputs[4])
    tree_links.new(new_nodes["Group Input"].outputs[0], new_nodes["Capture Attribute.003"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute.001"].outputs[0], new_nodes["Capture Attribute"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute"].outputs[0], new_nodes["Group Output"].inputs[0])
    tree_links.new(new_nodes["Math.002"].outputs[0], new_nodes["Capture Attribute.002"].inputs[2])
    tree_links.new(new_nodes["Map Range.002"].outputs[0], new_nodes["Math.002"].inputs[0])
    tree_links.new(new_nodes["Object Info.002"].outputs[3], new_nodes["Geometry Proximity.002"].inputs[0])
    tree_links.new(new_nodes["Geometry Proximity.002"].outputs[1], new_nodes["Map Range.002"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute.003"].outputs[0], new_nodes["Capture Attribute.002"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[6], new_nodes["Object Info.002"].inputs[0])
    tree_links.new(new_nodes["Group Input"].outputs[7], new_nodes["Map Range.002"].inputs[1])
    tree_links.new(new_nodes["Group Input"].outputs[8], new_nodes["Map Range.002"].inputs[2])
    tree_links.new(new_nodes["Capture Attribute.002"].outputs[0], new_nodes["Capture Attribute.001"].inputs[0])
    tree_links.new(new_nodes["Capture Attribute.002"].outputs[2], new_nodes["Group Output"].inputs[2])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False

def set_geo_nodes_mod_inputs(gn_mod, input_list):
    index = 0
    for inp_key in gn_mod.keys():
        if not inp_key.lower().startswith('input') or inp_key.lower().endswith('_attribute_name') or \
            inp_key.lower().endswith('_use_attribute'):
            continue
        try:
            gn_mod[inp_key] = input_list[index]
        except:
            pass
        index += 1

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

def apply_weight_sb_mod_geo_nodes(recv_ob, send_ob, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name):
    geo_nodes_mod = recv_ob.modifiers.new(name=SB_WEIGHT_GEO_NG_NAME, type='NODES')
    if geo_nodes_mod.node_group is None:
        node_group = bpy.data.node_groups.new(name="WeightSoftBodyGeoNodes", type='GeometryNodeTree')
    else:
        # copy ref to node_group, and remove modifier's ref to node_group, so that default values can be
        # populated
        node_group = geo_nodes_mod.node_group
        geo_nodes_mod.node_group = None
    create_weight_sb_mod_geo_node_group(node_group, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name)
    # assign node_group to Geometry Nodes modifier, which will populate modifier's default input
    # values from node_group's default input values
    geo_nodes_mod.node_group = node_group
    # set Geometry Nodes modifier input/output values
    set_geo_nodes_mod_inputs(geo_nodes_mod, (send_ob, 0.005, 0.066667, 1.0, 0.75,
                                             send_ob, 0.000, 0.03,
                                             send_ob, -0.001, 0.066667, 0.75, 1.0,
                                             send_ob, -0.001, 0.066667, 0.2, 1.0) )
    set_geo_nodes_mod_outputs(geo_nodes_mod, (goal_vg_name+"-test", mask_vg_name+"-test", mass_vg_name+"-test",
                                              spring_vg_name+"-test") )

def get_sbw_geo_nodes_mod(ob):
    mods = [ m for m in ob.modifiers if m.name == SB_WEIGHT_GEO_NG_NAME and m.type == 'NODES' ]
    if len(mods) > 0:
        return mods[0]

def create_weight_test_mat_nodes(material, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name):
    tree_nodes = material.node_tree.nodes
    # delete all nodes
    tree_nodes.clear()
    # create nodes
    new_nodes = {}
    # Material Output
    node = tree_nodes.new(type="ShaderNodeOutputMaterial")
    node.location = (470, 314)
    node.target = "ALL"
    new_nodes["Material Output"] = node
    # Emission
    node = tree_nodes.new(type="ShaderNodeEmission")
    node.location = (274, 314)
    node.inputs[1].default_value = 1.000000
    node.inputs[2].default_value = 0.000000
    new_nodes["Emission"] = node
    # ColorRamp
    node = tree_nodes.new(type="ShaderNodeValToRGB")
    node.location = (-20, 314)
    node.color_ramp.color_mode = "RGB"
    node.color_ramp.interpolation = "EASE"
    node.color_ramp.elements.remove(node.color_ramp.elements[0])
    elem = node.color_ramp.elements[0]
    elem.position = 0.000000
    elem.color = (0.000000, 0.000000, 1.000000, 1.000000)
    elem = node.color_ramp.elements.new(0.500000)
    elem.color = (0.000000, 1.000000, 0.000000, 1.000000)
    elem = node.color_ramp.elements.new(1.000000)
    elem.color = (1.000000, 0.000000, 0.000000, 1.000000)
    new_nodes["ColorRamp"] = node
    # Attribute
    node = tree_nodes.new(type="ShaderNodeAttribute")
    node.location = (-333, 98)
    node.attribute_name = mass_vg_name+"-test"
    node.attribute_type = "GEOMETRY"
    new_nodes["Attribute.001"] = node
    # Attribute
    node = tree_nodes.new(type="ShaderNodeAttribute")
    node.location = (-333, -78)
    node.attribute_name = spring_vg_name+"-test"
    node.attribute_type = "GEOMETRY"
    new_nodes["Attribute.002"] = node
    # Attribute
    node = tree_nodes.new(type="ShaderNodeAttribute")
    node.location = (-333, 274)
    node.attribute_name = mask_vg_name+"-test"
    node.attribute_type = "GEOMETRY"
    new_nodes["Attribute.003"] = node
    # Attribute
    node = tree_nodes.new(type="ShaderNodeAttribute")
    node.location = (-333, 451)
    node.attribute_name = goal_vg_name+"-test"
    node.attribute_type = "GEOMETRY"
    new_nodes["Attribute"] = node
    # create links
    tree_links = material.node_tree.links
    tree_links.new(new_nodes["ColorRamp"].outputs[0], new_nodes["Emission"].inputs[0])
    tree_links.new(new_nodes["Emission"].outputs[0], new_nodes["Material Output"].inputs[0])
    tree_links.new(new_nodes["Attribute"].outputs[2], new_nodes["ColorRamp"].inputs[0])
    # deselect all new nodes
    for n in new_nodes.values(): n.select = False
    return new_nodes

def create_weighting_object(context, recv_ob, send_ob, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name):
    # duplicate 'receiver' object
    bpy.ops.object.select_all(action='DESELECT')
    recv_ob.select_set(True)
    context.view_layer.objects.active = recv_ob
    bpy.ops.object.duplicate()
    dup_recv_ob = context.active_object
    # create geo nodes modifier and node group
    apply_weight_sb_mod_geo_nodes(dup_recv_ob, send_ob, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name)
    # add rainbow test material to dup_recv_ob, in new material slot, blue is 0 and red is 1
    bpy.ops.object.material_slot_add()
    weight_test_mat = bpy.data.materials.new(name="WeightTestMat")
    weight_test_mat.use_nodes = True
    create_weight_test_mat_nodes(weight_test_mat, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name)
    dup_recv_ob.material_slots[len(dup_recv_ob.material_slots)-1].material = weight_test_mat
    # hide previous objects
    recv_ob.hide_set(True)
    send_ob.hide_set(True)

class AMH2B_OT_AddSoftBodyWeightTestCalc(bpy.types.Operator):
    bl_description = "Create Soft Body vertex weights test mesh from duplicate of active object. Select two mesh " \
        "objects, first object is 'sender', second object (active object) is 'receiver'. Proximity from surface of " \
        "'sender' to 'receiver' is calculated"
    bl_idname = "amh2b.create_sb_weight_test_calc"
    bl_label = "Create Weight Test"
    bl_options = {'REGISTER', 'UNDO'}

    # returns True if two Objects are selected, one of them is active_object, and both Objects are type MESH
    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        sel_ob = context.selected_objects
        return context.object.mode == 'OBJECT' and len(sel_ob) == 2 and act_ob in sel_ob and \
            len([ob for ob in sel_ob if ob.type == 'MESH']) == 2

    def execute(self, context):
        a = context.scene.amh2b
        act_ob = context.active_object
        sel_ob = context.selected_objects
        create_weighting_object(context, act_ob, sel_ob[0] if sel_ob[0] != act_ob else sel_ob[1],
            a.sb_dt_goal_vg_name, a.sb_dt_mask_vg_name, a.sb_dt_mass_vg_name, a.sb_dt_spring_vg_name)
        return {'FINISHED'}

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

class AMH2B_OT_FinishSoftBodyWeightCalc(bpy.types.Operator):
    bl_description = "With active object, convert test weights into Vertex Groups for use with Soft Body sim and " \
        "'Weight Data Transfer' function. 'Vertex Group Name' section controls names of Vertex Groups used by Soft Body " \
        "weight calculator, and temp Attribute names"
    #"Convert test weights into Vertex Groups to use with Soft Body, and with Weight Data Transfer"
    bl_idname = "amh2b.convert_sb_weight_test_calc"
    bl_label = "Convert Test Weights"
    bl_options = {'REGISTER', 'UNDO'}

    # returns True if active_object exists, is a mesh, and View3D Object mode is the active context
    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        return act_ob != None and act_ob.type == 'MESH' and context.object.mode == 'OBJECT'

    def execute(self, context):
        gn_mod = get_sbw_geo_nodes_mod(context.active_object)
        if gn_mod is None:
            self.report({'ERROR'}, "Active object is missing WeightSoftBody Geometry Nodes")
            return {'CANCELLED'}
        a = context.scene.amh2b
        finish_weighting_object(context, context.active_object, gn_mod, context.scene.amh2b.sb_apply_sk_mix,
            a.sb_dt_goal_vg_name, a.sb_dt_mask_vg_name, a.sb_dt_mass_vg_name, a.sb_dt_spring_vg_name)
        return {'FINISHED'}

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

class AMH2B_OT_DataTransferSBWeight(bpy.types.Operator):
    bl_description = "Transfer Soft Body vertex weight data to active object from other selected object (select " \
        "only two mesh type objects). 'Vertex Group Name' section controls names of Vertex Groups used by Soft Body " \
        "weight calculator, and temp Attribute names"
    bl_idname = "amh2b.sb_weight_data_transfer"
    bl_label = "Transfer Weight Data"
    bl_options = {'REGISTER', 'UNDO'}

    # returns True if two Objects are selected, one of them is active_object, and both Objects are type MESH
    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        sel_ob = context.selected_objects
        return context.object.mode == 'OBJECT' and len(sel_ob) == 2 and act_ob in sel_ob and \
            len([ob for ob in sel_ob if ob.type == 'MESH']) == 2

    def execute(self, context):
        act_ob = context.active_object
        sel_ob = context.selected_objects
        a = context.scene.amh2b
        data_transfer_sb_weights(context, act_ob, sel_ob[0] if sel_ob[0] != act_ob else sel_ob[1],
            a.sb_dt_gen_data_layers, a.sb_dt_vert_mapping, a.sb_dt_individual, a.sb_dt_apply_mod, a.sb_dt_include_goal,
            a.sb_dt_include_mask, a.sb_dt_include_mass, a.sb_dt_include_spring, a.sb_dt_goal_vg_name,
            a.sb_dt_mask_vg_name, a.sb_dt_mass_vg_name, a.sb_dt_spring_vg_name)
        return {'FINISHED'}

def add_sb_modifier(ob):
    pass

def preset_soft_body(context, ob, goal_vg_name, mask_vg_name, mass_vg_name, spring_vg_name):
    existing_mods = [ m for m in ob.modifiers if m.type == 'SOFT_BODY' ]
    # if no soft body modifier exists object then add one
    if len(existing_mods) == 0:
        sb_mod = ob.modifiers.new(name="Softbody", type='SOFT_BODY')
    else:
        sb_mod = existing_mods[0]
    sb_mod.settings.vertex_group_mass = mass_vg_name
    sb_mod.settings.vertex_group_goal = goal_vg_name
    sb_mod.settings.vertex_group_spring = spring_vg_name
    sb_mod.settings.goal_spring = 0.65
    sb_mod.settings.goal_friction = 15.0
    sb_mod.settings.goal_default = 1.0
    sb_mod.settings.pull = 0.6
    sb_mod.settings.push = 0.4
    sb_mod.settings.damping = 5.0
    sb_mod.settings.bend = 1.0
    # create mask modifier for mask Vertex Group if it does not already exist
    existing_mods = [ m for m in ob.modifiers if m.type == 'MASK' and m.vertex_group == mask_vg_name]
    if len(existing_mods) == 0:
        mask_mod = ob.modifiers.new(name="SoftBodyWeight Mask", type='MASK')
        mask_mod.vertex_group = mask_vg_name

class AMH2B_OT_PresetSoftBody(bpy.types.Operator):
    bl_description = "Ensure active object has Soft Body modifier, then autofill Vertex Group names, and use " \
        "preset Soft Body settings"
    bl_idname = "amh2b.preset_soft_body"
    bl_label = "Preset Soft Body"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        return context.object.mode == 'OBJECT' and act_ob != None and act_ob.type == 'MESH'

    def execute(self, context):
        act_ob = context.active_object
        a = context.scene.amh2b
        preset_soft_body(context, act_ob, a.sb_dt_goal_vg_name, a.sb_dt_mask_vg_name, a.sb_dt_mass_vg_name,
            a.sb_dt_spring_vg_name)
        return {'FINISHED'}
