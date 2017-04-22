import io
import unittest

from quake import pak


class TestPakReadWrite(unittest.TestCase):
    def setUp(self):
        self.buff = io.BytesIO()

    def test_read(self):
        pak_file = pak.PakFile('./test_data/test.pak', 'r')
        self.assertFalse(pak_file.fp.closed, 'File should be open')

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

        pak_file = pak.PakFile(buff, 'a')
        pak_file.write('./test_data/test.bsp')
        pak_file.close()

        buff.seek(0)

        pak_file = pak.PakFile(buff, 'r')
        self.assertTrue('./test_data/test.bsp' in pak_file.namelist(), 'Appended file should be in Pak file')

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

if __name__ == '__main__':
    unittest.main()
