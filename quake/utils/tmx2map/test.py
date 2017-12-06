import json
import warnings
import os
import math

import numpy
import tmx

from quake import map as m

# Helper matrices
hflip_matrix = numpy.identity(4)
hflip_matrix[0, 0] = -1

vflip_matrix = numpy.identity(4)
vflip_matrix[1, 1] = -1

dflip_matrix = numpy.zeros((4, 4))
dflip_matrix[0, 1] = 1
dflip_matrix[1, 0] = 1
dflip_matrix[2, 2] = 1
dflip_matrix[3, 3] = 1


def angle_between(dest, base):
    """Returns the angle in positive degrees from base to dest in the
    xy-plane.

    dest: A vector
    base: A vector

    Returns:
        Angle in degrees [0, 360)
    """

    target = dest[0], dest[1]
    p_axis = -base[1], base[0]
    b_axis = base[0], base[1]

    x_proj = numpy.dot(target, b_axis)
    y_proj = numpy.dot(target, p_axis)

    return -math.degrees(math.atan2(y_proj, x_proj)) % 360


def vector_from_angle(degrees):
    """Returns a unit vector in the xy-plane rotated by the given degrees from
    the positive x-axis"""
    radians = math.radians(degrees)
    z_rot_matrix = numpy.identity(4)
    z_rot_matrix[0, 0] = math.cos(radians)
    z_rot_matrix[0, 1] = -math.sin(radians)
    z_rot_matrix[1, 0] = math.sin(radians)
    z_rot_matrix[1, 1] = math.cos(radians)

    return tuple(numpy.dot(z_rot_matrix, (1, 0, 0, 0))[:3])


filepath = "./data/tilemap.tmx"
tilemap = tmx.TileMap.load(filepath)

width = tilemap.width
height = tilemap.height

with open('mapping.json') as file:
    tile_mapping = json.loads(file.read())

# Loading in the 3D tile data
tiles = {}
tile_size_3d = tile_mapping["tilesize"]
tile_size_2d = tilemap.width

for tileset in tile_mapping["tilesets"]:
    filename = tileset["filename"]

    # Grab the tileset def from the tilemap
    tileset_definition = [t for t in tilemap.tilesets if os.path.basename(t.image.source) == filename]
    if not tileset_definition:
        continue

    tileset_definition = tileset_definition[0]
    tile_count = tileset_definition.tilecount
    first_gid = tileset_definition.firstgid

    for tile_id in tileset["tiles"]:
        gid = int(tile_id) + first_gid
        tile_filename = tileset["tiles"][tile_id]

        with open(tile_filename) as file:
            tiles[gid] = m.loads(file.read())

entities = []

for layer in tilemap.layers:
    # Tile layer
    if isinstance(layer, tmx.Layer):
        e = m.Entity()
        e.classname = 'worldspawn'
        e.wad = tiles[2][0].wad
        e.brushes = []

        for index, tile in enumerate(layer.tiles):
            if not tiles.get(tile.gid):
                warnings.warn("Failed to find tile mapping for gid: {}".format(tile.gid))
                continue

            x = index % width
            y = tilemap.height - (index // height)

            offset_x = x * tile_size_3d + (tile_size_3d / 2)
            offset_y = y * tile_size_3d - (tile_size_3d / 2)

            # Calculate tile transformation matrix
            mat = numpy.identity(4)
            mat[:3, 3] = offset_x, offset_y, 0

            flip_face = False

            if tile.hflip:
                mat = numpy.dot(mat, hflip_matrix)
                flip_face = not flip_face

            if tile.dflip:
                mat = numpy.dot(mat, dflip_matrix)
                flip_face = not flip_face

            if tile.vflip:
                mat = numpy.dot(mat, vflip_matrix)
                flip_face = not flip_face

            prefab = tiles[tile.gid]
            for entity in prefab:
                # TODO: Copy properties

                # TODO: Transform white-listed properties
                # - origin
                # - angle

                # Transform brushes
                for copy_brush in entity.brushes:
                    b = m.Brush()
                    b.planes = []

                    for copy_plane in copy_brush.planes:
                        q = m.Plane()
                        q.points = []
                        q.texture_name = copy_plane.texture_name
                        q.offset = copy_plane.offset
                        q.rotation = copy_plane.rotation
                        q.scale = copy_plane.scale

                        for copy_point in copy_plane.points:
                            transformed_point = tuple(numpy.dot(mat, (*copy_point, 1))[:3])
                            q.points.append(transformed_point)

                        if flip_face:
                            # Re-order the points to flip the face
                            q.points = list(reversed(q.points))

                        b.planes.append(q)
                    e.brushes.append(b)
        entities.append(e)

    # Object layer
    elif isinstance(layer, tmx.ObjectGroup):
        for obj in layer.objects:
            z = 0

            e = m.Entity()
            for prop in obj.properties:
                if prop.name == 'Z':
                    z = prop.value

                else:
                    setattr(e, prop.name, prop.value)

            scale = tile_size_3d / tile_size_2d
            origin = obj.x * scale, (tilemap.height * tile_size_3d) - obj.y * scale, z
            e.origin = "{} {} {}".format(*origin)
            e.classname = obj.name
            entities.append(e)


with open('./output/out.map', 'w') as out_file:
    data = m.dumps(entities)
    out_file.write(data)
