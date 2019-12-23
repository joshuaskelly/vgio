import io
import unittest

from vgio.duke3d.tests.basecase import TestCase
from vgio.duke3d import grp


class TestGrpReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertFalse(grp.is_grpfile('./test_data/test.art'))
        self.assertTrue(grp.is_grpfile('./test_data/test.grp'))

    def test_read(self):
        grp_file = grp.GrpFile('./test_data/test.grp', 'r')
        self.assertFalse(grp_file.fp.closed, 'File should be open')
        self.assertEqual(len(grp_file.infolist()), 1, 'Grp file should contain exactly one entry.')

        info = grp_file.getinfo('duke3d.cfg')
        self.assertIsNotNone(info, 'FileInfo should not be None')
        self.assertEqual(info.filename, 'duke3d.cfg', 'FileInfo names should match')
        self.assertEqual(info.file_size, 19, 'FileInfo size of test file should be 4724')
        self.assertEqual(info.file_offset, 32, 'FileInfo offset of test file should be 12')

        file = grp_file.open('duke3d.cfg')
        self.assertIsNotNone(file, 'File should not be None')
        file.close()

        fp = grp_file.fp
        grp_file.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(grp_file.fp, 'File pointer should be cleaned up')

    def test_write(self):
        grp_file = grp.GrpFile(self.buff, 'w')
        self.assertFalse(grp_file.fp.closed, 'File should be open')

        grp_file.write('./test_data/test.art')

        self.assertTrue('test.art' in grp_file.namelist(), 'Art file should be in Grp file')

        fp = grp_file.fp
        grp_file.close()
        self.assertFalse(fp.closed, 'File should be open')
        self.assertIsNone(grp_file.fp, 'File pointer should be cleaned up')

        self.buff.close()
        
    def test_write_string(self):
        w0 = grp.GrpFile(self.buff, 'w')
        w0.writestr('duke3d.cfg', b'PlayerName = "DUKE"')
        w0.writestr(grp.GrpInfo('readme.txt'), 'test')

        info = grp.GrpInfo('bytes')
        info.file_size = len(b'bytes')
        w0.writestr(info, io.BytesIO(b'bytes'))

        w0.close()

        self.buff.seek(0)

        w1 = grp.GrpFile(self.buff, 'r')

        self.assertTrue('duke3d.cfg' in w1.namelist(), 'Cfg file should be in Grp file')
        self.assertTrue('readme.txt' in w1.namelist(), 'Txt file should be in Grp file')
        self.assertTrue('bytes' in w1.namelist(), 'Bytes should be in Grp file')
        self.assertEqual(w1.read('duke3d.cfg'), b'PlayerName = "DUKE"', 'Cfg file content should not change')
        self.assertEqual(w1.read('readme.txt').decode('ascii'), 'test', 'Txt file content should not change')
        self.assertEqual(w1.read('bytes'), b'bytes', 'Bytes content should not change')

        w1.close()
        self.buff.close()

    def test_append(self):
        with open('./test_data/test.grp', 'rb') as f:
            self.buff = io.BytesIO(f.read())

        grp_file = grp.GrpFile(self.buff, 'a')
        grp_file.write('./test_data/test.art')
        grp_file.close()

        self.buff.seek(0)

        grp_file = grp.GrpFile(self.buff, 'r')
        self.assertTrue('test.art' in grp_file.namelist(), 'Appended file should be in Grp file')
        self.assertEqual(len(grp_file.infolist()), 2, 'Grp file should contain exactly two entries.')

        fp = grp_file.fp
        grp_file.close()

        self.assertFalse(self.buff.closed, 'Grp file should not close passed file-like object')

        self.buff.close()

    def test_empty_grp_file(self):
        with grp.GrpFile(self.buff, 'w'):
            pass

        self.buff.seek(0)

        with grp.GrpFile(self.buff, 'r') as grp_file:
            self.assertEqual(len(grp_file.namelist()), 0, 'Grp file should have not entries')

    def test_zero_byte_file(self):
        with grp.GrpFile(self.buff, 'w') as grp_file:
            grp_file.writestr('zero.txt', b'')

        self.buff.seek(0)

        with grp.GrpFile(self.buff) as grp_file:
            info = grp_file.getinfo('zero.txt')
            self.assertEqual(info.file_offset, 32, 'File Info offset of test file should be 32')
            self.assertEqual(info.file_size, 0, 'File Info size of test file should be 0')

            data = grp_file.read('zero.txt')
            self.assertEqual(len(data), 0, 'Length of bytes read should be zero.')


if __name__ == '__main__':
    unittest.main()
