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
	"version": (1, 0, 0),
    "blender": (2, 79, 0),
	"location": "Properties > Material > PBR Material",
	"wiki_url":    "https://github.com/Digiography/blender_addon_pbr/wiki",
	"tracker_url": "https://github.com/Digiography/blender_addon_pbr/issues",
    "category": "Material",
}

import bpy
import os 

from bpy.props import (StringProperty,BoolProperty,IntProperty,FloatProperty,FloatVectorProperty,EnumProperty,PointerProperty,)
from bpy.types import (Panel,Operator,AddonPreferences,PropertyGroup,)

from . import addon_updater_ops

class ds_pbr_nodes_remove(Operator):

    bl_idname = "ds_pbr.nodes_remove"
    bl_label = "Remove Nodes"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout

        mat = context.material or bpy.data.materials.new('Material')
        
        nodes = mat.node_tree.nodes

        for node in nodes:
            nodes.remove(node)

class ds_pbr_auto_textures(Operator):

    bl_idname = "ds_pbr.auto_textures"
    bl_label = "Auto Textures"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout
        mat = context.material
        nodes = mat.node_tree.nodes
        ds_pbr_material_options = context.material.ds_pbr_material_options
        path = ds_pbr_material_options.textures_path

        if (path):

            for filename in os.listdir(path):

                if 'Base_Color' in filename:
                    nodes['ds_pbr_texture_base_color'].image = bpy.data.images.load(path + '/'+ filename)
                elif 'Normal' in filename:
                    nodes['ds_pbr_texture_normal'].image = bpy.data.images.load(path + '/'+ filename)
                elif 'Roughness' in filename:
                    nodes['ds_pbr_texture_roughness'].image = bpy.data.images.load(path + '/'+ filename)

                if (ds_pbr_material_options.option_ao_map == True):

                    if 'Ambient_Occlusion' in filename:
                        nodes['ds_pbr_texture_ao'].image = bpy.data.images.load(path + '/'+ filename)

                if (ds_pbr_material_options.option_metallic_map == True):

                    if 'Metallic' in filename and 'ds_pbr_texture_metallic' in nodes:
                        nodes['ds_pbr_texture_metallic'].image = bpy.data.images.load(path + '/'+ filename)

class ds_pbr_nodes_metallic_roughness(Operator):

    bl_idname = "ds_pbr.nodes_metallic_roughness"
    bl_label = "Metallic/Roughness"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout

        _ds_pbr_material_options = context.material.ds_pbr_material_options

        mat = context.material
        
        nodes = mat.node_tree.nodes

        ds_pbr_nodes_remove.execute(self,context)

        mat_output = nodes.new('ShaderNodeOutputMaterial')
        mat_output.location = 600,0
        mat_output.name='ds_pbr_output'

        node_shader = nodes.new('ShaderNodeBsdfPrincipled')
        node_shader.location = 400,0
        node_shader.name='ds_pbr_shader'

        mat_links = mat.node_tree.links
        
        mat_links.new(node_shader.outputs['BSDF'], mat_output.inputs['Surface'])

        if (_ds_pbr_material_options.option_ao_map == True):

            node_mix=nodes.new('ShaderNodeMixRGB')
            node_mix.location = 200,100
            node_mix.blend_type = 'MULTIPLY'
            node_mix.name='ds_pbr_mix_rgb'
            mat_links.new(node_mix.outputs['Color'], node_shader.inputs['Base Color'])

            node=nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            mat_links.new(node.outputs['Color'], node_mix.inputs['Color1'])
            
            node=nodes.new('ShaderNodeTexImage')
            node.location = 0,0
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_ao'
            mat_links.new(node.outputs['Color'], node_mix.inputs['Color2'])
        
        else:

            node=nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            mat_links.new(node.outputs['Color'], node_shader.inputs['Base Color'])

        if (_ds_pbr_material_options.option_metallic_map == True):

            node=nodes.new('ShaderNodeTexImage')
            node.location = 0,-250
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_metallic'
            mat_links.new(node.outputs['Color'], node_shader.inputs['Metallic'])   

        else:
            
            node_shader.inputs['Metallic'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_metallic

        node_shader.inputs['Specular'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_specular

        node=nodes.new('ShaderNodeTexImage')
        node.location = 0,-500
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_roughness'
        mat_links.new(node.outputs['Color'], node_shader.inputs['Roughness'])   

        node_map=nodes.new('ShaderNodeNormalMap')
        node_map.location = 200,-700
        node_map.name='ds_pbr_normal_map'
        mat_links.new(node_map.outputs['Normal'], node_shader.inputs['Normal'])

        node=nodes.new('ShaderNodeTexImage')
        node.location = 0,-750
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_normal'
        mat_links.new(node.outputs['Color'], node_map.inputs['Color'])

        ds_pbr_auto_textures.execute(self,context)

        return {'FINISHED'}

class ds_pbr_nodes_specular_gloss(Operator):

    bl_idname = "ds_pbr.nodes_specular_gloss"
    bl_label = "Specular/Gloss"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout

        _ds_pbr_material_options = context.material.ds_pbr_material_options

        mat = context.material
        
        nodes = mat.node_tree.nodes

        ds_pbr_nodes_remove.execute(self,context)

        mat_output = nodes.new('ShaderNodeOutputMaterial')
        mat_output.location = 600,0
        mat_output.name='ds_pbr_output'

        node_shader = nodes.new('ShaderNodeBsdfPrincipled')
        node_shader.location = 400,0
        node_shader.name='ds_pbr_shader'

        mat_links = mat.node_tree.links
        
        mat_links.new(node_shader.outputs['BSDF'], mat_output.inputs['Surface'])

        if (_ds_pbr_material_options.option_ao_map == True):

            node_mix=nodes.new('ShaderNodeMixRGB')
            node_mix.location = 200,100
            node_mix.blend_type = 'MULTIPLY'
            node_mix.name='ds_pbr_mix_rgb'
            mat_links.new(node_mix.outputs['Color'], node_shader.inputs['Base Color'])

            node=nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            mat_links.new(node.outputs['Color'], node_mix.inputs['Color1'])
            
            node=nodes.new('ShaderNodeTexImage')
            node.location = 0,0
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_ao'
            mat_links.new(node.outputs['Color'], node_mix.inputs['Color2'])
        
        else:

            node=nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            mat_links.new(node.outputs['Color'], node_shader.inputs['Base Color'])

        node_shader.inputs['Metallic'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_metallic
        node_shader.inputs['Specular'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_specular

        node_invert=nodes.new('ShaderNodeInvert')
        node_invert.location = 200,-450
        node_invert.name='ds_pbr_invert'
        mat_links.new(node_invert.outputs['Color'], node_shader.inputs['Roughness'])

        node=nodes.new('ShaderNodeTexImage')
        node.location = 0,-500
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_roughness'
        mat_links.new(node.outputs['Color'], node_invert.inputs['Color'])   

        node_map=nodes.new('ShaderNodeNormalMap')
        node_map.location = 200,-700
        node_map.name='ds_pbr_normal_map'
        mat_links.new(node_map.outputs['Normal'], node_shader.inputs['Normal'])

        node=nodes.new('ShaderNodeTexImage')
        node.location = 0,-750
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_normal'
        mat_links.new(node.outputs['Color'], node_map.inputs['Color'])

        ds_pbr_auto_textures.execute(self,context)

        return {'FINISHED'}

class ds_pbr_addon_prefs(AddonPreferences):

    bl_idname = __name__

    option_ao_map = BoolProperty(
        name="Ambient Occlussion",
        description="Add Ambient Occlussion Map via RGBMIX Node",
        default = False
    )
    option_metallic_map = BoolProperty(
        name="Metallic Map",
        description="Add Metaliic Map Node",
        default = False
    )
    option_metallic = FloatProperty(
        name = "Metaliic",
        description = "A float property",
        default = 0.500,
        min = 0.000,
        max = 1.000
    )        
    option_specular = FloatProperty(
        name = "Specular",
        description = "A float property",
        default = 0.500,
        min = 0.000,
        max = 1.000
    )
    
    auto_check_update = bpy.props.BoolProperty(
		name = "Auto-check for Update",
		description = "If enabled, auto-check for updates using an interval",
		default = False,
    )
    updater_intrval_months = bpy.props.IntProperty(
		name='Months',
		description = "Number of months between checking for updates",
		default=0,
		min=0
    )
    updater_intrval_days = bpy.props.IntProperty(
		name='Days',
		description = "Number of days between checking for updates",
		default=7,
		min=0,
    )
    updater_intrval_hours = bpy.props.IntProperty(
		name='Hours',
		description = "Number of hours between checking for updates",
		default=0,
		min=0,
		max=23
    )
    updater_intrval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description = "Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59
    )

    def draw(self, context):

        layout = self.layout
        layout.prop(self, 'option_ao_map')
        layout.prop(self, 'option_metallic_map')
        layout.prop(self, 'option_metallic')
        layout.prop(self, 'option_specular')

        addon_updater_ops.update_settings_ui(self,context)

class ds_pbr_material_options(PropertyGroup):

    name = __name__

    def get_option_ao_map(self):
        if "_option_ao_map" not in self:
            self["_option_ao_map"]=bpy.context.user_preferences.addons[__name__].preferences.option_ao_map
        return self["_option_ao_map"]
    def set_option_ao_map(self, value):
        self["_option_ao_map"] = value

    def get_option_metallic_map(self):
        if "_option_metallic_map" not in self:
            self["_option_metallic_map"]=bpy.context.user_preferences.addons[__name__].preferences.option_metallic_map
        return self["_option_metallic_map"]
    def set_option_metallic_map(self, value):
        self["_option_metallic_map"] = value

    option_ao_map = BoolProperty(
        name="Ambient Occlussion",
        description="Add Ambient Occlussion Map via RGBMIX Node",
        get = get_option_ao_map,
        set = set_option_ao_map
    )
    option_metallic_map = BoolProperty(
        name="Metallic Map",
        description="Add Metaliic Map Node",
        get = get_option_metallic_map,
        set = set_option_metallic_map
    )
    textures_path = StringProperty(
            name="Textures Path",
            subtype='FILE_PATH',
    )        

class ds_pbr_material(Panel):

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "PBR Material"
    bl_context = "material"
   
    @classmethod
    def poll(cls, context):
        return (context.material is not None)

    def draw(self, context):

        layout = self.layout

        addon_updater_ops.check_for_update_background(context)

        _ds_pbr_material_options = context.material.ds_pbr_material_options
        mat = context.material or bpy.data.materials.new('Material')
        nodes = mat.node_tree.nodes

        if ('ds_pbr_texture_normal' in nodes):

            layout.label('Textures',icon='IMASEL')

            split = layout.split(0.30)
            split.label('Base Color')
            split.template_ID(nodes['ds_pbr_texture_base_color'], 'image', open='image.open')

            if (_ds_pbr_material_options.option_metallic_map == True):

                if ('ds_pbr_texture_metallic' in nodes):

                    split = layout.split(0.30)
                    split.label('Metallic')
                    split.template_ID(nodes['ds_pbr_texture_metallic'], 'image', open='image.open')

            if (_ds_pbr_material_options.option_ao_map == True):

                if ('ds_pbr_texture_ao' in nodes):

                    split = layout.split(0.30)
                    split.label('Ambient Occulussion')
                    split.template_ID(nodes['ds_pbr_texture_ao'], 'image', open='image.open')

            split = layout.split(0.30)
            split.label('Normal')
            split.template_ID(nodes['ds_pbr_texture_normal'], 'image', open='image.open')

            split = layout.split(0.30)
            split.label('Roughness')
            split.template_ID(nodes['ds_pbr_texture_roughness'], 'image', open='image.open')
        
        layout.label('Auto Textures',icon='IMASEL')
        layout.prop(_ds_pbr_material_options, "textures_path")

        layout.label('Optional Nodes',icon='NODETREE')

        layout.prop(_ds_pbr_material_options, "option_ao_map")
        layout.prop(_ds_pbr_material_options, "option_metallic_map")

        layout.operator("ds_pbr.nodes_metallic_roughness")
        layout.operator("ds_pbr.nodes_specular_gloss")

        layout.separator()
		
        if addon_updater_ops.updater.update_ready == True:
            layout.label("Custom update message", icon="INFO")
        layout.label("")

        addon_updater_ops.update_notice_box_ui(self, context)

def register():

    from bpy.utils import register_class

    addon_updater_ops.register(bl_info)

    register_class(ds_pbr_addon_prefs)
    register_class(ds_pbr_material_options)
    register_class(ds_pbr_nodes_remove)
    register_class(ds_pbr_auto_textures)
    register_class(ds_pbr_nodes_metallic_roughness)
    register_class(ds_pbr_nodes_specular_gloss)
    register_class(ds_pbr_material)

    bpy.types.Material.ds_pbr_material_options = PointerProperty(type=ds_pbr_material_options)

def unregister():

    from bpy.utils import unregister_class

    addon_updater_ops.unregister()

    unregister_class(ds_pbr_addon_prefs)
    unregister_class(ds_pbr_material_options)
    unregister_class(ds_pbr_nodes_remove)
    unregister_class(ds_pbr_auto_textures)
    unregister_class(ds_pbr_nodes_metallic_roughness)
    unregister_class(ds_pbr_nodes_specular_gloss)
    unregister_class(ds_pbr_material)

    del bpy.types.Material.ds_pbr_material_options

if __name__ == "__main__":

    register()