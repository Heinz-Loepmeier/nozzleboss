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
- This is not a slicer, you can't export a .stl file directly to G-code, you either need to import pre-sliced G-code first or built extrusion paths from sratch.  
- Be care when changing the geometry of the G-code, it's pretty easy to create non-planar paths and crash the hotend.  
- Only supports firmware retraction (G10/G11) for now.  
- Only supports relative extrusion mode, 'Start' G-code has M83 command by default.  


### Installation
- Download github repo as .zip
- Blender-->Edit-->Preferences-->Add-ons 
- Click "Install..." and select nozzleboss-master.zip (macOS might have auto-extracted your .zip file, just recompress the folder to .zip)
- activate checkmark for 'Import-Export: nozzleboss' in Add-on list
