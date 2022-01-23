# nozzleboss
nozzleboss is a G-code importer and re-exporter Add-on for Blender.

The G-code gets converted to a mesh and can be modified with all of Blenders modeling tools.   
Besides having vertex level control over the extrusion path, the Add-on allows you to create   
texture-based 'Flow' and 'Speed' weight maps using Blenders vertex paint mode.  

_Example image, 3 settings_

Concept of weight maps can be extended to other G-code commands as well.  
By default every import also creates a vertex color map called 'Tool', which depending  
on the underlying color, will insert a different G-code command for each color.  
To edit such a command go to Blenders text editor and choose the textblock called 'T0',  
which by default is represented by the color black.  

_changing color every other layer with 'Tool' vertex color map_


### Limitations: 
- Only supports firmware retraction (G10/G11) for now.  
- Only supports relative extrusion mode, 'Start' G-code has M83 command by default.  
- Be careful when changing the geometry of the G-code, it's pretty easy to create non-planar paths and crash the hotend.  
- This is not a slicer, you can't export a .stl file directly to G-code, you either need to import pre-sliced G-code first or built extrusion paths from scratch.  
- When generating your own extrusion paths inside of Blender keep the neccessary mesh structure of the path in mind.
   To hold vertex colors and use the sculpt tools on the mesh, Blender requires you to create polygons from the extrusion path and   
   so does the G-code exporter. When starting from a 2D polyline, just extrude in Z and the created polygons will have the right vertex index order.
- Note that you can't specify things like nozzle diameter, layer height or extrusion width. Extrusion values are calculated from the height and length of a polygon, since the polygon has no width, it uses a factor of _1.2 x polygon height_ as polygon width.

 


### Installation
- Download github repo as .zip
- Blender-->Edit-->Preferences-->Add-ons 
- Click "Install..." and select nozzleboss-master.zip (macOS might have auto-extracted your .zip file, just recompress the folder to .zip)
- activate checkmark for 'Import-Export: nozzleboss' in Add-on list