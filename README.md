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
_Building extrusion paths form scratch and changing colors every other layer with 'Tool' vertex color map_  
_I'm using an array modifier here and sculpting the paths with a hook/smooth brush while the Z-axis is locked._



If you are not familiar with Blender, navigating the user interface takes some getting used to.  
Here is an example [.blend file](https://github.com/Heinz-Loepmeier/misc/blob/main/nozzleboss_blend.zip) with an already sliced and textured test cube, and all relevant windows opened up.  
Change the 'Start' and 'End' G-code for your printer and try to export.  
Detailed explanation of every setting is in the [Wiki](https://github.com/Heinz-Loepmeier/nozzleboss/wiki).  
For development updates and some occasional howtos follow me on [Twitter](https://twitter.com/aeth1) or have a look at my [Instagram](https://www.instagram.com/nozzleboss/)  
to see what can be done with path based printing.




### Limitations: 
- Only supports firmware retraction (G10/G11) for now.  
- Only supports relative extrusion mode, 'Start' G-code has M83 command by default.  
- Be careful when changing the geometry of the G-code, it's pretty easy to create non-planar paths and crash the hotend.  
- This is not a slicer, you can't export a .stl file directly to G-code, you either need to import pre-sliced G-code first or built extrusion paths from scratch.  
- When generating your own extrusion paths inside of Blender keep the neccessary mesh structure of the path in mind.  
   To hold vertex colors and use the sculpt tools on the mesh, Blender requires you to create polygons from the extrusion path and
   so does the G-code exporter.  
   When starting from a 2D polyline, just extrude in Z and the created polygons will have the right vertex index order.
- Note that you can't specify things like nozzle diameter, layer height or extrusion width. Extrusion values are calculated from the height and length of a polygon, since the polygon has no width, it uses a factor of _1.2 x polygon height_ as polygon width.
- Can import vasemode or variable height G-code, but not both at the same time. (which prusaslicer allows you to) 


### Installation
- Download github repo as .zip
- Blender-->Edit-->Preferences-->Add-ons 
- Click "Install..." and select nozzleboss-master.zip (macOS might have auto-extracted your .zip file, just recompress the folder to .zip)
- activate checkmark for 'Import-Export: nozzleboss' in Add-on list
- Addon appears in N-Panel (press 'n' in viewport) and NOT via File-->Export/Import
