import io
import unittest

from vgio.quake.tests.basecase import TestCase
from vgio.quake import pak


class TestPakReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertFalse(pak.is_pakfile('./test_data/test.bsp'))
        self.assertFalse(pak.is_pakfile('./test_data/test.lmp'))
        self.assertFalse(pak.is_pakfile('./test_data/test.map'))
        self.assertFalse(pak.is_pakfile('./test_data/test.mdl'))
        self.assertTrue(pak.is_pakfile('./test_data/test.pak'))
        self.assertFalse(pak.is_pakfile('./test_data/test.spr'))
        self.assertFalse(pak.is_pakfile('./test_data/test.wad'))

    def test_read(self):
        pak_file = pak.PakFile('./test_data/test.pak', 'r')
        self.assertFalse(pak_file.fp.closed, 'File should be open')
        self.assertEqual(len(pak_file.infolist()), 2, 'Pak file should contain exactly two entries.')

        info = pak_file.getinfo('./test_data/test.mdl')
        self.assertIsNotNone(info, 'FileInfo should not be None')
        self.assertEqual(info.filename, './test_data/test.mdl', 'FileInfo names should match')
        self.assertEqual(info.file_size, 4724, 'FileInfo size of test file should be 4724')
        self.assertEqual(info.file_offset, 12, 'FileInfo offset of test file should be 12')

        file = pak_file.open('./test_data/test.mdl')
        self.assertIsNotNone(file, 'File should not be None')
        file.close()

        fp = pak_file.fp
        pak_file.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(pak_file.fp, 'File pointer should be cleaned up')

    def test_write(self):
        pak_file = pak.PakFile(self.buff, 'w')
        self.assertFalse(pak_file.fp.closed, 'File should be open')

        pak_file.write('./test_data/test.mdl')
        pak_file.write('./test_data/test.bsp', './progs/test.bsp')

        self.assertTrue('./test_data/test.mdl' in pak_file.namelist(), 'Mdl file should be in Pak file')
        self.assertTrue('./progs/test.bsp' in pak_file.namelist(), 'Bsp file should be in Pak file')

        fp = pak_file.fp
        pak_file.close()
        self.assertFalse(fp.closed, 'File should be open')
        self.assertIsNone(pak_file.fp, 'File pointer should be cleaned up')

        self.buff.close()

    def test_write_string(self):
        p0 = pak.PakFile(self.buff, 'w')
        p0.writestr('test.cfg', b'bind ALT +strafe')
        p0.writestr(pak.PakInfo('docs/readme.txt'), 'test')
        p0.close()

        self.buff.seek(0)

        p1 = pak.PakFile(self.buff, 'r')

        self.assertTrue('test.cfg' in p1.namelist(), 'Cfg file should be in Pak file')
        self.assertTrue('docs/readme.txt' in p1.namelist(), 'Txt file should be in Pak file')
        self.assertEqual(p1.read('test.cfg'), b'bind ALT +strafe', 'Cfg file content should not change')
        self.assertEqual(p1.read('docs/readme.txt').decode('ascii'), 'test', 'Txt file conent should not change')

        p1.close()
        self.buff.close()

    def test_append(self):
        with open('./test_data/test.pak', 'rb') as f:
            self.buff = io.BytesIO(f.read())

        pak_file = pak.PakFile(self.buff, 'a')
        pak_file.write('./test_data/test.bsp')
        pak_file.close()

        self.buff.seek(0)

        pak_file = pak.PakFile(self.buff, 'r')
        self.assertTrue('./test_data/test.bsp' in pak_file.namelist(), 'Appended file should be in Pak file')
        self.assertEqual(len(pak_file.infolist()), 3, 'Pak file should contain exactly three entries.')

        fp = pak_file.fp
        pak_file.close()

        self.assertFalse(self.buff.closed, 'Pak file should not close passed file-like object')

        self.buff.close()

    def test_context_manager(self):
        with pak.PakFile('./test_data/test.pak', 'r') as pak_file:
            self.assertFalse(pak_file.fp.closed, 'File should be open')
            self.assertEqual(pak_file.mode, 'r', 'File mode should be \'r\'')
            fp = pak_file.fp
            pak_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(pak_file.fp, 'File pointer should be cleaned up')

    def test_empty_pak_file(self):
        with pak.PakFile(self.buff, 'w'):
            pass

        self.buff.seek(0)

        with pak.PakFile(self.buff, 'r') as pak_file:
            self.assertEqual(len(pak_file.namelist()), 0, 'Pak file should have not entries')
            self.assertEqual(pak_file.start_of_directory, 12, 'Directory should start immediately after header')

    def test_zero_byte_file(self):
        with pak.PakFile(self.buff, 'w') as pak_file:
            pak_file.writestr('zero.txt', b'')

        self.buff.seek(0)

        with pak.PakFile(self.buff) as pak_file:
            info = pak_file.getinfo('zero.txt')
            self.assertEqual(info.file_offset, 12, 'File Info offset of test file should be 12')
            self.assertEqual(info.file_size, 0, 'File Info size of test file should be 0')

            data = pak_file.read('zero.txt')
            self.assertEqual(len(data), 0, 'Length of bytes read should be zero.')

if __name__ == '__main__':
    unittest.main()
