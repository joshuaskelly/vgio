"""This module provides file I/O for Devil Daggers texture files."""

import struct

from vgio._core import ReadWriteFile


class Header:
    """Class for representing a HxMesh file header.

    Attributes:
        index_count:  The number of triangle indexes.

        vertex_count:  The number of vertices.

        vertex_size:  The size of each vertex. Should be 32

        mesh_partition_flag:  Indicates if a mesh contains a mesh partition?
    """

    format = '<2i2B'
    size = struct.calcsize(format)

    __slots__ = (
        'index_count',
        'vertex_count',
        'vertex_size',
        'mesh_partition_flag'
    )

    def __init__(self,
                 index_count,
                 vertex_count,
                 vertex_size,
                 mesh_partition_flag):
        self.index_count = index_count
        self.vertex_count = vertex_count
        self.vertex_size = vertex_size
        self.mesh_partition_flag = mesh_partition_flag

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.index_count,
            header.vertex_count,
            header.vertex_size,
            header.mesh_partition_flag
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Vertex:
    """Class for representing an HxMesh vertex.

    Example:
        Create a vertex object::

            from vgio.devildaggers.hxmesh import Vertex
            position = 0, 0, 0
            normal = 0, 0, 1
            uv = 0, 1
            vertex = Vertex(*position, *normal, *uv)

    Attributes:
        position:  Vertex position.

        normal:  Vertex normal.

        uv:  Vertex UV coordinates.
    """

    format = '<8f'
    size = struct.calcsize(format)

    __slots__ = (
        'position',
        'normal',
        'uv'
    )

    def __init__(self,
                 position_x,
                 position_y,
                 position_z,
                 normal_x,
                 normal_y,
                 normal_z,
                 u,
                 v):
        """Constructs an HxMesh Vertex object.

        Args:
            position_x: The position x-coordinate

            position_y: The position y-coordinate

            position_z: The position z-coordinate

            normal_x: The normal x-coordinate

            normal_y: The normal y-coordinate

            normal_z: The normal z-coordinate

            u: The UV u-coordinate

            v: The UV v-coordinate
        """

        self.position = position_x, position_y, position_z
        self.normal = normal_x, normal_y, normal_z
        self.uv = u, v

    @classmethod
    def write(cls, file, vertex):
        vertex_data = struct.pack(
            cls.format,
            *vertex.position,
            *vertex.normal,
            *vertex.uv
        )

        file.write(vertex_data)

    @classmethod
    def read(cls, file):
        vertex_data = file.read(cls.size)
        vertex_struct = struct.unpack(cls.format, vertex_data)

        return Vertex(*vertex_struct)


class HxMesh(ReadWriteFile):
    """Class for working with HxMesh files.

    Example:
        Load a file named "boid" and access mesh object attributes::

            from vgio.devildaggers.hxmesh import HxMesh
            with HxMesh.open('boid') as boid:
                indices = boid.indices
                vertices = boid.vertices

    Attributes:
        indices: An unstructured sequence of triangle indices.

        vertices: A sequence of Vertex objects.
    """

    def __init__(self):
        """Constructs an HxMesh object."""
        super().__init__()

        self.indices = []
        self.vertices = []

    @classmethod
    def _read_file(cls, file, mode):
        hxmesh = HxMesh()

        header = Header.read(file)
        hxmesh.vertices = [Vertex.read(file) for _ in range(header.vertex_count)]

        index_format = f'<{header.index_count}i'
        index_data = file.read(struct.calcsize(index_format))
        hxmesh.indices = struct.unpack(index_format, index_data)

        return hxmesh

    @classmethod
    def _write_file(cls, file, hxmesh):
        header = Header(
            len(hxmesh.indices),
            len(hxmesh.vertices),
            32,
            0
        )

        Header.write(file, header)

        for vertex in hxmesh.vertices:
            Vertex.write(file, vertex)

        index_format = f'<{len(hxmesh.indices)}i'
        index_data = struct.pack(index_format, *hxmesh.indices)
        file.write(index_data)
