import io
import re
import unittest

from quake import map


class TestMapReadWrite(unittest.TestCase):
    def setUp(self):
        self.buff = io.BytesIO()

    def test_loads(self):
        map_file = open('./test_data/test.map')
        map_text = map_file.read(-1)
        map_file.close()

        world_spawn, info_player_start = map.loads(map_text)

        self.assertEqual(world_spawn.classname, 'worldspawn')
        self.assertEqual(world_spawn.sounds, '1')
        self.assertEqual(world_spawn.wad, '/gfx/base.wad')
        self.assertEqual(world_spawn.worldtype, '0')

        brush = world_spawn.brushes[0]
        self.assertEqual(len(brush.planes), 6)

        first_plane = brush.planes[0]
        self.assertEqual(first_plane.points, ((128, 0, 0), (128, 1, 0), (128, 0, 1)))
        self.assertEqual(first_plane.texture_name, 'GROUND1_6')
        self.assertEqual(first_plane.offset, (0.0, 0.0))
        self.assertEqual(first_plane.rotation, 0.0)
        self.assertEqual(first_plane.scale, (1.0, 1.0))

    def test_special_texture_names(self):
        map_text = """
        {
        "classname" "worldspawn"
        {
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) *TEX 0 0 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) +TEX 0 0 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) -TEX 0 0 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) /TEX 0 0 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) {TEX 0 0 0 1.0 1.0
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

        world_spawn, info_player_start = map.loads(m0_text)

        self.assertEqual(world_spawn.classname, 'worldspawn')
        self.assertEqual(world_spawn.sounds, '1')
        self.assertEqual(world_spawn.wad, '/gfx/base.wad')
        self.assertEqual(world_spawn.worldtype, '0')

        brush = world_spawn.brushes[0]
        self.assertEqual(len(brush.planes), 6)

        first_plane = brush.planes[0]
        self.assertEqual(first_plane.points, ((128, 0, 0), (128, 1, 0), (128, 0, 1)))
        self.assertEqual(first_plane.texture_name, 'GROUND1_6')
        self.assertEqual(first_plane.offset, (0.0, 0.0))
        self.assertEqual(first_plane.rotation, 0.0)
        self.assertEqual(first_plane.scale, (1.0, 1.0))

    def test_parse_error(self):
        map_text = """
        {
        {
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) OKAY 0 0 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) OKAY 0 0 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) OKAY 0 0 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 ) OKAY 0 0 0 1.0 1.0
        ( 2 0 0 ) ( 2 1 0 ) ( 2 0 1 } OOPS 0 0 0 1.0 1.0
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

if __name__ == '__main__':
    unittest.main()