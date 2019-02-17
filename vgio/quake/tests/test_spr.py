import unittest

from vgio.quake.tests.basecase import TestCase
from vgio.quake import spr


class TestSprReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertFalse(spr.is_sprfile('./test_data/test.bsp'))
        self.assertFalse(spr.is_sprfile('./test_data/test.lmp'))
        self.assertFalse(spr.is_sprfile('./test_data/test.map'))
        self.assertFalse(spr.is_sprfile('./test_data/test.mdl'))
        self.assertFalse(spr.is_sprfile('./test_data/test.pak'))
        self.assertTrue(spr.is_sprfile('./test_data/test.spr'))
        self.assertFalse(spr.is_sprfile('./test_data/test.wad'))

    def test_sprite_frame(self):
        f0 = spr.SpriteFrame()
        f0.type = spr.SINGLE
        f0.origin = 0, 0
        f0.width = 4
        f0.height = 4
        f0.pixels = (0,) * f0.width * f0.height

        spr.SpriteFrame.write(self.buff, f0)
        self.buff.seek(0)

        f1 = spr.SpriteFrame.read(self.buff)

        self.assertEqual(f0.type, f1.type, 'Type should be equal')
        self.assertEqual(f0.origin, f1.origin, 'Origin should be equal')
        self.assertEqual(f0.width, f1.width, 'Width should be equal')
        self.assertEqual(f0.height, f1.height, 'Height should be equal')
        self.assertEqual(f0.pixels, f1.pixels, 'Pixels should be equal')

    def test_sprite_frame_group(self):
        f0 = spr.SpriteFrame()
        f0.type = spr.SINGLE
        f0.origin = 0, 0
        f0.width = 4
        f0.height = 4
        f0.pixels = (0,) * 4 * 4

        g0 = spr.SpriteGroup()
        g0.type = spr.GROUP
        g0.number_of_frames = 1
        g0.intervals = (1.0,)
        g0.frames.append(f0)

        spr.SpriteGroup.write(self.buff, g0)
        self.buff.seek(0)

        g1 = spr.SpriteGroup.read(self.buff)

        self.assertEqual(g0.type, g1.type, 'Types should be equal')
        self.assertEqual(g0.number_of_frames, g1.number_of_frames, 'Number of frames should be equal')
        self.assertEqual(g0.intervals, g1.intervals, 'Intervals should be equal')

        f1 = g1.frames[0]

        self.assertEqual(f0.type, f1.type, 'Type should be equal')
        self.assertEqual(f0.origin, f1.origin, 'Origin should be equal')
        self.assertEqual(f0.width, f1.width, 'Width should be equal')
        self.assertEqual(f0.height, f1.height, 'Height should be equal')
        self.assertEqual(f0.pixels, f1.pixels, 'Pixels should be equal')

    def test_spr(self):
        s0 = spr.Spr.open('./test_data/test.spr')
        s0.close()

        s0.save(self.buff)
        self.buff.seek(0)

        s1 = spr.Spr.open(self.buff)

        self.assertEqual(s0.identifier, s1.identifier, 'Identifier should be equal')
        self.assertEqual(s0.version, s1.version, 'Version numbers should be equal')
        self.assertEqual(s0.type, s1.type, 'Types should be equal')
        self.assertEqual(s0.bounding_radius, s1.bounding_radius, 'Bounding radii should be equal')
        self.assertEqual(s0.width, s1.width, 'Widths should be equal')
        self.assertEqual(s0.height, s1.height, 'Heights should be equal')
        self.assertEqual(s0.number_of_frames, s1.number_of_frames, 'Number of frames should be equal')
        self.assertEqual(s0.beam_length, s1.beam_length, 'Beam lengths should be equal')
        self.assertEqual(s0.sync_type, s1.sync_type, 'Sync types should be equal')

        self.assertFalse(s1.fp.closed, 'File should be open')
        fp = s1.fp
        s1.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(s1.fp, 'File pointer should be cleaned up')

    def test_context_manager(self):
        with spr.Spr.open('./test_data/test.spr', 'a') as spr_file:
            self.assertFalse(spr_file.fp.closed, 'File should be open')
            self.assertEqual(spr_file.mode, 'a', 'File mode should be \'a\'')
            fp = spr_file.fp
            spr_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(spr_file.fp, 'File pointer should be cleaned up')

if __name__ == '__main__':
    unittest.main()
