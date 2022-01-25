#!/usr/bin/env python
import bpy, bmesh
import math

import re
import numpy as np
np.set_printoptions(suppress=True)

from .utils import bevel_path


def segments_to_meshdata(segments):#edges only on extrusion
        segs = segments
        verts=[]
        edges=[]
        del_offset=0 #to travel segs in a row, one gets deleted, need to keep track of index for edges
        for i in range(len(segs)):
                if i>=len(segs)-1:
                        if segs[i].style == 'extrude':
                                verts.append([segs[i].coords['X'],segs[i].coords['Y'],segs[i].coords['Z'] ])

                        break

                #start of extrusion for first time
                if segs[i].style == 'travel' and segs[i+1].style == 'extrude':
                        verts.append([segs[i].coords['X'],segs[i].coords['Y'],segs[i].coords['Z'] ])
                        verts.append([segs[i+1].coords['X'],segs[i+1].coords['Y'],segs[i+1].coords['Z'] ])
                        edges.append([i-del_offset,(i-del_offset)+1])

                #mitte, current and next are extrusion, only add next, current is already in vert list
                if segs[i].style == 'extrude' and segs[i+1].style == 'extrude':
                        verts.append([segs[i+1].coords['X'],segs[i+1].coords['Y'],segs[i+1].coords['Z'] ])
                        edges.append([i-del_offset,(i-del_offset)+1])

   

                if segs[i].style == 'travel' and segs[i+1].style == 'travel':
                        del_offset+=1

        return verts, edges
        
 


def obj_from_pydata(name, verts, edges=None, close=True, collection_name=None):
    if edges is None:
        # join vertices into one uninterrupted chain of edges.
        edges = [[i, i+1] for i in range(len(verts)-1)]
        if close:
            edges.append([len(verts)-1, 0]) #connect last to first
            
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, edges, [])   
      
    obj = bpy.data.objects.new(name, me)
   
   
    #Move into collection if specified
    if collection_name != None: #make argument optional
        
        #collection exists                   
        collection = bpy.data.collections.get(collection_name)
        if collection: 
            bpy.data.collections[collection_name].objects.link(obj)   
            
        
        else:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection) #link collection to main scene
            bpy.data.collections[collection_name].objects.link(obj) 
    
    return obj





class GcodeParser:
        comment = "" 
        
        def __init__(self):
                self.model = GcodeModel(self)
        
        def parseFile(self, path):
                # read the gcode file
                with open(path, 'r') as f:
                        # init line counter
                        self.lineNb = 0
                        # for all lines
                        for line in f:
                                # inc line counter
                                self.lineNb += 1
                                # remove trailing linefeed
                                self.line = line.rstrip()
                                # parse a line
                                self.parseLine()
                        
                #self.model.postProcess()
                return self.model
                
        def parseLine(self):
                # strip comments:
                bits = self.line.split(';',1)
                if (len(bits) > 1):
                    GcodeParser.comment = bits[1]
                
                # extract & clean command
                command = bits[0].strip()
                
                # TODO strip logical line number & checksum
                
                # code is fist word, then args
                comm = command.split(None, 1)
                code = comm[0] if (len(comm)>0) else None
                args = comm[1] if (len(comm)>1) else None
                
                if code:
                        if hasattr(self, "parse_"+code):
                                getattr(self, "parse_"+code)(args)
                                #self.parseArgs(args)
                        else:
                            if code[0] == "T":
                                
                                self.model.toolnumber = int(code[1:])
                                #print(self.model.toolnumber)
                            else:
                                pass
                                #print("incorrect gcode")#self.warn("Unknown code '%s'"%code)
                
        def parseArgs(self, args):
                dic = {}
                if args:
                        bits = args.split()
                        for bit in bits:
                                letter = bit[0]
                                try:
                                        coord = float(bit[1:])
                                except ValueError:
                                        coord = 1
                                dic[letter] = coord
                return dic
            

        def parse_G1(self, args, type="G1"):
                # G1: Controlled move
                self.model.do_G1(self.parseArgs(args), type)

        def parse_G0(self, args, type="G0"):
                # G1: Controlled move
                self.model.do_G1(self.parseArgs(args), type)

                        
        def parse_G90(self, args):
                # G90: Set to Absolute Positioning
                self.model.setRelative(False)
                
        def parse_G91(self, args):
                # G91: Set to Relative Positioning
                self.model.setRelative(True)
                
        def parse_G92(self, args):
                # G92: Set Position
                self.model.do_G92(self.parseArgs(args))
                
        # def parse_M163(self, args):
        #         self.model.do_M163(self.parseArgs(args))
                
        def warn(self, msg):
                print ("[WARN] Line %d: %s (Text:'%s')" % (self.lineNb, msg, self.line))
                
        def error(self, msg):
                print ("[ERROR] Line %d: %s (Text:'%s')" % (self.lineNb, msg, self.line))
                raise Exception("[ERROR] Line %d: %s (Text:'%s')" % (self.lineNb, msg, self.line))
        

class GcodeModel:
        
        def __init__(self, parser):
                # save parser for messages
                self.parser = parser
                # latest coordinates & extrusion relative to offset, feedrate
                self.relative = {
                        "X":0.0,
                        "Y":0.0,
                        "Z":0.0,
                        "F":0.0,
                        "E":0.0}
                # offsets for relative coordinates and position reset (G92)
                self.offset = {
                        "X":0.0,
                        "Y":0.0,
                        "Z":0.0,
                        "E":0.0}
                # if true, args for move (G1) are given relatively (default: absolute)
                self.isRelative = False
                self.color = [0,0,0,0,0,0,0,0] #RGBCMYKW
                self.toolnumber = 0
                
                # the segments
                self.segments = []
                self.layers = []
                #self.distance = None
                #self.extrudate = None
                #self.bbox = None
                
        def do_G1(self, args, type):
                # G0/G1: Rapid/Controlled move
                # clone previous coords
                coords = dict(self.relative)

                # update changed coords
                for axis in args.keys():
                        #print(coords)                    
                        if axis in coords:
                                if self.isRelative: 
                                        coords[axis] += args[axis]
                                else:
                                        coords[axis] = args[axis]
                        else:
                                self.warn("Unknown axis '%s'"%axis)
                                
                # build segment
                absolute = {
                        "X": self.offset["X"] + coords["X"],
                        "Y": self.offset["Y"] + coords["Y"],
                        "Z": self.offset["Z"] + coords["Z"],
                        "F": coords["F"]       # no feedrate offset
                       
                         #self.offset["E"] +    ofsett wont work for relative E
                }
                
                #if gcode line has no E = travel move
                #but still add E = 0 to segment (so coords dictionaries have same shape for subdividing linspace function)
                if "E" not in args :#"E" in coords:
                    absolute["E"] = 0
                else:
                    absolute["E"] = args["E"]
                    
                    
          
                seg = Segment(
                        type,
                        absolute,
                        self.color,
                        self.toolnumber,
                        #self.layerIdx,
                        self.parser.lineNb,
                        self.parser.line)
             
                if seg.coords['X'] != self.relative['X']+self.offset["X"] or seg.coords['Y'] != self.relative['Y']+self.offset["Y"] or seg.coords['Z'] != self.relative['Z']+self.offset["Z"]:     
                    self.addSegment(seg)
                    
                    

                # update model coords
                self.relative = coords
                
        def do_G92(self, args):
                # G92: Set Position
                # this changes the current coords, without moving, so do not generate a segment
                
                # no axes mentioned == all axes to 0
                if not len(args.keys()):
                        args = {"X":0.0, "Y":0.0, "Z":0.0} #, "E":0.0 
                # update specified axes
                for axis in args.keys():
                        if axis in self.offset:
                                # transfer value from relative to offset
                                self.offset[axis] += self.relative[axis] - args[axis]
                                self.relative[axis] = args[axis]
                        else:
                                self.warn("Unknown axis '%s'"%axis)
                                
        def do_M163(self, args):
                #seg color [R,G,B,C,Y,M,K,W]
                col = list(self.color)    #list() creates new list, otherwise you just change reference and all segs have same color
                extr_idx = int(args['S']) # e.g. M163 S0 P1
                weight = args['P']
                #change CMYKW
                col[extr_idx+3] = weight #+3 weil ersten 3 stellen RGB sind, need only CMYKW values for extrude
                self.color = col
                
                #take RGB values for seg from last comment (above first M163 statement)
                comment = eval(GcodeParser.comment) #string comment to list
                #RGB = [GcodeParser.comment[1], GcodeParser.com
                RGB = comment[:3]
                self.color[:3] = RGB
                


        def setRelative(self, isRelative):
                self.isRelative = isRelative
                
        def addSegment(self, segment):
                self.segments.append(segment)
                
                
        def warn(self, msg):
                self.parser.warn(msg)
                
        def error(self, msg):
                self.parser.error(msg)

        def classifySegments(self):
                
                # start model at 0, act as prev_coords
                coords = {
                        "X":0.0,
                        "Y":0.0,
                        "Z":0.0,
                        "F":0.0,
                        "E":0.0}
                        
                # first layer at Z=0
                currentLayerIdx = 0
                currentLayerZ = 0 #better to use self.first_layer_height
                layer = []#add layer to model.layers
                
                for i, seg in enumerate(self.segments):
                        # default style is travel (move, no extrusion)
                        style = "travel"
                        
                        
                        # some horizontal movement, and positive extruder movement: extrusion
                        if (
                                ( (seg.coords["X"] != coords["X"]) or (seg.coords["Y"] != coords["Y"]) or (seg.coords["Z"] != coords["Z"]) ) and
                                (seg.coords["E"] > 0 ) ): #!= coords["E"]
                                style = "extrude"


                        #segments to layer lists
                        #look ahead and if next seg has E and differenz Z, add new layer for current segment
                        if i==len(self.segments)-1:
                                layer.append(seg)
                                currentLayerIdx += 1
                                seg.style = style
                                seg.layerIdx = currentLayerIdx
                                self.layers.append(layer)#add layer to list of Layers, used to later draw single layer objects
                                break
                        
                        # positive extruder movement of next point in a different Z signals a layer change for this segment
                        if self.segments[i].coords["Z"]  != currentLayerZ and self.segments[i+1].coords["E"]>0:
                            self.layers.append(layer)#layer abschließen, add layer to list of Layers, used to later draw single layer objects
                            layer = [] #start new layer
                            currentLayerZ = seg.coords["Z"]
                            currentLayerIdx += 1
                            #prev_seg.layerIdx = currentLayerIdx # lookback, previous point before texrsuion is part of new layer too, both create an edge

                        # set style and layer in segment
                        seg.style = style
                        seg.layerIdx = currentLayerIdx
                        layer.append(seg)
                        coords = seg.coords

        def subdivide(self, subd_threshold):
            #divide edge if > subd_threshold

                subdivided_segs=[]
                
                # start model at 0
                coords = {
                        "X":0.0,
                        "Y":0.0,
                        "Z":0.0,
                        "F":0.0, #no interpolation
                        "E":0.0}

                for seg in self.segments:
                        # calc XYZ distance
                        d  = (seg.coords["X"]-coords["X"])**2
                        d += (seg.coords["Y"]-coords["Y"])**2
                        d += (seg.coords["Z"]-coords["Z"])**2
                        seg.distance = math.sqrt(d)
                        
                        if seg.distance > subd_threshold:
                                
                                subdivs=math.ceil(seg.distance/subd_threshold) #ceil makes sure that linspace interval is at least 2
                                #print("num of subd: ", math.ceil(subdivs))
                                P1=coords
                                P2=seg.coords

                                #interpolated points
                                interp_coords = np.linspace(list(P1.values()), list(P2.values()), num=subdivs, endpoint=True)

                                for i in range(len(interp_coords)):   #inteprolated points array back to segment object

                                       new_coords = {"X":interp_coords[i][0], "Y":interp_coords[i][1], "Z":interp_coords[i][2], "F":seg.coords["F"]}  #E/subdivs is for relative extrusion, absolute extrusion need "E":interp_coords[i][4]
                                       #print("interp_coords_new:", new_coords)
                                       if seg.coords["E"] > 0:
                                           new_coords["E"] = round(seg.coords["E"]/(subdivs-1),5)
                                       else:
                                           new_coords["E"] = 0
                                           
                                           
                                           
                                       #make sure P1 hasn't been written before, compare with previous line
                                       if new_coords['X'] != coords['X'] or new_coords['Y'] != coords['Y'] or new_coords['Z'] != coords['Z']:   #write segment only if movement changes, avoid double coordinates due to same start and endpoint of linspace
                                               
                                               new_seg=Segment(seg.type, new_coords, seg.color, seg.toolnumber, seg.lineNb, seg.line)
                                               new_seg.layerIdx = seg.layerIdx
                                               new_seg.style = seg.style
                                               subdivided_segs.append(new_seg)
                                                             
                        else:
                                
                                subdivided_segs.append(seg) 

                                
                        coords = seg.coords #P1 becomes P2

                self.segments=subdivided_segs
                

                 
            
        #create blender curve and vertex_info in text file(coords, style, color...)
        def draw(self, split_layers=False):
                if split_layers:
                        i=0
                        for layer in self.layers:
                                verts, edges = segments_to_meshdata(layer)
                                if len(verts)>0:
                                        obj_from_pydata(str(i), verts, edges, close=False, collection_name="Layers")
                                        i+=1

                else:
                        verts, edges = segments_to_meshdata(self.segments)
                        obj = obj_from_pydata("Gcode", verts, edges, close=False, collection_name="Layers")
                        
                        #set active and bevel
                        bpy.context.view_layer.objects.active = bpy.data.objects[obj.name]
                        bevel_path(bpy.data.objects[obj.name])
                        
                        #create vcol maps and textblocks
                        obj.data.vertex_colors.new(name='Speed')
                        obj.data.vertex_colors.new(name='Flow')
                        obj.data.vertex_colors.new(name='Tool')

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




                


class Segment:
        def __init__(self, type, coords, color, toolnumber, lineNb, line):
                self.type = type
                self.coords = coords
                self.color = color
                self.toolnumber = toolnumber
                self.lineNb = lineNb
                self.line = line
                self.style = None
                self.layerIdx = None
                
                #self.distance = None
                #self.extrudate = None
        def __str__(self):
                return " <coords=%s, lineNb=%d, style=%s, layerIdx=%d, color=%s"%(str(self.coords), self.lineNb, self.style, self.layerIdx, str(self.color))     
            
class Layer:
        def __init__(self, Z):
            self.Z = Z
            self.segments = []
            self.distance = None
            self.extrudate = None
            
        def __str__(self):
            return "<Layer: Z=%f, len(segments)=%d>"%(self.Z, len(self.segments))     
        


        

if __name__ == '__main__':
        path = "test.gcode"

        parser = GcodeParser()
        model = parser.parseFile(path)
        
        
        
