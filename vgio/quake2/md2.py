"""This module provides file I/O for Quake 2 MD2 model files.

Example:
    md2_file = md2.Md2.open('model.md2')

References:
    Quake 2 Source
    - id Software
    - https://github.com/id-Software/Quake-2
"""

import io
import struct

from vgio._core import ReadWriteFile

__all__ = ['BadMd2File', 'is_md2file', 'Md2']


VERSION = 8
IDENTITY = b'IDP2'


class BadMd2File(Exception):
    pass


def _check_md2file(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4si'))
    identity, version = struct.unpack('<4si', data)

    return identity == IDENTITY and version == VERSION


def is_md2file(filename):
    """Quickly see if a file is a md2 file by checking the magic number.

    The filename argument may be a file for file-like object.

    Args:
        filename: File to check as string or file-like object.

    Returns:
        True if given file's magic number is correct.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_md2file(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_md2file(fp)

    except:
        return False


class Header:
    """Class for representing a Md2 file header"""
    format = "<4s16i"
    size = struct.calcsize(format)

    def __init__(self,
                 identity,
                 version,
                 skin_width,
                 skin_height,
                 frame_size,
                 number_of_skins,
                 number_of_vertexes,
                 number_of_st_vertexes,
                 number_of_triangles,
                 number_of_gl_commands,
                 number_of_frames,
                 skin_offset,
                 st_vertex_offset,
                 triangle_offset,
                 frame_offset,
                 gl_command_offset,
                 end_offset):
        self.identity = identity
        self.version = version
        self.skin_width = skin_width
        self.skin_height = skin_height
        self.frame_size = frame_size
        self.number_of_skins = number_of_skins
        self.number_of_vertexes = number_of_vertexes
        self.number_of_st_vertexes = number_of_st_vertexes
        self.number_of_triangles = number_of_triangles
        self.number_of_gl_commands = number_of_gl_commands
        self.number_of_frames = number_of_frames
        self.skin_offset = skin_offset
        self.st_vertex_offset = st_vertex_offset
        self.triangle_offset = triangle_offset
        self.frame_offset = frame_offset
        self.gl_command_offset = gl_command_offset
        self.end_offset = end_offset

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.identity,
            header.version,
            header.skin_width,
            header.skin_height,
            header.frame_size,
            header.number_of_skins,
            header.number_of_vertexes,
            header.number_of_st_vertexes,
            header.number_of_triangles,
            header.number_of_gl_commands,
            header.number_of_frames,
            header.skin_offset,
            header.st_vertex_offset,
            header.triangle_offset,
            header.frame_offset,
            header.gl_command_offset,
            header.end_offset
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Skin:
    format = '<64s'
    size = struct.calcsize(format)

    __slots__ = (
        'name'
    )

    def __init__(self,
                 name):
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name

    @classmethod
    def write(cls, file, skin):
        skin_data = struct.pack(
            cls.format,
            skin.name.encode('ascii')
        )

        file.write(skin_data)

    @classmethod
    def read(cls, file):
        skin_data = file.read(cls.size)
        skin_struct = struct.unpack(cls.format, skin_data)

        return Skin(*skin_struct)


class Skins:
    Class = Skin

    @classmethod
    def write(cls, file, skins):
        for skin in skins:
            cls.Class.write(file, skin)

    @classmethod
    def read(cls, file):
        return [Skin(*s) for s in struct.iter_unpack(cls.Class.format, file.read())]


class TriVertex:
    """Class for representing a trivertex

    A TriVertex is a set of XYZ coordinates and a light normal index.

    Note:
        The XYZ coordinates are packed into a (0, 0, 0) to (255, 255, 255)
        local space. The actual position can be calculated:

        position = (packed_vertex * frame.scale) + frame.translate

    Note:
        The light normal index is an index into a set of pre-calculated normal
        vectors. These can be found in the anorms attribute of the quake2
        module.

    Attributes:
        x: The x-coordinate

        y: The y-coordinate

        z: The z-coordinate

        light_normal_index: The index for the pre-calculated normal vector of
            this vertex used for lighting.
    """

    format = '<4B'
    size = struct.calcsize(format)

    __slots__ = (
        'x',
        'y',
        'z',
        'light_normal_index'
    )

    def __init__(self,
                 x,
                 y,
                 z,
                 light_normal_index):

        self.x = x
        self.y = y
        self.z = z
        self.light_normal_index = light_normal_index

    def __getitem__(self, key):
        return (self.x, self.y, self.z)[key]

    def __setitem__(self, key, value):
        if type(key) is int:
            if key == 0:
                self.x = value
            elif key == 1:
                self.y = value
            elif key == 2:
                self.z = value
            else:
                raise IndexError('list index out of range')

        elif type(key) is slice:
            start = key.start or 0
            stop = key.stop or 3

            for i in range(start, stop):
                self[i] = value[i]

    @classmethod
    def write(cls, file, tri_vertex):
        tri_vertex_data = struct.pack(
            cls.format,
            tri_vertex.x,
            tri_vertex.y,
            tri_vertex.z,
            tri_vertex.light_normal_index
        )

        file.write(tri_vertex_data)

    @classmethod
    def read(cls, file):
        tri_vertex_data = file.read(cls.size)
        tri_vertex_struct = struct.unpack(cls.format, tri_vertex_data)

        return TriVertex(*tri_vertex_struct)


class StVertex:
    """Class for representing an st vertex

    StVertices are similar to UV coordinates but are expressed in terms of
    surface space and span (0,0) to (texture_width, texture_height).

    Note:
        If an StVertex lies on a seam and belongs to a back facing triangle,
        the s-component must be incremented by half of the skin width.

    Attributes:
        s: The x-coordinate on the skin.

        t: The y-coordinate on the skin.
    """

    format = '<2h'
    size = struct.calcsize(format)
    count = 1

    __slots__ = (
        's',
        't'
    )

    def __init__(self,
                 s,
                 t):

        self.s = s
        self.t = t

    def __getitem__(self, key):
        return (self.s, self.t)[key]

    def __setitem__(self, key, value):
        if type(key) is int:
            if key == 0:
                self.s = value
            elif key == 1:
                self.t = value
            else:
                raise IndexError('list index out of range')

        elif type(key) is slice:
            start = key.start or 0
            stop = key.stop or 2

            for i in range(start, stop):
                self[i] = value[i]

    @classmethod
    def write(cls, file, st_vertex):
        st_vertex_data = struct.pack(
            cls.format,
            st_vertex.s,
            st_vertex.t
        )

        file.write(st_vertex_data)

    @classmethod
    def read(cls, file):
        st_vertex_data = file.read(cls.size)
        st_vertex_struct = struct.unpack(cls.format, st_vertex_data)

        return StVertex(*st_vertex_struct)


class StVertexes:
    Class = StVertex

    @classmethod
    def write(cls, file, st_vertexes):
        for st_vertex in st_vertexes:
            cls.Class.write(file, st_vertex)

    @classmethod
    def read(cls, file):
        return [cls.Class(*st) for st in struct.iter_unpack(cls.Class.format, file.read())]


class Triangle:
    """Class for representing a triangle

    Note:
        The triangle winding direction is clockwise.

    Attributes:
        vertexes: A triple of vertex indexes. XYZ data can be obtained by
            indexing into the frame.vertexes attribute.
    """

    format = '<6h'
    size = struct.calcsize(format)

    __slots__ = (
        'vertexes',
        'st_vertexes'
    )

    def __init__(self,
                 vertex_0,
                 vertex_1,
                 vertex_2,
                 st_vertex_0,
                 st_vertex_1,
                 st_vertex_2):

        self.vertexes = [vertex_0, vertex_1, vertex_2]
        self.st_vertexes = [st_vertex_0, st_vertex_1, st_vertex_2]

    def __getitem__(self, key):
        return self.vertexes[key]

    def __setitem__(self, key, value):
        self.vertexes[key] = value

    @classmethod
    def write(cls, file, triangle):
        triangle_data = struct.pack(
            cls.format,
            *triangle.vertexes,
            *triangle.st_vertexes
        )

        file.write(triangle_data)

    @classmethod
    def read(cls, file):
        triangle_data = file.read(cls.size)
        triangle_struct = struct.unpack(cls.format, triangle_data)

        return Triangle(*triangle_struct)


class Triangles:
    Class = Triangle

    @classmethod
    def write(cls, file, triangles):
        for triangle in triangles:
            cls.Class.write(file, triangle)

    @classmethod
    def read(cls, file):
        return [cls.Class(*c) for c in struct.iter_unpack(cls.Class.format, file.read())]


class Frame:
    """Class for representing a frame

    A Frame is an object that represents the state of the model at a single
    frame of animation.

    Attributes:
        scale: The frame scale

        translate: The frame offset

        name: The name of the frame.

        vertexes: A list of TriVertex objects.
    """

    format = '<6f16s'
    size = struct.calcsize(format)

    __slots__ = (
        'scale',
        'translate',
        'name',
        'vertexes'
    )

    def __init__(self,
                 scale_x,
                 scale_y,
                 scale_z,
                 translate_x,
                 translate_y,
                 translate_z,
                 name):

        self.scale = scale_x, scale_y, scale_z
        self.translate = translate_x, translate_y, translate_z
        self.name = name

        if type(name) is bytes:
            self.name = name.split(b'\00')[0].decode('ascii')

        self.vertexes = []

    @classmethod
    def write(cls, file, frame):
        frame_data = struct.pack(
            cls.format,
            *frame.scale,
            *frame.translate,
            frame.name.encode('ascii')
        )

        file.write(frame_data)

        for vertex in frame.vertexes:
            TriVertex.write(file, vertex)

    @classmethod
    def read(cls, file, number_of_vertexes):
        frame_data = file.read(cls.size)
        frame_struct = struct.unpack(cls.format, frame_data)

        frame = Frame(*frame_struct)
        frame.vertexes = [TriVertex.read(file) for _ in range(number_of_vertexes)]

        return frame


class GlVertex:
    format = '<2fi'
    size = struct.calcsize(format)

    __slots__ = (
        's',
        't',
        'vertex'
    )

    def __init__(self,
                 s,
                 t,
                 vertex):

        self.s = s
        self.t = t
        self.vertex = vertex

    @classmethod
    def write(cls, file, gl_vertex):
        gl_vertex_data = struct.pack(
            cls.format,
            gl_vertex.s,
            gl_vertex.t,
            gl_vertex.vertex
        )

        file.write(gl_vertex_data)

    @classmethod
    def read(cls, file):
        gl_vertex_data = file.read(cls.size)
        gl_vertex_struct = struct.unpack(cls.format, gl_vertex_data)

        return GlVertex(*gl_vertex_struct)


TRIANGLE_STRIP = 1
TRIANGLE_FAN = -1


class GlCommand:
    __slots__ = (
        'mode',
        'vertexes'
    )

    def __init__(self, mode):
        self.mode = mode

    @classmethod
    def write(cls, file, gl_command):
        vertex_count = len(gl_command.vertexes) * gl_command.mode
        vertex_count_data = struct.pack('<i', vertex_count)
        file.write(vertex_count_data)

        for vertex in gl_command.vertexes:
            GlVertex.write(file, vertex)

    @classmethod
    def read(cls, file):
        vertex_count = struct.unpack('<i', file.read(4))[0]

        if vertex_count == 0:
            return None

        mode = vertex_count // abs(vertex_count)
        vertexes = [GlVertex.read(file) for _ in range(abs(vertex_count))]

        gl_command = GlCommand(mode)
        gl_command.vertexes = vertexes

        return gl_command


class GlCommands:
    Class = GlCommand

    @classmethod
    def write(cls, file, gl_commands):
        for gl_command in gl_commands:
            cls.Class.write(file, gl_command)

        file.write(b'\x00')

    @classmethod
    def read(cls, file):
        result = []
        gl_command = GlCommand.read(file)

        while gl_command:
            result.append(gl_command)
            gl_command = GlCommand.read(file)

        return result


class Md2(ReadWriteFile):
    """Class for working with Md2 files

    Example:
        Basic usage::

            from vgio.quake2.md2 import Md2
            m = Md2.open(file)

    Attributes:
        identity: The magic number of the file, must be b'IDP2'

        version: The version of the file, should be 8.

        skin_width: The pixel width of the skin texture.

        skin_height: The pixel height of the skin texture.

        frames: A sequence of Frame objects.

        skins: A sequence of Skin objects.

        st_vertexes: A sequence of StVertex objects.

        triangles: A sequence of Triangle objects.

        gl_commands: A sequence of GlCommand objects.
    """
    class factory:
        Header = Header
        Skin = Skin
        Skins = Skins
        TriVertex = TriVertex
        StVertex = StVertex
        StVertexes = StVertexes
        Triangle = Triangle
        Triangles = Triangles
        Frame = Frame
        GlVertex = GlVertex
        GlCommand = GlCommand
        GlCommands = GlCommands

    def __init__(self):
        """Constructs an Md2 object."""
        super().__init__()

        self.identity = IDENTITY
        self.version = VERSION
        self.skin_width = 0
        self.skin_height = 0

        self.frames = []
        self.skins = []
        self.st_vertexes = []
        self.triangles = []
        self.gl_commands = []

    @classmethod
    def _read_file(cls, file, mode):
        def _read_chunk(Class, offset, count):
            length = Class.Class.size * count
            file.seek(offset)

            return Class.read(io.BytesIO(file.read(length)))

        md2 = cls()
        md2.fp = file
        md2.mode = mode

        factory = cls.factory

        header = factory.Header.read(file)

        if header.identity != IDENTITY:
            raise BadMd2File('Bad identity: {}'.format(header.identity))

        if header.version != VERSION:
            raise BadMd2File('Bad version number: {}'.format(header.version))

        md2.skin_width = header.skin_width
        md2.skin_height = header.skin_height

        md2.skins = _read_chunk(factory.Skins, header.skin_offset, header.number_of_skins)
        md2.st_vertexes = _read_chunk(factory.StVertexes, header.st_vertex_offset, header.number_of_st_vertexes)
        md2.triangles = _read_chunk(factory.Triangles, header.triangle_offset, header.number_of_triangles)

        file.seek(header.frame_offset)
        md2.frames = [factory.Frame.read(file, header.number_of_vertexes) for _ in range(header.number_of_frames)]

        file.seek(header.gl_command_offset)
        gl_command_data = file.read(struct.calcsize('<{}B'.format(header.number_of_gl_commands*4)))
        md2.gl_commands = factory.GlCommands.read(io.BytesIO(gl_command_data))

        return md2

    @classmethod
    def _write_file(cls, file, md2):
        def _write_chunk(class_, data):
            offset = file.tell()
            class_.write(file, data)
            size = file.tell() - offset

            return offset, size

        md2.validate()

        factory = cls.factory

        vertex_count = len(md2.frames[0].vertexes)

        # Stub out header info
        header = factory.Header(
            md2.identity,
            md2.version,
            md2.skin_width,
            md2.skin_height,
            factory.Frame.size + (factory.TriVertex.size * vertex_count),
            len(md2.skins),
            vertex_count,
            len(md2.st_vertexes),
            len(md2.triangles),
            len(md2.gl_commands),
            len(md2.frames),
            0,
            0,
            0,
            0,
            0,
            0
        )

        header.skin_offset, _ = _write_chunk(factory.Skins, md2.skins)
        header.st_vertex_offset, _ = _write_chunk(factory.StVertexes, md2.st_vertexes)
        header.triangle_offset, _ = _write_chunk(factory.Triangles, md2.triangles)

        header.frame_offset = file.tell()
        for frame in md2.frames:
            factory.Frame.write(file, frame)

        header.gl_command_offset, header.number_of_gl_commands = _write_chunk(factory.GlCommands, md2.gl_commands)
        header.end_offset = file.tell()

        # Finalize header
        file.seek(0)
        factory.Header.write(file, header)
        file.seek(header.end_offset)

    def validate(self):
        if self.identity != IDENTITY:
            raise BadMd2File('Bad identity: {}'.format(self.identity))

        if self.version != VERSION:
            raise BadMd2File('Bad version number: {}'.format(self.version))

        if len(set([len(f.vertexes) for f in self.frames])) != 1:
            raise BadMd2File('Inconsistent frame vertex count')
