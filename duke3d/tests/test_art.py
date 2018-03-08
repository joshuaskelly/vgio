import io
import unittest

from tests.basecase import TestCase
from duke3d import art


class TestArtReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertFalse(art.is_artfile('./test_data/test.art'))
        self.assertTrue(art.is_artfile('./test_data/test.art'))

    def test_read(self):
        art_file = art.ArtFile('./test_data/test.art', 'r')
        self.assertFalse(art_file.fp.closed, 'File should be open')
        self.assertEqual(len(art_file.infolist()), 1, 'Art file should contain exactly one entry.')

        info = art_file.getinfo('0')
        self.assertIsNotNone(info, 'FileInfo should not be None')
        self.assertEqual(info.filename, 'duke3d.cfg', 'FileInfo names should match')
        self.assertEqual(info.file_size, 19, 'FileInfo size of test file should be 4724')
        self.assertEqual(info.file_offset, 32, 'FileInfo offset of test file should be 12')

        file = art_file.open('duke3d.cfg')
        self.assertIsNotNone(file, 'File should not be None')
        file.close()

        fp = art_file.fp
        art_file.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(art_file.fp, 'File pointer should be cleaned up')
