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

from bpy.types import Operator

from .func import (create_weighting_object, get_sbw_geo_nodes_mod, finish_weighting_object, data_transfer_sb_weights,
    preset_soft_body, add_soft_body_spring, remove_soft_body_spring)

class AMH2B_OT_AddSoftBodyWeightTestCalc(Operator):
    """Create Soft Body vertex weights test mesh by duplicating active object. Select two mesh objects, first """ \
        """object is 'sender', second object (active object) is 'receiver'. Proximity from surface of 'sender' """ \
        """to 'receiver' is calculated"""
    bl_idname = "amh2b.create_sb_weight_test_calc"
    bl_label = "Create Weight Test"
    bl_options = {'REGISTER', 'UNDO'}

    # returns True if two Objects are selected, one of them is active_object, and both Objects are type MESH
    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        sel_ob = context.selected_objects
        return act_ob != None and context.mode == 'OBJECT' and len(sel_ob) == 2 and act_ob in sel_ob and \
            len([ob for ob in sel_ob if ob.type == 'MESH']) == 2

    def execute(self, context):
        a = context.scene.amh2b
        act_ob = context.active_object
        sel_ob = context.selected_objects
        create_weighting_object(context, a.nodes_override_create, act_ob, sel_ob[0] if sel_ob[0] != act_ob else sel_ob[1],
            a.sb_dt_goal_vg_name, a.sb_dt_mask_vg_name, a.sb_dt_mass_vg_name, a.sb_dt_spring_vg_name)
        return {'FINISHED'}

class AMH2B_OT_FinishSoftBodyWeightCalc(Operator):
    """With active object, convert test weights into Vertex Groups for use with Soft Body sim and 'Weight Data """ \
        """Transfer' function. 'Vertex Group Name' section controls names of Vertex Groups used by Soft Body """ \
        """weight calculator, and temp Attribute names"""
    #"Convert test weights into Vertex Groups to use with Soft Body, and with Weight Data Transfer"
    bl_idname = "amh2b.convert_sb_weight_test_calc"
    bl_label = "Convert Test Weights"
    bl_options = {'REGISTER', 'UNDO'}

    # returns True if active_object exists, is a mesh, and View3D Object mode is the active context
    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        return act_ob != None and act_ob.type == 'MESH' and context.mode == 'OBJECT'

    def execute(self, context):
        gn_mod = get_sbw_geo_nodes_mod(context.active_object, context.scene.amh2b.sb_weight_geo_modifier)
        if gn_mod is None:
            self.report({'ERROR'}, "Active object is missing WeightSoftBody Geometry Nodes")
            return {'CANCELLED'}
        a = context.scene.amh2b
        finish_weighting_object(context, context.active_object, gn_mod, context.scene.amh2b.sb_apply_sk_mix,
            a.sb_dt_goal_vg_name, a.sb_dt_mask_vg_name, a.sb_dt_mass_vg_name, a.sb_dt_spring_vg_name)
        return {'FINISHED'}

class AMH2B_OT_DataTransferSBWeight(Operator):
    """Transfer Soft Body vertex weight data to active object from other selected object (select only two mesh """ \
        """type objects). 'Vertex Group Name' section controls names of Vertex Groups used by Soft Body weight """ \
        """calculator, and temp Attribute names"""
    bl_idname = "amh2b.sb_weight_data_transfer"
    bl_label = "Transfer Weight Data"
    bl_options = {'REGISTER', 'UNDO'}

    # returns True if two Objects are selected, one of them is active_object, and both Objects are type MESH
    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        sel_ob = context.selected_objects
        return act_ob != None and context.mode == 'OBJECT' and len(sel_ob) == 2 and act_ob in sel_ob and \
            len([ob for ob in sel_ob if ob.type == 'MESH']) == 2

    def execute(self, context):
        act_ob = context.active_object
        sel_ob = context.selected_objects
        a = context.scene.amh2b
        data_transfer_sb_weights(context, act_ob, sel_ob[0] if sel_ob[0] != act_ob else sel_ob[1],
            a.sb_dt_vert_mapping, a.sb_dt_individual, a.sb_dt_apply_mod, a.sb_dt_include_goal, a.sb_dt_include_mask,
            a.sb_dt_include_mass, a.sb_dt_include_spring, a.sb_dt_goal_vg_name, a.sb_dt_mask_vg_name,
            a.sb_dt_mass_vg_name, a.sb_dt_spring_vg_name)
        return {'FINISHED'}

class AMH2B_OT_PresetSoftBody(Operator):
    """Ensure active object has Soft Body modifier, then autofill Vertex Group names, and use preset Soft Body """ \
        """settings. For faster results, set current frame of animation to 0 """
    bl_idname = "amh2b.preset_soft_body"
    bl_label = "Preset Soft Body"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        return act_ob != None and act_ob.type == 'MESH' and context.mode == 'OBJECT'

    def execute(self, context):
        act_ob = context.active_object
        a = context.scene.amh2b
        preset_soft_body(act_ob, a.sb_dt_goal_vg_name, a.sb_dt_mass_vg_name, a.sb_dt_spring_vg_name)
        return {'FINISHED'}

class AMH2B_OT_AddSoftBodySpring(Operator):
    """With active object Mesh, add vertexes/edges to connect Mesh with locations given by Attribute. """ \
        """Optionally, Mesh vertexes can connect with closest point on another object's Mesh - by editing """ \
        """Geometry Nodes tree"""
    bl_idname = "amh2b.add_soft_body_spring"
    bl_label = "Add Springs"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        return act_ob != None and act_ob.type == 'MESH' and context.mode == 'OBJECT'

    def execute(self, context):
        act_ob = context.active_object
        other_sel = [ ob for ob in context.selected_objects if ob != context.active_object ]
        if len(other_sel) == 0:
            other_ob = None
        else:
            other_ob = other_sel[0]
        a = context.scene.amh2b
        add_soft_body_spring(a.nodes_override_create, act_ob, a.sb_add_spring_attrib, other_ob)
        return {'FINISHED'}

class AMH2B_OT_RemoveSoftBodySpring(Operator):
    """With active object and all selected objects Meshes, remove soft body springs by using Mesh Cleanup -> """ \
        """Delete Loose (verts/edges) to remove soft body springs"""
    bl_idname = "amh2b.remove_soft_body_spring"
    bl_label = "Remove Springs"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        act_ob = context.active_object
        return act_ob != None and act_ob.type == 'MESH' and context.mode == 'OBJECT'

    def execute(self, context):
        remove_soft_body_spring(context)
        return {'FINISHED'}
