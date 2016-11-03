bl_info = {
    "name": "DOOM WAD format",
    "author": "Joshua Skelton",
    "version": (0, 0, 1),
    "blender": (2, 77, 0),
    "location": "File > Import > DOOM WAD (.WAD)",
    "description": "DOOM Tools for Blender. Import assets from WAD files.",
    "warning": "",
    "wiki_url": ""
                "",
    "support": 'COMMUNITY',
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib
    if "import_wad" in locals():
        importlib.reload(import_wad)

import os
import bpy
from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        path_reference_mode,
        axis_conversion,
        )

class ImportWAD(bpy.types.Operator, ImportHelper):
    """Loads a DOOM WAD File"""
    bl_idname = "import_scene.wad"
    bl_label = "Import WAD"
    bl_options = {'UNDO'}

    filename_ext = ".wad"
    filter_glob = StringProperty(
            default="*.wad",
            options={'HIDDEN'},
            )

    def execute(self, context):
        from . import import_wad
        print("executing")
        return import_wad.load(self, context, self.filepath)

    def draw(self, context):
        layout = self.layout

        space = context.space_data

        if space.system_bookmarks:
            row = layout.row()
            row.template_list("FILEBROWSER_UL_dir",
                              "system_bookmarks",
                              space,
                              "system_bookmarks",
                              space,
                              "system_bookmarks_active",
                              item_dyntip_propname="path",
                              rows=1,
                              maxrows=10)

def menu_func_import(self, context):
    self.layout.operator(ImportWAD.bl_idname, text="DOOM WAD (.WAD)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
