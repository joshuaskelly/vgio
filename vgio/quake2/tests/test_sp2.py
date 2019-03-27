from vgio.quake2.tests.basecase import TestCase
from vgio.quake2 import sp2

significant_digits = 5

import io
import unittest


class TestTestReadWrite(TestCase):
    def setUp(self):
        self.buff = io.BytesIO()

    def test_header(self):
        identity = """ !"#"""
        version = -2147483648
        number_of_frames = 0

        expected = sp2.Header(
            identity,
            version,
            number_of_frames
        )

        sp2.Header.write(self.buff, expected)
        self.buff.seek(0)

        actual = sp2.Header.read(self.buff)

        self.assertEqual(expected.identity, actual.identity, 'Identity values should be equal')
        self.assertEqual(expected.version, actual.version, 'Version values should be equal')
        self.assertEqual(expected.number_of_frames, actual.number_of_frames, 'Number_of_frames values should be equal')

        self.assertEqual(self.buff.read(), b'', 'Buffer should be fully consumed')

    def test_sprite_frame(self):
        width = 2147483647
        height = -2147483648
        origin = 0, 2147483647
        name = """ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_"""

        expected = sp2.SpriteFrame(
            width,
            height,
            *origin,
            name
        )

        sp2.SpriteFrame.write(self.buff, expected)
        self.buff.seek(0)

        actual = sp2.SpriteFrame.read(self.buff)

        self.assertEqual(expected.width, actual.width, 'Width values should be equal')
        self.assertEqual(expected.height, actual.height, 'Height values should be equal')
        self.assertEqual(expected.origin, actual.origin, 'Origin values should be equal')
        self.assertEqual(expected.name, actual.name, 'Name values should be equal')

        self.assertEqual(self.buff.read(), b'', 'Buffer should be fully consumed')


if __name__ == '__main__':
    unittest.main()