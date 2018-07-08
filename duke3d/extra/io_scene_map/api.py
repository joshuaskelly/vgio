import math
import numpy

from .duke3d.map import Map as MapFile, is_mapfile


class Sector(object):
    def __init__(self, map_object, sector_struct):
        self._map = map_object
        self._struct = sector_struct
        self.walls = [self._map.walls[w] for w in range(self._struct.wall_pointer,self._struct.wall_pointer+self._struct.wall_number)]

    def floor_z(self, point):
        first_wall = self.walls[-1]
        a = first_wall.point
        b = first_wall.next_wall.point
        wall_vec = numpy.subtract(b, a)
        wall_vec = wall_vec / numpy.linalg.norm(wall_vec)
        point_vec = numpy.subtract(point, a)
        distance_from_wall = numpy.dot(wall_vec, point_vec)

        floor_angle = self._struct.floor_heinum / 4096 * -45
        theta = math.radians(floor_angle)
        v = distance_from_wall / math.cos(theta)
        z = -(v * math.sin(theta) + (self._struct.floor_z >> 4))

        return z #-(self._struct.floor_z >> 4)

    def ceiling_z(self, point):
        return -(self._struct.ceiling_z >> 4)

    @property
    def loops(self):
        result = []
        wall_set = set(self.walls[:])

        while wall_set:
            first = list(wall_set)[0]
            loop = first.loop
            wall_set = wall_set - {*loop.walls}
            result.append(loop)

        return result


class Wall(object):
    def __init__(self, map_object, wall_struct):
        self._map = map_object
        self._struct = wall_struct

    @property
    def point(self):
        return self._struct.x, self._struct.y

    @property
    def next_wall(self):
        return self._map.walls[self._struct.point2]

    @property
    def loop(self):
        walls = [self]
        n = self.next_wall
        while n != self:
            walls.append(n)
            n = n.next_wall

        return Loop(walls)


class Loop(object):
    def __init__(self, walls):
        self.walls = walls

    @property
    def points(self):
        if not self.walls:
            return []

        first_point = self.walls[0].point
        return [w.point for w in self.walls] + [first_point]


class Map(object):
    def __init__(self, file):
        self._map_file = MapFile.open(file)
        self._map_file.close()
        self.walls = [Wall(self, w) for w in self._map_file.walls]
        self.sectors = [Sector(self, s) for s in self._map_file.sectors]
