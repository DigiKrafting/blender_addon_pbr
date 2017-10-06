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
	"version": (1, 2, 0),
    "blender": (2, 79, 0),
	"location": "Properties > Material > PBR Material",
	"wiki_url":    "https://github.com/Digiography/blender_addon_pbr/wiki",
	"tracker_url": "https://github.com/Digiography/blender_addon_pbr/issues",
    "category": "Material",
}

import bpy

from bpy.props import (StringProperty,BoolProperty,IntProperty,FloatProperty,FloatVectorProperty,EnumProperty,PointerProperty,)
from bpy.types import (Panel,Operator,AddonPreferences,PropertyGroup,)

from  os import (listdir,path)

class ds_pbr_nodes_remove(Operator):

    bl_idname = "ds_pbr.nodes_remove"
    bl_label = "Remove Nodes"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout

        _material = context.material

        if _material and _material.node_tree:

            _nodes = _material.node_tree.nodes

            for node in _nodes:
                _nodes.remove(node)

class ds_pbr_auto_textures(Operator):

    bl_idname = "ds_pbr.auto_textures"
    bl_label = "Auto Textures"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout
        _material = context.material
        _nodes = _material.node_tree.nodes
        _ds_pbr_material_options = context.material.ds_pbr_material_options
        _path = _ds_pbr_material_options.textures_path

        if (_path):
            
            _path_files=_path
            
            if _path[0:2]=='//':
                _path_files=bpy.path.abspath(_path)

            for filename in listdir(_path_files):
                
                _filename=filename.lower()
                _filepath=path.join(_path,filename)
                
                if 'base_color' in _filename or 'basecolor' in _filename or 'alberto' in _filename or '_alb.' in _filename or '_alb_' in _filename:
                    _nodes['ds_pbr_texture_base_color'].image = bpy.data.images.load(_filepath)

                if (_ds_pbr_material_options.option_nodes_type == "specular"):

                    if 'specular' in _filename or '_spec' in _filename  or '_s.' in _filename or '_s_' in _filename:
                        _nodes['ds_pbr_texture_base_color'].image = bpy.data.images.load(_filepath)

                if 'normal' in _filename or '_norm' in _filename  or '_n.' in _filename or '_n_' in _filename:
                    _nodes['ds_pbr_texture_normal'].image = bpy.data.images.load(_filepath)
                
                if 'roughness' in _filename:
                    _nodes['ds_pbr_texture_roughness'].image = bpy.data.images.load(_filepath)

                if (_ds_pbr_material_options.option_ao_map == True):

                    if 'ambient_occlusion' in _filename or '_ao.' in _filename or '_ao_' in _filename:
                        _nodes['ds_pbr_texture_ao'].image = bpy.data.images.load(_filepath)

                if (_ds_pbr_material_options.option_metallic_map == True):

                    if 'ds_pbr_texture_metallic' in _nodes:
                        if 'metallic' in _filename or '_m.' in _filename or '_m_' in _filename:
                            _nodes['ds_pbr_texture_metallic'].image = bpy.data.images.load(_filepath)

class ds_pbr_nodes_metallic_roughness(Operator):

    bl_idname = "ds_pbr.nodes_metallic_roughness"
    bl_label = "Metallic/Roughness"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout

        _ds_pbr_material_options = context.material.ds_pbr_material_options
        _ds_pbr_material_options['nodes_type']='metallic'

        _material = context.material
        
        _nodes = _material.node_tree.nodes

        ds_pbr_nodes_remove.execute(self,context)

        _material_output = _nodes.new('ShaderNodeOutputMaterial')
        _material_output.location = 600,0
        _material_output.name='ds_pbr_output'

        node_shader = _nodes.new('ShaderNodeBsdfPrincipled')
        node_shader.location = 400,0
        node_shader.name='ds_pbr_shader'

        _material_links = _material.node_tree.links
        
        _material_links.new(node_shader.outputs['BSDF'], _material_output.inputs['Surface'])

        if (_ds_pbr_material_options.option_ao_map == True):

            node_mix=_nodes.new('ShaderNodeMixRGB')
            node_mix.location = 200,100
            node_mix.blend_type = 'MULTIPLY'
            node_mix.name='ds_pbr_mix_rgb'
            _material_links.new(node_mix.outputs['Color'], node_shader.inputs['Base Color'])

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            _material_links.new(node.outputs['Color'], node_mix.inputs['Color1'])
            
            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,0
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_ao'
            _material_links.new(node.outputs['Color'], node_mix.inputs['Color2'])
        
        else:

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            _material_links.new(node.outputs['Color'], node_shader.inputs['Base Color'])

        if (_ds_pbr_material_options.option_metallic_map == True):

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,-250
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_metallic'
            _material_links.new(node.outputs['Color'], node_shader.inputs['Metallic'])   

        else:
            
            node_shader.inputs['Metallic'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_metallic

        node_shader.inputs['Specular'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_specular

        node=_nodes.new('ShaderNodeTexImage')
        node.location = 0,-500
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_roughness'
        _material_links.new(node.outputs['Color'], node_shader.inputs['Roughness'])   

        node_map=_nodes.new('ShaderNodeNormalMap')
        node_map.location = 200,-700
        node_map.name='ds_pbr_normal_map'
        _material_links.new(node_map.outputs['Normal'], node_shader.inputs['Normal'])

        node=_nodes.new('ShaderNodeTexImage')
        node.location = 0,-750
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_normal'
        _material_links.new(node.outputs['Color'], node_map.inputs['Color'])

        ds_pbr_auto_textures.execute(self,context)

        return {'FINISHED'}

class ds_pbr_nodes_specular_gloss(Operator):

    bl_idname = "ds_pbr.nodes_specular_gloss"
    bl_label = "Specular/Gloss"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout

        _ds_pbr_material_options = context.material.ds_pbr_material_options
        _ds_pbr_material_options['nodes_type']='specular'

        _material = context.material
        
        _nodes = _material.node_tree.nodes

        ds_pbr_nodes_remove.execute(self,context)

        _material_output = _nodes.new('ShaderNodeOutputMaterial')
        _material_output.location = 600,0
        _material_output.name='ds_pbr_output'

        node_shader = _nodes.new('ShaderNodeBsdfPrincipled')
        node_shader.location = 400,0
        node_shader.name='ds_pbr_shader'

        _material_links = _material.node_tree.links
        
        _material_links.new(node_shader.outputs['BSDF'], _material_output.inputs['Surface'])

        if (_ds_pbr_material_options.option_ao_map == True):

            node_mix=_nodes.new('ShaderNodeMixRGB')
            node_mix.location = 200,100
            node_mix.blend_type = 'MULTIPLY'
            node_mix.name='ds_pbr_mix_rgb'
            _material_links.new(node_mix.outputs['Color'], node_shader.inputs['Base Color'])

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            _material_links.new(node.outputs['Color'], node_mix.inputs['Color1'])
            
            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,0
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_ao'
            _material_links.new(node.outputs['Color'], node_mix.inputs['Color2'])
        
        else:

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            _material_links.new(node.outputs['Color'], node_shader.inputs['Base Color'])

        node_shader.inputs['Metallic'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_metallic
        node_shader.inputs['Specular'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_specular

        node_invert=_nodes.new('ShaderNodeInvert')
        node_invert.location = 200,-450
        node_invert.name='ds_pbr_invert'
        _material_links.new(node_invert.outputs['Color'], node_shader.inputs['Roughness'])

        node=_nodes.new('ShaderNodeTexImage')
        node.location = 0,-500
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_roughness'
        _material_links.new(node.outputs['Color'], node_invert.inputs['Color'])   

        node_map=_nodes.new('ShaderNodeNormalMap')
        node_map.location = 200,-700
        node_map.name='ds_pbr_normal_map'
        _material_links.new(node_map.outputs['Normal'], node_shader.inputs['Normal'])

        node=_nodes.new('ShaderNodeTexImage')
        node.location = 0,-750
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_normal'
        _material_links.new(node.outputs['Color'], node_map.inputs['Color'])

        ds_pbr_auto_textures.execute(self,context)

        return {'FINISHED'}

class ds_pbr_addon_prefs(AddonPreferences):

    bl_idname = __name__

    option_ao_map = BoolProperty(
        name="Ambient Occlusion",
        description="Add Ambient Occlusion Map via RGB Mix Node",
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

    def draw(self, context):

        layout = self.layout

        layout.label('Defaults',icon='PREFERENCES')
        
        layout.prop(self, 'option_ao_map')
        layout.prop(self, 'option_metallic_map')
        layout.prop(self, 'option_metallic')
        layout.prop(self, 'option_specular')

class ds_pbr_material_options(PropertyGroup):

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
        name="Ambient Occlusion",
        description="Add Ambient Occlusion Map via RGB Mix Node",
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
            subtype='DIR_PATH',
    )        
    option_nodes_type = StringProperty(
        name="Nodes Type",
        description="Nodes Type",
        default = ''
    )

class ds_pbr_material(Panel):

    bl_idname = "ds_pbr.material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "PBR Material"
    bl_context = "material"
   
    @classmethod
    def poll(cls, context):
        return (context.material is not None)

    def draw(self, context):

        layout = self.layout

        _ds_pbr_material_options = context.material.ds_pbr_material_options
        _material = context.material or bpy.data.materials.new('Material')
        _nodes = _material.node_tree.nodes

        if ('ds_pbr_texture_normal' in _nodes):

            layout.label('Textures',icon='IMASEL')

            split = layout.split(0.30)
            split.label('Base Color')
            split.template_ID(_nodes['ds_pbr_texture_base_color'], 'image', open='image.open')

            if (_ds_pbr_material_options.option_metallic_map == True):

                if ('ds_pbr_texture_metallic' in _nodes):

                    split = layout.split(0.30)
                    split.label('Metallic')
                    split.template_ID(_nodes['ds_pbr_texture_metallic'], 'image', open='image.open')

            if (_ds_pbr_material_options.option_ao_map == True):

                if ('ds_pbr_texture_ao' in _nodes):

                    split = layout.split(0.30)
                    split.label('Ambient Occulussion')
                    split.template_ID(_nodes['ds_pbr_texture_ao'], 'image', open='image.open')

            split = layout.split(0.30)
            split.label('Normal')
            split.template_ID(_nodes['ds_pbr_texture_normal'], 'image', open='image.open')

            split = layout.split(0.30)
            split.label('Roughness')
            split.template_ID(_nodes['ds_pbr_texture_roughness'], 'image', open='image.open')
        
        layout.label('Auto Textures',icon='IMASEL')
        layout.prop(_ds_pbr_material_options, "textures_path")

        layout.label('Optional Nodes',icon='NODETREE')

        layout.prop(_ds_pbr_material_options, "option_ao_map")
        layout.prop(_ds_pbr_material_options, "option_metallic_map")

        layout.operator("ds_pbr.nodes_metallic_roughness")
        layout.operator("ds_pbr.nodes_specular_gloss")

        layout.separator()

def register():

    from bpy.utils import register_class

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