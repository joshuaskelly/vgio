import io
import unittest

from quake import mdl

significant_digits = 5


class TestBspReadWrite(unittest.TestCase):
    def setUp(self):
        self.buff = io.BytesIO()

    def test_skin(self):
        s0 = mdl.Skin()
        s0.type = mdl.SINGLE
        s0.pixels = tuple(range(256))

        size = 16, 16

        mdl.Skin.write(self.buff, s0, size)
        self.buff.seek(0)

        s1 = mdl.Skin.read(self.buff, size)

        self.assertEqual(s0.type, s1.type, 'Type should be equal')
        self.assertEqual(s0.pixels, s1.pixels, 'Type should be equal')

    def test_skin_group(self):
        s0 = mdl.SkinGroup()
        s0.type = mdl.GROUP
        s0.number_of_skins = 2
        s0.intervals = (1.0, 0.5)
        s0.pixels = tuple(range(256)) * 2

        size = 16, 16

        mdl.SkinGroup.write(self.buff, s0, size)
        self.buff.seek(0)

        s1 = mdl.SkinGroup.read(self.buff, size)

        self.assertEqual(s0.type, s1.type, 'Type should be equal')
        self.assertEqual(s0.number_of_skins, s1.number_of_skins, 'Number_of_skins should be equal')
        self.assertEqual(s0.intervals, s1.intervals, 'Intervals should be equal')
        self.assertEqual(s0.pixels, s1.pixels, 'Pixels should be equal')

    def test_st_vertex(self):
        s0 = mdl.StVertex()
        s0.on_seam = 0
        s0.s = 0
        s0.t = 16

        mdl.StVertex.write(self.buff, s0)
        self.buff.seek(0)

        s1 = mdl.StVertex.read(self.buff)

        self.assertEqual(s0.on_seam, s1.on_seam, 'On seam should be equal')
        self.assertEqual(s0.s, s1.s, 'S coordinate should be equal')
        self.assertEqual(s0.t, s1.t, 'T coordinate should be equal')

    def test_triangle(self):
        t0 = mdl.Triangle()
        t0.faces_front = 0
        t0.vertices = 0, 1, 2

        mdl.Triangle.write(self.buff, t0)
        self.buff.seek(0)

        t1 = mdl.Triangle.read(self.buff)

        self.assertEqual(t0.faces_front, t1.faces_front, 'Faces front should be equal')
        self.assertEqual(t0.vertices, t1.vertices, 'Vertices should be equal')

    def test_tri_vertex(self):
        t0 = mdl.TriVertex()
        t0.x = 0
        t0.y = 16
        t0.z = 255
        t0.light_normal_index = 0

        mdl.TriVertex.write(self.buff, t0)
        self.buff.seek(0)

        t1 = mdl.TriVertex.read(self.buff)

        self.assertEqual(t0.x, t1.x, 'X coordinates should be equal')
        self.assertEqual(t0.y, t1.y, 'Y coordinates should be equal')
        self.assertEqual(t0.z, t1.z, 'Z coordinates should be equal')
        self.assertEqual(t0.light_normal_index, t1.light_normal_index, 'Light normal index should be equal')

    def test_frame(self):
        f0 = mdl.Frame()
        f0.type = mdl.SINGLE

        tv0 = mdl.TriVertex()
        tv0.x = 0
        tv0.y = 16
        tv0.z = 255
        tv0.light_normal_index = 1

        f0.bounding_box_min = tv0
        f0.bounding_box_max = tv0
        f0.name = 'metal_0'
        f0.vertices = [tv0, tv0]

        mdl.Frame.write(self.buff, f0, 2)
        self.buff.seek(0)

        f1 = mdl.Frame.read(self.buff, 2)

        self.assertEqual(f0.type, f1.type, 'Types should be equal')
        self.assertEqual(f0.name, f1.name, 'Types should be equal')

    def test_frame_group(self):
        f0 = mdl.FrameGroup()
        f0.type = mdl.GROUP
        f0.number_of_frames = 1

        tv0 = mdl.TriVertex()
        tv0.x = 0
        tv0.y = 16
        tv0.z = 255
        tv0.light_normal_index = 1

        f0.bounding_box_min = tv0
        f0.bounding_box_max = tv0
        f0.intervals = 1.0,

        fr = mdl.Frame()
        fr.type = mdl.SINGLE
        fr.bounding_box_min = tv0
        fr.bounding_box_max = tv0
        fr.name = 'metal_0'
        fr.vertices = tv0, tv0

        f0.frames = fr,

        mdl.FrameGroup.write(self.buff, f0, 2)
        self.buff.seek(0)

        f1 = mdl.FrameGroup.read(self.buff, 2)

        self.assertEqual(f0.type, f1.type, 'Type should be equal')
        self.assertEqual(f0.number_of_frames, f1.number_of_frames, 'Number of frames should be equal')
        self.assertEqual(f0.intervals, f1.intervals, 'Intervals should be equal')

    def test_mdl(self):
        m0 = mdl.Mdl.open('./test_data/test.mdl')
        m0.close()

        m0.save(self.buff)
        self.buff.seek(0)

        m1 = mdl.Mdl.open(self.buff)

        self.assertEqual(m0.identifier, m1.identifier, 'Identifier should be equal')
        self.assertEqual(m0.version, m1.version, 'Version should be equal')
        self.assertEqual(m0.scale, m1.scale, 'Scale should be equal')
        self.assertEqual(m0.origin, m1.origin, 'Origin should be equal')
        self.assertEqual(m0.bounding_radius, m1.bounding_radius, 'Bounding radius should be equal')
        self.assertEqual(m0.eye_position, m1.eye_position, 'Eye position should be equal')
        self.assertEqual(m0.number_of_skins, m1.number_of_skins, 'Number of skins should be equal')
        self.assertEqual(m0.skin_width, m1.skin_width, 'Skin width should be equal')
        self.assertEqual(m0.skin_height, m1.skin_height, 'Skin height should be equal')
        self.assertEqual(m0.number_of_vertices, m1.number_of_vertices, 'Number of vertices should be equal')
        self.assertEqual(m0.number_of_triangles, m1.number_of_triangles, 'Number of triangles should be equal')
        self.assertEqual(m0.number_of_frames, m1.number_of_frames, 'Number of frames should be equal')
        self.assertEqual(m0.synctype, m1.synctype, 'Sync type should be equal')
        self.assertEqual(m0.flags, m1.flags, 'Flags should be equal')
        self.assertEqual(m0.size, m1.size, 'Size should be equal')

    def test_context_manager(self):
        with mdl.Mdl.open('./test_data/test.mdl', 'a') as mdl_file:
            self.assertFalse(mdl_file.fp.closed, 'File should be open')
            self.assertEqual(mdl_file.mode, 'a', 'File mode should be \'a\'')
            fp = mdl_file.fp
            mdl_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(mdl_file.fp, 'File pointer should be cleaned up')
