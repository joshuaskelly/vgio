import math


class Thing(object):
    LUMP_NAME = 'THINGS'

    def __init__(self, thing_struct, index, map):
        self.index = index
        self.x = thing_struct.x
        self.y = thing_struct.y
        self.angle = thing_struct.angle
        self.type = thing_struct.type
        self.options = thing_struct.options


class LineDefFlags(object):
    def __init__(self, flags):
        self.impassable     = flags & 1 << 0 > 0
        self.block_monsters = flags & 1 << 1 > 0
        self.two_sided      = flags & 1 << 2 > 0
        self.upper_unpegged = flags & 1 << 3 > 0
        self.lower_unpegged = flags & 1 << 4 > 0
        self.secret         = flags & 1 << 5 > 0
        self.block_sound    = flags & 1 << 6 > 0
        self.not_on_map     = flags & 1 << 7 > 0
        self.already_on_map = flags & 1 << 8 > 0


class LineDef(object):
    LUMP_NAME = 'LINEDEFS'

    def __init__(self, linedef_struct, index, map):
        self.index = index
        self.vertex_1 = map.vertexes[linedef_struct.vertex_1]
        self.vertex_2 = map.vertexes[linedef_struct.vertex_2]
        self.flags = LineDefFlags(linedef_struct.flags)
        self.specials = linedef_struct.specials
        self.tag = linedef_struct.tag
        self.front_side = map.sidedefs[linedef_struct.front_side] if linedef_struct.front_side < 65535 else None
        self.back_side = map.sidedefs[linedef_struct.back_side] if linedef_struct.back_side < 65535 else None

        self.segs = []
        self.front_side.linedef = self
        if self.back_side:
            self.back_side.linedef = self


class SideDef(object):
    LUMP_NAME = 'SIDEDEFS'

    def __init__(self, sidedef_struct, index, map):
        self.index = index
        self.x_offset = sidedef_struct.x_offset
        self.y_offset = sidedef_struct.y_offset
        self.top_texture = sidedef_struct.top_texture
        self.bottom_texture = sidedef_struct.bottom_texture
        self.middle_texture = sidedef_struct.middle_texture
        self.sector = map.sectors[sidedef_struct.sector]

        self.linedef = None
        self.segs = []
        self.sector.sidedefs.append(self)


class Vertex(object):
    LUMP_NAME = 'VERTEXES'

    def __init__(self, vertex_struct, index, map):
        self.index = index
        self.x = vertex_struct.x
        self.y = vertex_struct.y


class Seg(object):
    LUMP_NAME = 'SEGS'

    def __init__(self, seg_struct, index, map):
        self.index = index
        self.vertex_1 = map.vertexes[seg_struct.vertex_1]
        self.vertex_2 = map.vertexes[seg_struct.vertex_2]
        self.angle = seg_struct.angle
        self.linedef = map.linedefs[seg_struct.linedef]
        self.side = map.sidedefs[seg_struct.side]
        self.offset = seg_struct.offset

        self.linedef.segs.append(self)
        self.side.segs.append(self)


class SSector(object):
    LUMP_NAME = 'SSECTORS'
    
    def __init__(self, ssector_struct, index, map):
        self.index = index
        self.number_of_segs = ssector_struct.number_of_segs
        self.first_seg = map.segs[ssector_struct.first_seg]


class BoundingBox(object):
    def __init__(self, bottom, left, top, right):
        self.bottom = bottom
        self.left = left
        self.top = top
        self.right = right


class Node(object):
    LUMP_NAME = 'NODES'

    def __init__(self, node_struct, index, map):
        self.index = index
        self.x = node_struct.x
        self.y = node_struct.y
        self.dx = node_struct.dx
        self.dy = node_struct.dy
        self.right_bounding_box = BoundingBox(node_struct.right_bounding_box_bottom, node_struct.right_bounding_box_left, node_struct.right_bounding_box_top, node_struct.right_bounding_box_right)
        self.left_bounding_box = BoundingBox(node_struct.left_bounding_box_bottom, node_struct.left_bounding_box_left, node_struct.left_bounding_box_top, node_struct.left_bounding_box_right)
        self.right_child = node_struct.right_child
        self.left_child = node_struct.left_child


class Sector(object):
    LUMP_NAME = 'SECTORS'

    def __init__(self,sector_struct, index, map):
        self.index = index
        self.floor_height = sector_struct.floor_height
        self.ceiling_height = sector_struct.ceiling_height
        self.floor_texture = sector_struct.floor_texture
        self.ceiling_texture = sector_struct.ceiling_texture
        self.light_level = sector_struct.light_level
        self.special = sector_struct.special
        self.tag = sector_struct.tag

        self.sidedefs = []


class Reject(object):
    LUMP_NAME = 'REJECT'

    def __init__(self, reject_struct, index, map):
        self.index = index


class BlockMap(object):
    LUMP_NAME = 'BLOCKMAP'

    def __init__(self, blockmap_struct, index, map):
        self.index = index


class Mesh:
    def __init__(self, vertices, triangles):
        self.vertices = vertices
        self.triangles = triangles


class Map(object):
    valid_lumps = ['THINGS','LINEDEFS','SIDEDEFS','VERTEXES','SEGS','SSECTORS','NODES','SECTORS','REJECT','BLOCKMAP','BEHAVIOR','SCRIPTS']

    def __init__(self, map_struct):
        def load_lumps(lump_type):
            lump = map_struct[lump_type.LUMP_NAME]

            if not lump or not lump.data:
                return []

            return [lump_type(lump.data[i], i, self) for i in range(len(lump.data))]

        self.name = map_struct[0].name
        self.vertexes = load_lumps(Vertex)
        self.sectors = load_lumps(Sector)
        self.sidedefs = load_lumps(SideDef)
        self.things = load_lumps(Thing)
        self.linedefs = load_lumps(LineDef)
        self.segs = load_lumps(Seg)
        self.ssectors = load_lumps(SSector)
        self.nodes = load_lumps(Node)
        self.reject = load_lumps(Reject)
        self.blockmap = load_lumps(BlockMap)

    def mesh(self):
        mesh = Mesh([], [])

        for sector in self.sectors:
            edges = []
            next_edge = {}

            for side in sector.sidedefs:
                line = side.linedef

                if line.back_side is not None and line.back_side.sector is line.front_side.sector:
                    continue

                if line.front_side is side:
                    e = (line.vertex_1.index, line.vertex_2.index)

                else:
                    e = (line.vertex_2.index, line.vertex_1.index)

                v0 = self.vertexes[e[0]]
                v1 = self.vertexes[e[1]]

                if not line.back_side:
                    start = len(mesh.vertices)

                    mesh.vertices.append((v0.x, sector.floor_height, v0.y))
                    mesh.vertices.append((v1.x, sector.floor_height, v1.y))
                    mesh.vertices.append((v0.x, sector.ceiling_height, v0.y))
                    mesh.vertices.append((v1.x, sector.ceiling_height, v1.y))

                    mesh.triangles.append((start + 0, start + 1, start + 3))
                    mesh.triangles.append((start + 0, start + 3, start + 2))

                else:
                    neighbor = line.back_side.sector

                    # Lower wall
                    if sector.floor_height < neighbor.floor_height:
                        start = len(mesh.vertices)

                        mesh.vertices.append((v0.x, sector.floor_height, v0.y))
                        mesh.vertices.append((v1.x, sector.floor_height, v1.y))
                        mesh.vertices.append(
                            (v0.x, neighbor.floor_height, v0.y))
                        mesh.vertices.append(
                            (v1.x, neighbor.floor_height, v1.y))

                        mesh.triangles.append(
                            (start + 0, start + 1, start + 3))
                        mesh.triangles.append(
                            (start + 0, start + 3, start + 2))

                    # Middle wall
                    if side.middle_texture != '-':
                        start = len(mesh.vertices)

                        f = max(sector.floor_height, neighbor.floor_height)
                        c = min(sector.ceiling_height, neighbor.ceiling_height)

                        mesh.vertices.append((v0.x, f, v0.y))
                        mesh.vertices.append((v1.x, f, v1.y))
                        mesh.vertices.append((v0.x, c, v0.y))
                        mesh.vertices.append((v1.x, c, v1.y))

                        mesh.triangles.append(
                            (start + 0, start + 1, start + 3))
                        mesh.triangles.append(
                            (start + 0, start + 3, start + 2))

                    # Upper wall
                    if sector.ceiling_height > neighbor.floor_height:
                        start = len(mesh.vertices)

                        mesh.vertices.append(
                            (v0.x, sector.ceiling_height, v0.y))
                        mesh.vertices.append(
                            (v1.x, sector.ceiling_height, v1.y))
                        mesh.vertices.append(
                            (v0.x, neighbor.ceiling_height, v0.y))
                        mesh.vertices.append(
                            (v1.x, neighbor.ceiling_height, v1.y))

                        mesh.triangles.append(
                            (start + 0, start + 1, start + 3))
                        mesh.triangles.append(
                            (start + 0, start + 3, start + 2))

                edges.append(e)
                next_edge[e[0]] = e

            polygons = []
            while len(edges) > 0:
                polygon = []

                start_edge = edges[0]
                current_edge = start_edge
                do = True

                while do or current_edge != start_edge:
                    do = False
                    polygon.append(current_edge)
                    if (current_edge in edges):
                        edges.remove(current_edge)
                    else:
                        print(current_edge)
                    current_edge = next_edge[current_edge[1]]

                polygons.append(polygon)

            outer_hull = []
            holes = []
            for polygon in polygons:
                data = []
                for v in polygon:
                    data.append(self.vertexes[v[0]].x)
                    data.append(self.vertexes[v[0]].y)

                clockwise = _earcut.signedArea(data, 0, len(data), 2) <= 0

                if clockwise:
                    outer_hull.append([(data[i], data[i + 1]) for i in
                                       range(0, len(data), 2)])
                else:
                    holes.append([(data[i], data[i + 1]) for i in
                                  range(0, len(data), 2)])

            data = []
            data += outer_hull
            data += holes

            info = _earcut.flatten(data)
            data = info['vertices']
            dim = info['dimensions']
            holes = info['holes']
            triangles = _earcut.earcut(data, holes, dim)

            for i in range(0, len(triangles), 3):
                start = len(mesh.vertices)
                verts = triangles[i:i + 3]

                for vert in verts:
                    mesh.vertices.append((data[vert * 2 + 0],
                                          sector.floor_height,
                                          data[vert * 2 + 1]))

                for vert in reversed(verts):
                    mesh.vertices.append((data[vert * 2 + 0],
                                          sector.ceiling_height,
                                          data[vert * 2 + 1]))

                mesh.triangles.append((start + 0, start + 1, start + 2))
                mesh.triangles.append((start + 3, start + 4, start + 5))


        return mesh


class _earcut:

    @staticmethod
    def earcut(data, holeIndices=None, dim=None):
        unflatten_when_done = False

        if isinstance(data[0], list) or isinstance(data[0], tuple):
            info = _earcut.flatten(data)
            dim = info['dimensions']
            data = info['vertices']
            holeIndices = info['holes']
            unflatten_when_done = True

        else:
            dim = dim or 2

        hasHoles = holeIndices and len(holeIndices)
        outerLen =  holeIndices[0] * dim if hasHoles else len(data)
        outerNode = _earcut.linkedList(data, 0, outerLen, dim, True)
        triangles = []

        if not outerNode:
            return triangles

        minX = None
        minY = None
        maxX = None
        maxY = None
        x = None
        y = None
        size = None

        if hasHoles:
            outerNode = _earcut.eliminateHoles(data, holeIndices, outerNode, dim)

        # if the shape is not too simple, we'll use z-order curve hash later; calculate polygon bbox
        if (len(data) > 80 * dim):
            minX = maxX = data[0]
            minY = maxY = data[1]

            for i in range(dim, outerLen, dim):
                x = data[i]
                y = data[i + 1]
                if x < minX:
                    minX = x
                if y < minY:
                    minY = y
                if x > maxX:
                    maxX = x
                if y > maxY:
                    maxY = y

            # minX, minY and size are later used to transform coords into integers for z-order calculation
            size = max(maxX - minX, maxY - minY)

        _earcut.earcutLinked(outerNode, triangles, dim, minX, minY, size)

        if unflatten_when_done:
            return _earcut.unflatten(triangles)

        return triangles


    # create a circular doubly linked _list from polygon points in the specified winding order
    @staticmethod
    def linkedList(data, start, end, dim, clockwise):
        i = None
        last = None

        if (clockwise == (_earcut.signedArea(data, start, end, dim) > 0)):
            for i in range(start, end, dim):
                last = _earcut.insertNode(i, data[i], data[i + 1], last)

        else:
            for i in reversed(range(start, end, dim)):
                last = _earcut.insertNode(i, data[i], data[i + 1], last)

        if (last and _earcut.equals(last, last.next)):
            _earcut.removeNode(last)
            last = last.next

        return last


    # eliminate colinear or duplicate points
    @staticmethod
    def filterPoints(start, end):
        if not start:
            return start
        if not end:
            end = start

        p = start
        again = True

        while again or p != end:
            again = False

            if (not p.steiner and (_earcut.equals(p, p.next) or _earcut.area(p.prev, p, p.next) == 0)):
                _earcut.removeNode(p)
                p = end = p.prev
                if (p == p.next):
                    return None

                again = True

            else:
                p = p.next

        return end

    # main ear slicing loop which triangulates a polygon (given as a linked _list)
    @staticmethod
    def earcutLinked(ear, triangles, dim, minX, minY, size, _pass=None):
        if not ear:
            return

        # interlink polygon nodes in z-order
        if not _pass and size:
            _earcut.indexCurve(ear, minX, minY, size)

        stop = ear
        prev = None
        next = None

        # iterate through ears, slicing them one by one
        while ear.prev != ear.next:
            prev = ear.prev
            next = ear.next

            if _earcut.isEarHashed(ear, minX, minY, size) if size else _earcut.isEar(ear):
                # cut off the triangle
                triangles.append(prev.i // dim)
                triangles.append(ear.i // dim)
                triangles.append(next.i // dim)

                _earcut.removeNode(ear)

                # skipping the next vertice leads to less sliver triangles
                ear = next.next
                stop = next.next

                continue

            ear = next

            # if we looped through the whole remaining polygon and can't find any more ears
            if ear == stop:
                # try filtering points and slicing again
                if not _pass:
                    _earcut.earcutLinked(_earcut.filterPoints(ear), triangles, dim, minX, minY, size, 1)

                    # if this didn't work, try curing all small self-intersections locally
                elif _pass == 1:
                    ear = _earcut.cureLocalIntersections(ear, triangles, dim)
                    _earcut.earcutLinked(ear, triangles, dim, minX, minY, size, 2)

                    # as a last resort, try splitting the remaining polygon into two
                elif _pass == 2:
                    _earcut.splitEarcut(ear, triangles, dim, minX, minY, size)

                break

    # check whether a polygon node forms a valid ear with adjacent nodes
    @staticmethod
    def isEar(ear):
        a = ear.prev
        b = ear
        c = ear.next

        if _earcut.area(a, b, c) >= 0:
            return False # reflex, can't be an ear

        # now make sure we don't have other points inside the potential ear
        p = ear.next.next

        while p != ear.prev:
            if _earcut.pointInTriangle(a.x, a.y, b.x, b.y, c.x, c.y, p.x, p.y) and _earcut.area(p.prev, p, p.next) >= 0:
                    return False
            p = p.next

        return True

    @staticmethod
    def isEarHashed(ear, minX, minY, size):
        a = ear.prev
        b = ear
        c = ear.next

        if _earcut.area(a, b, c) >= 0:
            return False # reflex, can't be an ear

        # triangle bbox; min & max are calculated like this for speed
        minTX = (a.x if a.x < c.x else c.x) if a.x < b.x else (b.x if b.x < c.x else c.x)
        minTY = (a.y if a.y < c.y else c.y) if a.y < b.y else (b.y if b.y < c.y else c.y)
        maxTX = (a.x if a.x > c.x else c.x) if a.x > b.x else (b.x if b.x > c.x else c.x)
        maxTY = (a.y if a.y > c.y else c.y) if a.y > b.y else (b.y if b.y > c.y else c.y)

        # z-order range for the current triangle bbox;
        minZ = _earcut.zOrder(minTX, minTY, minX, minY, size)
        maxZ = _earcut.zOrder(maxTX, maxTY, minX, minY, size)

        # first look for points inside the triangle in increasing z-order
        p = ear.nextZ

        while p and p.z <= maxZ:
            if p != ear.prev and p != ear.next and _earcut.pointInTriangle(a.x, a.y, b.x, b.y, c.x, c.y, p.x, p.y) and _earcut.area(p.prev, p, p.next) >= 0:
                return False
            p = p.nextZ

        # then look for points in decreasing z-order
        p = ear.prevZ

        while p and p.z >= minZ:
            if p != ear.prev and p != ear.next and _earcut.pointInTriangle(a.x, a.y, b.x, b.y, c.x, c.y, p.x, p.y) and _earcut.area(p.prev, p, p.next) >= 0:
                return False
            p = p.prevZ

        return True

    # go through all polygon nodes and cure small local self-intersections
    @staticmethod
    def cureLocalIntersections(start, triangles, dim):
        do = True
        p = start

        while do or p != start:
            do = False

            a = p.prev
            b = p.next.next

            if not _earcut.equals(a, b) and _earcut.intersects(a, p, p.next, b) and _earcut.locallyInside(a, b) and _earcut.locallyInside(b, a):
                triangles.append(a.i / dim)
                triangles.append(p.i / dim)
                triangles.append(b.i / dim)

                # remove two nodes involved
                _earcut.removeNode(p)
                _earcut.removeNode(p.next)

                p = start = b

            p = p.next

        return p

    # try splitting polygon into two and triangulate them independently
    @staticmethod
    def splitEarcut(start, triangles, dim, minX, minY, size):
        # look for a valid diagonal that divides the polygon into two
        do = True
        a = start

        while do or a != start:
            do = False
            b = a.next.next

            while b != a.prev:
                if a.i != b.i and _earcut.isValidDiagonal(a, b):
                    # split the polygon in two by the diagonal
                    c = _earcut.splitPolygon(a, b)

                    # filter colinear points around the cuts
                    a = _earcut.filterPoints(a, a.next)
                    c = _earcut.filterPoints(c, c.next)

                    # run earcut on each half
                    _earcut.earcutLinked(a, triangles, dim, minX, minY, size)
                    _earcut.earcutLinked(c, triangles, dim, minX, minY, size)
                    return

                b = b.next

            a = a.next

    # link every hole into the outer loop, producing a single-ring polygon without holes
    @staticmethod
    def eliminateHoles(data, holeIndices, outerNode, dim):
        queue = []
        i = None
        _len = len(holeIndices)
        start = None
        end = None
        _list = None

        for i in range(len(holeIndices)):
            start = holeIndices[i] * dim
            end =  holeIndices[i + 1] * dim if i < _len - 1 else len(data)
            _list = _earcut.linkedList(data, start, end, dim, False)

            if (_list == _list.next):
                _list.steiner = True

            queue.append(_earcut.getLeftmost(_list))

        queue = sorted(queue, key=lambda i: i.x)

        # process holes from left to right
        for i in range(len(queue)):
            _earcut.eliminateHole(queue[i], outerNode)
            outerNode = _earcut.filterPoints(outerNode, outerNode.next)

        return outerNode

    @staticmethod
    def compareX(a, b):
        return a.x - b.x

    # find a bridge between vertices that connects hole with an outer ring and and link it
    @staticmethod
    def eliminateHole(hole, outerNode):
        outerNode = _earcut.findHoleBridge(hole, outerNode)
        if outerNode:
            b = _earcut.splitPolygon(outerNode, hole)
            _earcut.filterPoints(b, b.next)

    # David Eberly's algorithm for finding a bridge between hole and outer polygon
    @staticmethod
    def findHoleBridge(hole, outerNode):
        do = True
        p = outerNode
        hx = hole.x
        hy = hole.y
        qx = -math.inf
        m = None

        # find a segment intersected by a ray from the hole's leftmost point to the left;
        # segment's endpoint with lesser x will be potential connection point
        while do or p != outerNode:
            do = False
            if hy <= p.y and hy >= p.next.y and p.next.y - p.y != 0:
                x = p.x + (hy - p.y) * (p.next.x - p.x) / (p.next.y - p.y)

                if x <= hx and x > qx:
                    qx = x

                    if (x == hx):
                        if hy == p.y:
                            return p
                        if hy == p.next.y:
                            return p.next

                    m = p if p.x < p.next.x else p.next

            p = p.next

        if not m:
            return None

        if hx == qx:
            return m.prev # hole touches outer segment; pick lower endpoint

        # look for points inside the triangle of hole point, segment intersection and endpoint;
        # if there are no points found, we have a valid connection;
        # otherwise choose the point of the minimum angle with the ray as connection point

        stop = m
        mx = m.x
        my = m.y
        tanMin = math.inf
        tan = None

        p = m.next

        while p != stop:
            hx_or_qx = hx if hy < my else qx
            qx_or_hx = qx if hy < my else hx

            if hx >= p.x and p.x >= mx and _earcut.pointInTriangle(hx_or_qx, hy, mx, my, qx_or_hx, hy, p.x, p.y):

                tan = abs(hy - p.y) / (hx - p.x) # tangential

                if (tan < tanMin or (tan == tanMin and p.x > m.x)) and _earcut.locallyInside(p, hole):
                    m = p
                    tanMin = tan

            p = p.next

        return m

    # interlink polygon nodes in z-order
    @staticmethod
    def indexCurve(start, minX, minY, size):
        do = True
        p = start

        while do or p != start:
            do = False

            if p.z == None:
                p.z = _earcut.zOrder(p.x, p.y, minX, minY, size)

            p.prevZ = p.prev
            p.nextZ = p.next
            p = p.next

        p.prevZ.nextZ = None
        p.prevZ = None

        _earcut.sortLinked(p)

    # Simon Tatham's linked _list merge sort algorithm
    # http:#www.chiark.greenend.org.uk/~sgtatham/algorithms/_listsort.html
    @staticmethod
    def sortLinked(_list):
        do = True
        i = None
        p = None
        q = None
        e = None
        tail = None
        numMerges = None
        pSize = None
        qSize = None
        inSize = 1

        while do or numMerges > 1:
            do = False
            p = _list
            _list = None
            tail = None
            numMerges = 0

            while p:
                numMerges += 1
                q = p
                pSize = 0
                for i in range(inSize):
                    pSize += 1
                    q = q.nextZ
                    if not q:
                        break

                qSize = inSize

                while pSize > 0 or (qSize > 0 and q):

                    if pSize == 0:
                        e = q
                        q = q.nextZ
                        qSize -= 1

                    elif (qSize == 0 or not q):
                        e = p
                        p = p.nextZ
                        pSize -= 1

                    elif (p.z <= q.z):
                        e = p
                        p = p.nextZ
                        pSize -= 1

                    else:
                        e = q
                        q = q.nextZ
                        qSize -= 1

                    if tail:
                        tail.nextZ = e

                    else:
                        _list = e

                    e.prevZ = tail
                    tail = e

                p = q

            tail.nextZ = None
            inSize *= 2

        return _list


    # z-order of a point given coords and size of the data bounding box
    @staticmethod
    def zOrder(x, y, minX, minY, size):
        # coords are transformed into non-negative 15-bit integer range
        x = 32767 * (x - minX) / size
        y = 32767 * (y - minY) / size

        x = (x | (x << 8)) & 0x00FF00FF
        x = (x | (x << 4)) & 0x0F0F0F0F
        x = (x | (x << 2)) & 0x33333333
        x = (x | (x << 1)) & 0x55555555

        y = (y | (y << 8)) & 0x00FF00FF
        y = (y | (y << 4)) & 0x0F0F0F0F
        y = (y | (y << 2)) & 0x33333333
        y = (y | (y << 1)) & 0x55555555

        return x | (y << 1)

    # find the leftmost node of a polygon ring
    @staticmethod
    def getLeftmost(start):
        do = True
        p = start
        leftmost = start

        while do or p != start:
            do = False
            if p.x < leftmost.x:
                leftmost = p
            p = p.next

        return leftmost

    # check if a point lies within a convex triangle
    @staticmethod
    def pointInTriangle(ax, ay, bx, by, cx, cy, px, py):
        return (cx - px) * (ay - py) - (ax - px) * (cy - py) >= 0 and \
            (ax - px) * (by - py) - (bx - px) * (ay - py) >= 0 and \
            (bx - px) * (cy - py) - (cx - px) * (by - py) >= 0

    # check if a diagonal between two polygon nodes is valid (lies in polygon interior)
    @staticmethod
    def isValidDiagonal(a, b):
        return a.next.i != b.i and a.prev.i != b.i and not _earcut.intersectsPolygon(a, b) and \
               _earcut.locallyInside(a, b) and _earcut.locallyInside(b, a) and _earcut.middleInside(a, b)

    # signed area of a triangle
    @staticmethod
    def area(p, q, r):
        return (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

    # check if two points are equal
    @staticmethod
    def equals(p1, p2):
        return p1.x == p2.x and p1.y == p2.y


    # check if two segments intersect
    @staticmethod
    def intersects(p1, q1, p2, q2):
        if (_earcut.equals(p1, q1) and _earcut.equals(p2, q2)) or (_earcut.equals(p1, q2) and _earcut.equals(p2, q1)):
            return True

        return _earcut.area(p1, q1, p2) > 0 != _earcut.area(p1, q1, q2) > 0 and \
               _earcut.area(p2, q2, p1) > 0 != _earcut.area(p2, q2, q1) > 0

    # check if a polygon diagonal intersects any polygon segments
    @staticmethod
    def intersectsPolygon(a, b):
        do = True
        p = a

        while do or p != a:
            do = False
            if (p.i != a.i and p.next.i != a.i and p.i != b.i and p.next.i != b.i and _earcut.intersects(p, p.next, a, b)):
                return True

            p = p.next

        return False

    # check if a polygon diagonal is locally inside the polygon
    @staticmethod
    def locallyInside(a, b):
        if _earcut.area(a.prev, a, a.next) < 0:
            return  _earcut.area(a, b, a.next) >= 0 and _earcut.area(a, a.prev, b) >= 0
        else:
            return _earcut.area(a, b, a.prev) < 0 or _earcut.area(a, a.next, b) < 0

    # check if the middle point of a polygon diagonal is inside the polygon
    @staticmethod
    def middleInside(a, b):
        do = True
        p = a
        inside = False
        px = (a.x + b.x) / 2
        py = (a.y + b.y) / 2

        while do or p != a:
            do = False
            if ((p.y > py) != (p.next.y > py)) and (px < (p.next.x - p.x) * (py - p.y) / (p.next.y - p.y) + p.x):
                inside = not inside

            p = p.next

        return inside

    # link two polygon vertices with a bridge; if the vertices belong to the same ring, it splits polygon into two;
    # if one belongs to the outer ring and another to a hole, it merges it into a single ring
    @staticmethod
    def splitPolygon(a, b):
        a2 = _earcut.Node(a.i, a.x, a.y)
        b2 = _earcut.Node(b.i, b.x, b.y)
        an = a.next
        bp = b.prev

        a.next = b
        b.prev = a

        a2.next = an
        an.prev = a2

        b2.next = a2
        a2.prev = b2

        bp.next = b2
        b2.prev = bp

        return b2


    # create a node and optionally link it with previous one (in a circular doubly linked _list)
    @staticmethod
    def insertNode(i, x, y, last):
        p = _earcut.Node(i, x, y)

        if not last:
            p.prev = p
            p.next = p

        else:
            p.next = last.next
            p.prev = last
            last.next.prev = p
            last.next = p

        return p

    @staticmethod
    def removeNode(p):
        p.next.prev = p.prev
        p.prev.next = p.next

        if p.prevZ:
            p.prevZ.nextZ = p.nextZ

        if p.nextZ:
            p.nextZ.prevZ = p.prevZ

    @staticmethod
    class Node(object):
        def __init__(self, i, x, y):
        # vertice index in coordinates array
            self.i = i

            # vertex coordinates

            self.x = x
            self.y = y

            # previous and next vertice nodes in a polygon ring
            self.prev = None
            self.next = None

            # z-order curve value
            self.z = None

            # previous and next nodes in z-order
            self.prevZ = None
            self.nextZ = None

            # indicates whether this is a steiner point
            self.steiner = False


    # return a percentage difference between the polygon area and its triangulation area;
    # used to verify correctness of triangulation
    @staticmethod
    def deviation(data, holeIndices, dim, triangles):
        _len = len(holeIndices)
        hasHoles = holeIndices and len(holeIndices)
        outerLen = holeIndices[0] * dim if hasHoles else len(data)

        polygonArea = abs(_earcut.signedArea(data, 0, outerLen, dim))

        if hasHoles:
            for i in range(_len):
                start = holeIndices[i] * dim
                end = holeIndices[i + 1] * dim if i < _len - 1 else len(data)
                polygonArea -= abs(_earcut.signedArea(data, start, end, dim))

        trianglesArea = 0

        for i in range(0, len(triangles), 3):
            a = triangles[i] * dim
            b = triangles[i + 1] * dim
            c = triangles[i + 2] * dim
            trianglesArea += abs(
                (data[a] - data[c]) * (data[b + 1] - data[a + 1]) -
                (data[a] - data[b]) * (data[c + 1] - data[a + 1]))

        if polygonArea == 0 and trianglesArea == 0:
            return 0

        return abs((trianglesArea - polygonArea) / polygonArea)

    @staticmethod
    def signedArea(data, start, end, dim):
        sum = 0
        j = end - dim

        for i in range(start, end, dim):
            sum += (data[j] - data[i]) * (data[i + 1] + data[j + 1])
            j = i

        return sum


    # turn a polygon in a multi-dimensional array form (e.g. as in GeoJSON) into a form Earcut accepts
    @staticmethod
    def flatten(data):
        dim = len(data[0][0])
        result = {
            'vertices': [],
            'holes': [],
            'dimensions': dim
        }
        holeIndex = 0

        for i in range(len(data)):
            for j in range(len(data[i])):
                for d in range(dim):
                    result['vertices'].append(data[i][j][d])

            if i > 0:
                holeIndex += len(data[i - 1])
                result['holes'].append(holeIndex)

        return result

    @staticmethod
    def unflatten(data):
        result = []

        for i in range(0, len(data), 3):
            result.append(tuple(data[i:i + 3]))

        return result