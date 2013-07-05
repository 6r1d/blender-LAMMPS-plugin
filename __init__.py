bl_info = {
    "name":         "LAMMPS",
    "author":       "6r1d",
    "blender":      (2,6,7),
    "version":      (0,0,1),
    "location":     "File > Import-Export",
    "description":  "Import LAMMPS data format",
    "category":     "Import-Export"
}
        
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty)
import random

def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)

def add_sphere(x, y, z):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=6, 
        ring_count=6, 
        size=0.04, 
        location=(x, y, z), 
        rotation=(0, 0, 0), 
        layers=(
            True, False, False, False, False, False, False, False,
            False, False, False, False, False, False, False, False,
            False, False, False, False
        )
    )

class ImportLammps(Operator, ImportHelper):
    """LAMMPS importer"""
    bl_idname = "import.lammps"
    bl_label = "LAMMPS importer"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    multiplier = 8
    
    def __init__(self):
        pass
      

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        
        add_sphere(0,0,0)
        self.sphere = bpy.context.object
        
        with open(self.filepath, 'r') as file_object:
            stacks = {}
            materials = {}
            
            for row in file_object:
                if row.startswith("ITEM:"):
                    key = row.split()[1]
                    stacks[key]=[]
                    stacks[key+"_metadata"]=[]
                elif(key=="ATOMS"):
                    if str(row.split()[1]) not in materials:
                        materials[str(row.split()[1])] = bpy.data.materials.new(str(row.split()[1]))
                        materials[str(row.split()[1])].diffuse_color = (
                            random.random(),
                            random.random(),
                            random.random()
                        )
                    newrow = row.split()[2:]
                    newrow = [
                        float(c_value)*self.multiplier for c_value in newrow
                    ]
                    stacks[key].append(newrow)
                    # store metadata
                    stacks[key+"_metadata"].append( row.split()[:2] )
                else:
                    pass

        # Switch off selected object outline
        #bpy.data.screens["Default"].(null) = False

        print(materials.keys())

        for row, meta in zip(stacks["ATOMS"], stacks["ATOMS_metadata"]):
            ob = self.sphere.copy()
            ob.data = self.sphere.data.copy()
            ob.location = (row[0], row[1], row[2])
            bpy.context.scene.objects.link(ob)
            setMaterial(ob, materials[str(meta[1])])
        
        bpy.context.scene.update()
        
        # Switch on selected object outline
        #bpy.data.screens["Default"].(null) = True
        
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func(self, context):
    self.layout.operator(ImportLammps.bl_idname, text="LAMMPS Format")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()
