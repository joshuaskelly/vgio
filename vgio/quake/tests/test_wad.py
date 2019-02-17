import io
import unittest

from vgio.quake.tests.basecase import TestCase
from vgio.quake import wad


class TestWadReadWrite(TestCase):
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
        wad_file.write('./test_data/test.bsp', 'e1m1.bsp')

        self.assertTrue('test.mdl' in wad_file.namelist(), 'Mdl file should be in Wad file')
        self.assertTrue('e1m1.bsp' in wad_file.namelist(), 'Bsp file should be in Wad file')

        fp = wad_file.fp
        wad_file.close()
        self.assertFalse(fp.closed, 'File should be open')
        self.assertIsNone(wad_file.fp, 'File pointer should be cleaned up')

        self.buff.close()

    def test_write_string(self):
        w0 = wad.WadFile(self.buff, 'w')
        w0.writestr('test.cfg', b'bind ALT +strafe')
        w0.writestr(wad.WadInfo('readme.txt'), 'test')

        info = wad.WadInfo('bytes')
        info.file_size = len(b'bytes')
        info.type = wad.TYPE_LUMP
        w0.writestr(info, io.BytesIO(b'bytes'))

        w0.close()

        self.buff.seek(0)

        w1 = wad.WadFile(self.buff, 'r')

        self.assertTrue('test.cfg' in w1.namelist(), 'Cfg file should be in Wad file')
        self.assertTrue('readme.txt' in w1.namelist(), 'Txt file should be in Wad file')
        self.assertTrue('bytes' in w1.namelist(), 'Bytes should be in Wad file')
        self.assertEqual(w1.read('test.cfg'), b'bind ALT +strafe', 'Cfg file content should not change')
        self.assertEqual(w1.read('readme.txt').decode('ascii'), 'test', 'Txt file content should not change')
        self.assertEqual(w1.read('bytes'), b'bytes', 'Bytes content should not change')

        w1.close()
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

    def test_empty_pak_file(self):
        with wad.WadFile(self.buff, 'w'):
            pass

        self.buff.seek(0)

        with wad.WadFile(self.buff, 'r') as wad_file:
            self.assertEqual(len(wad_file.namelist()), 0, 'Wad file should have not entries')
            self.assertEqual(wad_file.start_of_directory, 12, 'Directory should start immediately after header')
            
    def test_zero_byte_file(self):
        with wad.WadFile(self.buff, 'w') as wad_file:
            wad_file.writestr('zero.txt', b'')

        self.buff.seek(0)

        with wad.WadFile(self.buff) as wad_file:
            info = wad_file.getinfo('zero.txt')
            self.assertEqual(info.file_offset, 12, 'File Info offset of test file should be 12')
            self.assertEqual(info.file_size, 0, 'File Info size of test file should be 0')

            data = wad_file.read('zero.txt')
            self.assertEqual(len(data), 0, 'Length of bytes read should be zero.')

if __name__ == '__main__':
    unittest.main()
