bl_info = {
    'name': 'Duke3D MAP format',
    'author': 'Joshua Skelton',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': 'File > Import-Export',
    'description': 'Load a Duke3D MAP file.',
    'warning': '',
    'wiki_url': '',
    'support': 'COMMUNITY',
    'category': 'Import-Export'}

if 'bpy' in locals():
    import importlib

    if 'import_bsp' in locals():
        importlib.reload(import_map)

import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty
)

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
)


class ImportBSP(bpy.types.Operator, ImportHelper):
    """Load a Duke3D MAP File"""

    bl_idname = 'import_scene.map'
    bl_label = 'Import MAP'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.map'
    filter_glob = StringProperty(
        default='*.map',
        options={'HIDDEN'},
    )

    global_scale = FloatProperty(
            name='Scale',
            min=0.001, max=1000.0,
            default=1.0 / 32.0,
            )

    def execute(self, context):
        keywords = self.as_keywords(ignore=("filter_glob",))
        from . import import_map

        return import_map.load(self, context, **keywords)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'global_scale')


def menu_func_import(self, context):
    self.layout.operator(ImportBSP.bl_idname,
                         text='Duke3D Map (.map)')


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == '__main__':
    register()
