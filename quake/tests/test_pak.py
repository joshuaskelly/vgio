import io
import unittest

from quake.tests import basecase
from quake import pak


class TestPakReadWrite(basecase.TestCase):
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
        pak_file.write('./test_data/test.bsp')

        self.assertTrue('./test_data/test.mdl' in pak_file.namelist(), 'Mdl file should be in Pak file')
        self.assertTrue('./test_data/test.bsp' in pak_file.namelist(), 'Bsp file should be in Pak file')

        fp = pak_file.fp
        pak_file.close()
        self.assertFalse(fp.closed, 'File should be open')
        self.assertIsNone(pak_file.fp, 'File pointer should be cleaned up')

        self.buff.close()

    def test_append(self):
        f = open('./test_data/test.pak', 'rb')
        buff = io.BytesIO(f.read(-1))
        f.close()

        pak_file = pak.PakFile(buff, 'a')
        pak_file.write('./test_data/test.bsp')
        pak_file.close()

        buff.seek(0)

        pak_file = pak.PakFile(buff, 'r')
        self.assertTrue('./test_data/test.bsp' in pak_file.namelist(), 'Appended file should be in Pak file')
        self.assertEqual(len(pak_file.infolist()), 3, 'Pak file should contain exactly three entries.')

        fp = pak_file.fp
        pak_file.close()

        self.assertFalse(buff.closed, 'Pak file should not close passed file-like object')

        buff.close()

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

if __name__ == '__main__':
    unittest.main()
