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

# duplicate selected objects, return active object afterwards
def dup_selected():
    bpy.ops.object.duplicate(linked=False)
    return bpy.context.active_object

def check_create_basis_shape_key(obj):
    if obj.data.shape_keys is None:
        sk_basis = obj.shape_key_add(name='Basis')
        sk_basis.interpolation = 'KEY_LINEAR'

def delete_all_objects_except(except_objects):
    # save a temp copy of list of all objects, because some objects will be deleted
    all_objs_current = [ ob for ob in bpy.data.objects ]
    bpy.ops.object.select_all(action='DESELECT')
    for delete_obj in (ob for ob in all_objs_current if ob not in except_objects):
        # un-hide
        delete_obj.hide_set(False)
        delete_obj.hide_select = False
        # select for deletion
        delete_obj.select_set(True)
    # delete all except the given "except objects"
    bpy.ops.object.delete()

def add_armature_to_objects(arm_obj, objs_list):
    for dest_obj in objs_list:
        if dest_obj != arm_obj and dest_obj.type != 'ARMATURE':
            add_armature_to_obj(arm_obj, dest_obj)

def add_armature_to_obj(arm_obj, dest_obj):
    # create ARMATURE modifier and set refs, etc.
    mod = dest_obj.modifiers.new("ReposeArmature", 'ARMATURE')
    if mod is None:
        print("Error: Unable to add armature to object" + dest_obj.name)
        return

    mod.object = arm_obj
    mod.use_deform_preserve_volume = True
    # Move modifier to top of stack, because this armature needs to move the mesh before
    # any other modifications occur, to match the re-posed main armature.
    while dest_obj.modifiers.find(mod.name) != 0:
        bpy.ops.object.modifier_move_up({"object": dest_obj}, modifier=mod.name)

def get_scene_user_collection(scene, users_collection):
    for coll in users_collection:
        if coll == scene.collection or coll in scene.collection.children_recursive:
            return coll

def is_object_in_sub_collection(ob, coll):
    # is 'ob' in any sub-collections?
    for cr_coll in coll.children_recursive:
        if ob.name in [ i.name for i in cr_coll.objects]:
            return True
    return False

def get_objects_using_armature(arm_ob):
    ob_list = []
    for ob in bpy.data.objects:
        for mod in ob.modifiers:
            if mod.type != 'ARMATURE' or mod.object != arm_ob:
                continue
            ob_list.append(ob)
            break
    return ob_list
