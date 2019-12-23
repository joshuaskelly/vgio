import io
import unittest

from vgio.devildaggers import hxmesh


class TestHxMeshReadWrite(unittest.TestCase):
    def setUp(self):
        self.buff = io.BytesIO()

    def assertVerticesEqual(self, expected, actual):
        self.assertEqual(expected.position, actual.position, 'Position values should be equal')
        self.assertEqual(expected.normal, actual.normal, 'Normal values should be equal')
        self.assertEqual(expected.uv, actual.uv, 'Uv values should be equal')

    def test_header(self):
        index_count = 130
        vertex_count = 50
        vertex_size = 32
        mesh_partition_flag = 255

        expected = hxmesh.Header(
            index_count,
            vertex_count,
            vertex_size,
            mesh_partition_flag
        )

        hxmesh.Header.write(self.buff, expected)
        self.buff.seek(0)

        actual = hxmesh.Header.read(self.buff)

        self.assertEqual(expected.index_count, actual.index_count, 'Index_count values should be equal')
        self.assertEqual(expected.vertex_count, actual.vertex_count, 'Vertex_count values should be equal')
        self.assertEqual(expected.vertex_size, actual.vertex_size, 'Vertex_size values should be equal')
        self.assertEqual(expected.mesh_partition_flag, actual.mesh_partition_flag, 'Mesh_partition_flag values should be equal')

        self.assertEqual(self.buff.read(), b'', 'Buffer should be fully consumed')

    def test_vertex(self):
        position = -1.0, 0.0, 1.0
        normal = -1.0, 0.0, 1.0
        uv = -1.0, 0.0

        expected = hxmesh.Vertex(
            *position,
            *normal,
            *uv
        )

        hxmesh.Vertex.write(self.buff, expected)
        self.buff.seek(0)

        actual = hxmesh.Vertex.read(self.buff)

        self.assertVerticesEqual(expected, actual)
        self.assertEqual(self.buff.read(), b'', 'Buffer should be fully consumed')

    def test_hxmesh(self):
        h0 = hxmesh.HxMesh()
        h0.vertices = (
            hxmesh.Vertex(0, 0, 0, 1, 0, 0, 0, 0),
            hxmesh.Vertex(0, 0, 16, 1, 0, 0, 0, 1),
            hxmesh.Vertex(16, 0, 16, 1, 0, 0, 1, 1)
        )
        h0.indices = (0, 1, 2)

        h0.save(self.buff)
        self.buff.seek(0)

        h1 = hxmesh.HxMesh.open(self.buff)

        for expected, actual in zip(h0.vertices, h1.vertices):
            self.assertVerticesEqual(expected, actual)

        self.assertEqual(h0.indices, h1.indices, 'Indices should be equal')


if __name__ == '__main__':
    unittest.main()
