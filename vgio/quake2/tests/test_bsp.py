import unittest

from vgio.quake2.tests.basecase import TestCase
from vgio.quake2 import bsp

significant_digits = 5


class TestBspReadWrite(TestCase):
    def test_lump(self):
        offset = 0
        length = 2147483647

        l0 = bsp.Lump(offset, length)

        bsp.Lump.write(self.buff, l0)
        self.buff.seek(0)

        l1 = bsp.Lump.read(self.buff)

        self.assertEqual(l0.offset, l1.offset, 'Offsets should be equal')
        self.assertEqual(l0.length, l1.length, 'Lengths should be equal')

    def test_header(self):
        identity = b'IBSP'
        version = 38
        lumps = [bsp.Lump(i, 2<<i) for i in range(19)]

        h0 = bsp.Header(identity, version, lumps)

        bsp.Header.write(self.buff, h0)
        self.buff.seek(0)

        h1 = bsp.Header.read(self.buff)

        self.assertEqual(h0.identity, h1.identity, 'Identities should be equal')
        self.assertEqual(h0.version, h0.version, 'Versions should be equal')

        for i in range(19):
            l0 = h0.lumps[i]
            l1 = h1.lumps[i]

            self.assertEqual(l0.offset, l1.offset, 'Offsets should be equal')
            self.assertEqual(l0.length, l1.length, 'Lengths should be equal')

    def test_plane(self):
        normal = 0.0, 0.0, 1.0
        distance = 1.0
        type = 0

        p0 = bsp.Plane(*normal,
                         distance,
                         type)

        bsp.Plane.write(self.buff, p0)
        self.buff.seek(0)

        p1 = bsp.Plane.read(self.buff)

        self.assertAlmostEqual(p0.normal, p1.normal, significant_digits, 'Normal vectors should be equal')
        self.assertAlmostEqual(p0.distance, p1.distance, significant_digits, 'Distances should be equal')
        self.assertEqual(p0.type, p1.type, 'Types should equal')

    def test_vertex(self):
        v0 = bsp.Vertex(1.0, -0.5, 1.25)

        bsp.Vertex.write(self.buff, v0)
        self.buff.seek(0)

        v1 = bsp.Vertex.read(self.buff)

        self.assertAlmostEqual(v0.x, v1.x, significant_digits, 'X coordinates should be equal')
        self.assertAlmostEqual(v0.y, v1.y, significant_digits, 'Y coordinates should be equal')
        self.assertAlmostEqual(v0.z, v1.z, significant_digits, 'Z coordinates should be equal')

    def test_node(self):
        plane_number = 0
        children = 1, 2
        bounding_box_min = -32767, -32767, -32767
        bounding_box_max = 32767, 32767, 32767
        first_face = 0
        number_of_faces = 4

        n0 = bsp.Node(plane_number,
                      *children,
                      *bounding_box_min,
                      *bounding_box_max,
                      first_face,
                      number_of_faces)

        bsp.Node.write(self.buff, n0)
        self.buff.seek(0)

        n1 = bsp.Node.read(self.buff)

        self.assertEqual(n0.plane_number, n1.plane_number, 'Plane numbers should be equal')
        self.assertEqual(n0.children, n1.children, 'Children should be equal')
        self.assertEqual(n0.bounding_box_min, n1.bounding_box_min, 'Bounding box minimums should be equal')
        self.assertEqual(n0.bounding_box_max, n1.bounding_box_max, 'Bounding box maximums should be equal')
        self.assertEqual(n0.first_face, n1.first_face, 'First faces should be equal')
        self.assertEqual(n0.number_of_faces, n1.number_of_faces, 'Number of faces should be equal')

    def test_texture_info(self):
        s = 1.0, -1.0, 0
        s_offset = 1.25
        t = -5.0, 6.0, 7.75
        t_offset = 0.0
        flags = 0
        value = 0
        texture_name = 'e1u1/arrow0'
        next_texture_info = -1

        t0 = bsp.TextureInfo(*s,
                             s_offset,
                             *t,
                             t_offset,
                             flags,
                             value,
                             texture_name,
                             next_texture_info)

        bsp.TextureInfo.write(self.buff, t0)
        self.buff.seek(0)

        t1 = bsp.TextureInfo.read(self.buff)

        self.assertAlmostEqual(t0.s, t1.s, significant_digits, 's vectors should be equal')
        self.assertAlmostEqual(t0.s_offset, t1.s_offset, significant_digits, 's offsets should be equal')
        self.assertAlmostEqual(t0.t, t1.t, significant_digits, 't vectors should be equal')
        self.assertAlmostEqual(t0.t_offset, t1.t_offset, significant_digits, 't offsets should be equal')
        self.assertEqual(t0.flags, t1.flags, 'Flags should be equal')
        self.assertEqual(t0.value, t1.value, 'Values should be equal')
        self.assertEqual(t0.texture_name, t1.texture_name, 'Texture Names should be equal')
        self.assertEqual(t0.next_texture_info, t1.next_texture_info, 'Next Texture Infos should be equal')

    def test_face(self):
        plane_number = 0
        side = 0
        first_edge = 0
        number_of_edges = 8
        texture_info = 0
        styles = 0, 1, 2, 3
        light_offset = 0

        f0 = bsp.Face(plane_number,
                      side,
                      first_edge,
                      number_of_edges,
                      texture_info,
                      *styles,
                      light_offset)

        bsp.Face.write(self.buff, f0)
        self.buff.seek(0)

        f1 = bsp.Face.read(self.buff)

        self.assertEqual(f0.plane_number, f1.plane_number, 'Plane numbers should be equal')
        self.assertEqual(f0.side, f1.side, 'Sides should be equal')
        self.assertEqual(f0.first_edge, f1.first_edge, 'First edges should be equal')
        self.assertEqual(f0.number_of_edges, f1.number_of_edges, 'Number of edges should be equal')
        self.assertEqual(f0.texture_info, f1.texture_info, 'Texture infos should be equal')
        self.assertEqual(f0.styles, f1.styles, 'Styles should be equal')
        self.assertEqual(f0.light_offset, f1.light_offset, 'Light offset should be equal')

    def test_leaf(self):
        contents = 0
        cluster = 2 << 8
        area = 32767
        bounding_box_min = -32767, -32767, -32767
        bounding_box_max = 32767, 32767, 32767
        first_leaf_face = 0
        number_of_leaf_faces = 2 << 2
        first_leaf_brush = 2 << 4
        number_of_leaf_brushes = 2 << 8

        l0 = bsp.Leaf(contents,
                      cluster,
                      area,
                      *bounding_box_min,
                      *bounding_box_max,
                      first_leaf_face,
                      number_of_leaf_faces,
                      first_leaf_brush,
                      number_of_leaf_brushes)

        bsp.Leaf.write(self.buff, l0)
        self.buff.seek(0)

        l1 = bsp.Leaf.read(self.buff)

        self.assertEqual(l0.contents, l1.contents, 'Contents should be equal')
        self.assertEqual(l0.cluster, l1.cluster, 'Clusters should be equal')
        self.assertEqual(l0.area, l1.area, 'Areas should be equal')
        self.assertEqual(l0.bounding_box_min, l1.bounding_box_min, 'bounding_box_min should be equal')
        self.assertEqual(l0.first_leaf_face, l1.first_leaf_face, 'first_leaf_face should be equal')
        self.assertEqual(l0.number_of_leaf_faces, l1.number_of_leaf_faces, 'number_of_leaf_faces should be equal')
        self.assertEqual(l0.first_leaf_brush, l1.first_leaf_brush, 'first_leaf_brush should be equal')
        self.assertEqual(l0.number_of_leaf_brushes, l1.number_of_leaf_brushes, 'number_of_leaf_brushes should be equal')

    def test_edge(self):
        vertexes = 0, 1
        e0 = bsp.Edge(*vertexes)

        bsp.Edge.write(self.buff, e0)
        self.buff.seek(0)

        e1 = bsp.Edge.read(self.buff)

        self.assertEqual(e0.vertexes, e1.vertexes, 'Vertexes should equal')

    def test_model(self):
        bounding_box_min = -32767, -32767, -32767
        bounding_box_max = 32767, 32767, 32767
        origin = 0, 0, 0
        head_node = 0
        first_face = 0
        number_of_faces = 8

        m0 = bsp.Model(*bounding_box_min,
                       *bounding_box_max,
                       *origin,
                       head_node,
                       first_face,
                       number_of_faces)

        bsp.Model.write(self.buff, m0)
        self.buff.seek(0)

        m1 = bsp.Model.read(self.buff)

        self.assertEqual(m0.bounding_box_min, m1.bounding_box_min, 'Bounding box minimums should be equal')
        self.assertEqual(m0.bounding_box_max, m1.bounding_box_max, 'Bounding box maximums should be equal')
        self.assertEqual(m0.origin, m1.origin, 'Origins should be equal')
        self.assertEqual(m0.head_node, m1.head_node, 'Head nodes should be equal')
        self.assertEqual(m0.first_face, m1.first_face, 'First faces should be equal')
        self.assertEqual(m0.number_of_faces, m1.number_of_faces, 'Number of faces should be equal')

    def test_brush(self):
        first_side = 0
        number_of_sides = 2 << 8
        contents = 4

        b0 = bsp.Brush(first_side,
                       number_of_sides,
                       contents)

        bsp.Brush.write(self.buff, b0)
        self.buff.seek(0)

        b1 = bsp.Brush.read(self.buff)

        self.assertEqual(b0.first_side, b1.first_side, 'first_side should be equal')
        self.assertEqual(b0.number_of_sides, b1.number_of_sides, 'number_of_sides should be equal')
        self.assertEqual(b0.contents, b1.contents, 'contents should be equal')

    def test_brush_side(self):
        plane_number = 32767
        texture_info = 256

        b0 = bsp.BrushSide(plane_number,
                       texture_info)

        bsp.BrushSide.write(self.buff, b0)
        self.buff.seek(0)

        b1 = bsp.BrushSide.read(self.buff)

        self.assertEqual(b0.plane_number, b1.plane_number, 'plane_number should be equal')
        self.assertEqual(b0.texture_info, b1.texture_info, 'texture_info should be equal')

    def test_area(self):
        number_of_area_portals = 0
        first_area_portal = 0

        a0 = bsp.Area(number_of_area_portals,
                      first_area_portal)

        bsp.Area.write(self.buff, a0)
        self.buff.seek(0)

        a1 = bsp.Area.read(self.buff)

        self.assertEqual(a0.number_of_area_portals, a1.number_of_area_portals, 'number_of_area_portals should be equal')
        self.assertEqual(a0.first_area_portal, a1.first_area_portal, 'first_area_portal should be equal')

    def test_area_portal(self):
        portal_number = 0
        other_area = 0

        a0 = bsp.AreaPortal(portal_number,
                            other_area)

        bsp.AreaPortal.write(self.buff, a0)
        self.buff.seek(0)

        a1 = bsp.AreaPortal.read(self.buff)

        self.assertEqual(a0.portal_number, a1.portal_number, 'portal_number should be equal')
        self.assertEqual(a0.other_area, a1.other_area, 'other_area should be equal')

    def test_bsp(self):
        b0 = bsp.Bsp.open('./test_data/test.bsp')
        b0.close()

        b0.save(self.buff)
        self.buff.seek(0)

        b1 = bsp.Bsp.open(self.buff)

        self.assertEqual(b0.identity, b1.identity, 'Identities should be equal')
        self.assertEqual(b0.version, b1.version, 'Versions should be equal')
        self.assertEqual(b0.entities, b1.entities, 'Entities should be equal')

        for i, pair in enumerate(zip(b0.planes, b1.planes)):
            p0, p1 = pair
            self.assertAlmostEqual(p0.normal, p1.normal, significant_digits, 'Normal vectors should be equal')
            self.assertAlmostEqual(p0.distance, p1.distance, significant_digits, 'Distances should be equal')
            self.assertEqual(p0.type, p1.type, 'Types should equal')

        for i, pair in enumerate(zip(b0.vertexes, b1.vertexes)):
            v0, v1 = pair
            self.assertAlmostEqual(v0.x, v1.x, significant_digits, 'X coordinates should be equal')
            self.assertAlmostEqual(v0.y, v1.y, significant_digits, 'Y coordinates should be equal')
            self.assertAlmostEqual(v0.z, v1.z, significant_digits, 'Z coordinates should be equal')

        self.assertEqual(b0.visibilities, b1.visibilities, 'Visibilities should be equal')

        for i, pair in enumerate(zip(b0.nodes, b1.nodes)):
            n0, n1 = pair
            self.assertEqual(n0.plane_number, n1.plane_number, 'Plane numbers should be equal')
            self.assertEqual(n0.children, n1.children, 'Children should be equal')
            self.assertEqual(n0.bounding_box_min, n1.bounding_box_min, 'Bounding box minimums should be equal')
            self.assertEqual(n0.bounding_box_max, n1.bounding_box_max, 'Bounding box maximums should be equal')
            self.assertEqual(n0.first_face, n1.first_face, 'First faces should be equal')
            self.assertEqual(n0.number_of_faces, n1.number_of_faces, 'Number of faces should be equal')

        for i, pair in enumerate(zip(b0.texture_infos, b1.texture_infos)):
            t0, t1 = pair
            self.assertAlmostEqual(t0.s, t1.s, significant_digits, 's vectors should be equal')
            self.assertAlmostEqual(t0.s_offset, t1.s_offset, significant_digits, 's offsets should be equal')
            self.assertAlmostEqual(t0.t, t1.t, significant_digits, 't vectors should be equal')
            self.assertAlmostEqual(t0.t_offset, t1.t_offset, significant_digits, 't offsets should be equal')
            self.assertEqual(t0.flags, t1.flags, 'Flags should be equal')
            self.assertEqual(t0.value, t1.value, 'Values should be equal')
            self.assertEqual(t0.texture_name, t1.texture_name, 'Texture Names should be equal')
            self.assertEqual(t0.next_texture_info, t1.next_texture_info, 'Next Texture Infos should be equal')

        for i, pair in enumerate(zip(b0.faces, b1.faces)):
            f0, f1 = pair
            self.assertEqual(f0.plane_number, f1.plane_number, 'Plane numbers should be equal')
            self.assertEqual(f0.side, f1.side, 'Sides should be equal')
            self.assertEqual(f0.first_edge, f1.first_edge, 'First edges should be equal')
            self.assertEqual(f0.number_of_edges, f1.number_of_edges, 'Number of edges should be equal')
            self.assertEqual(f0.texture_info, f1.texture_info, 'Texture infos should be equal')
            self.assertEqual(f0.styles, f1.styles, 'Styles should be equal')
            self.assertEqual(f0.light_offset, f1.light_offset, 'Light offset should be equal')

        self.assertEqual(b0.lighting, b1.lighting, 'Lighting should be equal')

        for i, pair in enumerate(zip(b0.leafs, b1.leafs)):
            l0, l1 = pair
            self.assertEqual(l0.contents, l1.contents, 'Contents should be equal')
            self.assertEqual(l0.cluster, l1.cluster, 'Clusters should be equal')
            self.assertEqual(l0.area, l1.area, 'Areas should be equal')
            self.assertEqual(l0.bounding_box_min, l1.bounding_box_min, 'bounding_box_min should be equal')
            self.assertEqual(l0.first_leaf_face, l1.first_leaf_face, 'first_leaf_face should be equal')
            self.assertEqual(l0.number_of_leaf_faces, l1.number_of_leaf_faces, 'number_of_leaf_faces should be equal')
            self.assertEqual(l0.first_leaf_brush, l1.first_leaf_brush, 'first_leaf_brush should be equal')
            self.assertEqual(l0.number_of_leaf_brushes, l1.number_of_leaf_brushes, 'number_of_leaf_brushes should be equal')

        self.assertEqual(b0.leaf_faces, b1.leaf_faces, 'Leaf Faces should be equal')
        self.assertEqual(b0.leaf_brushes, b1.leaf_brushes, 'Leaf Brushes should be equal')

        for i, pair in enumerate(zip(b0.edges, b1.edges)):
            e0, e1 = pair
            self.assertEqual(e0.vertexes, e1.vertexes, 'Vertexes should equal')

        self.assertEqual(b0.surf_edges, b1.surf_edges, 'Surf Edges should be equal')

        for i, pair in enumerate(zip(b0.models, b1.models)):
            m0, m1 = pair
            self.assertEqual(m0.bounding_box_min, m1.bounding_box_min, 'Bounding box minimums should be equal')
            self.assertEqual(m0.bounding_box_max, m1.bounding_box_max, 'Bounding box maximums should be equal')
            self.assertEqual(m0.origin, m1.origin, 'Origins should be equal')
            self.assertEqual(m0.head_node, m1.head_node, 'Head nodes should be equal')
            self.assertEqual(m0.first_face, m1.first_face, 'First faces should be equal')
            self.assertEqual(m0.number_of_faces, m1.number_of_faces, 'Number of faces should be equal')

        for i, pair in enumerate(zip(b0.brushes, b1.brushes)):
            br0, br1 = pair
            self.assertEqual(br0.first_side, br1.first_side, 'first_side should be equal')
            self.assertEqual(br0.number_of_sides, br1.number_of_sides, 'number_of_sides should be equal')
            self.assertEqual(br0.contents, br1.contents, 'contents should be equal')

        for i, pair in enumerate(zip(b0.brush_sides, b1.brush_sides)):
            br0, br1 = pair
            self.assertEqual(br0.plane_number, br1.plane_number, 'plane_number should be equal')
            self.assertEqual(br0.texture_info, br1.texture_info, 'texture_info should be equal')

        self.assertEqual(b0.pop, b1.pop, 'Pops should be equal')

        for i, pair in enumerate(zip(b0.areas, b1.areas)):
            a0, a1 = pair
            self.assertEqual(a0.number_of_area_portals, a1.number_of_area_portals, 'number_of_area_portals should be equal')
            self.assertEqual(a0.first_area_portal, a1.first_area_portal, 'first_area_portal should be equal')

        for i, pair in enumerate(zip(b0.area_portals, b1.area_portals)):
            a0, a1 = pair
            self.assertEqual(a0.portal_number, a1.portal_number, 'portal_number should be equal')
            self.assertEqual(a0.other_area, a1.other_area, 'other_area should be equal')


if __name__ == '__main__':
    unittest.main()
