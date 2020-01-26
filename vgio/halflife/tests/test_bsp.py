import unittest

from vgio.halflife.tests.basecase import TestCase
from vgio.halflife import bsp

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
        version = 30
        lumps = [bsp.Lump(i, 2 << i) for i in range(15)]

        h0 = bsp.Header(version, lumps)

        bsp.Header.write(self.buff, h0)
        self.buff.seek(0)

        h1 = bsp.Header.read(self.buff)

        self.assertEqual(h0.version, h0.version, 'Versions should be equal')

        for i in range(15):
            l0 = h0._lumps[i]
            l1 = h1._lumps[i]

            self.assertEqual(l0.offset, l1.offset, 'Offsets should be equal')
            self.assertEqual(l0.length, l1.length, 'Lengths should be equal')

    def test_entities_lump_helper(self):
        e0 = """
{
"classname" "info_player_start"
"origin" "256 384 160"
"angles" "0 0 0"
}
"""
        bsp._Entities.write(self.buff, e0)
        self.buff.seek(0)

        e1 = bsp._Entities.read(self.buff)

        self.assertEqual(e0, e1, 'Entities should be equal')

    def test_plane(self):
        normal = 0.0, 0.0, 1.0
        distance = 1.0
        type = 0

        p0 = bsp.Plane(*normal, distance, type)

        bsp.Plane.write(self.buff, p0)
        self.buff.seek(0)

        p1 = bsp.Plane.read(self.buff)

        self.assertAlmostEqual(p0.normal, p1.normal, significant_digits, 'Normal vectors should be equal')
        self.assertAlmostEqual(p0.distance, p1.distance, significant_digits, 'Distances should be equal')
        self.assertEqual(p0.type, p1.type, 'Types should equal')

    def test_miptexture_external(self):
        name = '!waterblue'
        width = 64
        height = 64

        m0 = bsp.Miptexture(
            name,
            width,
            height
        )

        bsp.Miptexture.write(self.buff, m0)
        self.buff.seek(0)

        m1 = bsp.Miptexture.read(self.buff)

        self.assertEqual(m0.name, m1.name, 'Names should be equal')
        self.assertEqual(m0.width, m1.width, 'Widths should be equal')
        self.assertEqual(m0.height, m1.height, 'Heights should be equal')
        self.assertEqual(m0.offsets, m1.offsets, 'Offsets should be equal')
        self.assertEqual(m0.pixels, m1.pixels, 'Pixel data should be equal')

    def test_miptexture_internal(self):
        name = '!test'
        width = 32
        height = 32
        offsets = 40, 1064, 1320, 1384
        pixels = bytes([i % 256 for i in range(32 * 32 * 85 // 64)])

        m0 = bsp.Miptexture(
            name,
            width,
            height,
            offsets,
            pixels
        )

        bsp.Miptexture.write(self.buff, m0)
        self.buff.seek(0)

        m1 = bsp.Miptexture.read(self.buff)

        self.assertEqual(m0.name, m1.name, 'Names should be equal')
        self.assertEqual(m0.width, m1.width, 'Widths should be equal')
        self.assertEqual(m0.height, m1.height, 'Heights should be equal')
        self.assertEqual(m0.offsets, m1.offsets, 'Offsets should be equal')
        self.assertEqual(m0.pixels, m1.pixels, 'Pixel data should be equal')

    def test_textures_lump_helper(self):
        m0 = bsp.Miptexture(
            'test0',
            16,
            16
        )

        n0 = bsp.Miptexture(
            'origin',
            16,
            16,
            (40, 296, 360, 376),
            bytes([i % 256 for i in range(16 * 16 * 85 // 64)])
        )

        bsp._Textures.write(self.buff, (m0, n0))
        self.buff.seek(0)

        m1, n1 = bsp._Textures.read(self.buff)

        self.assertEqual(m0.name, m1.name, 'Names should be equal')
        self.assertEqual(m0.width, m1.width, 'Widths should be equal')
        self.assertEqual(m0.height, m1.height, 'Heights should be equal')
        self.assertEqual(m0.offsets, m1.offsets, 'Offsets should be equal')
        self.assertEqual(m0.pixels, m1.pixels, 'Pixel data should be equal')

        self.assertEqual(n0.name, n1.name, 'Names should be equal')
        self.assertEqual(n0.width, n1.width, 'Widths should be equal')
        self.assertEqual(n0.height, n1.height, 'Heights should be equal')
        self.assertEqual(n0.offsets, n1.offsets, 'Offsets should be equal')
        self.assertEqual(n0.pixels, n1.pixels, 'Pixel data should be equal')

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

        n0 = bsp.Node(
            plane_number,
            *children,
            *bounding_box_min,
            *bounding_box_max,
            first_face,
            number_of_faces
        )

        bsp.Node.write(self.buff, n0)
        self.buff.seek(0)

        n1 = bsp.Node.read(self.buff)

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

        t0 = bsp.TextureInfo(
            *s,
            s_offset,
            *t,
            t_offset,
            miptexture_number,
            flags
        )

        bsp.TextureInfo.write(self.buff, t0)
        self.buff.seek(0)

        t1 = bsp.TextureInfo.read(self.buff)

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

        f0 = bsp.Face(
            plane_number,
            side,
            first_edge,
            number_of_edges,
            texture_info,
            *styles,
            light_offset
        )

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

    def test_clipnode(self):
        plane_number = 0
        children = 0, 1

        c0 = bsp.ClipNode(
            plane_number,
            *children
        )

        bsp.ClipNode.write(self.buff, c0)
        self.buff.seek(0)

        c1 = bsp.ClipNode.read(self.buff)

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

        l0 = bsp.Leaf(
            contents,
            visibilitiy_offset,
            *bounding_box_min,
            *bounding_box_max,
            first_mark_surface,
            number_of_marked_surfaces,
            *ambient_level
        )

        bsp.Leaf.write(self.buff, l0)
        self.buff.seek(0)

        l1 = bsp.Leaf.read(self.buff)

        self.assertEqual(l0.contents, l1.contents, 'contents should be equal')
        self.assertEqual(l0.visibilitiy_offset, l1.visibilitiy_offset, 'visibilitiy_offset should be equal')
        self.assertEqual(l0.bounding_box_min, l1.bounding_box_min, 'bounding_box_min should be equal')
        self.assertEqual(l0.bounding_box_max, l1.bounding_box_max, 'bounding_box_max should be equal')
        self.assertEqual(l0.first_mark_surface, l1.first_mark_surface, 'first_mark_surface should be equal')
        self.assertEqual(l0.number_of_marked_surfaces, l1.number_of_marked_surfaces, 'number_of_marked_surfaces should be equal')
        self.assertEqual(l0.ambient_level, l1.ambient_level, 'ambient_level should be equal')

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
        head_node = 0, 1, 2, 0
        visleafs = 0
        first_face = 0
        number_of_faces = 8

        m0 = bsp.Model(
            *bounding_box_min,
            *bounding_box_max,
            *origin,
            *head_node,
            visleafs,
            first_face,
            number_of_faces
        )

        bsp.Model.write(self.buff, m0)
        self.buff.seek(0)

        m1 = bsp.Model.read(self.buff)

        self.assertEqual(m0.bounding_box_min, m1.bounding_box_min, 'Bounding box minimums should be equal')
        self.assertEqual(m0.bounding_box_max, m1.bounding_box_max, 'Bounding box maximums should be equal')
        self.assertEqual(m0.origin, m1.origin, 'Origins should be equal')
        self.assertEqual(m0.head_node, m1.head_node, 'Head nodes should be equal')
        self.assertEqual(m0.visleafs, m1.visleafs, 'Visleafs should be equal')
        self.assertEqual(m0.first_face, m1.first_face, 'First faces should be equal')
        self.assertEqual(m0.number_of_faces, m1.number_of_faces, 'Number of faces should be equal')

    def test_bsp(self):
        b0 = bsp.Bsp.open('./test_data/test.bsp')
        b0.close()

        b0.save(self.buff)
        self.buff.seek(0)

        b1 = bsp.Bsp.open(self.buff)

        self.assertEqual(b0.version, b1.version, 'Versions should be equal')
        self.assertEqual(b0.entities, b1.entities, 'Entities should be equal')

    def test_context_manager(self):
        with bsp.Bsp.open('./test_data/test.bsp', 'a') as bsp_file:
            self.assertFalse(bsp_file.fp.closed, 'File should be open')
            self.assertEqual(bsp_file.mode, 'a', 'File mode should be \'a\'')
            fp = bsp_file.fp
            bsp_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(bsp_file.fp, 'File pointer should be cleaned up')


if __name__ == '__main__':
    unittest.main()
