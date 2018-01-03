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
	"version": (1, 8, 0),
    "blender": (2, 79, 0),
	"location": "Properties > Material > PBR Material",
	"wiki_url":    "https://github.com/Digiography/blender_addon_pbr/wiki",
	"tracker_url": "https://github.com/Digiography/blender_addon_pbr/issues",
    "category": "Material",
}

node_name={
    'base_color':{
        'label':'Base Color',
        'matches':['base_color','basecolor','diffuse','alberto','_alb.','_alb_','_col_','_color','color.']
    },
    'metallic':{
        'label':'Metallic',
        'matches':['_metallic','metallic.','_m.','_m_']
    },
    'specular':{
        'label':'Specular',
        'matches':['specular','_spec','_s.','_s_']
    },
    'ao':{
        'label':'Ambient Occlusion',
        'matches':['_ambient','_occlusion','ambient_occlusion','_ao.','_ao_']
    },
    'normal':{
        'label':'Normal',
        'matches':['normal_opengl','_normal','normal.','_norm','_n.','_n_','_bump','bump.']
    },
    'roughness':{
        'label':'Roughness',
        'matches':['roughness','_rough','_r.']
    },
    'emissive':{
        'label':'Emissive',
        'matches':['emissive','_em.','_e.']        
    },
    'gloss':{
        'label':'Glossiness',
        'matches':['_gloss','gloss.','_g.']
    },
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

# Texture Matching Function
       
def ds_match_texture(name,filename):

    _filename=filename.lower()
    _matches=node_name[name]['matches']
    
    for _match in _matches:

        if _match in _filename:
            return True
    
    return False              

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
        _object = context.object

        if (_path):
            
            _path_files=_path
            
            # Check if path is relative

            if _path[0:2]=='//':
                _path_files=bpy.path.abspath(_path)

            for filename in listdir(_path_files):
                
                _filename=filename.lower()
                _filepath=path.join(_path,filename)
                
                _match=True

                if (_ds_pbr_material_options.option_use_mesh_name and _ds_pbr_material_options.option_use_matt_name)and(_material.name.lower() not in _filename or _object.name.lower() not in _filename):
                    _match=False
                elif _ds_pbr_material_options.option_use_matt_name and _material.name.lower() not in _filename:
                    _match=False
                elif _ds_pbr_material_options.option_use_mesh_name and _object.name.lower() not in _filename:
                    _match=False

                if _match:

                    # Base Color

                    if ds_match_texture('base_color',_filename):
                        _nodes['ds_pbr_texture_base_color'].image = bpy.data.images.load(_filepath)
                    
                    # Normal

                    if ds_match_texture('normal',_filename):
                        _nodes['ds_pbr_texture_normal'].image = bpy.data.images.load(_filepath)

                    # Roughness

                    if ds_match_texture('roughness',_filename):
                        _nodes['ds_pbr_texture_roughness'].image = bpy.data.images.load(_filepath)
                    elif ds_match_texture('gloss',_filename):
                        _nodes['ds_pbr_texture_roughness'].image = bpy.data.images.load(_filepath)

                    # Ambient Occlusion

                    if (_ds_pbr_material_options.option_ao_node == True):

                        if ds_match_texture('ao',_filename):
                            _nodes['ds_pbr_texture_ao'].image = bpy.data.images.load(_filepath)
                    
                    # Metallic

                    if (_ds_pbr_material_options.option_metallic_node == True):
                        
                        if 'ds_pbr_texture_metallic' in _nodes:

                            if ds_match_texture('metallic',_filename):
                                _nodes['ds_pbr_texture_metallic'].image = bpy.data.images.load(_filepath)

                    # Specular

                    if (_ds_pbr_material_options.option_specular_node == True):
                        
                        if 'ds_pbr_texture_specular' in _nodes:

                            if ds_match_texture('specular',_filename):
                                _nodes['ds_pbr_texture_specular'].image = bpy.data.images.load(_filepath)

                    # Emissive

                    if (_ds_pbr_material_options.option_emissive_node == True):

                        if ds_match_texture('emissive',_filename):
                            _nodes['ds_pbr_texture_emissive'].image = bpy.data.images.load(_filepath)

# Create Auto

class ds_pbr_nodes_auto(Operator):

    bl_idname = "ds_pbr.nodes_auto"
    bl_label = "Create - Auto Detect"
    bl_context = "material"

    def execute(self, context):

        layout = self.layout

        _material = context.material
        _ds_pbr_material_options = context.material.ds_pbr_material_options
        _path = _ds_pbr_material_options.option_textures_path
        _path_files=_path
        
        _gloss = False
        _metallic = False
        _specular = False
        _ao = False
        _emissive = False

        if _path[0:2]=='//':
            _path_files=bpy.path.abspath(_path)

        for filename in listdir(_path_files):
            
            _filename=filename.lower()
            _filepath=path.join(_path,filename)
            _match=True

            if (_ds_pbr_material_options.option_use_mesh_name and _ds_pbr_material_options.option_use_matt_name)and(_material.name.lower() not in _filename or _object.name.lower() not in _filename):
                _match=False
            elif _ds_pbr_material_options.option_use_matt_name and _material.name.lower() not in _filename:
                _match=False
            elif _ds_pbr_material_options.option_use_mesh_name and _object.name.lower() not in _filename:
                _match=False

            if _match:
                
                if ds_match_texture('metallic',_filename):
                    _metallic = True
                elif ds_match_texture('specular',_filename):
                    _specular = True
                elif ds_match_texture('ao',_filename):
                    _ao = True
                elif ds_match_texture('emissive',_filename):
                    _emissive = True
                elif ds_match_texture('gloss',_filename):
                    _gloss = True
    
        _ds_pbr_material_options.option_metallic_node = _metallic
        _ds_pbr_material_options.option_specular_node = _specular
        _ds_pbr_material_options.option_ao_node = _ao
        _ds_pbr_material_options.option_emissive_node = _emissive

        if _gloss == False:
            bpy.ops.ds_pbr.nodes('EXEC_DEFAULT',nodes_type='metallic_roughness')
        else:
            bpy.ops.ds_pbr.nodes('EXEC_DEFAULT',nodes_type='specular_gloss')

        return {'FINISHED'}

# PBR Nodes

class ds_pbr_nodes(Operator):

    bl_idname = "ds_pbr.nodes"
    bl_label = "PBR Nodes"
    bl_context = "material"
    nodes_type = bpy.props.StringProperty(
        name="nodes_type",
        default = 'metallic_roughness'
    ) 
    def execute(self, context):

        layout = self.layout

        # Set Vars

        _ds_pbr_material_options = context.material.ds_pbr_material_options
        _ds_pbr_material_options['nodes_type']=self.nodes_type

        _material = context.material
        _material_links = _material.node_tree.links
        
        _nodes = _material.node_tree.nodes
        
        # Clear Nodes

        ds_pbr_nodes_remove.execute(self,context)
        
        # Output Material

        _material_output = _nodes.new('ShaderNodeOutputMaterial')

        if (_ds_pbr_material_options.option_emissive_node == False):
            _material_output.location = 600,0
        else:
            _material_output.location = 1200,0

        _material_output.name='ds_pbr_output'

        if (_ds_pbr_material_options.option_emissive_node == True):

            # Add Shader

            _node_add_shader=_nodes.new('ShaderNodeAddShader')
            _node_add_shader.location = 1000,0
            _node_add_shader.name = 'ds_pbr_add_shader'
            _material_links.new(_node_add_shader.outputs['Shader'], _material_output.inputs['Surface'])
            
            # Shader Emission
            
            _node_emission=_nodes.new('ShaderNodeEmission')
            _node_emission.location = 800,-100
            _node_emission.name = 'ds_pbr_emission'
            _material_links.new(_node_emission.outputs['Emission'], _node_add_shader.inputs[1])

            # Emissive
            
            node=_nodes.new('ShaderNodeTexImage')
            node.location = 600,-100
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_emissive'
            _material_links.new(node.outputs['Color'], _node_emission.inputs['Color'])
        
        # Shader

        node_shader = _nodes.new('ShaderNodeBsdfPrincipled')
        node_shader.location = 400,0
        node_shader.name='ds_pbr_shader'

        if (_ds_pbr_material_options.option_emissive_node == False):
            _material_links.new(node_shader.outputs['BSDF'], _material_output.inputs['Surface'])
        else:
            _material_links.new(node_shader.outputs['BSDF'], _node_add_shader.inputs[0])
        
        if (_ds_pbr_material_options.option_ao_node == True):
            
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

        # Metallic

        if (_ds_pbr_material_options.option_metallic_node == True):

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,-250
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_metallic'
            _material_links.new(node.outputs['Color'], node_shader.inputs['Metallic'])   

        else:
            
            node_shader.inputs['Metallic'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_metallic

        # Specular

        if (_ds_pbr_material_options.option_specular_node == True):

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,-250
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_specular'
            _material_links.new(node.outputs['Color'], node_shader.inputs['Specular'])   

        else:
            
            node_shader.inputs['Specular'].default_value=bpy.context.user_preferences.addons[__name__].preferences.option_specular

        if self.nodes_type=='metallic_roughness':

            # Roughness

            node=_nodes.new('ShaderNodeTexImage')
            node.location = 0,-500
            node.color_space = 'NONE'
            node.name='ds_pbr_texture_roughness'
            _material_links.new(node.outputs['Color'], node_shader.inputs['Roughness'])   

        elif self.nodes_type=='specular_gloss':
        
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

    option_ao_node = BoolProperty(
        name="Ambient Occlusion",
        description="Add Ambient Occlusion Map via RGB Mix Node",
        default = False
    )
    option_metallic_node = BoolProperty(
        name="Metallic Node",
        description="Add Metaliic Node",
        default = False
    )
    option_specular_node = BoolProperty(
        name="Specular Node",
        description="Add Specular Node",
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
        layout.prop(self, 'option_ao_node')
        layout.prop(self, 'option_metallic_node')
        layout.prop(self, 'option_Specular_node')
        layout.prop(self, 'option_metallic')
        layout.prop(self, 'option_specular')

# Material Panel Properties

class ds_pbr_material_options(PropertyGroup):

    def get_option_ao_node(self):
        if "_option_ao_node" not in self:
            self["_option_ao_node"]=bpy.context.user_preferences.addons[__name__].preferences.option_ao_node
        return self["_option_ao_node"]
    def set_option_ao_node(self, value):
        self["_option_ao_node"] = value

    def get_option_metallic_node(self):
        if "_option_metallic_node" not in self:
            self["_option_metallic_node"]=bpy.context.user_preferences.addons[__name__].preferences.option_metallic_node
        return self["_option_metallic_node"]
    def set_option_metallic_node(self, value):
        self["_option_metallic_node"] = value

    def get_option_specular_node(self):
        if "_option_specular_node" not in self:
            self["_option_specular_node"]=bpy.context.user_preferences.addons[__name__].preferences.option_specular_node
        return self["_option_specular_node"]
    def set_option_specular_node(self, value):
        self["_option_specular_node"] = value

    def get_option_relative(self):
        if "_option_relative" not in self:
            self["_option_relative"]=bpy.context.user_preferences.addons[__name__].preferences.option_relative
        return self["_option_relative"]
    def set_option_relative(self, value):
        self["_option_relative"] = value

    option_ao_node = BoolProperty(
        name="Ambient Occlusion",
        description="Add Ambient Occlusion Map via RGB Mix Node",
        get = get_option_ao_node,
        set = set_option_ao_node
    )
    option_metallic_node = BoolProperty(
        name="Metallic Node",
        description="Add Metaliic Node",
        get = get_option_metallic_node,
        set = set_option_metallic_node
    )
    option_specular_node = BoolProperty(
        name="Specular Node",
        description="Add Specular Node",
        get = get_option_specular_node,
        set = set_option_specular_node
    )
    option_emissive_node = BoolProperty(
        name="Emissive Node",
        description="Add Emissive Node",
        default = False
    )     
    option_relative = BoolProperty(
        name="Relative Paths",
        description="Use Relative Paths for images.",
        get = get_option_relative,
        set = set_option_relative
    )
    option_use_matt_name = BoolProperty(
        name="Material Name",
        description="Use Material Name for image matching."
    )
    option_use_mesh_name = BoolProperty(
        name="Mesh Name",
        description="Use Mesh Name for image matching."
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

# File select dialog overrides

class ds_pbr_texture_select_clr(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_select_clr"
    bl_label = "Roughness"
    node_name = bpy.props.StringProperty(
        name="node_name",
        default = ''
    )     
    def execute(self, context):
        context.material.node_tree.nodes['ds_pbr_texture_'+self.node_name].image=None
        return {'FINISHED'}

class ds_pbr_texture_select(bpy.types.Operator):
    bl_idname = "ds_pbr.texture_select"
    bl_label = "Select Image"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    bl_context = "material"
    option_relative = bpy.props.BoolProperty(name="Relative")
    node_name = bpy.props.StringProperty(
        name="Texture",
        default = ''
    )     
    def execute(self, context):
        _nodes = context.material.node_tree.nodes
        if self.option_relative==True:
            _filepath=bpy.path.relpath(self.filepath)
        else:
            _filepath=bpy.path.abspath(self.filepath)
        _nodes['ds_pbr_texture_'+self.node_name].image=bpy.data.images.load(_filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath and context.material.ds_pbr_material_options.option_textures_path:
            self.filepath = context.material.ds_pbr_material_options.option_textures_path
        self.option_relative=context.material.ds_pbr_material_options.option_relative
        context.window_manager.fileselect_add(self)
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

        layout.label('Textures',icon='IMASEL')
        
        # Base Color

        col=layout.row(align=True)
        box=col.row()
        box.label(node_name['base_color']['label'] +':',icon='IMAGE_DATA')
        row=col.row().split(0.85)
        if 'ds_pbr_texture_base_color' in _nodes and _nodes['ds_pbr_texture_base_color'].image:
            row.label(_nodes['ds_pbr_texture_base_color'].image.filepath)
        else:
            row.label('')
        box=row.row().split(0.50)
        box.operator(ds_pbr_texture_select.bl_idname, icon="FILE_FOLDER",text="").node_name='base_color'
        box.operator(ds_pbr_texture_select_clr.bl_idname, icon="X",text="").node_name='base_color'

        if (_ds_pbr_material_options.option_metallic_node == True and 'ds_pbr_texture_metallic' in _nodes):

            # Metallic

            col=layout.row(align=True)
            box=col.row()
            box.label(node_name['metallic']['label'] +':',icon='IMAGE_DATA')
            row=col.row().split(0.85)
            if _nodes['ds_pbr_texture_metallic'].image:
                row.label(_nodes['ds_pbr_texture_metallic'].image.filepath)
            else:
                row.label('')
            box=row.row().split(0.50)
            box.operator(ds_pbr_texture_select.bl_idname, icon="FILE_FOLDER",text="").node_name='metallic'
            box.operator(ds_pbr_texture_select_clr.bl_idname, icon="X",text="").node_name='metallic'

        if (_ds_pbr_material_options.option_specular_node == True and 'ds_pbr_texture_specular' in _nodes):

            # Specular

            col=layout.row(align=True)
            box=col.row()
            box.label(node_name['specular']['label'] +':',icon='IMAGE_DATA')
            row=col.row().split(0.85)
            if _nodes['ds_pbr_texture_specular'].image:
                row.label(_nodes['ds_pbr_texture_specular'].image.filepath)
            else:
                row.label('')
            box=row.row().split(0.50)
            box.operator(ds_pbr_texture_select.bl_idname, icon="FILE_FOLDER",text="").node_name='specular'
            box.operator(ds_pbr_texture_select_clr.bl_idname, icon="X",text="").node_name='specular'

        if (_ds_pbr_material_options.option_ao_node == True):

            if ('ds_pbr_texture_ao' in _nodes):

                # Ambient Occlusion

                col=layout.row(align=True)
                box=col.row()
                box.label(node_name['ao']['label'] +':',icon='IMAGE_DATA')
                row=col.row().split(0.85)
                if _nodes['ds_pbr_texture_ao'].image:
                    row.label(_nodes['ds_pbr_texture_ao'].image.filepath)
                else:
                    row.label('')
                box=row.row().split(0.50)
                box.operator(ds_pbr_texture_select.bl_idname, icon="FILE_FOLDER",text="").node_name='ao'
                box.operator(ds_pbr_texture_select_clr.bl_idname, icon="X",text="").node_name='ao'
        
        # Normal

        col=layout.row(align=True)
        box=col.row()
        box.label(node_name['normal']['label'] +':',icon='IMAGE_DATA')
        row=col.row().split(0.85)
        if 'ds_pbr_texture_normal' in _nodes and _nodes['ds_pbr_texture_normal'].image:
            row.label(_nodes['ds_pbr_texture_normal'].image.filepath)
        else:
            row.label('')
        box=row.row().split(0.50)
        box.operator(ds_pbr_texture_select.bl_idname, icon="FILE_FOLDER",text="").node_name='normal'
        box.operator(ds_pbr_texture_select_clr.bl_idname, icon="X",text="").node_name='normal'
        
        # Roughness

        col=layout.row(align=True)
        box=col.row()
        box.label(node_name['roughness']['label'] +':',icon='IMAGE_DATA')
        row=col.row().split(0.85)
        if 'ds_pbr_texture_roughness' in _nodes and _nodes['ds_pbr_texture_roughness'].image:
            row.label(_nodes['ds_pbr_texture_roughness'].image.filepath)
        else:
            row.label('')
        box=row.row().split(0.50)
        box.operator(ds_pbr_texture_select.bl_idname, icon="FILE_FOLDER",text="").node_name='roughness'
        box.operator(ds_pbr_texture_select_clr.bl_idname, icon="X",text="").node_name='roughness'

        if 'ds_pbr_texture_emissive' in _nodes:

            col=layout.row(align=True)
            box=col.row()
            box.label(node_name['emissive']['label'] +':',icon='IMAGE_DATA')
            row=col.row().split(0.85)
            if _nodes['ds_pbr_texture_emissive'].image:
                row.label(_nodes['ds_pbr_texture_emissive'].image.filepath)
            else:
                row.label('')
            box=row.row().split(0.50)
            box.operator(ds_pbr_texture_select.bl_idname, icon="FILE_FOLDER",text="").node_name='emissive'
            box.operator(ds_pbr_texture_select_clr.bl_idname, icon="X",text="").node_name='emissive'

        # Check if .blend file is saved

        if not bpy.data.filepath and _ds_pbr_material_options.option_relative == True:
            layout.label('Blender file not saved. Required for relative paths.',icon='ERROR')

        # Relative Paths

        col=layout.row(align=True)
        box=col.row()
        box.prop(_ds_pbr_material_options, "option_relative")
        box=col.row()
        box.prop(_ds_pbr_material_options, "option_use_mesh_name")
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
        box.prop(_ds_pbr_material_options, "option_ao_node")
        box.prop(_ds_pbr_material_options, "option_metallic_node")
        box.prop(_ds_pbr_material_options, "option_specular_node")
        box.prop(_ds_pbr_material_options, "option_emissive_node")
        
        box=row.column()
        box.label('Nodes',icon='NODETREE')

        row = box.row()

        if _ds_pbr_material_options.option_textures_path=='':
            row.enabled = False

        box.operator("ds_pbr.nodes_auto")

        box.operator("ds_pbr.nodes",text='Create Metallic Roughness').nodes_type='metallic_roughness'
        box.operator("ds_pbr.nodes",text='Create Specular Gloss').nodes_type='specular_gloss'
        box.operator("ds_pbr.nodes_remove")

        layout.separator()

def register():

    from bpy.utils import register_class

    register_class(ds_pbr_render_cycles)
    register_class(ds_pbr_render_game)

    register_class(ds_pbr_texture_select)
    register_class(ds_pbr_texture_select_clr)    

    register_class(ds_pbr_textures_path_select)
    register_class(ds_pbr_textures_path_select_clr)

    register_class(ds_pbr_addon_prefs)
    register_class(ds_pbr_material_options)
    register_class(ds_pbr_nodes_remove)
    register_class(ds_pbr_auto_textures)
    register_class(ds_pbr_nodes_auto)
    register_class(ds_pbr_nodes)
    register_class(ds_pbr_material)

    bpy.types.Material.ds_pbr_material_options = PointerProperty(type=ds_pbr_material_options)

def unregister():

    from bpy.utils import unregister_class

    unregister_class(ds_pbr_render_cycles)
    unregister_class(ds_pbr_render_game)

    unregister_class(ds_pbr_texture_select)
    unregister_class(ds_pbr_texture_select_clr)    
    
    unregister_class(ds_pbr_textures_path_select)
    unregister_class(ds_pbr_textures_path_select_clr)

    unregister_class(ds_pbr_addon_prefs)
    unregister_class(ds_pbr_material_options)
    unregister_class(ds_pbr_nodes_remove)
    unregister_class(ds_pbr_auto_textures)
    unregister_class(ds_pbr_nodes_auto)
    unregister_class(ds_pbr_nodes)
    unregister_class(ds_pbr_material)

    del bpy.types.Material.ds_pbr_material_options

if __name__ == "__main__":

    register()