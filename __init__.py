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
	"version": (1, 7, 0),
    "blender": (2, 79, 0),
	"location": "Properties > Material > PBR Material",
	"wiki_url":    "https://github.com/Digiography/blender_addon_pbr/wiki",
	"tracker_url": "https://github.com/Digiography/blender_addon_pbr/issues",
    "category": "Material",
}

# Main Imports

import bpy

from bpy.props import (StringProperty,BoolProperty,IntProperty,FloatProperty,FloatVectorProperty,EnumProperty,PointerProperty,)
from bpy.types import (Panel,Operator,AddonPreferences,PropertyGroup,)

from  os import (listdir,path)

# Clear Nodes

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

        return {'FINISHED'}

# Texture Matching Functions

def is_texture_base_color(filename):

    _filename=filename.lower()

    if 'base_color' in _filename or 'basecolor' in _filename  or 'diffuse' in _filename or 'alberto' in _filename or '_alb.' in _filename or '_alb_' in _filename:
        return True
    else:
        return False

def is_texture_normal(filename):

    _filename=filename.lower()

    if 'normal' in _filename or '_norm' in _filename  or '_n.' in _filename or '_n_' in _filename or '_bump' in _filename:
        return True
    else:
        return False

def is_texture_specular(filename):

    _filename=filename.lower()

    if 'specular' in _filename or '_spec' in _filename  or '_s.' in _filename or '_s_' in _filename:
        return True
    else:
        return False

def is_texture_roughness(filename):

    _filename=filename.lower()

    if 'roughness' in _filename or  '_rough' in _filename:
        return True
    else:
        return False

def is_texture_ao(filename):

    _filename=filename.lower()

    if 'ambient' in _filename or 'occlusion' in _filename or 'ambient_occlusion' in _filename or '_ao.' in _filename or '_ao_' in _filename:
        return True
    else:
        return False

def is_texture_metallic(filename):

    _filename=filename.lower()

    if 'metallic' in _filename or '_m.' in _filename or '_m_' in _filename:
        return True
    else:
        return False              

# Convert Existing Nodes

class ds_pbr_nodes_convert(Operator):

    bl_idname = "ds_pbr.nodes_convert"
    bl_label = "Convert Nodes"
    bl_context = "material"
    node_type = bpy.props.StringProperty(
        name="node_type",
        default = 'metallic_roughness'
    ) 
    def execute(self, context):

        layout = self.layout
        
        _images={}

        _material = context.material
        _ds_pbr_material_options = context.material.ds_pbr_material_options
        
        if _material and _material.node_tree:

            _nodes = _material.node_tree.nodes

            for node in _nodes:

                if node.type=='TEX_IMAGE':

                    _image_name = node.image.name
                    
                    # Base Color

                    if is_texture_base_color(_image_name):
                        _images['base_color']=node.image
                    
                    # Specular

                    if (_ds_pbr_material_options.option_nodes_type == "specular"):

                        if is_texture_specular(_image_name):
                            _images['base_color']=node.image
                    
                    # Normal

                    if is_texture_normal(_image_name):
                        _images['normal']=node.image
                    
                    # Roughness

                    if is_texture_roughness(_image_name):
                        _images['roughness']=node.image
                
                    # Ambient Occlusion

                    if is_texture_ao(_image_name):
                        _images['ao']=node.image

                    # Metallic

                    if is_texture_metallic(_image_name):
                        _images['metallic']=node.image

            if len(_images)>0:

                ds_pbr_nodes_remove.execute(self,context)

                if self.node_type=='metallic_roughness':
                    ds_pbr_nodes_metallic_roughness.execute(self,context)
                elif self.node_type=='specular_gloss':
                    ds_pbr_nodes_specular_gloss.execute(self,context)

                for _image in _images:
                    _nodes['ds_pbr_texture_'+_image].image = _images[_image]
                    _ds_pbr_material_options['option_texture_'+_image+'_path']=_images[_image].name

        return {'FINISHED'}

# Auto Textures - Match input nodes based on filename

class ds_pbr_auto_textures(Operator):

    bl_idname = "ds_pbr.auto_textures"
    bl_label = "Auto Textures"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout
        _material = context.material
        _nodes = _material.node_tree.nodes
        _ds_pbr_material_options = context.material.ds_pbr_material_options
        _path = _ds_pbr_material_options.option_textures_path

        if (_path):
            
            _path_files=_path
            
            # Check if path is relative

            if _path[0:2]=='//':
                _path_files=bpy.path.abspath(_path)

            for filename in listdir(_path_files):
                
                _filename=filename.lower()
                _filepath=path.join(_path,filename)
                
                _match=True

                if _ds_pbr_material_options.option_use_matt_name and _material.name.lower() not in _filename:
                    _match=False

                if _match:

                    # Base Color

                    if is_texture_base_color(_filename):
                        _nodes['ds_pbr_texture_base_color'].image = bpy.data.images.load(_filepath)
                        _ds_pbr_material_options.option_texture_base_color_path=_filepath
                    
                    # Specular

                    if (_ds_pbr_material_options.option_nodes_type == "specular"):

                        if is_texture_specular(_filename):
                            _nodes['ds_pbr_texture_base_color'].image = bpy.data.images.load(_filepath)
                            _ds_pbr_material_options.option_texture_base_color_path=_filepath
                    
                    # Normal

                    if is_texture_normal(_filename):
                        _nodes['ds_pbr_texture_normal'].image = bpy.data.images.load(_filepath)
                        _ds_pbr_material_options.option_texture_normal_path=_filepath

                    # Roughness

                    if is_texture_roughness(_filename):
                        _nodes['ds_pbr_texture_roughness'].image = bpy.data.images.load(_filepath)
                        _ds_pbr_material_options.option_texture_roughness_path=_filepath

                    # Ambient Occlusion

                    if (_ds_pbr_material_options.option_ao_map == True):

                        if is_texture_ao(_filename):
                            _nodes['ds_pbr_texture_ao'].image = bpy.data.images.load(_filepath)
                            _ds_pbr_material_options.option_texture_ao_path=_filepath
                    
                    # Metallic

                    if (_ds_pbr_material_options.option_metallic_map == True):
                        
                        if 'ds_pbr_texture_metallic' in _nodes:

                            if is_texture_metallic(_filename):
                                _nodes['ds_pbr_texture_metallic'].image = bpy.data.images.load(_filepath)
                                _ds_pbr_material_options.option_texture_metallic_path=_filepath

# Metallic Roughness Nodes

class ds_pbr_nodes_metallic_roughness(Operator):

    bl_idname = "ds_pbr.nodes_metallic_roughness"
    bl_label = "Metallic/Roughness"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout

        # Set Vars

        _ds_pbr_material_options = context.material.ds_pbr_material_options
        _ds_pbr_material_options['nodes_type']='metallic'

        _material = context.material
        _material_links = _material.node_tree.links
        
        _nodes = _material.node_tree.nodes

        # Clear Nodes

        ds_pbr_nodes_remove.execute(self,context)

        # Output Material

        _material_output = _nodes.new('ShaderNodeOutputMaterial')
        _material_output.location = 600,0
        _material_output.name='ds_pbr_output'

        # Shader

        node_shader = _nodes.new('ShaderNodeBsdfPrincipled')
        node_shader.location = 400,0
        node_shader.name='ds_pbr_shader'
        
        _material_links.new(node_shader.outputs['BSDF'], _material_output.inputs['Surface'])

        if (_ds_pbr_material_options.option_ao_map == True):

            # Mix RGB

            node_mix=_nodes.new('ShaderNodeMixRGB')
            node_mix.location = 200,100
            node_mix.blend_type = 'MULTIPLY'
            node_mix.name='ds_pbr_mix_rgb'
            _material_links.new(node_mix.outputs['Color'], node_shader.inputs['Base Color'])

            # Base Color

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            _material_links.new(node.outputs['Color'], node_mix.inputs['Color1'])

            # Ambient Occlusion
            
            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,0
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_ao'
            _material_links.new(node.outputs['Color'], node_mix.inputs['Color2'])
        
        else:

            # Base Color

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            _material_links.new(node.outputs['Color'], node_shader.inputs['Base Color'])

        # Metallic

        if (_ds_pbr_material_options.option_metallic_map == True):

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,-250
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_metallic'
            _material_links.new(node.outputs['Color'], node_shader.inputs['Metallic'])   

        else:
            
            node_shader.inputs['Metallic'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_metallic

        node_shader.inputs['Specular'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_specular

        # Roughness

        node=_nodes.new('ShaderNodeTexImage')
        node.location = 0,-500
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_roughness'
        _material_links.new(node.outputs['Color'], node_shader.inputs['Roughness'])   

        # Normal Map

        node_map=_nodes.new('ShaderNodeNormalMap')
        node_map.location = 200,-700
        node_map.name='ds_pbr_normal_map'
        _material_links.new(node_map.outputs['Normal'], node_shader.inputs['Normal'])
        
        # Normal

        node=_nodes.new('ShaderNodeTexImage')
        node.location = 0,-750
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_normal'
        _material_links.new(node.outputs['Color'], node_map.inputs['Color'])

        # Assign Textures
    
        ds_pbr_auto_textures.execute(self,context)

        return {'FINISHED'}

# Specular Gloss Nodes

class ds_pbr_nodes_specular_gloss(Operator):

    bl_idname = "ds_pbr.nodes_specular_gloss"
    bl_label = "Specular/Gloss"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout

        # Set Vars

        _ds_pbr_material_options = context.material.ds_pbr_material_options
        _ds_pbr_material_options['nodes_type']='specular'

        _material = context.material
        _material_links = _material.node_tree.links
        
        _nodes = _material.node_tree.nodes
        
        # Clear Nodes

        ds_pbr_nodes_remove.execute(self,context)
        
        # Output Material

        _material_output = _nodes.new('ShaderNodeOutputMaterial')
        _material_output.location = 600,0
        _material_output.name='ds_pbr_output'
        
        # Shader
        
        node_shader = _nodes.new('ShaderNodeBsdfPrincipled')
        node_shader.location = 400,0
        node_shader.name='ds_pbr_shader'
        
        _material_links.new(node_shader.outputs['BSDF'], _material_output.inputs['Surface'])

        if (_ds_pbr_material_options.option_ao_map == True):
            
            # Mix RGB

            node_mix=_nodes.new('ShaderNodeMixRGB')
            node_mix.location = 200,100
            node_mix.blend_type = 'MULTIPLY'
            node_mix.name='ds_pbr_mix_rgb'
            _material_links.new(node_mix.outputs['Color'], node_shader.inputs['Base Color'])
            
            # Base Color

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            _material_links.new(node.outputs['Color'], node_mix.inputs['Color1'])
            
            # Ambient Occlusion

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,0
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_ao'
            _material_links.new(node.outputs['Color'], node_mix.inputs['Color2'])
        
        else:
            
            # Base Color

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,250
            node.name='ds_pbr_texture_base_color'
            _material_links.new(node.outputs['Color'], node_shader.inputs['Base Color'])

        node_shader.inputs['Metallic'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_metallic
        node_shader.inputs['Specular'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_specular
        
        # Roughness Invert

        node_invert=_nodes.new('ShaderNodeInvert')
        node_invert.location = 200,-450
        node_invert.name='ds_pbr_invert'
        _material_links.new(node_invert.outputs['Color'], node_shader.inputs['Roughness'])
        
        # Roughness

        node=_nodes.new('ShaderNodeTexImage')
        node.location = 0,-500
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_roughness'
        _material_links.new(node.outputs['Color'], node_invert.inputs['Color'])   
        
        # Normal Map

        node_map=_nodes.new('ShaderNodeNormalMap')
        node_map.location = 200,-700
        node_map.name='ds_pbr_normal_map'
        _material_links.new(node_map.outputs['Normal'], node_shader.inputs['Normal'])
        
        # Normal

        node=_nodes.new('ShaderNodeTexImage')
        node.location = 0,-750
        node.color_space = 'NONE'
        node.name='ds_pbr_texture_normal'
        _material_links.new(node.outputs['Color'], node_map.inputs['Color'])

        # Assign Textures

        ds_pbr_auto_textures.execute(self,context)

        return {'FINISHED'}

# Addon Preferences Panel

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
    option_relative = BoolProperty(
        name="Relative Paths",
        description="Use Relative Paths for images.",
        default = True
    )
    option_metallic = FloatProperty(
        name = "Metaliic",
        description = "Metalic Value",
        default = 0.500,
        min = 0.000,
        max = 1.000
    )        
    option_specular = FloatProperty(
        name = "Specular",
        description = "Specular Value",
        default = 0.500,
        min = 0.000,
        max = 1.000
    )
    
    def draw(self, context):

        layout = self.layout

        layout.label('Defaults',icon='PREFERENCES')
        
        layout.prop(self, 'option_relative')
        layout.prop(self, 'option_ao_map')
        layout.prop(self, 'option_metallic_map')
        layout.prop(self, 'option_metallic')
        layout.prop(self, 'option_specular')

# Material Panel Properties

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

    def get_option_relative(self):
        if "_option_relative" not in self:
            self["_option_relative"]=bpy.context.user_preferences.addons[__name__].preferences.option_relative
        return self["_option_relative"]
    def set_option_relative(self, value):
        self["_option_relative"] = value

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
    option_relative = BoolProperty(
        name="Use Relative Paths",
        description="Use Relative Paths for images.",
        get = get_option_relative,
        set = set_option_relative
    )
    option_use_matt_name = BoolProperty(
        name="Use Material Name",
        description="Use Material Name for image matching."
    )
    option_textures_path = StringProperty(
        name="Auto Textures Path",
        description="Use auto assign textures images to input nodes.",
        default = ''
    )        
    option_nodes_type = StringProperty(
        name="Nodes Type",
        description="Nodes Type",
        default = ''
    )
    option_texture_base_color_path = StringProperty(
        name="Base Color",
        description="Base Color Path",
    )
    option_texture_normal_path = StringProperty(
        name="Normal",
        description="Normal Path",
    )
    option_texture_ao_path = StringProperty(
        name="Ambient Occlusion",
        description="Ambient Occlusion Path",
    )
    option_texture_metallic_path = StringProperty(
        name="Metallic",
        description="Metallic Path",
    )
    option_texture_roughness_path = StringProperty(
        name="Roughness",
        description="Roughness Path",
    )

# File select dialog overrides

class ds_pbr_texture_base_color_select_clr(bpy.types.Operator):
    bl_idname = "ds_pbr.base_color_clr"
    bl_label = "Base Color"
    def execute(self, context):
        context.material.node_tree.nodes['ds_pbr_texture_base_color'].image=None
        context.material.ds_pbr_material_options.option_texture_base_color_path=''
        return {'FINISHED'}

class ds_pbr_texture_base_color_select(bpy.types.Operator):
    bl_idname = "ds_pbr.base_color"
    bl_label = "Base Color"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    bl_context = "material"

    option_relative = bpy.props.BoolProperty(name="Relative")

    def execute(self, context):
        _nodes = context.material.node_tree.nodes
        if self.option_relative==True:
            _filepath=bpy.path.relpath(self.filepath)
        else:
            _filepath=bpy.path.abspath(self.filepath)
        _nodes['ds_pbr_texture_base_color'].image=bpy.data.images.load(_filepath)
        context.material.ds_pbr_material_options.option_texture_base_color_path=_filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath and context.material.ds_pbr_material_options.option_textures_path:
            self.filepath = context.material.ds_pbr_material_options.option_textures_path
        self.option_relative=context.material.ds_pbr_material_options.option_relative
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ds_pbr_texture_normal_select_clr(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_normal_clr"
    bl_label = "Normal"
    def execute(self, context):
        context.material.node_tree.nodes['ds_pbr_texture_normal'].image=None
        context.material.ds_pbr_material_options.option_texture_normal_path=''
        return {'FINISHED'}

class ds_pbr_texture_normal_select(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_normal"
    bl_label = "Normal"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    bl_context = "material"

    option_relative = bpy.props.BoolProperty(name="Relative")

    def execute(self, context):
        _nodes = context.material.node_tree.nodes
        if self.option_relative==True:
            _filepath=bpy.path.relpath(self.filepath)
        else:
            _filepath=bpy.path.abspath(self.filepath)
        _nodes['ds_pbr_texture_normal'].image=bpy.data.images.load(_filepath)
        context.material.ds_pbr_material_options.option_texture_normal_path=_filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath and context.material.ds_pbr_material_options.option_textures_path:
            self.filepath = context.material.ds_pbr_material_options.option_textures_path
        self.option_relative=context.material.ds_pbr_material_options.option_relative
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ds_pbr_texture_ao_select_clr(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_ao_clr"
    bl_label = "Ambient Occlusion"
    def execute(self, context):
        context.material.node_tree.nodes['ds_pbr_texture_ao'].image=None
        context.material.ds_pbr_material_options.option_texture_ao_path=''
        return {'FINISHED'}

class ds_pbr_texture_ao_select(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_ao"
    bl_label = "Ambient Occlusion"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    bl_context = "material"
    option_relative = bpy.props.BoolProperty(name="Relative")
    def execute(self, context):
        _nodes = context.material.node_tree.nodes
        if self.option_relative==True:
            _filepath=bpy.path.relpath(self.filepath)
        else:
            _filepath=bpy.path.abspath(self.filepath)
        _nodes['ds_pbr_texture_ao'].image=bpy.data.images.load(_filepath)
        context.material.ds_pbr_material_options.option_texture_ao_path=_filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath and context.material.ds_pbr_material_options.option_textures_path:
            self.filepath = context.material.ds_pbr_material_options.option_textures_path
        self.option_relative=context.material.ds_pbr_material_options.option_relative
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ds_pbr_texture_metallic_select_clr(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_metallic_clr"
    bl_label = "Metallic"
    def execute(self, context):
        context.material.node_tree.nodes['ds_pbr_texture_metallic'].image=None
        context.material.ds_pbr_material_options.option_texture_metallic_path=''
        return {'FINISHED'}

class ds_pbr_texture_metallic_select(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_metallic"
    bl_label = "Metallic"
    bl_context = "material"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    option_relative = bpy.props.BoolProperty(name="Relative")

    def execute(self, context):
        _nodes = context.material.node_tree.nodes
        if self.option_relative==True:
            _filepath=bpy.path.relpath(self.filepath)
        else:
            _filepath=bpy.path.abspath(self.filepath)
        _nodes['ds_pbr_texture_metallic'].image=bpy.data.images.load(_filepath)
        context.material.ds_pbr_material_options.option_texture_metallic_path=_filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath and context.material.ds_pbr_material_options.option_textures_path:
            self.filepath = context.material.ds_pbr_material_options.option_textures_path
        self.option_relative=context.material.ds_pbr_material_options.option_relative
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ds_pbr_texture_roughness_select_clr(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_roughness_clr"
    bl_label = "Roughness"
    def execute(self, context):
        context.material.node_tree.nodes['ds_pbr_texture_roughness'].image=None
        context.material.ds_pbr_material_options.option_texture_roughness_path=''
        return {'FINISHED'}

class ds_pbr_texture_roughness_select(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_roughness"
    bl_label = "Roughness"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    bl_context = "material"
    option_relative = bpy.props.BoolProperty(name="Relative")

    def execute(self, context):
        _nodes = context.material.node_tree.nodes
        if self.option_relative==True:
            _filepath=bpy.path.relpath(self.filepath)
        else:
            _filepath=bpy.path.abspath(self.filepath)
        _nodes['ds_pbr_texture_roughness'].image=bpy.data.images.load(_filepath)
        context.material.ds_pbr_material_options.option_texture_roughness_path=_filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath and context.material.ds_pbr_material_options.option_textures_path:
            self.filepath = context.material.ds_pbr_material_options.option_textures_path
        self.option_relative=context.material.ds_pbr_material_options.option_relative
        context.window_manager.fileselect_add(self,)
        return {'RUNNING_MODAL'}

class ds_pbr_textures_path_select_clr(bpy.types.Operator):
    bl_idname = "ds_pbr.textures_path_select_clr"
    bl_label = "Auto Textures Path"
    def execute(self, context):
        context.material.ds_pbr_material_options.option_textures_path=''
        return {'FINISHED'}

class ds_pbr_textures_path_select(bpy.types.Operator):
    bl_idname = "ds_pbr.textures_path_select"
    bl_label = "Auto Textures Path"
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    option_relative = bpy.props.BoolProperty(name="Relative")

    def execute(self, context):
        if self.option_relative==True:
            _directory=bpy.path.relpath(self.directory)
        else:
            _directory=bpy.path.abspath(self.directory)
        context.material.ds_pbr_material_options.option_textures_path=_directory
        return {'FINISHED'}

    def invoke(self, context, event):
        self.option_relative=context.material.ds_pbr_material_options.option_relative
        context.window_manager.fileselect_add(self,)
        return {'RUNNING_MODAL'}

# Set Render Engines

class ds_pbr_render_cycles(bpy.types.Operator):
    bl_idname = "ds_pbr.render_cycles"
    bl_label = "CYCLES"
    bl_context = "scene"
    def execute(self, context):
        bpy.context.scene.render.engine='CYCLES'
        return {'FINISHED'}

class ds_pbr_render_game(bpy.types.Operator):
    bl_idname = "ds_pbr.render_game"
    bl_label = "BLENDER_GAME"
    bl_context = "scene"
    def execute(self, context):
        bpy.context.scene.render.engine='BLENDER_GAME'
        return {'FINISHED'}

# Material Panel

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
        
        if ('ds_pbr_texture_base_color' not in _nodes):

            if _material and _material.node_tree:

                _found = False
                _nodes = _material.node_tree.nodes
                
                for node in _nodes:

                    if node.type=='TEX_IMAGE':
                        _found=True

                if _found:

                    layout.operator("ds_pbr.nodes_convert",text="Convert to Metallic Roughness").node_type='metallic_roughness'
                    layout.operator("ds_pbr.nodes_convert",text="Convert to Specular Gloss").node_type='specular_gloss'

        if ('ds_pbr_texture_normal' in _nodes):

            layout.label('Textures',icon='IMASEL')
            
            # Base Color

            col=layout.row(align=True)
            box=col.row()
            box.label(ds_pbr_texture_base_color_select.bl_label +':',icon='IMAGE_DATA')
            row=col.row().split(0.85)
            row.label(_ds_pbr_material_options.option_texture_base_color_path)
            box=row.row().split(0.50)
            box.operator(ds_pbr_texture_base_color_select.bl_idname, icon="FILE_FOLDER",text="")
            box.operator(ds_pbr_texture_base_color_select_clr.bl_idname, icon="X",text="")

            if (_ds_pbr_material_options.option_metallic_map == True and 'ds_pbr_texture_metallic' in _nodes):

                # Metallic

                col=layout.row(align=True)
                box=col.row()
                box.label(ds_pbr_texture_metallic_select.bl_label +':',icon='IMAGE_DATA')
                row=col.row().split(0.85)
                row.label(_ds_pbr_material_options.option_texture_metallic_path)
                box=row.row().split(0.50)
                box.operator(ds_pbr_texture_metallic_select.bl_idname, icon="FILE_FOLDER",text="")
                box.operator(ds_pbr_texture_metallic_select_clr.bl_idname, icon="X",text="")

            if (_ds_pbr_material_options.option_ao_map == True):

                if ('ds_pbr_texture_ao' in _nodes):

                    # Ambient Occlusion

                    col=layout.row(align=True)
                    box=col.row()
                    box.label(ds_pbr_texture_ao_select.bl_label +':',icon='IMAGE_DATA')
                    row=col.row().split(0.85)
                    row.label(_ds_pbr_material_options.option_texture_ao_path)
                    box=row.row().split(0.50)
                    box.operator(ds_pbr_texture_ao_select.bl_idname, icon="FILE_FOLDER",text="")
                    box.operator(ds_pbr_texture_ao_select_clr.bl_idname, icon="X",text="")
            
            # Normal

            col=layout.row(align=True)
            box=col.row()
            box.label(ds_pbr_texture_normal_select.bl_label +':',icon='IMAGE_DATA')
            row=col.row().split(0.85)
            row.label(_ds_pbr_material_options.option_texture_normal_path)
            box=row.row().split(0.50)
            box.operator(ds_pbr_texture_normal_select.bl_idname, icon="FILE_FOLDER",text="")
            box.operator(ds_pbr_texture_normal_select_clr.bl_idname, icon="X",text="")
            
            # Roughness

            col=layout.row(align=True)
            box=col.row()
            box.label(ds_pbr_texture_roughness_select.bl_label +':',icon='IMAGE_DATA')
            row=col.row().split(0.85)
            row.label(_ds_pbr_material_options.option_texture_roughness_path)
            box=row.row().split(0.50)
            box.operator(ds_pbr_texture_roughness_select.bl_idname, icon="FILE_FOLDER",text="")
            box.operator(ds_pbr_texture_roughness_select_clr.bl_idname, icon="X",text="")

        # Check if .blend file is saved

        if not bpy.data.filepath and _ds_pbr_material_options.option_relative == True:
            layout.label('Blender file not saved. Required for relative paths.',icon='ERROR')

        # Relative Paths

        col=layout.row(align=True)
        box=col.row()
        box.prop(_ds_pbr_material_options, "option_relative")
        box=col.row()
        box.prop(_ds_pbr_material_options, "option_use_matt_name")
        

        # Auto Textures Folder

        col=layout.row(align=True)
        box=col.row()
        box.label(ds_pbr_textures_path_select.bl_label,icon='FILESEL')
        row=col.row().split(0.85)
        row.prop(_ds_pbr_material_options,"option_textures_path",text="")
        box=row.row().split(0.50)
        box.operator(ds_pbr_textures_path_select.bl_idname, icon="FILE_FOLDER",text="")
        box.operator(ds_pbr_textures_path_select_clr.bl_idname, icon="X",text="")
        
        # Check if render engine is PBR capable

        if (bpy.context.scene.render.engine != 'CYCLES' and bpy.context.scene.render.engine != 'BLENDER_GAME'):
                
                layout.label('Cycles or Blender Game Render Engine required for PBR','INFO')
                row = layout.row(align=True)
                col = row.split(percentage=0.5)
                col.operator('ds_pbr.render_cycles')
                col.operator('ds_pbr.render_game')

        # Optional Nodes

        row = layout.row(align=True)

        box=row.column()
        box.label('Optional Nodes',icon='NODETREE')
        box.prop(_ds_pbr_material_options, "option_ao_map")
        box.prop(_ds_pbr_material_options, "option_metallic_map")
        
        box=row.column()
        box.operator("ds_pbr.nodes_metallic_roughness")
        box.operator("ds_pbr.nodes_specular_gloss")
        box.operator("ds_pbr.nodes_remove")

        layout.separator()

def register():

    from bpy.utils import register_class

    register_class(ds_pbr_render_cycles)
    register_class(ds_pbr_render_game)
    register_class(ds_pbr_texture_base_color_select)
    register_class(ds_pbr_texture_normal_select)
    register_class(ds_pbr_texture_ao_select)
    register_class(ds_pbr_texture_metallic_select)
    register_class(ds_pbr_texture_roughness_select)

    register_class(ds_pbr_texture_base_color_select_clr)
    register_class(ds_pbr_texture_normal_select_clr)
    register_class(ds_pbr_texture_ao_select_clr)
    register_class(ds_pbr_texture_metallic_select_clr)
    register_class(ds_pbr_texture_roughness_select_clr)    

    register_class(ds_pbr_textures_path_select)
    register_class(ds_pbr_textures_path_select_clr)

    register_class(ds_pbr_addon_prefs)
    register_class(ds_pbr_material_options)
    register_class(ds_pbr_nodes_remove)
    register_class(ds_pbr_nodes_convert)    
    register_class(ds_pbr_auto_textures)
    register_class(ds_pbr_nodes_metallic_roughness)
    register_class(ds_pbr_nodes_specular_gloss)
    register_class(ds_pbr_material)

    bpy.types.Material.ds_pbr_material_options = PointerProperty(type=ds_pbr_material_options)

def unregister():

    from bpy.utils import unregister_class

    unregister_class(ds_pbr_render_cycles)
    unregister_class(ds_pbr_render_game)
    unregister_class(ds_pbr_texture_base_color_select)
    unregister_class(ds_pbr_texture_normal_select)
    unregister_class(ds_pbr_texture_ao_select)
    unregister_class(ds_pbr_texture_metallic_select)
    unregister_class(ds_pbr_texture_roughness_select)

    unregister_class(ds_pbr_texture_base_color_select_clr)
    unregister_class(ds_pbr_texture_normal_select_clr)
    unregister_class(ds_pbr_texture_ao_select_clr)
    unregister_class(ds_pbr_texture_metallic_select_clr)
    unregister_class(ds_pbr_texture_roughness_select_clr)    
    
    unregister_class(ds_pbr_textures_path_select)
    unregister_class(ds_pbr_textures_path_select_clr)

    unregister_class(ds_pbr_addon_prefs)
    unregister_class(ds_pbr_material_options)
    unregister_class(ds_pbr_nodes_remove)
    unregister_class(ds_pbr_nodes_convert)    
    unregister_class(ds_pbr_auto_textures)
    unregister_class(ds_pbr_nodes_metallic_roughness)
    unregister_class(ds_pbr_nodes_specular_gloss)
    unregister_class(ds_pbr_material)

    del bpy.types.Material.ds_pbr_material_options

if __name__ == "__main__":

    register()