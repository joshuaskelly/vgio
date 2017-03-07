bl_info = {
    "name": "Quake BSP format",
    "author": "Joshua Skelton",
    "version": (0, 0, 1),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Load a Quake BSP file.",
    "warning": "",
    "wiki_url": ""
                "",
    "support": 'COMMUNITY',
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib

    if "import_bsp" in locals():
        importlib.reload(import_bsp)
    if "export_bsp" in locals():
        importlib.reload(export_bsp)

import bpy
from bpy.props import StringProperty

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    path_reference_mode,
)


class ImportBSP(bpy.types.Operator, ImportHelper):
    """Load a Quake BSP File"""
    bl_idname = "import_scene.bsp"
    bl_label = "Import BSP"
    bl_options = {'UNDO'}

    filename_ext = ".bsp"
    filter_glob = StringProperty(
        default="*.bsp",
        options={'HIDDEN'},
    )

    def execute(self, context):
        from . import import_bsp

        return import_bsp.load(self, context, self.filepath)

    def draw(self, context):
        layout = self.layout

        space = context.space_data

        if space.system_bookmarks:
            row = layout.row()
            row.template_list("FILEBROWSER_UL_dir", "system_bookmarks", space,
                              "system_bookmarks",
                              space, "system_bookmarks_active",
                              item_dyntip_propname="path", rows=1, maxrows=10)


class ExportBSP(bpy.types.Operator, ExportHelper):
    """Save a Quake BSP File"""

    bl_idname = "export_scene.bsp"
    bl_label = 'Export BSP'
    bl_options = {'PRESET'}

    filename_ext = ".bsp"
    filter_glob = StringProperty(
        default="*.bsp",
        options={'HIDDEN'},
    )

    path_mode = path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import export_bsp

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            "path_mode",
                                            ))

        return export_bsp.save(self, context, **keywords)


def menu_func_import(self, context):
    self.layout.operator(ImportBSP.bl_idname,
                         text="Quake BSP (.bsp)")


def menu_func_export(self, context):
    self.layout.operator(ExportBSP.bl_idname,
                         text="Quake BSP (.bsp)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    #bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    #bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
