import bpy
import time
import os
from mathutils import Vector
import numpy as np


from bpy.props import (StringProperty,
                       BoolProperty,
                       PointerProperty,
                       FloatProperty,
                       IntProperty,
                       FloatVectorProperty
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
                       
                       
from bpy_extras.io_utils import ImportHelper

from .parser import *
from .utils import *





class gcode_settings(bpy.types.PropertyGroup): 
    
    flow_map: StringProperty(
        name="Flow Multiplier weightmap - grayscale of vertex color gets mapped to min and max range",
        default="Flow"
        )
    speed_map: StringProperty(
        name="Speed Multiplier weightmap - grayscale of vertex color gets mapped to min and max range",
        default="Speed"
        )
        
         
    T0: StringProperty(
        name="Custom G-code per color",
        default="T0"
        )
    T1: StringProperty(
        name="Custom G-code per color",
        default="T1"
        )
        
    start: StringProperty(
        name="Start G-code to append to every exported G-code file",
        default="Start"
        )
    end: StringProperty(
        name="End G-code to append to every exported G-code file",
        default="End"
        )

    split_layers: BoolProperty(
        name="Split into Layers",
        description="Save every layer as single Object in Collection",
        default = False
        )

    subdivide: BoolProperty(
        name="Line Segmentation",
        description="Subdivide Segments that are bigger then value, needed to increase resolution when modifyng the mesh",
        default = False
        )
        
        
    tool_color: BoolProperty(
        name="Toolchange based on color:",
        description="Will insert textblock associated with that color. Color value is taken from 'Tool' Vertex Color map",
        default = False
        )

    max_segment_size: FloatProperty(
        name = "",
        description = "Only Segments bigger then this value get subdivided, too small values here can cause performance issues",
        default = 1,
        min = 0.1,
        max = 999.0
        )

    min_flow: FloatProperty(
        name = "",
        description = "Factor the extrusion value is multiplied with based on the underlying vertex color of that segment",
        default = 0.4
        )
    max_flow: FloatProperty(
        name = "",
        description = "Factor the extrusion value is multiplied with based on the underlying vertex color of that segment",
        default = 1.
        )
        
    min_speed: FloatProperty(
        name = "",
        description = "Factor the extrusion speed value is multiplied with based on the underlying vertex color of that segment",
        default = 0.2
        )
    max_speed: FloatProperty(
        name = "",
        description = "Factor the extrusion speed value is multiplied with based on the underlying vertex color of that segment",
        default = 1.
        )
        
                
    travel_speed: IntProperty(
        name = "",
        description = "In mm/s. Exported G-code will have mm/min though",
        default = 60
        )
        
    extrusion_speed: IntProperty(
        name = "",
        description = "In mm/s. Exported G-code will have mm/min though",
        default = 30
        )
        

    color_T0: FloatVectorProperty(
        name="Color",
        description="When ever this color is reached on export, add custom G-code in T0 textblock to export file",
        subtype='COLOR', size=3, min=0, max=1, precision=3, step=0.1,
        default=(1.0, 1.0, 1.0)
    )
    
    color_T1: FloatVectorProperty(
        name="Color",
        description="When ever this color is reached on export, add custom G-code in T0 textblock to export file",
        subtype='COLOR', size=3, min=0, max=1, precision=3, step=0.1,
        default=(0.0, 0.0, 0.0)
    )





class NOZZLEBOSS_PT_Panel(bpy.types.Panel):
 
    bl_label = "nozzleboss"
    bl_idname = 'NOZZLEBOSS_PT_Panel' 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "nozzleboss" 
    
    
#   @classmethod
#   def poll(cls, context):
#       try: return context.object.type in ('MESH')
#        except: return False


    def draw(self, context): 
        layout = self.layout 

        scn = context.scene
        nozzleboss = scn.nozzleboss 
        obj = context.object
        

        col = layout.box().column(align=True)
        col.label(text="Import settings:")
   
        
        row = col.row(align=True)
        row.prop(nozzleboss, 'subdivide')

        sub = row.row()
        sub.prop(nozzleboss, "max_segment_size")  
        sub.enabled =  nozzleboss.subdivide #sub is not grayed out when 'linesegmentatio/subdivide/ bool is True
         
         
        col2=col.column(align=True) 
        col2.scale_y=1.5
        col2.separator(factor=1)
        col2.operator("wm.gcode_import") #call it by id name, since specified, otherwise just takes class name
        col.separator(factor=1)

        
        col = layout.box().column(align=True)
        col.label(text="Export settings:")
        col.prop(nozzleboss, "travel_speed", text='Travel Speed')
        col.prop(nozzleboss, "extrusion_speed", text='Extrusion Speed')

        col.separator(factor=1.5)
        
        row=col.row() #aus col new row machen, beginnt neue zeile und startet dann in der reihe
        row.label(text="Flow Multiplier:") 
        row.separator(factor=2)
        row.label(text="min:") 
        row.label(text="max:") 
        row = col.row(align=True)
        row.prop_search(nozzleboss, "flow_map", context.active_object.data, "vertex_colors", text="")
        row.separator()
        row.prop(nozzleboss, "min_flow")
        row.prop(nozzleboss, "max_flow")

        col.separator()
        col.label(text="Speed Multiplier:") 
        row = col.row(align=True)
        row.prop_search(nozzleboss, "speed_map", context.active_object.data, "vertex_colors", text="")    
        row.separator()   
        row.prop(nozzleboss, "min_speed")
        row.prop(nozzleboss, "max_speed")
     
        col.separator(factor=2)
    
        #col.label(text="Tool change based on color:") 
        col.prop(nozzleboss, 'tool_color')
       
        
        row = col.row(align=True)
        row.enabled = nozzleboss.tool_color
        row.prop(nozzleboss, "color_T0", text="")
        row.prop_search(nozzleboss, "T0", bpy.data, "texts", text="")   
        row.separator(factor=2)   
        row.prop(nozzleboss, "color_T1", text="")
        row.prop_search(nozzleboss, "T1", bpy.data, "texts", text="")   


        col.separator(factor=2)

        row=col.row(align=True) #start new column in row mode (row mode every element gets put behind each other)
        row.label(text='Start G-code:')
        row.prop_search(nozzleboss, "start", bpy.data, "texts", text="")   
        row=col.row(align=True)
        row.label(text='End G-code:')
        row.prop_search(nozzleboss, "end", bpy.data, "texts", text="")   
        
        col.separator(factor=2)
        row=col.row(align=True) 
        #row.label(text='Start G-code:')
        row.scale_y= 1.5# only works on operators and not on labels i think
        row.operator("wm.gcode_export")
        

        
        
    

def import_gcode(context, filepath):
        scene = context.scene
        nozzleboss = scene.nozzleboss
        
        import time
        then = time.time()

        parse = GcodeParser()
        model = parse.parseFile(filepath)
        
        if nozzleboss.subdivide:
            model.subdivide(nozzleboss.max_segment_size)
        model.classifySegments()
        if nozzleboss.split_layers:
            model.draw(split_layers=True)
        else:
            model.draw(split_layers=False)
            
        

        now=time.time()
        print("then", then)
        print("importing Gcode took", now-then)

        return {'FINISHED'} 
    
    
def export_gcode(context):

    scene = context.scene
    nozzleboss = scene.nozzleboss
    then=time.time()
    filename = bpy.path.basename(bpy.data.filepath)
    filename = os.path.splitext(filename)[0] #strip .blend extension
    gcode_txt = open(bpy.path.abspath("//")+bpy.path.basename(filename)+".gcode","w")

    _txt = []
    start_code = read_textblock('Start')+'\n'#'G28\nM140 S50\nM109 S190\nM83\nG1 F600\n;RGB,-1,-1,-1\nM163 S0 P0\nM163 S1 P0\nM163 S2 P1\nM163 S3 P1\nM163 S4 P1\nM164 S0\nT0\n'
    _txt.append(start_code)
    extrusion_speed = nozzleboss.extrusion_speed
    travel_speed = nozzleboss.travel_speed




    obj = bpy.context.active_object
    verts = read_verts(obj.data)
    edges = read_edges(obj.data)
    #initial values
    P2=(0,0,0)
    prev_F=-1
    prev_tool_color = -1

    #create vertex colors maps, most cases importer could already do that, but in case you have handdrawn/beveled extrusion path
    if not obj.data.vertex_colors.get('Flow'):
        obj.data.vertex_colors.new(name='Flow')
    if not obj.data.vertex_colors.get('Speed'):
        obj.data.vertex_colors.new(name='Speed')
    if not obj.data.vertex_colors.get('Speed'):
        obj.data.vertex_colors.new(name='Speed')
    if not obj.data.vertex_colors.get('Tool'):
        obj.data.vertex_colors.new(name='Tool')
        
        
    #Read extrusion and speed multiplier vertex color map
    #gets right loop color for every v_idx
    extrusion_weights = read_weightmap_from_vcol(obj, 'Flow')
    speed_weights = read_weightmap_from_vcol(obj, 'Speed')
    tool_colors = read_weightmap_from_vcol(obj, 'Tool')
    
    #auto create textblocks to, need if you model from scratch (if you import existing they get created in parser)
    if not bpy.data.texts.get('T0'):
        bpy.data.texts.new('T0')
        bpy.data.texts['T0'].write('T0; switch to extruder T0 (any G-code macro can be passed here)\n')
    if not bpy.data.texts.get('T1'):
        bpy.data.texts.new('T1')
        bpy.data.texts['T1'].write('T1; switch to extruder T1 (any G-code macro can be passed here)\n')
    if not bpy.data.texts.get('Start'):
        bpy.data.texts.new('Start')
        bpy.data.texts['Start'].write(';nozzleboss\n')
        bpy.data.texts['Start'].write('G28 ;homing\n')
        bpy.data.texts['Start'].write('M104 S180 ;set hotend temp\n')
        bpy.data.texts['Start'].write('M190 S50 ;wait for bed temp\n')
        bpy.data.texts['Start'].write('M109 S200 ;wait for hotendtemp\n')
        bpy.data.texts['Start'].write('M83; relative extrusion mode (REQUIRED)\n')

    if not bpy.data.texts.get('End'):
        bpy.data.texts.new('End')
        bpy.data.texts['End'].write('G10 ;retract\n')
        bpy.data.texts['End'].write('M104 S0 ;deactivate hotend\n')
        bpy.data.texts['End'].write('M140 S0 ;deactivate bed\n')
        bpy.data.texts['End'].write('G28 ;homing\n')
        bpy.data.texts['End'].write('M84 ;turn off motors\n')





    islands = find_islands(edges)
    sorted_islands = sort_Z(islands, verts)
                                  
                                  
    ##islands of extrusions vert indices
    for island in sorted_islands:
        travel_dist = (Vector(verts[island[0]])-Vector(P2)).length #only retract when travel is longer than...
        if travel_dist > 1:
            _txt.append('G10 \n')
        
        #travel only from island to island    
        _txt.append(travel(P2,verts[island[0]], travel_speed*60, extrusion_speed*60)) #verts[island[0]]=next coords
        
        if travel_dist > 1:
            _txt.append('G11 \n')   
            
            
        
        #extrusion and height edges per island, parallel arrays
        e_edges = island[:int(len(island)/2)] #first half extrusion v_idx, real nozzle path
        h_edges = island[int(len(island)/2):] #second half of island corresponding height v_idx
        #print(h_edges)
        

            
            
        #extrude between all poitns in island
        for i in range(len(e_edges)): 
            if i == len(e_edges)-1:#break on last segment, if you want to close segment, 'rip' the last vert
              break
              

            #coord for seg length and height
            P1 = verts[e_edges[i]]
            P2 = verts[e_edges[i+1]]
            P3 = verts[h_edges[i+1]] 



    #calcE
            dist = np.linalg.norm(P2-P1)
            height=np.linalg.norm(P3-P2)

            width=height*1.5
            multiplier = extrusion_weights[e_edges[i+1]]#
            multiplier = remap(multiplier, nozzleboss.min_flow, nozzleboss.max_flow)
            E_volume=dist*height*width*multiplier
            E=E_volume/2.405281875  ##E axis in mm not mm³, 2.405 is 1mm of 1.75mm filament (r*(PI*r), 0.875*PI*0.875


    #calcF

            speed_weight =  remap(speed_weights[e_edges[i]], nozzleboss.min_speed, nozzleboss.max_speed)
            F = extrusion_speed*speed_weight 

            #check if tool color changed and append corresponding textblock
            if tool_colors[e_edges[i+1]]!=prev_tool_color:

                if tool_colors[e_edges[i+1]]<0.5:
                    _txt.append(read_textblock('T1'))
                else:
                    _txt.append(read_textblock('T0'))  

                prev_tool_color=tool_colors[e_edges[i+1]]   


            _txt.append(extrude(P1, P2, E, F, prev_F)) 


    #print(_txt)
    end_code = '\n'+read_textblock('End')
    
    
    _txt.append(end_code)
    gcode_txt.write(''.join(_txt))
    gcode_txt.close()

    
    print("took in seconds: ",time.time()-then)
    return {'FINISHED'}     
    


class WM_OT_gcode_import(Operator, ImportHelper):
    """Import Gcode, travel lines don't get drawn"""
    bl_idname = "wm.gcode_import"  
    bl_label = "Import G-code"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    
    def execute(self, context):
        return import_gcode(context, self.filepath)   
    
    
    
class WM_OT_gcode_export(Operator):
    bl_idname = "wm.gcode_export"  
    bl_label = "Export to G-code"
    bl_description = "Export active Object to G-code. Result can be found in folder of current .blend file"
    
    
    @classmethod
    def poll(cls, context):
        try:
            return context.object.type in ('MESH')
        except:
            return False

        
    def execute(self, context):
        return export_gcode(context)   
    
    
    
    



def register():
    bpy.utils.register_class(NOZZLEBOSS_PT_Panel)
    bpy.utils.register_class(gcode_settings)
    bpy.utils.register_class(WM_OT_gcode_import)
    bpy.utils.register_class(WM_OT_gcode_export)
    bpy.types.Scene.nozzleboss = bpy.props.PointerProperty(type= gcode_settings)
 



def unregister():
    bpy.utils.unregister_class(NOZZLEBOSS_PT_Panel)



if __name__ == "__main__":
    register()
