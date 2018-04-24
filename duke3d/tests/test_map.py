import unittest

from tests.basecase import TestCase
from duke3d import map


class TestMapReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertFalse(map.is_mapfile('./test_data/test.art'))

    def test_sector(self):
        s0 = map.Sector()
        s0.wall_pointer = 1
        s0.wall_number = 2
        s0.ceiling_z = 3
        s0.floor_z = 4
        s0.ceiling_stat = 5
        s0.floor_stat = 6
        s0.ceiling_picnum = 7
        s0.ceiling_heinum = 8
        s0.ceiling_shade = 9
        s0.ceiling_palette = 10
        s0.ceiling_x_panning = 11
        s0.ceiling_y_panning = 12
        s0.floor_picnum = 13
        s0.floor_heinum = 14
        s0.floor_shade = 15
        s0.floor_palette = 16
        s0.floor_x_panning = 17
        s0.floor_y_panning = 18
        s0.visibility = 19
        s0.lotag = 20
        s0.hitag = 21
        s0.extra = 22

        map.Sector.write(self.buff, s0)
        self.buff.seek(0)

        s1 = map.Sector.read(self.buff)

        self.assertEqual(s0.wall_pointer, s1.wall_pointer, 'Wall_pointer values should be equal')
        self.assertEqual(s0.wall_number, s1.wall_number, 'Wall_number values should be equal')
        self.assertEqual(s0.ceiling_z, s1.ceiling_z, 'Ceiling_z values should be equal')
        self.assertEqual(s0.floor_z, s1.floor_z, 'Floor_z values should be equal')
        self.assertEqual(s0.ceiling_stat, s1.ceiling_stat, 'Ceiling_stat values should be equal')
        self.assertEqual(s0.floor_stat, s1.floor_stat, 'Floor_stat values should be equal')
        self.assertEqual(s0.ceiling_picnum, s1.ceiling_picnum, 'Ceiling_picnum values should be equal')
        self.assertEqual(s0.ceiling_heinum, s1.ceiling_heinum, 'Ceiling_heinum values should be equal')
        self.assertEqual(s0.ceiling_shade, s1.ceiling_shade, 'Ceiling_shade values should be equal')
        self.assertEqual(s0.ceiling_palette, s1.ceiling_palette, 'Ceiling_palette values should be equal')
        self.assertEqual(s0.ceiling_x_panning, s1.ceiling_x_panning, 'Ceiling_x_panning values should be equal')
        self.assertEqual(s0.ceiling_y_panning, s1.ceiling_y_panning, 'Ceiling_y_panning values should be equal')
        self.assertEqual(s0.floor_picnum, s1.floor_picnum, 'Floor_picnum values should be equal')
        self.assertEqual(s0.floor_heinum, s1.floor_heinum, 'Floor_heinum values should be equal')
        self.assertEqual(s0.floor_shade, s1.floor_shade, 'Floor_shade values should be equal')
        self.assertEqual(s0.floor_palette, s1.floor_palette, 'Floor_palette values should be equal')
        self.assertEqual(s0.floor_x_panning, s1.floor_x_panning, 'Floor_x_panning values should be equal')
        self.assertEqual(s0.floor_y_panning, s1.floor_y_panning, 'Floor_y_panning values should be equal')
        self.assertEqual(s0.visibility, s1.visibility, 'Visibility values should be equal')
        self.assertEqual(s0.lotag, s1.lotag, 'Lotag values should be equal')
        self.assertEqual(s0.hitag, s1.hitag, 'Hitag values should be equal')
        self.assertEqual(s0.extra, s1.extra, 'Extra values should be equal')

    def test_wall(self):
        w0 = map.Wall()
        w0.x = 0
        w0.y = 1
        w0.point2 = 2
        w0.next_wall = -1
        w0.next_sector = 4
        w0.cstat = 5
        w0.picnum = 6
        w0.over_picnum = 7
        w0.shade = 8
        w0.palette = 9
        w0.x_repeat = 10
        w0.y_repeat = 11
        w0.x_panning = 12
        w0.y_panning = 13
        w0.lotag = 14
        w0.hitag = 15
        w0.extra = 16

        map.Wall.write(self.buff, w0)
        self.buff.seek(0)

        w1 = map.Wall.read(self.buff)
        self.assertEqual(w0.x, w1.x, 'X values should be equal')
        self.assertEqual(w0.y, w1.y, 'Y values should be equal')
        self.assertEqual(w0.point2, w1.point2, 'Point2 values should be equal')
        self.assertEqual(w0.next_wall, w1.next_wall, 'Next_wall values should be equal')
        self.assertEqual(w0.next_sector, w1.next_sector, 'Next_sector values should be equal')
        self.assertEqual(w0.cstat, w1.cstat, 'Cstat values should be equal')
        self.assertEqual(w0.picnum, w1.picnum, 'Picnum values should be equal')
        self.assertEqual(w0.over_picnum, w1.over_picnum, 'Over_picnum values should be equal')
        self.assertEqual(w0.shade, w1.shade, 'Shade values should be equal')
        self.assertEqual(w0.palette, w1.palette, 'Palette values should be equal')
        self.assertEqual(w0.x_repeat, w1.x_repeat, 'X_repeat values should be equal')
        self.assertEqual(w0.y_repeat, w1.y_repeat, 'Y_repeat values should be equal')
        self.assertEqual(w0.x_panning, w1.x_panning, 'X_panning values should be equal')
        self.assertEqual(w0.y_panning, w1.y_panning, 'Y_panning values should be equal')
        self.assertEqual(w0.lotag, w1.lotag, 'Lotag values should be equal')
        self.assertEqual(w0.hitag, w1.hitag, 'Hitag values should be equal')
        self.assertEqual(w0.extra, w1.extra, 'Extra values should be equal')

    def test_sprite(self):
        s0 = map.Sprite()
        s0.x = 0
        s0.y = 1
        s0.z = 2
        s0.cstat = 3
        s0.picnum = 4
        s0.shade = 5
        s0.palette = 6
        s0.clip_distance = 7
        s0.x_repeat = 8
        s0.y_repeat = 9
        s0.x_offset = 10
        s0.y_offset = 11
        s0.sector_number = 12
        s0.status_number = 13
        s0.angle = 14
        s0.owner = 15
        s0.x_velocity = 16
        s0.y_velocity = 17
        s0.z_velocity = 18
        s0.lotag = 19
        s0.hitag = 20
        s0.extra = 21

        map.Sprite.write(self.buff, s0)
        self.buff.seek(0)

        s1 = map.Sprite.read(self.buff)
        self.assertEqual(s0.x, s1.x, 'X values should be equal')
        self.assertEqual(s0.y, s1.y, 'Y values should be equal')
        self.assertEqual(s0.z, s1.z, 'Z values should be equal')
        self.assertEqual(s0.cstat, s1.cstat, 'Cstat values should be equal')
        self.assertEqual(s0.picnum, s1.picnum, 'Picnum values should be equal')
        self.assertEqual(s0.shade, s1.shade, 'Shade values should be equal')
        self.assertEqual(s0.palette, s1.palette, 'Palette values should be equal')
        self.assertEqual(s0.clip_distance, s1.clip_distance, 'Clip_distance values should be equal')
        self.assertEqual(s0.x_repeat, s1.x_repeat, 'X_repeat values should be equal')
        self.assertEqual(s0.y_repeat, s1.y_repeat, 'Y_repeat values should be equal')
        self.assertEqual(s0.x_offset, s1.x_offset, 'X_offset values should be equal')
        self.assertEqual(s0.y_offset, s1.y_offset, 'Y_offset values should be equal')
        self.assertEqual(s0.sector_number, s1.sector_number, 'Sector_number values should be equal')
        self.assertEqual(s0.status_number, s1.status_number, 'Status_number values should be equal')
        self.assertEqual(s0.angle, s1.angle, 'Angle values should be equal')
        self.assertEqual(s0.owner, s1.owner, 'Owner values should be equal')
        self.assertEqual(s0.x_velocity, s1.x_velocity, 'X_velocity values should be equal')
        self.assertEqual(s0.y_velocity, s1.y_velocity, 'Y_velocity values should be equal')
        self.assertEqual(s0.z_velocity, s1.z_velocity, 'Z_velocity values should be equal')
        self.assertEqual(s0.lotag, s1.lotag, 'Lotag values should be equal')
        self.assertEqual(s0.hitag, s1.hitag, 'Hitag values should be equal')
        self.assertEqual(s0.extra, s1.extra, 'Extra values should be equal')

    def test_context_manager(self):
        with map.Map.open('./test_data/test.map', 'a') as map_file:
            self.assertFalse(map_file.fp.closed, 'File should be open')
            self.assertEqual(map_file.mode, 'a', 'File mode should be \'a\'')
            fp = map_file.fp
            map_file._did_modify = False

        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(map_file.fp, 'File pointer should be cleaned up')


if __name__ == '__main__':
    unittest.main()
