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

bl_info = {
    "name": "PBR",
	"description": "PBR Workflow Tools",
	"author": "Digiography.Studio",
	"version": (2, 5, 1),
    "blender": (2, 80, 0),
	"location": "Properties > Material > PBR Material",
	"wiki_url":    "https://github.com/Digiography/blender_addon_pbr/wiki",
	"tracker_url": "https://github.com/Digiography/blender_addon_pbr/issues",
    "category": "Material",
}

# Imports

import bpy
from bpy.utils import register_class, unregister_class
from . import ds_pbr

# Addon Preferences Panel

class ds_pbr_addon_prefs(bpy.types.AddonPreferences):

    bl_idname = __package__

    option_ao_node : bpy.props.BoolProperty(
        name="Ambient Occlusion",
        description="Add Ambient Occlusion Map via RGB Mix Node",
        default = False
    )
    option_metallic_node : bpy.props.BoolProperty(
        name="Metallic Node",
        description="Add Metallic Node",
        default = False
    )
    option_specular_node : bpy.props.BoolProperty(
        name="Specular Node",
        description="Add Specular Node",
        default = False
    )
    option_relative : bpy.props.BoolProperty(
        name="Relative Paths",
        description="Use Relative Paths for images.",
        default = True
    )
    option_metallic : bpy.props.FloatProperty(
        name = "Metallic",
        description = "Metallic Value",
        default = 0.500,
        min = 0.000,
        max = 1.000
    )        
    option_specular : bpy.props.FloatProperty(
        name = "Specular",
        description = "Specular Value",
        default = 0.500,
        min = 0.000,
        max = 1.000
    )
  
    def draw(self, context):

        layout = self.layout

        layout.label(text='Defaults',icon='PREFERENCES')
        
        layout.prop(self, 'option_relative')
        layout.prop(self, 'option_ao_node')
        layout.prop(self, 'option_metallic_node')
        layout.prop(self, 'option_specular_node')
        layout.prop(self, 'option_metallic')
        layout.prop(self, 'option_specular')

classes = (
    ds_pbr_addon_prefs,
)

def register():

    for cls in classes:
        register_class(cls)

    ds_pbr.register()

def unregister():

    ds_pbr.unregister()

    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":

	register()    