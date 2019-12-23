import io
import unittest

from unittest import mock

from vgio._core import ReadWriteFile


class TestReadWriteFile(unittest.TestCase):
    def setUp(self):
        self.buff = io.BytesIO()

    def test_open_bad_file_like_object(self):
        with self.assertRaises(OSError):
            ReadWriteFile.open(1, 'r')

    def test_open_bytes_for_write(self):
        with self.assertRaises(TypeError):
            ReadWriteFile.open(b'', 'w')

    def test_open_as_read_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            ReadWriteFile.open(self.buff, 'r')

    def test_open_for_read(self):
        with mock.patch.object(ReadWriteFile, '_read_file', return_value=ReadWriteFile()) as mocked_read_method:
            read_file = ReadWriteFile.open(self.buff, 'r')

            self.assertEqual(read_file.fp, self.buff)
            self.assertEqual(read_file.mode, 'r')
            mocked_read_method.assert_called_once_with(self.buff, 'r')

            read_file.close()

            self.assertTrue(self.buff.closed, 'File pointer should be closed')
            self.assertIsNone(read_file.fp, 'File pointer should be cleaned up')

    def test_open_as_write_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            write_file = ReadWriteFile.open(self.buff, 'w')
            write_file.close()

    def test_open_for_write(self):
        with mock.patch.object(ReadWriteFile, '_write_file') as mocked_write_method:
            write_file = ReadWriteFile.open(self.buff, 'w')

            self.assertEqual(write_file.fp, self.buff, 'File pointer should be set correctly')
            self.assertEqual(write_file.mode, 'w', "File mode should be 'w'")
            self.assertTrue(write_file._did_modify, 'File should be marked as modified')

            write_file.close()

            self.assertTrue(self.buff.closed, 'File pointer should be closed')
            self.assertIsNone(write_file.fp, 'File pointer should be cleaned up')
            mocked_write_method.assert_called_once_with(self.buff, write_file)

    def test_open_for_append(self):
        with mock.patch.object(ReadWriteFile, '_read_file', return_value=ReadWriteFile()) as mocked_read_method, mock.patch.object(ReadWriteFile, '_write_file') as mocked_write_method:
            append_file = ReadWriteFile.open(self.buff, 'a')

            self.assertEqual(append_file.fp, self.buff)
            self.assertEqual(append_file.mode, 'a')
            self.assertTrue(append_file._did_modify)
            mocked_read_method.assert_called_once_with(self.buff, 'a')

            append_file.close()

            self.assertTrue(self.buff.closed, 'File pointer should be closed')
            mocked_write_method.assert_called_once_with(self.buff, append_file)
            self.assertIsNone(append_file.fp, 'File pointer should be cleaned up')

    def test_save(self):
        def t(file, object_):
            file.write(b'0')

        with mock.patch.object(ReadWriteFile, '_write_file', side_effect=t) as mocked_write_method:
            file = ReadWriteFile()
            file.save(self.buff)

            self.assertFalse(self.buff.closed)

            self.buff.seek(0)
            contents = self.buff.read()

            self.assertEqual(contents, b'0')

    def test_context_manager(self):
        with mock.patch.object(ReadWriteFile, '_read_file', return_value=ReadWriteFile()) as mocked_read_method:
            with ReadWriteFile.open(self.buff, 'r') as read_file:
                self.assertFalse(read_file.fp.closed)
                self.assertEqual(read_file.mode, 'r')
                fp = read_file.fp

            self.assertTrue(fp.closed)
            self.assertIsNone(read_file.fp)


if __name__ == '__main__':
    unittest.main()
