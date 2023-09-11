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

from math import radians

LL_COPY_ROT_CONST_NAME = "LidLookCopyRot"
LL_LIMIT_ROT_CONST_NAME = "LidLookLimitRot"

LL_RIG_MPFB2_DEFAULT = "MPFB2_DEFAULT"
LL_RIG_MHX_IMPORT = "MHX_IMPORT"

LIDLOOK_DATA = [
    {
        "rig_type": LL_RIG_MPFB2_DEFAULT,
        "label": "MPFB2 Default",
        "data": [
            {
                "bone_name": "orbicularis03.L",
                "subtarget": "eye.L",
                "influence": 0.35,
                "min_x": radians(-10.0),
                "max_x": radians(7.0),
                "invert_x": False,
                },
            {
                "bone_name": "orbicularis04.L",
                "subtarget": "eye.L",
                "influence": 0.5,
                "min_x": radians(-10.0),
                "max_x": radians(7.0),
                "invert_x": False,
                },
            {
                "bone_name": "orbicularis03.R",
                "subtarget": "eye.R",
                "influence": 0.35,
                "min_x": radians(-10.0),
                "max_x": radians(7.0),
                "invert_x": False,
                "driver_source": "orbicularis03.L",
                },
            {
                "bone_name": "orbicularis04.R",
                "subtarget": "eye.R",
                "influence": 0.5,
                "min_x": radians(-10.0),
                "max_x": radians(7.0),
                "invert_x": False,
                "driver_source": "orbicularis04.L",
                },
            ],
        },
    {
        "rig_type": LL_RIG_MHX_IMPORT,
        "label": "MHX Import",
        "data": [
            {
                "bone_name": "uplid.L",
                "subtarget": "eye_parent.L",
                "influence": 0.5,
                "min_x": radians(-5.0),
                "max_x": radians(10.0),
                "invert_x": True,
                },
            {
                "bone_name": "lolid.L",
                "subtarget": "eye_parent.L",
                "influence": 0.35,
                "min_x": radians(-14.0),
                "max_x": radians(5.0),
                "invert_x": True,
                },
            {
                "bone_name": "uplid.R",
                "subtarget": "eye_parent.R",
                "influence": 0.5,
                "min_x": radians(-5.0),
                "max_x": radians(10.0),
                "invert_x": True,
                "driver_source": "uplid.L",
                },
            {
                "bone_name": "lolid.R",
                "subtarget": "eye_parent.R",
                "influence": 0.35,
                "min_x": radians(-14.0),
                "max_x": radians(5.0),
                "invert_x": True,
                "driver_source": "lolid.L",
                },
            ],
        },
    ]

def elid_rig_type_items(self, context):
    items = []
    for ll_data in LIDLOOK_DATA:
        rt = ll_data.get("rig_type")
        if rt is None:
            continue
        label = ll_data.get("label")
        desc = ll_data.get("description")
        if label is None:
            label = rt
        if desc is None:
            desc = ""
        items.append( (rt, label, desc) )
    return sorted(items, key = lambda x: x[0]) if len(items) > 0 else [ (" ", "", "") ]

def get_lidlook_data_by_rig_type(elid_rig_type):
    for d in LIDLOOK_DATA:
        if d.get("rig_type") == elid_rig_type:
            return d.get("data")

def add_copy_driver(ob, bone_name, other_bone_name, const_name, attr_list):
    for attr_name in attr_list:
        d = ob.driver_add("pose.bones[\"%s\"].constraints[\"%s\"].%s" % (bone_name, const_name, attr_name))
        if d is None:
            continue
        drv = d.driver
        drv.type = 'AVERAGE'
        v = drv.variables.new()
        v.name = attr_name
        v.type = 'SINGLE_PROP'
        v.targets[0].id_type = 'OBJECT'
        v.targets[0].id = ob
        v.targets[0].transform_space = 'WORLD_SPACE'
        v.targets[0].transform_type = 'LOC_X'
        v.targets[0].rotation_mode = 'AUTO'
        v.targets[0].data_path = "pose.bones[\"%s\"].constraints[\"%s\"].%s" % (other_bone_name, const_name, attr_name)
        drv.expression = attr_name

def add_lid_look(ob, elid_rig_type):
    constraint_data = get_lidlook_data_by_rig_type(elid_rig_type)
    if constraint_data is None:
        return 0
    add_count = 0
    for cd in constraint_data:
        bone_name = cd.get("bone_name")
        if bone_name is None:
            continue
        pose_bone = ob.pose.bones.get(bone_name)
        subtarget = cd.get("subtarget")
        if pose_bone is None or subtarget is None:
            continue
        min_x = cd.get("min_x")
        max_x = cd.get("max_x")
        invert_x = cd.get("invert_x")
        influence = cd.get("influence")
        con_copy = pose_bone.constraints.new(type='COPY_ROTATION')
        con_copy.name = LL_COPY_ROT_CONST_NAME
        con_copy.target = ob
        con_copy.subtarget = subtarget
        con_copy.use_x = True
        con_copy.use_y = False
        con_copy.use_z = False
        if invert_x != None:
            con_copy.invert_x = invert_x
        con_copy.target_space = 'LOCAL'
        con_copy.owner_space = 'LOCAL'
        if influence != None:
            con_copy.influence = influence
        con_limit = pose_bone.constraints.new(type='LIMIT_ROTATION')
        con_limit.name = LL_LIMIT_ROT_CONST_NAME
        con_limit.use_limit_x = True
        if min_x != None:
            con_limit.min_x = min_x
        if max_x != None:
            con_limit.max_x = max_x
        con_limit.owner_space = 'LOCAL'
        driver_src_bone_name = cd.get("driver_source")
        if driver_src_bone_name != None:
            add_copy_driver(ob, pose_bone.name, driver_src_bone_name, LL_COPY_ROT_CONST_NAME, [ 'influence' ] )
            add_copy_driver(ob, pose_bone.name, driver_src_bone_name, LL_LIMIT_ROT_CONST_NAME,
                            [ 'influence', 'min_x', 'max_x' ] )
        add_count += 1
    return add_count

def remove_lid_look(ob, elid_rig_type):
    constraint_data = get_lidlook_data_by_rig_type(elid_rig_type)
    if constraint_data is None:
        return 0
    remove_count = 0
    bone_names_list = []
    for d in constraint_data:
        bone_name = d.get("bone_name")
        if bone_name is None:
            continue
        bone = ob.pose.bones.get(bone_name)
        if bone is None:
            continue
        # get list of bone constraints needing removal
        constraints_to_remove = []
        for con in bone.constraints:
            if con.type == 'COPY_ROTATION' and con.name.startswith(LL_COPY_ROT_CONST_NAME):
                constraints_to_remove.append(con)
            elif con.type == 'LIMIT_ROTATION' and con.name.startswith(LL_LIMIT_ROT_CONST_NAME):
                constraints_to_remove.append(con)
        # remove bone constraints
        for con in constraints_to_remove:
            bone.constraints.remove(con)
        if bone_name not in bone_names_list:
            bone_names_list.append(bone_name)
            remove_count += 1
    return remove_count
