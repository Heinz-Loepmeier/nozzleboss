# nozzleboss
### nozzleboss is a G-code importer and re-exporter Add-on for Blender.  
![intro_extrasmall](https://user-images.githubusercontent.com/17910445/150960353-a4e39422-3d2e-4e46-be27-bc2b35ba813f.gif)  
_The G-code gets converted to a mesh and can be modified with all of Blenders modeling tools_
 
### Extrusion/Speed multiplier
Besides having vertex level control over the extrusion path, the Add-on allows you to create   
texture-based 'Flow' and 'Speed' weight maps using Blenders vertex paint mode.  
The 'Speed' multiplier works exactly like Mark Wheadons ['Velocity painting'](https://github.com/MarkWheadon/velocity-painting) technique, except  
you can use Blenders vertex colors to get the texture onto the model, which is quite convenient.


![3_settings_nozzleboss_small](https://user-images.githubusercontent.com/17910445/151602354-62088802-b811-4b28-ba15-ea538a656761.png)  
_3 different min and max Flow/Speed multiplier settings_

### Tool selection based on vertex colors
Concept of weight maps can be extended to other G-code commands as well.  
By default every import also creates a vertex color map called 'Tool', which depending  
on the underlying color, will insert a different G-code command for each color.  
To edit such a command go to Blenders text editor and choose the textblock called 'T0',  
which by default is represented by the color black and textblock 'T1' for the vertex color white.
Everytime the color changes the provided text is inserted into the G-code


![scratch_extrasmall](https://user-images.githubusercontent.com/17910445/150961183-9e54d273-54b1-474b-a630-9ebda929d559.gif)  
_Building extrusion paths from scratch and changing colors every other layer with 'Tool' vertex color map_  
_I'm using an array modifier here and sculpting the paths with a hook/smooth brush while the Z-axis is locked._



If you are not familiar with Blender and get any errors on export, try starting with this [example.blend](https://github.com/Heinz-Loepmeier/misc/blob/main/nozzleboss_blend.zip) file here,  
it has a pre-sliced and textured test cube, and all relevant windows opened up.  
Change the 'Start' and 'End' G-code for your printer and try to export.  
Detailed explanation of every setting is in the [Wiki](https://github.com/Heinz-Loepmeier/nozzleboss/wiki).  
For development updates and some occasional howtos follow me on [Twitter](https://twitter.com/nozzleboss) or have a look at my [Instagram](https://www.instagram.com/nozzleboss/)  
to see what can be done with path based printing.




### Limitations: 
- Only supports firmware retraction (G10/G11) for now.  
- Only supports relative extrusion mode, 'Start' G-code has M83 command by default.
- .gcode file gets saved to same location as current .blend file 
- When generating your own extrusion paths, keep the neccessary mesh structure in mind:
   I recommend turning on ['Developer Extras and showing vertex indices'](https://blender.stackexchange.com/questions/158493/displaying-vertex-indices-in-blender-2-8-using-debug-mode)
   -Start with a simple 2D path/polyline
   - Make sure that your path's vertex indices are in linear order and start like this 0-1-2-3-...
   - Mesh operations like subdivide or ripping vertices can scramble the order to something like this 0-6-1-5-...
   - To reorder use Blenders 'Convert to curve' and convert back to mesh.
   - If you have a nicely ordered 2D path, extrude the path in the negative Z direction. (nozzleboss will only export extruded paths)
      - Height of the extrusion defines your layerheight
      - Creating polygons is used for storing and showing vertex colors used for weightmaps.
      - Actual toolpath of the nozzle is your initial 2D path

- Extrusion values are calculated from the height and length of a polygon/extruded path.
- Can import vasemode or variable height G-code, but not both at the same time. (which prusaslicer allows you to) 
- This is not a slicer, you can't export a .stl file directly to G-code, you either need to import pre-sliced G-code first or build extrusion paths from scratch. 


### Installation
- Download github repo as .zip
- Blender-->Edit-->Preferences-->Add-ons 
- Click "Install..." and select nozzleboss-master.zip (macOS might have auto-extracted your .zip file, just recompress the folder to .zip)
- activate checkmark for 'Import-Export: nozzleboss' in Add-on list
- Addon appears in N-Panel (press 'n' in viewport) and NOT via File-->Export/Import
