import unittest

from vgio.halflife.tests.basecase import TestCase
from vgio.halflife import spr

significant_digits = 5


class TestBspReadWrite(TestCase):
    def test_header(self):
        h0 = spr.Header(
            b'IDSP',
            2,
            spr.SpriteType.VP_PARALLEL_UPRIGHT,
            spr.TextureFormatType.NORMAL,
            16.0,
            16,
            16,
            1,
            32.0,
            spr.SyncType.SYNCHRONIZED
        )

        spr.Header.write(self.buff, h0)
        self.buff.seek(0)

        h1 = spr.Header.read(self.buff)

        self.assertEqual(h0.identity, h1.identity, 'Identities should be equal')
        self.assertEqual(h0.version, h1.version, 'version should be equal')
        self.assertEqual(h0.type, h1.type, 'type_ should be equal')
        self.assertEqual(h0.texture_format, h1.texture_format, 'texture_format should be equal')
        self.assertEqual(h0.radius, h1.radius, 'radius should be equal')
        self.assertEqual(h0.width, h1.width, 'width should be equal')
        self.assertEqual(h0.height, h1.height, 'height should be equal')
        self.assertEqual(h0.frame_count, h1.frame_count, 'frame_count should be equal')
        self.assertEqual(h0.beam_length, h1.beam_length, 'beam_length should be equal')
        self.assertEqual(h0.sync_type, h1.sync_type, 'sync_type should be equal')

    def test_frame(self):
        f0 = spr.Frame(
            1,
            16,
            16,
            32,
            32,
            b'\x00' * 1024
        )

        spr.Frame.write(self.buff, f0)
        self.buff.seek(0)

        f1 = spr.Frame.read(self.buff)

        self.assertEqual(f0.type, f1.type, 'Types should be equal')
        self.assertEqual(f0.origin, f1.origin, 'Origins should be equal')
        self.assertEqual(f0.width, f1.width, 'Widths should be equal')
        self.assertEqual(f0.height, f1.height, 'Heights should be equal')
        self.assertEqual(f0.pixels, f1.pixels, 'Pixels should be equal')

    def test_spr(self):
        f0 = spr.Frame(
            1,
            16,
            16,
            32,
            32,
            b'\x00' * 1024
        )

        s0 = spr.Spr(
            b'IDSP',
            2,
            spr.SpriteType.VP_PARALLEL_UPRIGHT,
            spr.TextureFormatType.NORMAL,
            32.0,
            32,
            32,
            0,
            spr.SyncType.SYNCHRONIZED,
            [f0],
            b'\x00' * 768
        )

        s0.save(self.buff)
        self.buff.seek(0)

        s1 = spr.Spr.open(self.buff)

        self.assertEqual(s0.identity, s1.identity, 'Identities should be equal')
        self.assertEqual(s0.version, s1.version, 'version should be equal')
        self.assertEqual(s0.type, s1.type, 'type_ should be equal')
        self.assertEqual(s0.texture_format, s1.texture_format, 'texture_format should be equal')
        self.assertEqual(s0.radius, s1.radius, 'radius should be equal')
        self.assertEqual(s0.width, s1.width, 'width should be equal')
        self.assertEqual(s0.height, s1.height, 'height should be equal')
        self.assertEqual(s0.beam_length, s1.beam_length, 'beam_length should be equal')
        self.assertEqual(s0.sync_type, s1.sync_type, 'sync_type should be equal')

        f1 = s1.frames[0]

        self.assertEqual(f0.type, f1.type, 'Types should be equal')
        self.assertEqual(f0.origin, f1.origin, 'Origins should be equal')
        self.assertEqual(f0.width, f1.width, 'Widths should be equal')
        self.assertEqual(f0.height, f1.height, 'Heights should be equal')
        self.assertEqual(f0.pixels, f1.pixels, 'Pixels should be equal')


if __name__ == '__main__':
    unittest.main()
