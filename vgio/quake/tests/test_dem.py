import io
import unittest

from vgio.quake.tests.basecase import TestCase
from vgio.quake import dem


class TestDemReadWrite(TestCase):
    def test_dem(self):
        d0 = dem.Dem.open('./test_data/test.dem')
        d0.close()

        d0.save(self.buff)
        self.buff.seek(0)

        b = io.BufferedReader(self.buff)
        d1 = dem.Dem.open(b)

        self.assertEqual(d1.cd_track, '2', 'Cd track should be 2')
        self.assertEqual(len(d1.message_blocks), 168, 'The demo should have 168 message blocks')

        last_message_of_first_block = d1.message_blocks[0].messages[-1]

        self.assertTrue(hasattr(last_message_of_first_block, 'sign_on'), 'The last message of the first block should be a SignOnNum')
        self.assertEqual(last_message_of_first_block.sign_on, 1, 'Sign on value should be 1')
        self.assertEqual(d1.message_blocks[-1].messages[0].__class__.__name__, 'Disconnect', 'The last message should be a Disconnect')

        self.assertFalse(d1.fp.closed, 'File should be open')
        fp = d1.fp
        d1.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(d1.fp, 'File pointer should be cleaned up')

    def test_context_manager(self):
        with dem.Dem.open('./test_data/test.dem', 'a') as dem_file:
            self.assertFalse(dem_file.fp.closed, 'File should be open')
            self.assertEqual(dem_file.mode, 'a', 'File mode should be \'a\'')
            fp = dem_file.fp
            dem_file._did_modify = False
    
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(dem_file.fp, 'File pointer should be cleaned up')


if __name__ == '__main__':
    unittest.main()
