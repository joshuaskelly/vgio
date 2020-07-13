import io
import unittest

from vgio.halflife.tests.basecase import TestCase
from vgio.halflife import wad


class TestWadReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertFalse(wad.is_wadfile('./test_data/test_quake.wad'))
        self.assertTrue(wad.is_wadfile('./test_data/test_hl.wad'))

    def test_read(self):
        wad_file = wad.WadFile('./test_data/test_hl.wad', 'r')
        self.assertFalse(wad_file.fp.closed, 'File should be open')

        info = wad_file.getinfo('test')
        self.assertIsNotNone(info, 'FileInfo should not be None')
        self.assertEqual(info.filename, 'test')
        self.assertEqual(info.file_size, 2172, 'FileInfo size of test file should be 2172')
        self.assertEqual(info.file_offset, 12, 'FileInfo offset of test file should be 12')
        self.assertEqual(info.type, wad.LumpType.LUMP, 'FileInfo type of test file should be LUMP')

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

        # TODO: make write test
        #wad_file.write('./test_data/test.mdl')
        #wad_file.write('./test_data/test.bsp', 'e1m1.bsp')

        #self.assertTrue('test.mdl' in wad_file.namelist(), 'Mdl file should be in Wad file')
        #self.assertTrue('e1m1.bsp' in wad_file.namelist(), 'Bsp file should be in Wad file')

        fp = wad_file.fp
        wad_file.close()
        self.assertFalse(fp.closed, 'File should be open')
        self.assertIsNone(wad_file.fp, 'File pointer should be cleaned up')

        self.buff.close()

    def test_append(self):
        f = open('./test_data/test_hl.wad', 'rb')
        buff = io.BytesIO(f.read(-1))
        f.close()

        wad_file = wad.WadFile(buff, 'a')
        # TODO: make write tests
        #wad_file.write('./test_data/test.bsp')
        wad_file.close()

        buff.seek(0)

        wad_file = wad.WadFile(buff, 'r')
        # self.assertTrue('test.bsp' in wad_file.namelist(), 'Appended file should be in Wad file')

        fp = wad_file.fp
        wad_file.close()

        self.assertFalse(buff.closed, 'Wad file should not close passed file-like object')

        buff.close()

    def test_context_manager(self):
        with wad.WadFile('./test_data/test_hl.wad', 'r') as wad_file:
            self.assertFalse(wad_file.fp.closed, 'File should be open')
            self.assertEqual(wad_file.mode, 'r', 'File mode should be \'r\'')
            fp = wad_file.fp
            wad_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(wad_file.fp, 'File pointer should be cleaned up')

    def test_empty_pak_file(self):
        with wad.WadFile(self.buff, 'w'):
            pass

        self.buff.seek(0)

        with wad.WadFile(self.buff, 'r') as wad_file:
            self.assertEqual(len(wad_file.namelist()), 0, 'Wad file should have not entries')
            self.assertEqual(wad_file.end_of_data, 12, 'Directory should start immediately after header')

if __name__ == '__main__':
    unittest.main()
