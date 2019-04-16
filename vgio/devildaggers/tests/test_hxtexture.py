import io
import unittest

from vgio.devildaggers import hxtexture


class TestHxtextureReadWrite(unittest.TestCase):
    def setUp(self):
        self.buff = io.BytesIO()

    def test_header(self):
        texture_format = 0x4011
        width = 64
        height = 64
        mip_level_count = 8

        expected = hxtexture.Header(
            texture_format,
            width,
            height,
            mip_level_count
        )

        hxtexture.Header.write(self.buff, expected)
        self.buff.seek(0)

        actual = hxtexture.Header.read(self.buff)

        self.assertEqual(expected.texture_format, actual.texture_format, 'Format values should be equal')
        self.assertEqual(expected.width, actual.width, 'Width values should be equal')
        self.assertEqual(expected.height, actual.height, 'Height values should be equal')
        self.assertEqual(expected.mip_level_count, actual.mip_level_count, 'Mip_level_count values should be equal')

        self.assertEqual(self.buff.read(), b'', 'Buffer should be fully consumed')

    def test_hxtexture(self):
        h0 = hxtexture.HxTexture()
        h0.width = 4
        h0.height = 4
        h0.mip_level_count = 1
        h0.pixels = b'\x7f\x7f\x7f\xff' * 16

        h0.save(self.buff)
        self.buff.seek(0)

        h1 = hxtexture.HxTexture.open(self.buff)

        self.assertEqual(h0.texture_format, h1.texture_format, 'Texture formats should be equal')
        self.assertEqual(h0.width, h1.width, 'Widths should be equal')
        self.assertEqual(h0.height, h1.height, 'Heights should be equal')
        self.assertEqual(h0.mip_level_count, h1.mip_level_count, 'Mip level counts should be equal')
        self.assertEqual(h0.pixels, h1.pixels, 'Pixels should be equal')

        self.assertEqual(self.buff.read(), b'', 'Buffer should be fully consumed')


if __name__ == '__main__':
    unittest.main()
