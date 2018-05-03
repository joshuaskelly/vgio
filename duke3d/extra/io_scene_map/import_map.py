import bpy
import bmesh
from mathutils import Matrix, Vector

from .api import Map


class LazyCache(object):
    def __init__(self, on_cache_miss):
        self._on_cache_miss = on_cache_miss
        self._cache = {}

    def __getitem__(self, item):
        if item not in self._cache:
            self._cache[item] = self._on_cache_miss(item)

        return self._cache[item]


def load(operator, context, filepath='',
         global_scale=1.0):

    #if not is_mapfile(filepath):
    #    operator.report(
    #        {'ERROR'},
    #        '{} not a recognized MAP file'.format(filepath)
    #    )
    #    return {'CANCELLED'}

    map_file = Map(filepath)
    #map_file.close()

    global_matrix = Matrix.Scale(global_scale, 4)

    for sector_index, sector in enumerate(map_file.sectors):
        print('Processing sector: {}'.format(sector_index))
        me = bpy.data.meshes.new('sector.{}'.format(sector_index))
        bm = bmesh.new()
        bedges = []

        for il, loop in enumerate(sector.loops):
            print('  Processing loop: {}'.format(il))
            # Build vertices
            points = [(*p, sector.floor_z(p)) for p in loop.points]
            bverts = [bm.verts.new(p) for p in points[:-2]]
            bm.verts.ensure_lookup_table()

            # Build edges
            edges = list(zip(bverts[:], bverts[1:] + [bverts[0]]))
            #edges = [bm.edges.new(e) for e in edges]
            bes = []
            for ie, e in enumerate(edges):
                print('    Processing edge: {} {}'.format(ie, e))
                bes.append(bm.edges.new(e))
            edges = bes

            bm.edges.ensure_lookup_table()
            bedges += edges

        # Triangulate face
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bedges, normal=(0, 0, 1))
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new('sector.{}'.format(sector_index), me)
        bpy.context.scene.objects.link(ob)

    """
    for sector_index, sector in enumerate(map_file.sectors):
        points = []

        me = bpy.data.meshes.new('sector.{}'.format(sector_index))
        bm = bmesh.new()

        def on_cache_miss(vertex):
            v = bm.verts.new(vertex)
            v.co = global_matrix * v.co
            return v

        vertex_cache = LazyCache(on_cache_miss)
        edges = set()

        wall_range = range(sector.wall_pointer, sector.wall_pointer + sector.wall_number)
        for wall in [sector.walls[i] for i in wall_range]:
            pass

        for i in range(sector.wall_pointer, sector.wall_pointer + sector.wall_number):
            current_wall = map_file.walls[i]
            start_point = current_wall.x, -current_wall.y, -(sector.floor_z >> 4)
            start_point = vertex_cache[start_point]
            next_wall = map_file.walls[current_wall.point2]
            end_point = next_wall.x, -next_wall.y, -(sector.floor_z >> 4)
            end_point = vertex_cache[end_point]

            edges.add((start_point, end_point))

        bm.verts.ensure_lookup_table()
        edges = list(edges)
        bes = []

        for i, e in enumerate(edges):
            try:
                bes.append(bm.edges.new(e))
            except:
                pass

        bm.edges.ensure_lookup_table()

        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bes, normal=(0,0,1))

        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new('sector.{}'.format(sector_index), me)
        bpy.context.scene.objects.link(ob)
    """

    return {'FINISHED'}


"""
Notes:

Use bmesh.ops.triangle_fill()
https://docs.blender.org/api/blender_python_api_current/bmesh.ops.html#bmesh.ops.triangle_fill

The above should be something like:
1. Build a list of edges
2. Build a set of verts from edges
3. Add bmesh.verts
4. Add bmesh.edges
5. Call triangle_fill()
"""