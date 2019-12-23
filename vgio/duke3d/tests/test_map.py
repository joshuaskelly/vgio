import unittest

from vgio.duke3d.tests.basecase import TestCase
from vgio.duke3d import map


class TestMapReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertFalse(map.is_mapfile('./test_data/test.art'))

    def test_sector(self):
        s0 = map.Sector(
            wall_pointer=1,
            wall_number=2,
            ceiling_z=3,
            floor_z=4,
            ceiling_stat=5,
            floor_stat=6,
            ceiling_picnum=7,
            ceiling_heinum=8,
            ceiling_shade=9,
            ceiling_palette=10,
            ceiling_x_panning=11,
            ceiling_y_panning=12,
            floor_picnum=13,
            floor_heinum=14,
            floor_shade=15,
            floor_palette=16,
            floor_x_panning=17,
            floor_y_panning=18,
            visibility=19,
            lotag=20,
            hitag=21,
            extra=22
        )

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
        w0 = map.Wall(
            x=0,
            y=1,
            point2=2,
            next_wall=-1,
            next_sector=4,
            cstat=5,
            picnum=6,
            over_picnum=7,
            shade=8,
            palette=9,
            x_repeat=10,
            y_repeat=11,
            x_panning=12,
            y_panning=13,
            lotag=14,
            hitag=15,
            extra=16
        )

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
        s0 = map.Sprite(
            x=0,
            y=1,
            z=2,
            cstat=3,
            picnum=4,
            shade=5,
            palette=6,
            clip_distance=7,
            x_repeat=8,
            y_repeat=9,
            x_offset=10,
            y_offset=11,
            sector_number=12,
            status_number=13,
            angle=14,
            owner=15,
            x_velocity=16,
            y_velocity=17,
            z_velocity=18,
            lotag=19,
            hitag=20,
            extra=21
        )

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


if __name__ == '__main__':
    unittest.main()
