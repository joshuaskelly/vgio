import math
import sys

PYTHON_3 = sys.version[0] == '3'

def clearList(list):
    if PYTHON_3:
        list.clear()
    else:
        list[:] = []

def angle2DRad(p1, p2, p3):
    ab = [p2[0] - p1[0], p2[1] - p1[1]]
    cb = [p2[0] - p3[0], p2[1] - p3[1]]

    dot = ab[0] * cb[0] + ab[1] * cb[1]

    abSqr = ab[0] * ab[0] + ab[1] * ab[1]
    cbSqr = cb[0] * cb[0] + cb[1] * cb[1]

    cosSqr = dot * dot / float(abSqr) / float(cbSqr)

    cos2 = 2 * cosSqr - 1

    if cos2 <= -1:
        alpha2 = math.pi
    elif cos2 >= 1:
        alpha2 = 0
    else:
        alpha2 = math.acos(cos2)

    rs = alpha2 / 2.0

    if dot < 0:
        rs = math.pi - rs

    det = ab[0] * cb[1] - ab[1] * cb[0]
    if det < 0:
        rs = (2 * math.pi) - rs

    return rs

def lineSide(point, line):
    return (point[0] - line.x1()) * line.height() - (point[1] - line.y1()) * line.width()

def distance(p1, p2):
    return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))

def linesIntersect(line1, line2):
    # Check for parallel lines
    if line1.x1() == line1.x2() and line2.x1() == line2.x2() or line1.y1() == line1.y2() and line2.y1() == line2.y2():
        return False, None

    # Check for shared endpoints
    if (line1.x1() == line2.x1() and line1.y1() == line2.y1()) or \
       (line1.x2() == line2.x2() and line1.y2() == line2.y2()) or \
       (line1.x1() == line2.x2() and line1.y1() == line2.y2()) or \
       (line1.x2() == line2.x1() and line1.y2() == line2.y1()):
        return False, None

    # Check bounding boxes
    if max(line1.x1(), line1.x2()) < min(line2.x1(), line2.x2()) or \
       max(line2.x1(), line2.x2()) < min(line1.x1(), line1.x2()) or \
       max(line1.y1(), line1.y2()) < min(line2.y1(), line2.y2()) or \
       max(line2.y1(), line2.y2()) < min(line1.y1(), line1.y2()):
        return False, None

    # Check for perpendicular lines
    if line1.x1() == line1.x2() and line2.y1() == line2.y2():
        return True, [line1.x1, line2.y1()]
    if line1.y1() == line1.y2() and line2.x1() == line2.x2():
        return True, [line2.x1(), line1.y1()]

    # Do full intersection calculation
    a1 = line1.y2() - line1.y1()
    a2 = line2.y2() - line2.y1()
    b1 = line1.x1() - line1.x2()
    b2 = line2.x1() - line2.x2()
    c1 = (a1 * line1.x1()) + (b1 * line1.y1())
    c2 = (a2 * line2.x1()) + (b2 * line2.y1())
    det = a1 * b2 - a2 * b1

    if det == 0:
        return False, None

    # Calculate intersection point
    out = [(b2 * c1 - b1 * c2) / float(det), (a1 * c2 - a2 * c1) / float(det)]

    # Check that intersection point is on both lines
    if min(line1.x1(), line1.x2()) <= out[0] and out[0] <= max(line1.x1(), line1.x2()) and \
       min(line1.y1(), line1.y2()) <= out[1] and out[1] <= max(line1.y1(), line1.y2()) and \
       min(line2.x1(), line2.x2()) <= out[0] and out[0] <= max(line2.x1(), line2.x2()) and \
       min(line2.y1(), line2.y2()) <= out[1] and out[1] <= max(line2.y1(), line2.y2()):
        return True, out

    # Intersection point does not lie on both lines
    return False, None

class bbox_t:
    def __init__(self):
        self.reset()

    def reset(self):
        self.min = [0, 0]
        self.max = [0, 0]

    def extend(self, x, y):
        # Init if recently reset
        if self.min[0] == 0 and self.min[1] == 0 and self.max[0] == 0 and self.max[1] == 0:
            self.min = [x, y]
            self.max = [x, y]

            return

        # Extend to fit the given point
        if x < self.min[0]:
            self.min[0] = x
        if x > self.max[0]:
            self.max[0] = x
        if y < self.min[1]:
            self.min[1] = y
        if y > self.max[1]:
            self.max[1] = y

    def point_within(self, x, y):
        return x >= self.min[0] and x <= self.max[0] and y >= self.min[1] and y <= self.max[1]

    def contains(self, point):
        return self.point_within(point[0], point[1])

    def is_within(self, bmin, bmax):
        return self.min[0] >= bmin[0] and self.max[0] <= bmax[0] and self.min[1] >= bmin[1] and self.max[1] <= bmax[1]

    def is_valid(self):
        return self.max[0] - self.min[0] > 0 and self.max[1] - self.min[1] > 0

    def size(self):
        return self.max[0] - self.min[0], self.max[1] - self.min[1]

    def width(self):
        return self.max[0] - self.min[0]

    def height(self):
        return self.max[1] - self.min[1]

    def mid(self):
        return self.mid_x(), self.mid_y()

    def mid_x(self):
        return self.min[0] + (self.width() * 0.5)

    def mid_y(self):
        return self.min[1] + (self.height() * 0.5)



class gl_vertex_t:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z

        raise "IndexError: index outside of range"


class gl_polygon_t:
    def __init__(self):
        self.vertices = []
        self.n_vertices = 0


class vdist_t:
    def __init__(self, index, distance):
        self.index = index
        self.distance = distance

    def __lt__(self, other):
        return self.distance < other.distance

class fseg2_t:
    def __init__(self, tl=[0, 0], br=[0, 0]):
        self.tl = tl
        self.br = br

    def x1(self):
        return self.tl[0]

    def y1(self):
        return self.tl[1]

    def x2(self):
        return self.br[0]

    def y2(self):
        return self.br[1]

    def p1(self):
        return self.tl[0], self.tl[1]

    def p2(self):
        return self.br[0], self.br[1]

    def left(self):
        return min(self.tl[0], self.br[0])

    def top(self):
        return min(self.tl[1], self.br[1])

    def right(self):
        return max(self.br[0], self.tl[0])

    def bottom(self):
        return max(self.br[1], self.tl[1])

    def width(self):
        return self.br[0] - self.tl[0]

    def height(self):
        return self.br[1] - self.tl[1]

class Polygon2D:
    def __init__(self):
        self.subpolys = []

    def hasPolygon(self):
        return len(self.subpolys) == 0

    def setZ(self, z):
        for a in range(len(self.subpolys)):
            for v in range(len(self.subpolys[a].n_vertices)):
                self.subpolys[a].vertices[v].z = z

    def nSubPolys(self):
        return len(self.subpolys)

    def addSubPoly(self):
        self.subpolys.append(gl_polygon_t())

    def getSubPoly(self, index):
        if index > len(self.subpolys):
            raise "IndexError: index outside of range"

        return self.subpolys[index]

    def removeSubPoly(self, index):
        if index > len(self.subpolys):
            return

        self.subpolys.remove(self.subpolys[index])

    def clear(self):
        clearList(self.subpolys)

    def totalVertices(self):
        return sum([s.n_vertices for s in self.subpolys])


class PolygonSplitter:
    class edge_t:
        def __init__(self):
            self.v1 = 0
            self.v2 = 0
            self.ok = True
            self.done = False
            self.inpoly = False
            self.sister = -1

    class vertex_t:
        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y
            self.ok = True

            self.edges_in = []
            self.edges_out = []
            self.distance = -1

        def __getitem__(self, index):
            if index == 0:
                return self.x
            elif index == 1:
                return self.y

            raise "IndexError: index outside of range"

    class poly_outline_t:
        def __init__(self):
            self.edges = []
            self.bbox = bbox_t()
            self.clockwise = True
            self.convex = True


    def __init__(self):
        self.vertices = []
        self.edges = []
        self.concave_edges = []
        self.polygon_outlines = []
        self.split_edges_start = 0
        self.verbose = True
        self.last_angle = 0


    def clear(self):
        clearList(self.vertices)
        clearList(self.edges)
        clearList(self.polygon_outlines)

    def setVerbose(self, v):
        self.verbose = v

    def addVertex(self, x, y):
        # Check if vertex already exists
        for a in range(len(self.vertices)):
            if self.vertices[a].x == x and self.vertices[a].y == y:
                return a

        self.vertices.append(PolygonSplitter.vertex_t(x, y))
        self.vertices[-1].distance = 999999

        return len(self.vertices) - 1

    def addEdge(self, x1, y1, x2=None, y2=None):
        if x2 is None or y2 is None:
            return self.addEdgeFromVertices(x1, y1)

        return self.addEdgeFromCoords(x1, y1, x2, y2)

    def addEdgeFromCoords(self, x1, y1, x2, y2):
        v1 = self.addVertex(x1, y1)
        v2 = self.addVertex(x2, y2)

        return self.addEdgeFromVertices(v1, v2)

    def addEdgeFromVertices(self, v1, v2):
        # Check for duplicate edge
        for a in range(len(self.edges)):
            if self.edges[a].v1 == v1 and self.edges[a].v2 == v2:
                return a

        edge = PolygonSplitter.edge_t()
        edge.v1 = v1
        edge.v2 = v2
        edge.ok = True
        edge.done = False
        edge.inpoly = False
        edge.sister = -1

        self.edges.append(edge)

        # Add edge to it's vertices' edge list
        index = len(self.edges) - 1
        self.vertices[v1].edges_out.append(index)
        self.vertices[v2].edges_in.append(index)

        return index

    def findNextEdge(self, edge, ignore_done=True, only_convex=True, ignore_inpoly=False):
        e = self.edges[edge]
        v1 = self.vertices[e.v1]
        v2 = self.vertices[e.v2]

        min_angle = 2 * math.pi
        next = -1

        for a in range(len(v2.edges_out)):
            out = self.edges[v2.edges_out[a]]

            if ignore_done and out.done:
                continue

            if ignore_inpoly and out.inpoly:
                continue

            # Ignore edges on the reverse side of this
            if out.v1 == e.v2 and out.v2 == e.v1:
                continue

            if not out.ok:
                continue

            angle = angle2DRad(v1, v2, self.vertices[out.v2])

            if angle < min_angle:
                min_angle = angle
                next = v2.edges_out[a]

        self.last_angle = min_angle
        if only_convex and min_angle > math.pi:
            return -1

        return next

    def flipEdge(self, edge):
        e = self.edges[edge]
        v1 = self.vertices[e.v1]
        v2 = self.vertices[e.v2]

        for a in range(len(v1.edges_out)):
            if v1.edges_out[a] == edge:
                v1.edges_out.remove(v1.edges_out[a])
                break

        for a in range(len(v2.edges_in)):
            if v2.edges_in[a] == edge:
                v2.edges_in.remove(v2.edges_in[a])
                break

        # Flip the edge
        temp = e.v2
        e.v2 = e.v1
        e.v1 = temp

        v1.edges_in.append(edge)
        v2.edges_out.append(edge)

    def detectConcavity(self):
        clearList(self.concave_edges)

        for a in range(len(self.edges)):
            if not self.edges[a].ok:
                continue

            next = self.findNextEdge(a, False)
            if next < 0:
                self.concave_edges.append(a)

    def detectUnclosed(self):
        end_verts = []
        start_verts = []

        # Go through all vertices
        for a in range(len(self.vertices)):
            if not self.vertices[a].edges_out:
                end_verts.append(a)
            elif not self.vertices[a].edges_in:
                start_verts.append(a)

        # If there are no start or end verts, the polygon is closed
        if not end_verts and not start_verts:
            return False

        # Check if this is caused by flipped edges
        for a in range(len(self.vertices)):
            ev = self.vertices[end_verts[a]]

            for e in range(len(ev.edges_in)):
                edge = self.edges[ev.edges_in[e]]

                flipped = False
                for b in range(len(start_verts)):
                    sv = self.vertices[start_verts[b]]

                    if edge.v1 == start_verts[b] and edge.v2 == end_verts[a]:
                        self.flipEdge(ev.edges_in[e])

        # Re-check vertices
        clearList(end_verts)
        clearList(start_verts)

        for a in range(len(self.vertices)):
            if not self.vertices[a].ok:
                continue

            # If the vertex has no outgoing edges, polygon is unclosed
            if not self.vertices[a].edges_out:
                end_verts.append(a)
            elif not self.vertices[a].edges_in:
                start_verts.append(a)

        if not end_verts and not start_verts:
            return False

        # If still unclosed, check for detached edges and remove them
        for a in range(len(self.edges)):
            if not self.vertices[self.edges[a].v1].edges_in and not self.vertices[self.edges[a].v2].edges_out:
                self.edges[a].ok = False

                self.vertices[self.edges[a].v1].ok = False
                self.vertices[self.edges[a].v2].ok = False

        # Re-check vertices
        clearList(end_verts)
        clearList(start_verts)

        for a in range(len(self.vertices)):
            if not self.vertices[a].ok:
                continue

            # If the vertex has no outgoing edges, polygon is unclosed
            if not self.vertices[a].edges_out:
                end_verts.append(a)
            elif not self.vertices[a].edges_in:
                start_verts.append(a)

        if not end_verts and not start_verts:
            return False

        return True

    def tracePolyOutline(self, edge_start):
        self.polygon_outlines.append(PolygonSplitter.poly_outline_t())
        poly = self.polygon_outlines[-1]
        poly.convex = True
        edge_sum = 0

        edge = edge_start
        v1 = 0
        v2 = 0
        next = 0

        for a in range(100000):
            v1 = self.edges[edge].v1
            v2 = self.edges[edge].v2
            next = -1

            poly.edges.append(edge)

            if edge == edge_start:
                poly.bbox.extend(self.vertices[v1].x, self.vertices[v1].y)
            else:
                self.edges[edge].inpoly = True

            poly.bbox.extend(self.vertices[v2].x, self.vertices[v2].y)
            edge_sum = self.vertices[v1].x * self.vertices[v2].y - self.vertices[v2].x * self.vertices[v1].y

            next = self.findNextEdge(edge, True, False, True)

            if next < 0:
                for b in range(len(poly.edges)):
                    self.edges[poly.edges[b]].inpoly = False

                self.polygon_outlines.pop()
                return False

            if self.last_angle > math.pi:
                poly.convex = False

            if next == edge_start:
                break

            edge = next

        poly.clockwise = edge_sum < 0
        self.edges[edge_start].inpoly = True

        return True

    def testTracePolyOutline(self, edge_start):
        edge = edge_start
        v1 = 0
        v2 = 0
        for a in range(100000):
            next = self.findNextEdge(edge, False, True)

            if next < 0:
                return False

            if next == edge_start:
                break

            edge = next

        return True

    def splitFromEdge(self, splitter_edge):
        v1 = self.edges[splitter_edge].v1
        v2 = self.edges[splitter_edge].v2

        min_dist = 999999
        closest = -1

        for a in range(len(self.vertices)):
            if lineSide(self.vertices[a], fseg2_t(self.vertices[v1], self.vertices[v2])) > 0 and self.vertices[a].ok:
                self.vertices[a].distance = distance(self.vertices[v2], self.vertices[a])
                if self.vertices[a].distance < min_dist:
                    min_dist = self.vertices[a].distance
                    closest = a

        if closest == -1:
            return False

        intersect = False
        pointi = [0, 0]

        for a in range(len(self.edges)):
            # Ignore edge if adjacent to the vertices we are looking at
            if self.edges[a].v1 == closest or \
               self.edges[a].v2 == closest or \
               self.edges[a].v1 == v2 or \
               self.edges[a].v2 == v2 or \
               not self.edges[a].ok:
                continue

            intersect, pointi = linesIntersect(fseg2_t(self.vertices[v2], self.vertices[closest]), fseg2_t(self.vertices[self.edges[a].v1], self.vertices[self.edges[a].v2]))
            if intersect:
                break

        if not intersect:
            # No intersections, create split
            e1 = self.addEdge(v2, closest)
            e2 = self.addEdge(closest, v2)
            self.edges[e1].sister = e2
            self.edges[e2].sister = e1

            return True

        # Find closest vertex
        sorted_verts = []
        for a in range(len(self.vertices)):
            if self.vertices[a].distance < 999999:
                sorted_verts.append(vdist_t(a, self.vertices[a].distance))

        # Go through potential split vertices, closest first
        sorted_verts = sorted(sorted_verts, key=lambda x: x.distance)

        for a in range(len(sorted_verts)):
            index = sorted_verts[a].index
            vert = self.vertices[index]

            intersect = False
            for a in range(len(self.edges)):
                if self.edges[a].v1 == index or \
                   self.edges[a].v2 == index or \
                   self.edges[a].v1 == v2 or \
                   self.edges[a].v2 == v2 or \
                   not self.edges[a].ok:
                    continue

                intersect, pointi = linesIntersect(fseg2_t(self.vertices[v2], vert), fseg2_t(self.vertices[self.edges[a].v1], self.vertices[self.edges[a].v2]))
                if intersect:
                    break

            if not intersect:
                e1 = self.addEdge(v2, index)
                e2 = self.addEdge(index, v2)
                self.edges[e1].sister = e2
                self.edges[e2].sister = e1

                return True

        # No split created
        return False

    def buildSubPoly(self, edge_start, poly):
        if not poly:
            return False

        edge = edge_start
        verts = []

        for a in range(1000):
            verts.append(self.edges[edge].v1)

            if edge != edge_start:
                self.edges[edge].done = True

            edge = self.findNextEdge(edge)

            if edge < 0:
                return False

            if edge == edge_start:
                break

        self.edges[edge_start].done = True

        # Check if polygon is valid
        if len(verts) >= 3:
            poly.n_vertices = len(verts)
            poly.vertices = []

            for a in range(len(verts)):
                vert = self.vertices[verts[a]]
                poly.vertices.append(gl_vertex_t(vert.x, vert.y, 0))

            return True

        return False

    def doSplitting(self, poly):
        self.split_edges_start = len(self.edges)

        # Trace outlines
        for a in range(len(self.edges)):
            if self.edges[a].inpoly or not self.edges[a].ok:
                continue
            self.tracePolyOutline(a)

        # Check if any edges are not part of a polygon outline
        for a in range(len(self.edges)):
            if not self.edges[a].inpoly:
                self.edges[a].ok = False

        # Check for cases where edges or vertices can be thrown out
        for a in range(len(self.polygon_outlines)):
            # Check if this polygon intersects with any others
            separate = True
            for b in range(len(self.polygon_outlines)):
                if b == a:
                    continue

                bb1 = self.polygon_outlines[a].bbox
                bb2 = self.polygon_outlines[b].bbox

                if not (bb2.min[0] > bb1.max[0] or bb2.max[0] < bb1.min[0] or \
                        bb2.min[1] > bb1.max[1] or bb2.max[1] < bb1.min[1]):
                    separate = False
                    break

            # If the polygon didn't intersect and is convex and clockwise (outer)
            if separate and self.polygon_outlines[a].clockwise and self.polygon_outlines[a].convex:
                for b in range(len(self.polygon_outlines)):
                    self.edges[self.polygon_outlines[a].edges[b]].done = True

                    v1 = self.edges[self.polygon_outlines[a].edges[b]].v1
                    if len(self.vertices[v1].edges_in) == 1 and len(self.vertices[v1].edges_out) == 1:
                        self.vertices[v1].ok = False

                    v2 = self.edges[self.polygon_outlines[a].edges[b]].v2
                    if len(self.vertices[v2].edges_in) == 1 and len(self.vertices[v2].edges_out) == 1:
                        self.vertices[v2].ok = False

            # If the polygon didn't intersect and is anticlockwise (inner), it is invalid
            elif separate and not self.polygon_outlines[a].clockwise:
                for b in range(len(self.polygon_outlines[a].edges)):
                    self.edges[self.polygon_outlines[a].edges[b]].ok = False

                    v1 = self.edges[self.polygon_outlines[a].edges[b]].v1
                    if len(self.vertices[v1].edges_in) == 1 and len(self.vertices[v1].edges_out) == 1:
                        self.vertices[v1].ok = False

                    v2 = self.edges[self.polygon_outlines[a].edges[b]].v2
                    if len(self.vertices[v2].edges_in) == 1 and len(self.vertices[v2].edges_out) == 1:
                        self.vertices[v2].ok = False

        # Detect concave edges/vertices
        self.detectConcavity()

        for l in range(100):
            for a in range(len(self.concave_edges)):
                self.splitFromEdge(self.concave_edges[a])

            self.detectConcavity()
            if not self.concave_edges:
                break

        # Remove unnecessary splits
        for a in range(self.split_edges_start, len(self.edges)):
            if not self.edges[a].ok:
                continue

            # Invalidate split
            self.edges[a].ok = False
            self.edges[self.edges[a].sister].ok = False

            # Check poly is still convex without split
            next = self.findNextEdge(a, False, True)
            if next >= 0:
                if self.testTracePolyOutline(next):
                    continue

            # Not convex, split is needed
            self.edges[a].ok = True
            self.edges[self.edges[a].sister].ok = True

        # Reset edge done status
        for a in range(len(self.edges)):
            self.edges[a].done = False

        # Build polygons
        for a in range(len(self.edges)):
            if self.edges[a].done or not self.edges[a].ok:
                continue

            poly.addSubPoly()
            if not self.buildSubPoly(a, poly.getSubPoly(poly.nSubPolys() - 1)):
                poly.removeSubPoly(poly.nSubPolys() - 1)

        return True

    def open(self, lines):
        if not lines:
            return

        self.clear()

        for line in lines:
            self.addEdge(line[0][0], line[0][1], line[1][0], line[1][1])
