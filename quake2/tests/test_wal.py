import unittest

from tests.basecase import TestCase
from quake2 import wal

significant_digits = 5


class TestWalReadWrite(TestCase):
    def test_wal(self):
        name = 'test0'
        width = 16
        height = 16
        offset_0 = (width * height >> 0) + 100
        offset_1 = (width * height >> 2) + offset_0
        offset_2 = (width * height >> 4) + offset_1
        offset_3 = (width * height >> 8) + offset_2
        animation_name = 'test1'
        flags = 0
        contents = 0
        value = 0
        pixels = b'\x00' * (width * height * 85 // 64)

        w0 = wal.Wal(name,
                     width,
                     height,
                     offset_0,
                     offset_1,
                     offset_2,
                     offset_3,
                     animation_name,
                     flags,
                     contents,
                     value,
                     pixels)

        wal.Wal.write(self.buff, w0)
        self.buff.seek(0)

        w1 = wal.Wal.read(self.buff)

        self.assertEqual(w0.name, w1.name, 'Name should be equal')
        self.assertEqual(w0.width, w1.width, 'Width should be equal')
        self.assertEqual(w0.height, w1.height, 'Height should be equal')
        self.assertEqual(w0.offsets, w1.offsets, 'Offset_0 should be equal')
        self.assertEqual(w0.animation_name, w1.animation_name, 'Animation_name should be equal')
        self.assertEqual(w0.flags, w1.flags, 'Flags should be equal')
        self.assertEqual(w0.contents, w1.contents, 'Contents should be equal')
        self.assertEqual(w0.value, w1.value, 'Value should be equal')
        self.assertEqual(w0.pixels, w1.pixels, 'Pixels should be equal')

if __name__ == '__main__':
    unittest.main()