import io
import unittest

from vgio.duke3d.tests.basecase import TestCase
from vgio.duke3d import art


class TestArtReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertFalse(art.is_artfile('./test_data/test.grp'))
        self.assertTrue(art.is_artfile('./test_data/test.art'))

    def test_read(self):
        art_file = art.ArtFile('./test_data/test.art', 'r')
        self.assertFalse(art_file.fp.closed, 'File should be open')

        info = art_file.getinfo(0)
        self.assertIsNotNone(info, 'FileInfo should not be None')
        self.assertEqual(info.tile_index, 0)
        self.assertEqual(info.file_size, 0, 'FileInfo size of test file should be 0')
        self.assertEqual(info.file_offset, 24, 'FileInfo offset of test file should be 12')

        file = art_file.open(0)
        self.assertIsNotNone(file, 'File should not be None')
        file.close()

        fp = art_file.fp
        art_file.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(art_file.fp, 'File pointer should be cleaned up')

    def test_write_bytes(self):
        w0 = art.ArtFile(self.buff, 'w')
        w0.writebytes((2, 2), b'\x01\x02\x03\x04')
        w0.writebytes(art.ArtInfo(0, (1, 1)), b'\x05')

        info = art.ArtInfo(0)
        info.tile_dimensions = 2, 1
        w0.writebytes(info, io.BytesIO(b'\x06\x07'))

        w0.close()

        self.buff.seek(0)

        w1 = art.ArtFile(self.buff, 'r')

        self.assertTrue(0 in w1.namelist(), 'Tile 0 should be in Art file')
        self.assertTrue(1 in w1.namelist(), 'Tile 1 should be in Art file')
        self.assertTrue(2 in w1.namelist(), 'Tile 2 should be in Art file')
        self.assertEqual(w1.read(0), b'\x01\x02\x03\x04', 'Tile 0 content should not change')
        self.assertEqual(w1.read(1), b'\x05', 'Tile 1 content should not change')
        self.assertEqual(w1.read(2), b'\x06\x07', 'Tile 2 content should not change')

        w1.close()
        self.buff.close()

    def test_append(self):
        f = open('./test_data/test.art', 'rb')
        buff = io.BytesIO(f.read(-1))
        f.close()

        art_file = art.ArtFile(buff, 'a')
        art_file.writebytes((2, 2), b'\x00\x00\x00\x00')
        art_file.close()

        buff.seek(0)

        art_file = art.ArtFile(buff, 'r')
        self.assertTrue(1 in art_file.namelist(), 'Appended file should be in Art file')

        fp = art_file.fp
        art_file.close()

        self.assertFalse(buff.closed, 'Art file should not close passed file-like object')

        buff.close()

    def test_context_manager(self):
        with art.ArtFile('./test_data/test.art', 'r') as art_file:
            self.assertFalse(art_file.fp.closed, 'File should be open')
            self.assertEqual(art_file.mode, 'r', 'File mode should be \'r\'')
            fp = art_file.fp
            art_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(art_file.fp, 'File pointer should be cleaned up')

    def test_empty_art_file(self):
        with art.ArtFile(self.buff, 'w'):
            pass

        self.buff.seek(0)

        with art.ArtFile(self.buff, 'r') as art_file:
            self.assertEqual(len(art_file.namelist()), 0, 'Art file should have not entries')
            self.assertEqual(art_file.start_of_data, 16, 'Data should start immediately after header')

    def test_zero_byte_file(self):
        with art.ArtFile(self.buff, 'w') as art_file:
            art_file.writebytes((0, 0), b'')

        self.buff.seek(0)

        with art.ArtFile(self.buff) as art_file:
            info = art_file.getinfo(0)
            self.assertEqual(info.file_offset, 24, 'File Info offset of test file should be 24')
            self.assertEqual(info.file_size, 0, 'File Info size of test file should be 0')
            self.assertEqual(info.tile_dimensions, (0, 0), 'Tile dimensions should be 0x0 pixels')
            self.assertEqual(info.picanim, 0, 'Tile picanim attributes should be 0')

            data = art_file.read(0)
            self.assertEqual(len(data), 0, 'Length of bytes read should be zero.')


if __name__ == '__main__':
    unittest.main()

