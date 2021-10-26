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

SC_VGRP_AUTO_PREFIX = "Auto"

# tailor Stitch
SC_VGRP_ASTITCH = SC_VGRP_AUTO_PREFIX+"Stch"
SC_VGRP_TSEWN = SC_VGRP_AUTO_PREFIX+"ClothSew"
SC_MN_ASTITCH = "AStitch"

# tailor Cuts and Pins
SC_VGRP_CUTS = SC_VGRP_AUTO_PREFIX+"MaskOut"
SC_VGRP_PINS = SC_VGRP_AUTO_PREFIX+"ClothPin"

# Deform Shape Keys match distance
FC_MATCH_DIST = 0.00001
# Deform Shape Key default name prefix
SC_DSKEY = "DSKey"

SC_TEMP_SK_X = "TempSK_X"
SC_TEMP_SK_Y = "TempSK_Y"
SC_TEMP_SK_Z = "TempSK_Z"
