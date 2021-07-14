import re
import unittest

from vgio.halflife.tests.basecase import TestCase
from vgio.halflife import map

significant_digits = 5


class TestMapReadWrite(TestCase):
    def test_loads(self):
        map_file = open('./test_data/test.map')
        map_text = map_file.read(-1)
        map_file.close()

        world_spawn, info_player_start, light = map.loads(map_text)

        self.assertEqual(world_spawn.classname, 'worldspawn')
        self.assertEqual(world_spawn.wad, 'half-life\\valve\\halflife.wad')
        self.assertEqual(world_spawn.mapversion, '220')

        self.assertEqual(info_player_start.classname, 'info_player_start')
        self.assertEqual(light.classname, 'light')

    def test_special_texture_names(self):
        map_text = """
        {
        "classname" "worldspawn"
        {
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) *TEX [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) +TEX [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) -TEX [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) /TEX [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) {TEX [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        }
        }
        """

        m0 = map.loads(map_text)
        planes = m0[0].brushes[0].planes

        self.assertEqual(planes[0].texture_name, '*TEX')
        self.assertEqual(planes[1].texture_name, '+TEX')
        self.assertEqual(planes[2].texture_name, '-TEX')
        self.assertEqual(planes[3].texture_name, '/TEX')
        self.assertEqual(planes[4].texture_name, '{TEX')

    def test_dumps(self):
        map_file = open('./test_data/test.map')
        map_text = map_file.read(-1)
        map_file.close()
        entities = map.loads(map_text)

        m0_text = map.dumps(entities)

        world_spawn, info_player_start, light = map.loads(map_text)

        self.assertEqual(world_spawn.classname, 'worldspawn')
        self.assertEqual(world_spawn.wad, 'half-life\\valve\\halflife.wad')
        self.assertEqual(world_spawn.mapversion, '220')

        self.assertEqual(info_player_start.classname, 'info_player_start')
        self.assertEqual(light.classname, 'light')

    def test_parse_error(self):
        map_text = """
        {
        {
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) OKAY [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) OKAY [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) OKAY [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) OKAY [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 } OOPS [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        }
        }
        """

        with self.assertRaises(map.ParseError) as cm:
            map.loads(map_text)

        exception = cm.exception
        message = exception.args[0]
        pattern = 'Expected "(.*)" got "(.*)" line \d+, column \d+'
        expected_symbol, actual_symbol = re.findall(pattern, message)[0]
        line_number, column_number = exception.location

        self.assertEqual(expected_symbol, ')')
        self.assertEqual(actual_symbol, '}')
        self.assertEqual(line_number, 8)
        self.assertEqual(column_number, 37)

    def test_float_points(self):
        map_text = """
        {
        {
        ( 192.33304448274095 -147.07821048680185 -64 ) ( 192.33304448274095 -147.07821048680185 -63 ) ( 191.62593770155439 -146.3711037056153 -64 ) GROUND1_6 [ 0.0 0.0 1.0 0.0 ] [ 0.0 1.0 0.0 0.0 ] 0.0 1.0 1.0
        ( 147.07821048680188 -192.33304448274092 -64 ) ( 146.37110370561533 -191.62593770155436 -64 ) ( 147.07821048680188 -192.33304448274092 -63 ) GROUND1_6 [ 0.0 0.0 1.0 0.0 ] [ 0.0 1.0 0.0 0.0 ] 0.0 1.0 1.0
        ( -124.45079348883236 -79.195959492893337 -64 ) ( -123.74368670764581 -78.488852711706784 -64 ) ( -124.45079348883236 -79.195959492893337 -63 ) GROUND1_6 [ 0.0 0.0 1.0 0.0 ] [ 0.0 1.0 0.0 0.0 ] 0.0 1.0 1.0
        ( -79.195959492893323 -124.45079348883237 -64 ) ( -79.195959492893323 -124.45079348883237 -63 ) ( -78.48885271170677 -123.74368670764582 -64 ) GROUND1_6 [ 0.0 0.0 1.0 0.0 ] [ 0.0 1.0 0.0 0.0 ] 0.0 1.0 1.0
        ( 67.882250993908571 -271.52900397563423 64 ) ( 67.175144212722017 -270.82189719444767 64 ) ( 68.589357775095124 -270.82189719444767 64 ) GROUND1_6 [ 0.0 0.0 1.0 0.0 ] [ 0.0 1.0 0.0 0.0 ] 0.0 1.0 1.0
        ( 67.882250993908571 -271.52900397563423 -0 ) ( 68.589357775095124 -270.82189719444767 -0 ) ( 67.175144212722017 -270.82189719444767 -0 ) GROUND1_6 [ 0.0 0.0 1.0 0.0 ] [ 0.0 1.0 0.0 0.0 ] 0.0 1.0 1.0
        }
        }
        """

        m0 = map.loads(map_text)
        s0 = map.dumps(m0)
        m1 = map.loads(s0)

        p0 = m0[0].brushes[0].planes[0].points[0][0]
        p1 = m1[0].brushes[0].planes[0].points[0][0]
        self.assertAlmostEqual(p0, p1, significant_digits)

    def test_texture_names_starting_with_numeral(self):
        map_text = """
        {
        {
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        }
        }
        """

        m0 = map.loads(map_text)
        self.assertEqual(m0[0].brushes[0].planes[0].texture_name, '32_tex')

    def test_floats_close_to_zero(self):
        map_text = """
        {
        {
        ( 2 0 1.5e-06 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) 32_tex [ 0 0 1 0 ] [ 0 1 0 0 ] 0 1.0 1.0
        }
        }
        """

        m0 = map.loads(map_text)
        self.assertAlmostEqual(m0[0].brushes[0].planes[0].points[0][2], 1.5e-06, significant_digits)


if __name__ == '__main__':
    unittest.main()
