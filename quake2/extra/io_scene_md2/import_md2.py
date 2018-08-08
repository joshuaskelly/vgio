from .quake2 import md2


def load(operator, context, filepath):
    if not md2.is_md2file(filepath):
        return {'FINISHED'}

    md2_file = md2.Md2.open(filepath)
    md2_file.close