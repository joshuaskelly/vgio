import unittest

from tests.basecase import TestCase
from quake.bsp import bsp29
from quake.bsp import bsp29a

significant_digits = 5


class TestBsp29ReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertTrue(bsp29.is_bspfile('./test_data/test.bsp'))
        self.assertFalse(bsp29.is_bspfile('./test_data/test.lmp'))
        self.assertFalse(bsp29.is_bspfile('./test_data/test.map'))
        self.assertFalse(bsp29.is_bspfile('./test_data/test.mdl'))
        self.assertFalse(bsp29.is_bspfile('./test_data/test.pak'))
        self.assertFalse(bsp29.is_bspfile('./test_data/test.spr'))
        self.assertFalse(bsp29.is_bspfile('./test_data/test.wad'))

    def test_plane(self):
        normal = 0.0, 0.0, 1.0
        distance = 1.0
        type = 0

        p0 = bsp29.Plane(*normal,
                         distance,
                         type)

        bsp29.Plane.write(self.buff, p0)
        self.buff.seek(0)

        p1 = bsp29.Plane.read(self.buff)

        self.assertAlmostEqual(p0.normal, p1.normal, significant_digits, 'Normal vectors should be equal')
        self.assertAlmostEqual(p0.distance, p1.distance, significant_digits, 'Distances should be equal')
        self.assertEqual(p0.type, p1.type, 'Types should equal')

    def test_miptexture(self):
        m0 = bsp29.Miptexture()
        m0.name = 'metal1_1'
        m0.width = 32
        m0.height = 32
        m0.offsets = 40, 1064, 1320, 1384
        m0.pixels = tuple([i % 256 for i in range(32 * 32 * 85 // 64)])

        bsp29.Miptexture.write(self.buff, m0)
        self.buff.seek(0)

        m1 = bsp29.Miptexture.read(self.buff)

        self.assertEqual(m0.name, m1.name, 'Names should be equal')
        self.assertEqual(m0.width, m1.width, 'Widths should be equal')
        self.assertEqual(m0.height, m1.height, 'Heights should be equal')
        self.assertEqual(m0.offsets, m1.offsets, 'Offsets should be equal')
        self.assertEqual(m0.pixels, m1.pixels, 'Pixel data should be equal')

    def test_vertex(self):
        v0 = bsp29.Vertex(1.0, -0.5, 1.25)

        bsp29.Vertex.write(self.buff, v0)
        self.buff.seek(0)

        v1 = bsp29.Vertex.read(self.buff)

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

        n0 = bsp29.Node(plane_number,
                      *children,
                      *bounding_box_min,
                      *bounding_box_max,
                      first_face,
                      number_of_faces)

        bsp29.Node.write(self.buff, n0)
        self.buff.seek(0)

        n1 = bsp29.Node.read(self.buff)

        self.assertEqual(n0.plane_number, n1.plane_number, 'Plane numbers should be equal')
        self.assertEqual(n0.children, n1.children, 'Children should be equal')
        self.assertEqual(n0.bounding_box_min, n1.bounding_box_min, 'Bounding box minimums should be equal')
        self.assertEqual(n0.bounding_box_max, n1.bounding_box_max, 'Bounding box maximums should be equal')
        self.assertEqual(n0.first_face, n1.first_face, 'First faces should be equal')
        self.assertEqual(n0.number_of_faces, n1.number_of_faces, 'Number of faces should be equal')

    def test_textureinfo(self):
        s = 1.0, -1.0, 0
        s_offset = 1.25
        t = -5.0, 6.0, 7.75
        t_offset = 0.0
        miptexture_number = 0
        flags = 8

        t0 = bsp29.TextureInfo(*s,
                             s_offset,
                             *t,
                             t_offset,
                             miptexture_number,
                             flags)

        bsp29.TextureInfo.write(self.buff, t0)
        self.buff.seek(0)

        t1 = bsp29.TextureInfo.read(self.buff)

        self.assertAlmostEqual(t0.s, t1.s, significant_digits, 's vectors should be equal')
        self.assertAlmostEqual(t0.s_offset, t1.s_offset, significant_digits, 's offsets should be equal')
        self.assertAlmostEqual(t0.t, t1.t, significant_digits, 't vectors should be equal')
        self.assertAlmostEqual(t0.t_offset, t1.t_offset, significant_digits, 't offsets should be equal')
        self.assertEqual(t0.miptexture_number, t1.miptexture_number, 'Miptexture numbers should be equal')
        self.assertEqual(t0.flags, t1.flags, 'Flags should be equal')

    def test_face(self):
        plane_number = 0
        side = 0
        first_edge = 0
        number_of_edges = 8
        texture_info = 0
        styles = 0, 1, 2, 3
        light_offset = 0

        f0 = bsp29.Face(plane_number,
                      side,
                      first_edge,
                      number_of_edges,
                      texture_info,
                      *styles,
                      light_offset)

        bsp29.Face.write(self.buff, f0)
        self.buff.seek(0)

        f1 = bsp29.Face.read(self.buff)

        self.assertEqual(f0.plane_number, f1.plane_number, 'Plane numbers should be equal')
        self.assertEqual(f0.side, f1.side, 'Sides should be equal')
        self.assertEqual(f0.first_edge, f1.first_edge, 'First edges should be equal')
        self.assertEqual(f0.number_of_edges, f1.number_of_edges, 'Number of edges should be equal')
        self.assertEqual(f0.texture_info, f1.texture_info, 'Texture infos should be equal')
        self.assertEqual(f0.styles, f1.styles, 'Styles should be equal')
        self.assertEqual(f0.light_offset, f1.light_offset, 'Light offset should be equal')

    def test_clipnode(self):
        plane_number = 0
        children = 0, 1

        c0 = bsp29.ClipNode(plane_number,
                          *children)

        bsp29.ClipNode.write(self.buff, c0)
        self.buff.seek(0)

        c1 = bsp29.ClipNode.read(self.buff)

        self.assertEqual(c0.plane_number, c1.plane_number, 'Plane numbers should equal')
        self.assertEqual(c0.children, c1.children, 'Children should equal')

    def test_leaf(self):
        contents = 0
        visibilitiy_offset = 0
        bounding_box_min = -32767, -32767, -32767
        bounding_box_max = 32767, 32767, 32767
        first_mark_surface = 0
        number_of_marked_surfaces = 4
        ambient_level = 0, 1, 2, 4

        l0 = bsp29.Leaf(contents,
                      visibilitiy_offset,
                      *bounding_box_min,
                      *bounding_box_max,
                      first_mark_surface,
                      number_of_marked_surfaces,
                      *ambient_level)

        bsp29.Leaf.write(self.buff, l0)
        self.buff.seek(0)

        l1 = bsp29.Leaf.read(self.buff)

        self.assertEqual(l0.contents, l1.contents, 'contents should be equal')
        self.assertEqual(l0.visibilitiy_offset, l1.visibilitiy_offset, 'visibilitiy_offset should be equal')
        self.assertEqual(l0.bounding_box_min, l1.bounding_box_min, 'bounding_box_min should be equal')
        self.assertEqual(l0.bounding_box_max, l1.bounding_box_max, 'bounding_box_max should be equal')
        self.assertEqual(l0.first_mark_surface, l1.first_mark_surface, 'first_mark_surface should be equal')
        self.assertEqual(l0.number_of_marked_surfaces, l1.number_of_marked_surfaces, 'number_of_marked_surfaces should be equal')
        self.assertEqual(l0.ambient_level, l1.ambient_level, 'ambient_level should be equal')

    def test_edge(self):
        vertexes = 0, 1
        e0 = bsp29.Edge(*vertexes)

        bsp29.Edge.write(self.buff, e0)
        self.buff.seek(0)

        e1 = bsp29.Edge.read(self.buff)

        self.assertEqual(e0.vertexes, e1.vertexes, 'Vertexes should equal')

    def test_model(self):
        bounding_box_min = -32767, -32767, -32767
        bounding_box_max = 32767, 32767, 32767
        origin = 0, 0, 0
        head_node = 0, 1, 2, 0
        visleafs = 0
        first_face = 0
        number_of_faces = 8

        m0 = bsp29.Model(*bounding_box_min,
                       *bounding_box_max,
                       *origin,
                       *head_node,
                       visleafs,
                       first_face,
                       number_of_faces)

        bsp29.Model.write(self.buff, m0)
        self.buff.seek(0)

        m1 = bsp29.Model.read(self.buff)

        self.assertEqual(m0.bounding_box_min, m1.bounding_box_min, 'Bounding box minimums should be equal')
        self.assertEqual(m0.bounding_box_max, m1.bounding_box_max, 'Bounding box maximums should be equal')
        self.assertEqual(m0.origin, m1.origin, 'Origins should be equal')
        self.assertEqual(m0.head_node, m1.head_node, 'Head nodes should be equal')
        self.assertEqual(m0.visleafs, m1.visleafs, 'Visleafs should be equal')
        self.assertEqual(m0.first_face, m1.first_face, 'First faces should be equal')
        self.assertEqual(m0.number_of_faces, m1.number_of_faces, 'Number of faces should be equal')

    def test_bsp(self):
        b0 = bsp29.Bsp.open('./test_data/test.bsp')
        b0.close()

        b0.save(self.buff)
        self.buff.seek(0)

        b1 = bsp29.Bsp.open(self.buff)

        self.assertEqual(b0.version, b1.version, 'Versions should be equal')
        self.assertEqual(b0.entities, b1.entities, 'Entities should be equal')

        for i, pair in enumerate(zip(b0.planes, b1.planes)):
            p0, p1 = pair
            self.assertAlmostEqual(p0.normal, p1.normal, significant_digits,'Normal vectors should be equal')
            self.assertAlmostEqual(p0.distance, p1.distance, significant_digits, 'Distances should be equal')
            self.assertEqual(p0.type, p1.type, 'Types should equal')

        for i, pair in enumerate(zip(b0.miptextures, b1.miptextures)):
            m0, m1 = pair
            self.assertEqual(m0.name, m1.name, 'Names should be equal')
            self.assertEqual(m0.width, m1.width, 'Widths should be equal')
            self.assertEqual(m0.height, m1.height, 'Heights should be equal')
            self.assertEqual(m0.offsets, m1.offsets, 'Offsets should be equal')
            self.assertEqual(m0.pixels, m1.pixels, 'Pixel data should be equal')

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
            self.assertEqual(t0.miptexture_number, t1.miptexture_number, 'Miptexture numbers should be equal')
            self.assertEqual(t0.flags, t1.flags, 'Flags should be equal')

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

        for i, pair in enumerate(zip(b0.clip_nodes, b1.clip_nodes)):
            c0, c1 = pair
            self.assertEqual(c0.plane_number, c1.plane_number, 'Plane numbers should equal')
            self.assertEqual(c0.children, c1.children, 'Children should equal')

        for i, pair in enumerate(zip(b0.leafs, b1.leafs)):
            l0, l1 = pair
            self.assertEqual(l0.contents, l1.contents, 'contents should be equal')
            self.assertEqual(l0.visibilitiy_offset, l1.visibilitiy_offset, 'visibilitiy_offset should be equal')
            self.assertEqual(l0.bounding_box_min, l1.bounding_box_min, 'bounding_box_min should be equal')
            self.assertEqual(l0.bounding_box_max, l1.bounding_box_max, 'bounding_box_max should be equal')
            self.assertEqual(l0.first_mark_surface, l1.first_mark_surface, 'first_mark_surface should be equal')
            self.assertEqual(l0.number_of_marked_surfaces, l1.number_of_marked_surfaces, 'number_of_marked_surfaces should be equal')
            self.assertEqual(l0.ambient_level, l1.ambient_level, 'ambient_level should be equal')

        self.assertEqual(b0.mark_surfaces, b1.mark_surfaces, 'Mark_surfaces should be equal')

        for i, pair in enumerate(zip(b0.edges, b1.edges)):
            e0, e1 = pair
            self.assertEqual(e0.vertexes, e1.vertexes, 'Vertexes should equal')

        self.assertEqual(b0.surf_edges, b1.surf_edges, 'Surf edges should be equal')

        for i, pair in enumerate(zip(b0.models, b1.models)):
            m0, m1 = pair
            self.assertEqual(m0.bounding_box_min, m1.bounding_box_min, 'Bounding box minimums should be equal')
            self.assertEqual(m0.bounding_box_max, m1.bounding_box_max, 'Bounding box maximums should be equal')
            self.assertEqual(m0.origin, m1.origin, 'Origins should be equal')
            self.assertEqual(m0.head_node, m1.head_node, 'Head nodes should be equal')
            self.assertEqual(m0.visleafs, m1.visleafs, 'Visleafs should be equal')
            self.assertEqual(m0.first_face, m1.first_face, 'First faces should be equal')
            self.assertEqual(m0.number_of_faces, m1.number_of_faces, 'Number of faces should be equal')

        self.assertFalse(b1.fp.closed, 'File should be open')
        fp = b1.fp
        b1.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(b1.fp, 'File pointer should be cleaned up')

    def test_context_manager(self):
        with bsp29.Bsp.open('./test_data/test.bsp', 'a') as bsp_file:
            self.assertFalse(bsp_file.fp.closed, 'File should be open')
            self.assertEqual(bsp_file.mode, 'a', 'File mode should be \'a\'')
            fp = bsp_file.fp
            bsp_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(bsp_file.fp, 'File pointer should be cleaned up')


class TestBsp29aReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertTrue(bsp29a.is_bspfile('./test_data/test.bsp2'))
        self.assertFalse(bsp29a.is_bspfile('./test_data/test.lmp'))
        self.assertFalse(bsp29a.is_bspfile('./test_data/test.map'))
        self.assertFalse(bsp29a.is_bspfile('./test_data/test.mdl'))
        self.assertFalse(bsp29a.is_bspfile('./test_data/test.pak'))
        self.assertFalse(bsp29a.is_bspfile('./test_data/test.spr'))
        self.assertFalse(bsp29a.is_bspfile('./test_data/test.wad'))

    def test_plane(self):
        normal = 0.0, 0.0, 1.0
        distance = 1.0
        type = 0

        p0 = bsp29a.Plane(*normal,
                       distance,
                       type)

        bsp29a.Plane.write(self.buff, p0)
        self.buff.seek(0)

        p1 = bsp29a.Plane.read(self.buff)

        self.assertAlmostEqual(p0.normal, p1.normal, significant_digits, 'Normal vectors should be equal')
        self.assertAlmostEqual(p0.distance, p1.distance, significant_digits, 'Distances should be equal')
        self.assertEqual(p0.type, p1.type, 'Types should equal')

    def test_miptexture(self):
        m0 = bsp29a.Miptexture()
        m0.name = 'metal1_1'
        m0.width = 32
        m0.height = 32
        m0.offsets = 40, 1064, 1320, 1384
        m0.pixels = tuple([i % 256 for i in range(32 * 32 * 85 // 64)])

        bsp29a.Miptexture.write(self.buff, m0)
        self.buff.seek(0)

        m1 = bsp29a.Miptexture.read(self.buff)

        self.assertEqual(m0.name, m1.name, 'Names should be equal')
        self.assertEqual(m0.width, m1.width, 'Widths should be equal')
        self.assertEqual(m0.height, m1.height, 'Heights should be equal')
        self.assertEqual(m0.offsets, m1.offsets, 'Offsets should be equal')
        self.assertEqual(m0.pixels, m1.pixels, 'Pixel data should be equal')

    def test_vertex(self):
        v0 = bsp29a.Vertex(1.0, -0.5, 1.25)

        bsp29a.Vertex.write(self.buff, v0)
        self.buff.seek(0)

        v1 = bsp29a.Vertex.read(self.buff)

        self.assertAlmostEqual(v0.x, v1.x, significant_digits, 'X coordinates should be equal')
        self.assertAlmostEqual(v0.y, v1.y, significant_digits, 'Y coordinates should be equal')
        self.assertAlmostEqual(v0.z, v1.z, significant_digits, 'Z coordinates should be equal')

    def test_node(self):
        plane_number = 0
        children = 1, 2
        bounding_box_min = -2147483647, -2147483647, -2147483647
        bounding_box_max = 2147483647, 2147483647, 2147483647
        first_face = 0
        number_of_faces = 4

        n0 = bsp29a.Node(plane_number,
                      *children,
                      *bounding_box_min,
                      *bounding_box_max,
                      first_face,
                      number_of_faces)

        bsp29a.Node.write(self.buff, n0)
        self.buff.seek(0)

        n1 = bsp29a.Node.read(self.buff)

        self.assertEqual(n0.plane_number, n1.plane_number, 'Plane numbers should be equal')
        self.assertEqual(n0.children, n1.children, 'Children should be equal')
        self.assertEqual(n0.bounding_box_min, n1.bounding_box_min, 'Bounding box minimums should be equal')
        self.assertEqual(n0.bounding_box_max, n1.bounding_box_max, 'Bounding box maximums should be equal')
        self.assertEqual(n0.first_face, n1.first_face, 'First faces should be equal')
        self.assertEqual(n0.number_of_faces, n1.number_of_faces, 'Number of faces should be equal')

    def test_textureinfo(self):
        s = 1.0, -1.0, 0
        s_offset = 1.25
        t = -5.0, 6.0, 7.75
        t_offset = 0.0
        miptexture_number = 0
        flags = 8

        t0 = bsp29a.TextureInfo(*s,
                             s_offset,
                             *t,
                             t_offset,
                             miptexture_number,
                             flags)

        bsp29a.TextureInfo.write(self.buff, t0)
        self.buff.seek(0)

        t1 = bsp29a.TextureInfo.read(self.buff)

        self.assertAlmostEqual(t0.s, t1.s, significant_digits, 's vectors should be equal')
        self.assertAlmostEqual(t0.s_offset, t1.s_offset, significant_digits, 's offsets should be equal')
        self.assertAlmostEqual(t0.t, t1.t, significant_digits, 't vectors should be equal')
        self.assertAlmostEqual(t0.t_offset, t1.t_offset, significant_digits, 't offsets should be equal')
        self.assertEqual(t0.miptexture_number, t1.miptexture_number, 'Miptexture numbers should be equal')
        self.assertEqual(t0.flags, t1.flags, 'Flags should be equal')

    def test_face(self):
        plane_number = 0
        side = 0
        first_edge = 0
        number_of_edges = 8
        texture_info = 0
        styles = 0, 1, 2, 3
        light_offset = 0

        f0 = bsp29a.Face(plane_number,
                      side,
                      first_edge,
                      number_of_edges,
                      texture_info,
                      *styles,
                      light_offset)

        bsp29a.Face.write(self.buff, f0)
        self.buff.seek(0)

        f1 = bsp29a.Face.read(self.buff)

        self.assertEqual(f0.plane_number, f1.plane_number, 'Plane numbers should be equal')
        self.assertEqual(f0.side, f1.side, 'Sides should be equal')
        self.assertEqual(f0.first_edge, f1.first_edge, 'First edges should be equal')
        self.assertEqual(f0.number_of_edges, f1.number_of_edges, 'Number of edges should be equal')
        self.assertEqual(f0.texture_info, f1.texture_info, 'Texture infos should be equal')
        self.assertEqual(f0.styles, f1.styles, 'Styles should be equal')
        self.assertEqual(f0.light_offset, f1.light_offset, 'Light offset should be equal')

    def test_clipnode(self):
        plane_number = 0
        children = 0, 1

        c0 = bsp29a.ClipNode(plane_number,
                          *children)

        bsp29a.ClipNode.write(self.buff, c0)
        self.buff.seek(0)

        c1 = bsp29a.ClipNode.read(self.buff)

        self.assertEqual(c0.plane_number, c1.plane_number, 'Plane numbers should equal')
        self.assertEqual(c0.children, c1.children, 'Children should equal')

    def test_leaf(self):
        contents = 0
        visibilitiy_offset = 0
        bounding_box_min = -2147483647, -2147483647, -2147483647
        bounding_box_max = 2147483647, 2147483647, 2147483647
        first_mark_surface = 0
        number_of_marked_surfaces = 4
        ambient_level = 0, 1, 2, 4

        l0 = bsp29a.Leaf(contents,
                      visibilitiy_offset,
                      *bounding_box_min,
                      *bounding_box_max,
                      first_mark_surface,
                      number_of_marked_surfaces,
                      *ambient_level)

        bsp29a.Leaf.write(self.buff, l0)
        self.buff.seek(0)

        l1 = bsp29a.Leaf.read(self.buff)

        self.assertEqual(l0.contents, l1.contents, 'contents should be equal')
        self.assertEqual(l0.visibilitiy_offset, l1.visibilitiy_offset, 'visibilitiy_offset should be equal')
        self.assertEqual(l0.bounding_box_min, l1.bounding_box_min, 'bounding_box_min should be equal')
        self.assertEqual(l0.bounding_box_max, l1.bounding_box_max, 'bounding_box_max should be equal')
        self.assertEqual(l0.first_mark_surface, l1.first_mark_surface, 'first_mark_surface should be equal')
        self.assertEqual(l0.number_of_marked_surfaces, l1.number_of_marked_surfaces, 'number_of_marked_surfaces should be equal')
        self.assertEqual(l0.ambient_level, l1.ambient_level, 'ambient_level should be equal')

    def test_edge(self):
        vertexes = 0, 1
        e0 = bsp29a.Edge(*vertexes)

        bsp29a.Edge.write(self.buff, e0)
        self.buff.seek(0)

        e1 = bsp29a.Edge.read(self.buff)

        self.assertEqual(e0.vertexes, e1.vertexes, 'Vertexes should equal')

    def test_model(self):
        bounding_box_min = -32767, -32767, -32767
        bounding_box_max = 32767, 32767, 32767
        origin = 0, 0, 0
        head_node = 0, 1, 2, 0
        visleafs = 0
        first_face = 0
        number_of_faces = 8

        m0 = bsp29a.Model(*bounding_box_min,
                       *bounding_box_max,
                       *origin,
                       *head_node,
                       visleafs,
                       first_face,
                       number_of_faces)

        bsp29a.Model.write(self.buff, m0)
        self.buff.seek(0)

        m1 = bsp29a.Model.read(self.buff)

        self.assertEqual(m0.bounding_box_min, m1.bounding_box_min, 'Bounding box minimums should be equal')
        self.assertEqual(m0.bounding_box_max, m1.bounding_box_max, 'Bounding box maximums should be equal')
        self.assertEqual(m0.origin, m1.origin, 'Origins should be equal')
        self.assertEqual(m0.head_node, m1.head_node, 'Head nodes should be equal')
        self.assertEqual(m0.visleafs, m1.visleafs, 'Visleafs should be equal')
        self.assertEqual(m0.first_face, m1.first_face, 'First faces should be equal')
        self.assertEqual(m0.number_of_faces, m1.number_of_faces, 'Number of faces should be equal')

    def test_bsp(self):
        b0 = bsp29a.Bsp.open('./test_data/test.bsp2')
        b0.close()

        b0.save(self.buff)
        self.buff.seek(0)

        b1 = bsp29a.Bsp.open(self.buff)

        self.assertEqual(b0.version, b1.version, 'Versions should be equal')
        self.assertEqual(b0.entities, b1.entities, 'Entities should be equal')

        for i, pair in enumerate(zip(b0.planes, b1.planes)):
            p0, p1 = pair
            self.assertAlmostEqual(p0.normal, p1.normal, significant_digits,'Normal vectors should be equal')
            self.assertAlmostEqual(p0.distance, p1.distance, significant_digits, 'Distances should be equal')
            self.assertEqual(p0.type, p1.type, 'Types should equal')

        for i, pair in enumerate(zip(b0.miptextures, b1.miptextures)):
            m0, m1 = pair
            self.assertEqual(m0.name, m1.name, 'Names should be equal')
            self.assertEqual(m0.width, m1.width, 'Widths should be equal')
            self.assertEqual(m0.height, m1.height, 'Heights should be equal')
            self.assertEqual(m0.offsets, m1.offsets, 'Offsets should be equal')
            self.assertEqual(m0.pixels, m1.pixels, 'Pixel data should be equal')

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
            self.assertEqual(t0.miptexture_number, t1.miptexture_number, 'Miptexture numbers should be equal')
            self.assertEqual(t0.flags, t1.flags, 'Flags should be equal')

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

        for i, pair in enumerate(zip(b0.clip_nodes, b1.clip_nodes)):
            c0, c1 = pair
            self.assertEqual(c0.plane_number, c1.plane_number, 'Plane numbers should equal')
            self.assertEqual(c0.children, c1.children, 'Children should equal')

        for i, pair in enumerate(zip(b0.leafs, b1.leafs)):
            l0, l1 = pair
            self.assertEqual(l0.contents, l1.contents, 'contents should be equal')
            self.assertEqual(l0.visibilitiy_offset, l1.visibilitiy_offset, 'visibilitiy_offset should be equal')
            self.assertEqual(l0.bounding_box_min, l1.bounding_box_min, 'bounding_box_min should be equal')
            self.assertEqual(l0.bounding_box_max, l1.bounding_box_max, 'bounding_box_max should be equal')
            self.assertEqual(l0.first_mark_surface, l1.first_mark_surface, 'first_mark_surface should be equal')
            self.assertEqual(l0.number_of_marked_surfaces, l1.number_of_marked_surfaces, 'number_of_marked_surfaces should be equal')
            self.assertEqual(l0.ambient_level, l1.ambient_level, 'ambient_level should be equal')

        self.assertEqual(b0.mark_surfaces, b1.mark_surfaces, 'Mark_surfaces should be equal')

        for i, pair in enumerate(zip(b0.edges, b1.edges)):
            e0, e1 = pair
            self.assertEqual(e0.vertexes, e1.vertexes, 'Vertexes should equal')

        self.assertEqual(b0.surf_edges, b1.surf_edges, 'Surf edges should be equal')

        for i, pair in enumerate(zip(b0.models, b1.models)):
            m0, m1 = pair
            self.assertEqual(m0.bounding_box_min, m1.bounding_box_min, 'Bounding box minimums should be equal')
            self.assertEqual(m0.bounding_box_max, m1.bounding_box_max, 'Bounding box maximums should be equal')
            self.assertEqual(m0.origin, m1.origin, 'Origins should be equal')
            self.assertEqual(m0.head_node, m1.head_node, 'Head nodes should be equal')
            self.assertEqual(m0.visleafs, m1.visleafs, 'Visleafs should be equal')
            self.assertEqual(m0.first_face, m1.first_face, 'First faces should be equal')
            self.assertEqual(m0.number_of_faces, m1.number_of_faces, 'Number of faces should be equal')

        self.assertFalse(b1.fp.closed, 'File should be open')
        fp = b1.fp
        b1.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(b1.fp, 'File pointer should be cleaned up')

    def test_context_manager(self):
        with bsp29a.Bsp.open('./test_data/test.bsp2', 'a') as bsp_file:
            self.assertFalse(bsp_file.fp.closed, 'File should be open')
            self.assertEqual(bsp_file.mode, 'a', 'File mode should be \'a\'')
            fp = bsp_file.fp
            bsp_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(bsp_file.fp, 'File pointer should be cleaned up')


if __name__ == '__main__':
    unittest.main()
