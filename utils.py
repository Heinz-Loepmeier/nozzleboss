import bpy
import numpy as np
import bmesh

def read_verts(mesh):
    mverts_co = np.zeros((len(mesh.vertices) * 3), dtype=float)
    mesh.vertices.foreach_get("co", mverts_co)
    return np.reshape(mverts_co, (len(mesh.vertices), 3))


def read_edges(mesh): #return np.array
    fastedges = np.zeros((len(mesh.edges)*2), dtype=int) # [0.0, 0.0] * len(mesh.edges)
    mesh.edges.foreach_get("vertices", fastedges)
    return np.reshape(fastedges, (len(mesh.edges), 2))


def read_textblock(name):
    txt = bpy.data.texts[name]
    textblock=[]
    for l in txt.lines:
        textblock.append(l.body+'\n')   
            
    textblock="".join(textblock) 
    return textblock


def travel(coords, next, travel_speed, extrusion_speed):
    x,y,z = coords[0], coords[1], coords[2]
    next_x, next_y, next_z = next[0], next[1], next[2]
    gcode_cmd=''

    gcode_cmd+='G1 F'+str(travel_speed)+'\n'
        
    gcode_cmd+='G1 '
    
    #only changed coords
    if next_x!=x:
        gcode_cmd+='X'+str(round(next_x,4))+' '
    if next_y!=y:
        gcode_cmd+='Y'+str(round(next_y,4))+' '
    if next_z!=z:
        gcode_cmd+='Z'+str(round(next_z,4))
#    gcode_cmd+='G11 \n'
#        

    gcode_cmd+='\nG1 '+'F'+str(extrusion_speed)+'\n'  
    
    return gcode_cmd



#only print changed axis
def extrude(coords, next, E, F, prev_F):
    gcode_cmd='G1 '
    x,y,z = coords[0], coords[1], coords[2]
    next_x, next_y, next_z = next[0], next[1], next[2]
    
    if x!=next_x:
        gcode_cmd+='X'+str(round(next_x,4))+' '
    if y!=next_y:
        gcode_cmd+='Y'+str(round(next_y,4))+' '
    if z!=next_z: 
        gcode_cmd+='Z'+str(round(next_z,4))+' '
    
    gcode_cmd+= 'E'+str(round(E,4))
    
        #cweighted speed, put in extrude function later
    if F!=prev_F:          
        gcode_cmd+=(' F'+str(int(F*60))+'\n')  
        prev_F=F   
                
    #return string of changed coords
    return gcode_cmd

def bevel_path(obj):#ver_idx wise only extrude, but in respect to layerheight and with vasemode detection
                    #and clean-up loose verts before extruding
                    
    #check if verts are connected, needed for vase mode detection
    def verts_connected(vidx_start, vidx_end):  
        depth = vidx_end-vidx_start
          
        all_connected=[]
        for i in range(depth):

            #check for each vert pair
            P1=bm.verts[i]
            P2=bm.verts[i+1]
            
            #check if vert pair is connected
            pair_connected=[]
            for e in P1.link_edges:

                if e in P2.link_edges:#only need to find one True here
                    pair_connected.append(True)


            #if any edge is shared by both verts, the vert pair has a connection
            if any(pair_connected):
                all_connected.append(True) 
                
            else:
                all_connected.append(False)
                

        #if all vert pairs were connected the edge path is continous        
        if all(all_connected) and len(all_connected)>0:
            #print('all verts are connected')   
            return True
            
        else:
            #print('path is broken')
            return False




    #cleanup, delete loose verts. cause extruding them will cause edge without face loop/without vertex color
    #own gcode parser seems to add needle vert to 
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete_loose(use_edges=False)
    bpy.ops.object.mode_set(mode='OBJECT')



    bm = bmesh.new()
    bm.from_mesh(obj.data)


    extruded = bmesh.ops.extrude_edge_only(bm, edges=[e for e in bm.edges]) 

    #return only bmverts from geom
    translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]

    #move extruded verts by layer_height
    #every z change is layer change, can handle variable layer height and vasemode (but not vasemode with variable layer_height)
    #becomes tricky with vasemode
    #first layer is non-planar und provides base
    #only on second layer spiraling starts
    # -on spiral start very small layerheight/extrusion
    # -increasing layer height until constant layer_height is reached

    old_Z=0

    normalmode = True
    start_spiraling = False
    vasemode=False

    first_layer_height = translate_verts[0].co[2]#first layer as reference for layerheight


    bm.verts.ensure_lookup_table()
    for v in translate_verts:

        cur_Z = round(v.co[2],5)
      
        #layer_change or start of spiraling mode  or already ion final vasemopde
        if old_Z!=cur_Z:

            #3 connected verts with changing Z-heught=spiraling vasemode
            if not vasemode: #no further spiralstart checks once you entered vase mode      
                if verts_connected(v.index, v.index+3) and v.co[2]<bm.verts[v.index+3].co[2]:#different Z = start spiral/increment layerheight
                    start_spiraling=True
                    normalmode=False
            
            
            if normalmode:
                layer_height=(cur_Z-old_Z)#+0.3
                old_Z=cur_Z
            

                
            elif start_spiraling:
                
                #increment layer height 
                layer_height = (cur_Z-first_layer_height)#layer_height-(v.co[2]-old_Z) #0.3 - (0.33-0.3)

                
               # until spirale reaches full layerheight
                if layer_height>first_layer_height:
                   # print(' reached vase mndoe')
                    vasemode=True
                    start_spiraling=False
                  
                    
                
            
            elif vasemode:#layer height stays constant after spiraling in
                layer_height=first_layer_height
                
                 
        #translate down   
        v.co[2]-=layer_height
            
        
        

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    
    
    
#find loose parts/islands in list np.array of edges
def find_islands(edges):
    
    lparts=[]
    paths={v_idx:set() for v_idx in edges.ravel()} 

    for e in edges:
        paths[e[0]].add(e[1])
        paths[e[1]].add(e[0])
        
    while True:
        try:
            i=next(iter(paths.keys()))
        except StopIteration:
            break
        lpart={i}
        cur={i}
        while True:
            eligible={sc for sc in cur if sc in paths}
            if not eligible:
                break
            cur={ve for sc in eligible for ve in paths[sc]}
            lpart.update(cur)
            for key in eligible: paths.pop(key)
        lparts.append(sorted(list(lpart))) #make index order of unordered set chronological, works in my case
    
    #return np.array(lparts)
    return np.array(lparts, dtype=object) 

def sort_Z(islands, verts):  #islands = vert_idx,  verts = verts_co
    sorted_verts=[]
    for island in islands: #island is list of vert_indices
        # mean z
        listz = [verts[v_idx][2] for v_idx in island[:int(len(island)/2)]] #take z coords of first half of islands (where extrusion path lies, other half of beveled path is only for meshing the path und getting height edges)
        meanz = np.mean(listz)
        # store island and meanz (and original idx to get sculpt colors of sorted.)
        sorted_verts.append((island, meanz)) #store vert_indices(island) with Z average


    sorted_islands = [data[0] for data in sorted(sorted_verts, key=lambda height: height[1])] #sort islands by Z average
    
    return sorted_islands #used z coords of upper half but return islands as whole beveled mesh and slice into extrusion and height edges in 
    
    
    
##map vertex indices (taken from poly.vertices) to loop_indices
#so you can access vertex color with vert index instead of loop index
def read_weightmap_from_vcol(obj, vcol_name):
    
    def read_polyverts(obj):#vert indices of polygon
        polyverts = np.zeros((len(obj.data.polygons) * 4), dtype=int)
        obj.data.polygons.foreach_get("vertices", polyverts)
        return polyverts
        
    def read_loops(obj): #foreach_get doesn't have a 'loop_indices' attribute
        loops=[]
        for p in obj.data.polygons:
            for li in p.loop_indices:
                loops.append(li)           
        return loops
    
    #map vert_idx to loop_index, loop index is corresponding to vert_color map entry for that vert_idx
    vertex_indices = read_polyverts(obj)
    loop_indices = read_loops(obj)
    #to get loop index and corresponding vertex color
    map = {v_idx: l_idx for v_idx, l_idx in zip(vertex_indices, loop_indices)}
    
    
    #order vcol loops by vert idx order
    vcol=[]
    for i in range(len(map)):#iter over v_idx in map in ascending order, to get parallel running color array for vert indices
#    for v_idx in map:
        loop_idx = map[i]
        col = obj.data.vertex_colors[vcol_name].data[loop_idx].color[:3]
        
        luma = (col[0]*0.299+col[1]*0.587+col[2]*0.114)#/3 already normalized
        
        vcol.append(luma)
    
    
    return vcol #return one luma value per vert of weightmap



def remap(weight, min, max):
    remapped_speed = np.interp(weight,[0,1],[min,max])
    return remapped_speed
