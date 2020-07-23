import io
import threading
import unittest

from unittest import mock

from vgio._core import ArchiveExtFile
from vgio._core import ReadWriteFile
from vgio._core import _SharedFile


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


class TestSharedFile(unittest.TestCase):
    def test_read(self):
        data = b'\x00\x01\x02\x03\x04\x05\x06\x07'
        buff = io.BytesIO(data)
        shared_file = _SharedFile(
            buff,
            0,
            len(data),
            lambda x: None,
            threading.RLock(),
            lambda: False
        )

        # Read one byte
        self.assertEqual(shared_file.read(1), b'\x00')

        # Read two bytes
        self.assertEqual(shared_file.read(2), b'\x01\x02')

        # Read byte at arbitrary position
        shared_file.seek(5)
        self.assertEqual(shared_file.tell(), 5)
        self.assertEqual(shared_file.read(1), b'\x05')

        shared_file.close()
        self.assertIsNone(shared_file._file)


class TestArchiveExtFile(unittest.TestCase):
    def setUp(self):
        data = b'\x00\x01\x02\x03\x04\x05\x06\x07'
        self.buff = io.BytesIO(data)
        shared_file = _SharedFile(
            self.buff,
            0,
            len(data),
            lambda x: None,
            threading.RLock(),
            lambda: False
        )

        class TestInfo:
            def __init__(self):
                self.filename = 'test'
                self.file_offset = 0
                self.file_size = len(data)

        self.ext_file = ArchiveExtFile(
            shared_file,
            'r',
            TestInfo()
        )

        self.data = data

    def tearDown(self):
        self.ext_file.close()

    def test_read(self):
        # Read one byte
        self.assertEqual(b'\x00', self.ext_file.read(1))

        # Read two bytes
        self.assertEqual(b'\x01\x02', self.ext_file.read(2))

        # Seek then read
        self.ext_file.seek(5)
        self.assertEqual(b'\x05', self.ext_file.read(1))

        # Read everything
        self.ext_file.seek(0)
        self.assertEqual(self.data, self.ext_file.read(-1))

        self.ext_file.seek(0, 2)
        self.assertEqual(b'', self.ext_file.read(1))

    def test_tell(self):
        # Start of the file
        self.assertEqual(0, self.ext_file.tell())

        # Arbitrary position inside file
        self.ext_file.seek(5)
        self.assertEqual(5, self.ext_file.tell())

        # End of file
        self.ext_file.seek(0, 2)
        self.assertEqual(8, self.ext_file.tell())

    def test_peek(self):
        # Start of file
        self.assertEqual(b'\x00', self.ext_file.peek(1)[:1])
        self.assertEqual(0, self.ext_file.tell())

        # Arbitrary position inside file
        self.ext_file.seek(5)
        self.assertEqual(b'\x05', self.ext_file.peek(1)[:1])
        self.assertEqual(5, self.ext_file.tell())

        # End of file
        self.ext_file.seek(0, 2)
        self.assertEqual(b'', self.ext_file.peek(1)[:1])
        self.assertEqual(8, self.ext_file.tell())


if __name__ == '__main__':
    unittest.main()
