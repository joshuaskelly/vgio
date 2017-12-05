import tmx

from quake import map as m

filepath = ".\\data\\tilemap.tmx"
tilemap = tmx.TileMap.load(filepath)

width = tilemap.width
height = tilemap.height

layer = tilemap.layers[0]
data = [tile.gid for tile in layer.tiles]

# Loading in the 3D tile data
tiles = {}
with open('./tiles/t0.map') as file:
    tiles[3] = m.loads(file.read())

with open('./tiles/t1.map') as file:
    tiles[2] = m.loads(file.read())
    tiles[1] = None

entities = []

for layer in tilemap.layers:
    if isinstance(layer, tmx.Layer):
        # We have a tile layer

        e = m.Entity()
        e.classname = 'worldspawn'
        e.wad = tiles[2][0].wad
        e.brushes = []

        for index, value in enumerate(data):
            x = index % width
            y = tilemap.height - (index // height)

            offset_x = x * 128 + (64)# - (width * 128 / 2 - width)
            offset_y = y * 128 - 64# - (height * 128 / 2 - height)

            if not tiles[value]:
                continue

            for copy_brush in tiles[value][0].brushes:
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
                        s = copy_point[0] + offset_x, copy_point[1] + offset_y, \
                            copy_point[2]
                        q.points.append(s)

                    b.planes.append(q)
                e.brushes.append(b)

        entities.append(e)

    elif isinstance(layer, tmx.ObjectGroup):
        # We have objects
        for obj in layer.objects:
            z = 0

            e = m.Entity()
            for prop in obj.properties:
                if prop.name == 'Z':
                    z = prop.value

                else:
                    setattr(e, prop.name, prop.value)

            origin = obj.x * 4, (tilemap.height * 128) - obj.y * 4, z
            e.origin = "{} {} {}".format(*origin)
            e.classname = obj.name

            entities.append(e)


with open('./output/out.map', 'w') as out_file:
    data = m.dumps(entities)
    out_file.write(data)
