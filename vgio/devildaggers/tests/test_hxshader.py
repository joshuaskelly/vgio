import io
import unittest

from vgio.devildaggers import hxshader


class TestHxshaderReadWrite(unittest.TestCase):
    def setUp(self):
        self.buff = io.BytesIO()

    def test_header(self):
        name_size = 16
        vertex_shader_size = 300
        frag_shader_size = 2147483647

        expected = hxshader.Header(
            name_size,
            vertex_shader_size,
            frag_shader_size
        )

        hxshader.Header.write(self.buff, expected)
        self.buff.seek(0)

        actual = hxshader.Header.read(self.buff)

        self.assertEqual(expected.name_size, actual.name_size, 'Name_size values should be equal')
        self.assertEqual(expected.vertex_shader_size, actual.vertex_shader_size, 'Vertex_shader_size values should be equal')
        self.assertEqual(expected.frag_shader_size, actual.frag_shader_size, 'Frag_shader_size values should be equal')

        self.assertEqual(self.buff.read(), b'', 'Buffer should be fully consumed')

    def test_hxshader(self):
        name = 'test_shader'
        vert_shader = """// test
#version 330
in vec3 in_position;
uniform mat4 world_matrix;
uniform mat4 view_proj_matrix;
out vec4 vert_position;
void main( )
{
	vert_position = ( world_matrix * vec4( in_position, 1.0 ));
	gl_Position = view_proj_matrix * vert_position;
}"""
        frag_shader = """// debug
#version 330
out vec4 out_colour0;
void main( )
{
	out_colour0 = vec4( 1.0, 1.0, 1.0, 1.0 );
}"""
        s0 = hxshader.HxShader()
        s0.name = name
        s0.vertex_shader = vert_shader
        s0.fragment_shader = frag_shader

        s0.save(self.buff)
        self.buff.seek(0)

        s1 = hxshader.HxShader.open(self.buff)

        self.assertEqual(s0.name, s1.name, 'Names should be the same')
        self.assertEqual(s0.vertex_shader, s1.vertex_shader, 'Vertex shaders should be the same')
        self.assertEqual(s0.fragment_shader, s1.fragment_shader, 'Fragment shaders should be the same')


if __name__ == '__main__':
    unittest.main()
