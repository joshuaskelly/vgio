import unittest

from tests.basecase import TestCase
from quake2 import md2

significant_digits = 5


class TestMd2ReadWrite(TestCase):
    @unittest.skip("Missing test artifacts")
    def test_check_file_type(self):
        self.assertTrue(md2.is_md2file('./test_data/test.md2'))

    def test_st_vertex(self):
        s = 0
        t = 16
        s0 = md2.StVertex(s, t)

        md2.StVertex.write(self.buff, s0)
        self.buff.seek(0)

        s1 = md2.StVertex.read(self.buff)

        self.assertEqual(s0.s, s1.s, 'S coordinate should be equal')
        self.assertEqual(s0.t, s1.t, 'T coordinate should be equal')

    def test_tri_vertex(self):
        x = 0
        y = 16
        z = 255
        light_normal_index = 0
        t0 = md2.TriVertex(x, y, z,
                           light_normal_index)

        md2.TriVertex.write(self.buff, t0)
        self.buff.seek(0)

        t1 = md2.TriVertex.read(self.buff)

        self.assertEqual(t0.x, t1.x, 'X coordinates should be equal')
        self.assertEqual(t0.y, t1.y, 'Y coordinates should be equal')
        self.assertEqual(t0.z, t1.z, 'Z coordinates should be equal')
        self.assertEqual(t0.light_normal_index, t1.light_normal_index, 'Light normal index should be equal')

    def test_triangle(self):
        vertexes = 0, 1, 2
        st_vertexes = 0, 1, 2
        t0 = md2.Triangle(*vertexes,
                          *st_vertexes)

        md2.Triangle.write(self.buff, t0)
        self.buff.seek(0)

        t1 = md2.Triangle.read(self.buff)

        self.assertEqual(t0.vertexes, t1.vertexes, 'Vertexes should be equal')
        self.assertEqual(t0.st_vertexes, t1.st_vertexes, 'St Coords should be equal')

    def test_frame(self):
        tv0 = md2.TriVertex(0, 16, 255, 0)
        tv1 = md2.TriVertex(0, 255, 128, 1)

        scale = 1.0, 1.0, 1.0
        offset = 0.0, 128.0, -64.0
        name = 'frame0'

        f0 = md2.Frame(*scale,
                       *offset,
                       name)

        f0.vertexes = tv0, tv1

        md2.Frame.write(self.buff, f0)
        self.buff.seek(0)

        f1 = md2.Frame.read(self.buff, 2)

        self.assertEqual(f0.scale, f1.scale, 'Scales should be equal')
        self.assertEqual(f0.translate, f1.translate, 'Offsets should be equal')
        self.assertEqual(f0.name, f1.name, 'Names should be equal')

    def test_header(self):
        identity = b'IDP2'
        version = 8
        skin_width = 128
        skin_height = 128
        frame_size = 20
        number_of_skins = 2 << 1
        number_of_vertexes = 2 << 2
        number_of_st_vertexes = 2 << 3
        number_of_triangles = 2 << 4
        number_of_gl_commands = 2 << 5
        number_of_frames = 2 << 6
        skin_offset = 2 << 7
        st_coord_offset = 2 << 8
        triangle_offset = 2 << 9
        frame_offset = 2 << 10
        gl_command_offset = 2 << 11
        end_offset = 2 << 12

        h0 = md2.Header(identity,
                        version,
                        skin_width,
                        skin_height,
                        frame_size,
                        number_of_skins,
                        number_of_vertexes,
                        number_of_st_vertexes,
                        number_of_triangles,
                        number_of_gl_commands,
                        number_of_frames,
                        skin_offset,
                        st_coord_offset,
                        triangle_offset,
                        frame_offset,
                        gl_command_offset,
                        end_offset)

        md2.Header.write(self.buff, h0)
        self.buff.seek(0)

        h1 = md2.Header.read(self.buff)

        self.assertEqual(h0.identity, h1.identity, 'Identities should be equal')
        self.assertEqual(h0.version, h1.version, 'Versions should be equal')
        self.assertEqual(h0.skin_width, h1.skin_width, 'Skin Widths should be equal')
        self.assertEqual(h0.skin_height, h1.skin_height, 'Skin Heights should be equal')
        self.assertEqual(h0.frame_size, h1.frame_size, 'Frame Sizes should be equal')
        self.assertEqual(h0.number_of_skins, h1.number_of_skins, 'Number of skins should be equal')
        self.assertEqual(h0.number_of_vertexes, h1.number_of_vertexes, 'Number of vertexes should be equal')
        self.assertEqual(h0.number_of_st_vertexes, h1.number_of_st_vertexes, 'Number of st_vertexes should be equal')
        self.assertEqual(h0.number_of_triangles, h1.number_of_triangles, 'Number of triangles should be equal')
        self.assertEqual(h0.number_of_gl_commands, h1.number_of_gl_commands, 'Number of gl commands should be equal')
        self.assertEqual(h0.number_of_frames, h1.number_of_frames, 'Number of frames should be equal')
        self.assertEqual(h0.skin_offset, h1.skin_offset, 'Skin Offsets should be equal')
        self.assertEqual(h0.st_vertex_offset, h1.st_vertex_offset, 'St Coord Offsets should be equal')
        self.assertEqual(h0.triangle_offset, h1.triangle_offset, 'Triangle Offsets should be equal')
        self.assertEqual(h0.frame_offset, h1.frame_offset, 'Frame Offsets should be equal')
        self.assertEqual(h0.gl_command_offset, h1.gl_command_offset, 'Gl Command Offsets should be equal')
        self.assertEqual(h0.end_offset, h1.end_offset, 'End Offsets should be equal')


if __name__ == '__main__':
    unittest.main()