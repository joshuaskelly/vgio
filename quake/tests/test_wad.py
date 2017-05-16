import io
import unittest

from quake.tests import basecase
from quake import wad


class TestWadReadWrite(basecase.TestCase):
    def test_check_file_type(self):
        self.assertFalse(wad.is_wadfile('./test_data/test.bsp'))
        self.assertFalse(wad.is_wadfile('./test_data/test.lmp'))
        self.assertFalse(wad.is_wadfile('./test_data/test.map'))
        self.assertFalse(wad.is_wadfile('./test_data/test.mdl'))
        self.assertFalse(wad.is_wadfile('./test_data/test.pak'))
        self.assertFalse(wad.is_wadfile('./test_data/test.spr'))
        self.assertTrue(wad.is_wadfile('./test_data/test.wad'))

    def test_read(self):
        wad_file = wad.WadFile('./test_data/test.wad', 'r')
        self.assertFalse(wad_file.fp.closed, 'File should be open')

        info = wad_file.getinfo('test')
        self.assertIsNotNone(info, 'FileInfo should not be None')
        self.assertEqual(info.filename, 'test')
        self.assertEqual(info.file_size, 5480, 'FileInfo size of test file should be 5480')
        self.assertEqual(info.file_offset, 12, 'FileInfo offset of test file should be 12')
        self.assertEqual(info.type, wad.TYPE_MIPTEX, 'FileInfo type of test file should be MIPTEX')

        file = wad_file.open('test')
        self.assertIsNotNone(file, 'File should not be None')
        file.close()

        fp = wad_file.fp
        wad_file.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(wad_file.fp, 'File pointer should be cleaned up')

    def test_write(self):
        wad_file = wad.WadFile(self.buff, 'w')
        self.assertFalse(wad_file.fp.closed, 'File should be open')

        wad_file.write('./test_data/test.mdl')
        wad_file.write('./test_data/test.bsp')

        self.assertTrue('test.mdl' in wad_file.namelist(), 'Mdl file should be in Wad file')
        self.assertTrue('test.bsp' in wad_file.namelist(), 'Bsp file should be in Wad file')

        fp = wad_file.fp
        wad_file.close()
        self.assertFalse(fp.closed, 'File should be open')
        self.assertIsNone(wad_file.fp, 'File pointer should be cleaned up')

        self.buff.close()

    def test_append(self):
        f = open('./test_data/test.wad', 'rb')
        buff = io.BytesIO(f.read(-1))
        f.close()

        wad_file = wad.WadFile(buff, 'a')
        wad_file.write('./test_data/test.bsp')
        wad_file.close()

        buff.seek(0)

        wad_file = wad.WadFile(buff, 'r')
        self.assertTrue('test.bsp' in wad_file.namelist(), 'Appended file should be in Wad file')

        fp = wad_file.fp
        wad_file.close()

        self.assertFalse(buff.closed, 'Wad file should not close passed file-like object')

        buff.close()

    def test_context_manager(self):
        with wad.WadFile('./test_data/test.wad', 'r') as wad_file:
            self.assertFalse(wad_file.fp.closed, 'File should be open')
            self.assertEqual(wad_file.mode, 'r', 'File mode should be \'r\'')
            fp = wad_file.fp
            wad_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(wad_file.fp, 'File pointer should be cleaned up')

if __name__ == '__main__':
    unittest.main()
