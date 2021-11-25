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
#   Blender 2.79 - 2.93 Addon
# A set of tools to automate the process of shading/texturing, and animating MakeHuman data imported in Blender.


amh2b_fk_ik_both_none_items = [
    ('BOTH', "Both", "", 1),
    ('FORWARDK', "FK", "", 2),
    ('INVERSEK', "IK", "", 3),
    ('NONE', "None", "", 4),
]
amh2b_src_rig_type_items = [
    ('I_AUTOMATIC', "Automatic", "", 1),
    ('I_MIXAMO_NATIVE_FBX', "Mixamo Native FBX", "", 2),
    ('I_MAKEHUMAN_CMU_MB', "MakeHuman CMU MB", "", 3),
]
amh2b_yes_no_items = [
    ('YES', "Yes", "", 1),
    ('NO', "No", "", 2),
]
