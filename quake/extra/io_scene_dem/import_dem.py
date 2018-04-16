import bpy

from .quake.dem import Dem


def load(operator, context, filepath='', global_scale=1.0):
    dem = Dem.open(filepath)
    dem.close()

    coords = []

    for message_block in dem.message_blocks:
        for message in message_block.messages:
            if hasattr(message, 'entity') and hasattr(message, 'origin') and message.entity == 1:
                x, y, z = message.origin
                x = (x or 0) * global_scale
                y = (y or 0) * global_scale
                z = (z or 0) * global_scale
                coords.append((x, y, z))
                break

    curve = bpy.data.curves.new('myCurve', type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 2

    polyline = curve.splines.new('BEZIER')

    polyline.bezier_points.add(len(coords))
    for i, coord in enumerate(coords):
        x, y, z = coord
        polyline.bezier_points[i].co = (x, y, z)
        polyline.bezier_points[i].handle_right_type = 'VECTOR'
        polyline.bezier_points[i].handle_left_type = 'VECTOR'

    ob = bpy.data.objects.new('myCurve', curve)
    bpy.context.scene.objects.link(ob)

    return {'FINISHED'}
