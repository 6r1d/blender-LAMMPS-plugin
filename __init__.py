bl_info = {
    "name": "LAMMPS text output import",
    "author": "6r1d",
    "blender": (2, 6, 7),
    "version": (0, 0, 11),
    "location": "File > Import > LAMMPS format",
    "description": "Import LAMMPS data format",
    "category": "Import-Export"
}

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
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
        return True

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        add_sphere(0, 0, 0)
        self.sphere = bpy.context.object
        self.sphere.name = 'lammps_import_root_object'

        with open(self.filepath, 'r') as file_object:
            stacks = {}
            materials = {}

            for row in file_object:
                if row.startswith("ITEM:"):
                    key = row.split()[1]
                    stacks[key] = []
                    stacks[key + "_metadata"] = []
                elif(key == "ATOMS"):
                    atom_type = str(row.split()[1])
                    if atom_type not in materials:
                        materials[atom_type] = bpy.data.materials.new(
                            atom_type
                        )
                        materials[atom_type].diffuse_color = (
                            random.random(),
                            random.random(),
                            random.random()
                        )
                    newrow = row.split()[2:]
                    newrow = [
                        float(c_value) * self.multiplier for c_value in newrow
                    ]
                    stacks[key].append(newrow)
                    # store metadata
                    stacks[key + "_metadata"].append(row.split()[:2])
                else:
                    pass

        # Simulation atoms must have name prefix
        name_prefix = str(random.randint(10000, 99999))

        for row, meta in zip(stacks["ATOMS"], stacks["ATOMS_metadata"]):
            ob = self.sphere.copy()
            ob.name = 'atom' + '_' + name_prefix
            ob.data = self.sphere.data.copy()
            ob.location = (row[0], row[1], row[2])
            bpy.context.scene.objects.link(ob)
            setMaterial(ob, materials[str(meta[1])])

        # Delete root sphere
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(
            pattern='lammps_import_root_object',
            case_sensitive=False,
            extend=False
        )
        bpy.ops.object.delete()

        # Select imported atoms
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(
            pattern='atom' + '_' + name_prefix + '*',
            case_sensitive=False,
            extend=True
        )

        bpy.context.scene.update()

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
