import unittest

from vgio.quake2.tests.basecase import TestCase
from vgio.quake2 import wal


class TestWalReadWrite(TestCase):
    def test_header(self):
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

        h0 = wal.Header(
            name,
            width,
            height,
            offset_0,
            offset_1,
            offset_2,
            offset_3,
            animation_name,
            flags,
            contents,
            value
        )

        wal.Header.write(self.buff, h0)
        self.buff.seek(0)

        h1 = wal.Header.read(self.buff)

        self.assertEqual(h0.name, h1.name, 'Name should be equal')
        self.assertEqual(h0.width, h1.width, 'Width should be equal')
        self.assertEqual(h0.height, h1.height, 'Height should be equal')
        self.assertEqual(h0.offsets, h1.offsets, 'Offset_0 should be equal')
        self.assertEqual(h0.animation_name, h1.animation_name, 'Animation_name should be equal')
        self.assertEqual(h0.flags, h1.flags, 'Flags should be equal')
        self.assertEqual(h0.contents, h1.contents, 'Contents should be equal')
        self.assertEqual(h0.value, h1.value, 'Value should be equal')

    def test_wal(self):
        w0 = wal.Wal.open('./test_data/test.wal', 'r')
        w0.close()

        w0.save(self.buff)
        self.buff.seek(0)

        w1 = wal.Wal.open(self.buff)
        w1.close()

        self.assertEqual(w0.name, w1.name)
        self.assertEqual(w0.width, w1.width)
        self.assertEqual(w0.height, w1.height)
        self.assertEqual(w0.offsets, w1.offsets)
        self.assertEqual(w0.animation_name, w1.animation_name)
        self.assertEqual(w0.flags, w1.flags)
        self.assertEqual(w0.contents, w1.contents)
        self.assertEqual(w0.value, w1.value)
        self.assertEqual(w0.pixels, w1.pixels)


if __name__ == '__main__':
    unittest.main()
