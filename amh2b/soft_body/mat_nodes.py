
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
