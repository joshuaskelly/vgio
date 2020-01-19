"""
Description:
    This module provides file I/O for Devil Daggers shader files.

Example::

    hxshader_file = hxshader.HxShader.open('boid')
"""

import struct

from vgio._core import ReadWriteFile


class Header:
    """Class for representing a HxShader file header

    Attributes:
        name_size:  Length of shader name.

        vertex_shader_size:  Length of the vertex shader.

        frag_shader_size:  Length of the fragment shader.
    """

    format = '<3i'
    size = struct.calcsize(format)

    __slots__ = (
        'name_size',
        'vertex_shader_size',
        'frag_shader_size'
    )

    def __init__(self,
                 name_size,
                 vertex_shader_size,
                 frag_shader_size):
        self.name_size = name_size
        self.vertex_shader_size = vertex_shader_size
        self.frag_shader_size = frag_shader_size

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(cls.format,
                                  header.name_size,
                                  header.vertex_shader_size,
                                  header.frag_shader_size)

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class HxShader(ReadWriteFile):
    """Class for working with HxShaders

    Attributes:
        name: Shader name.

        vertex_shader: Vertex shader code.

        fragment_shader: Fragment shader code.
    """

    def __init__(self):
        """Constructs an HxShader object."""

        super().__init__()

        self.name = ''
        self.vertex_shader = ''
        self.fragment_shader = ''

    @classmethod
    def _read_file(cls, file, mode):
        hs = HxShader()
        hs.fp = file
        hs.mode = mode

        def read_string(size):
            string_format = f'<{size}s'
            string_data = struct.unpack(string_format, file.read(struct.calcsize(string_format)))[0]

            return string_data.decode('ascii')

        header = Header.read(file)

        hs.name = read_string(header.name_size)
        hs.vertex_shader = read_string(header.vertex_shader_size)
        hs.fragment_shader = read_string(header.frag_shader_size)

        return hs

    @classmethod
    def _write_file(cls, file, shader):
        header = Header(
            len(shader.name),
            len(shader.vertex_shader),
            len(shader.fragment_shader)
        )

        Header.write(file, header)
        file.write(shader.name.encode())
        file.write(shader.vertex_shader.encode())
        file.write(shader.fragment_shader.encode())
