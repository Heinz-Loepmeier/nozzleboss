bl_info = {
    "name": "nozzleboss",
    "description": "G-code Importer/Editor/Re-Exporter",
    "author": "Heinz Löpmeier",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "3D View > nozzleboss",
    "category": "Import-Export"
}



if "bpy" in locals():
    import importlib
    importlib.reload(utils) 
    importlib.reload(parser) 
    importlib.reload(nozzleboss) 


else:
    from . import utils
    from . import parser
    from . import nozzleboss
    
import bpy
from bpy.props import PointerProperty
    
    
    
    


def register():
    bpy.utils.register_class(nozzleboss.NOZZLEBOSS_PT_Panel)
    bpy.utils.register_class(nozzleboss.gcode_settings)
    bpy.utils.register_class(nozzleboss.WM_OT_gcode_import)
    bpy.utils.register_class(nozzleboss.WM_OT_gcode_export)
    bpy.types.Scene.nozzleboss = bpy.props.PointerProperty(type= nozzleboss.gcode_settings)
 



def unregister():
    bpy.utils.unregister_class(nozzleboss.NOZZLEBOSS_PT_Panel)
    bpy.utils.unregister_class(nozzleboss.gcode_settings)
    bpy.utils.unregister_class(nozzleboss.WM_OT_gcode_import)
    bpy.utils.unregister_class(nozzleboss.WM_OT_gcode_export)
    del bpy.types.Scene.nozzleboss



if __name__ == "__main__":
    register()
