"""This module provides file I/O for Quake MDL model files.

Example:
    mdl_file = mdl.Mdl.open('player.mdl')

References:
    Quake Source
    - id Software
    - https://github.com/id-Software/Quake

    Quake Documentation Version 3.4
    - Olivier Montanuy, et al.
    - http://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_5.htm
"""

import struct

from types import SimpleNamespace

from vgio._core import ReadWriteFile
from vgio import quake

__all__ = ['BadMdlFile', 'is_mdlfile', 'BadMdlFile', 'Skin', 'SkinGroup',
           'StVertex', 'Triangle', 'TriVertex', 'Frame', 'FrameGroup', 'Mesh',
           'Image', 'Mdl']


class BadMdlFile(Exception):
    pass


IDENTITY = b'IDPO'
VERSION = 6


# Skin structure
def _calculate_skin_format(size):
    width, height = size
    return '<i%iB' % (width * height)

# Indexes of Skin structure
_SKIN_TYPE = 0
_SKIN_PIXELS = 1

# Skin Group structure
def _calculate_skin_group_format(number_of_pictures, size):
    width, height = size
    return '<%if%iB' % (number_of_pictures, width * height * number_of_pictures)

# ST Vertex structure
st_vertex_format = '<3l'
st_vertex_size = struct.calcsize(st_vertex_format)

# Indexes of ST Vertex structure
_ST_VERTEX_ON_SEAM = 0
_ST_VERTEX_S = 1
_ST_VERTEX_T = 2

# Triangle structure
triangle_format = '<4l'
triangle_size = struct.calcsize(triangle_format)

# Indexes of Triangle structure
_TRIANGLE_FACES_FRONT = 0
_TRIANGLE_VERTICES = 1

# TriVertex structure
trivertex_format = '<4B'
trivertex_size = struct.calcsize(trivertex_format)

# Indexes for TriVertex structure
_TRIVERTEX_X = 0
_TRIVERTEX_Y = 1
_TRIVERTEX_Z = 2
_TRIVERTEX_LIGHT_NORMAL_INDEX = 3


def _check_mdlfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4s'))

    return data == IDENTITY


def is_mdlfile(filename):
    """Quickly see if a file is a mdl file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_mdlfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_mdlfile(fp)

    except Exception:
        return False


class Header:
    """Class representing a MDL file header"""
    format = '<4si10f8if'
    size = struct.calcsize(format)

    def __init__(self,
                 identity,
                 version,
                 scale_x,
                 scale_y,
                 scale_z,
                 origin_x,
                 origin_y,
                 origin_z,
                 radius,
                 eye_position_x,
                 eye_position_y,
                 eye_position_z,
                 number_of_skins,
                 skin_width,
                 skin_height,
                 number_of_vertexes,
                 number_of_triangles,
                 number_of_frames,
                 sync_type,
                 flags,
                 size
                 ):

        self.identity = identity
        self.version = version
        self.scale = scale_x, scale_y, scale_z
        self.origin = origin_x, origin_y, origin_z
        self.radius = radius
        self.eye_position = eye_position_x, eye_position_y, eye_position_z
        self.number_of_skins = number_of_skins
        self.skin_width = skin_width
        self.skin_height = skin_height
        self.number_of_vertexes = number_of_vertexes
        self.number_of_triangles = number_of_triangles
        self.number_of_frames = number_of_frames
        self.sync_type = sync_type
        self.flags = flags
        self.size = size

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.identity,
            header.version,
            *header.scale,
            *header.origin,
            header.radius,
            *header.eye_position,
            header.number_of_skins,
            header.skin_width,
            header.skin_height,
            header.number_of_vertexes,
            header.number_of_triangles,
            header.number_of_frames,
            header.sync_type,
            header.flags,
            header.size,
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


SINGLE = 0
GROUP = 1


class Skin:
    """Class for representing a skin

    A skin is an indexed image embedded within the model. Models may contain
    more than one skin, and there may be as many skins as are there are
    separate parts in the model.

    Attributes:
        type: The SkinType for the skin. For a Skin object the type must
            be SINGLE

        pixels: A tuple of unstructured indexed pixel data represented as
            integers. A palette must be used to obtain RGB data.
            The size of this tuple is:

            mdl.skin_width * mdl.skin_height.
    """
    format = ''
    size = 0

    __slots__ = (
        'type',
        'pixels'
    )

    def __init__(self, type, *pixels):
        self.type = type
        self.pixels = pixels

    @staticmethod
    def write(file, skin, size):
        #width, height = size
        #skin_format = _calculate_skin_format(size)
        #skin_data = struct.pack(skin_format,
        #                        skin.type,
        #                        *skin.pixels)

        skin_data = struct.pack(
            skin.format,
            skin.type,
            *skin.pixels
        )

        file.write(skin_data)

    @classmethod
    def read(cls, file, size):
        skin_data = file.read(cls.size)
        skin_struct = struct.unpack(cls.format, skin_data)

        return cls(*skin_struct)

    @classmethod
    def create_class(cls, width, height):
        class _Skin(cls):
            format = f'<i{width * height}B'
            size = struct.calcsize(format)

        return _Skin


class SkinGroup:
    """Class for representing a skin group

    A skin group is a sequence of indexed images embedded within the model.

    Attributes:
        type: The SkinType for the skin group. For a SkinGroup the type
            must be GROUP

        number_of_skins: The number of skins contain within this SkinGroup.

        intervals: The time intervals between skin.

        pixels: A tuple of unstructured indexed pixel data represented as
            integers. A palette must be used to obtain RGB data.
            This size of this tuple is:

            mdl.skin_width * mdl.skin_height * number_of_frames
    """

    __slots__ = (
        'type',
        'number_of_skins',
        'intervals',
        'pixels'
    )

    def __init__(self):
        self.type = GROUP
        self.number_of_skins = None
        self.intervals = None
        self.pixels = None

    @staticmethod
    def write(file, skin_group, size):
        group = struct.pack('<l', skin_group.type)
        file.write(group)
        number_of_skins = struct.pack('<l', skin_group.number_of_skins)
        file.write(number_of_skins)
        skin_group_format = _calculate_skin_group_format(skin_group.number_of_skins, size)
        skin_group_data = struct.pack(skin_group_format,
                                      *skin_group.intervals,
                                      *skin_group.pixels)

        file.write(skin_group_data)

    @staticmethod
    def read(file, size):
        skin_group = SkinGroup()
        group = file.read(4)
        group = struct.unpack('<l', group)[0]
        number_of_skins = file.read(4)
        number_of_skins = struct.unpack('<l', number_of_skins)[0]
        skin_group_format = _calculate_skin_group_format(number_of_skins, size)
        skin_group_size = struct.calcsize(skin_group_format)
        data = file.read(skin_group_size)
        skin_group_struct = struct.unpack(skin_group_format, data)

        skin_group.type = group
        skin_group.number_of_skins = number_of_skins
        skin_group.intervals = skin_group_struct[:number_of_skins]
        skin_group.pixels = skin_group_struct[number_of_skins:]

        return skin_group


class StVertex:
    """Class for representing an st vertex

    StVertices are similar to UV coordinates but are expressed in terms of
    surface space and span (0,0) to (texture_width, texture_height).

    Note:
        If an StVertex lies on a seam and belongs to a back facing triangle,
        the s-component must be incremented by half of the skin width.

    Attributes:
        on_seam: Indicates if the StVertex is on a skin boundary. The value
            will be 0 if not on the seam and 0x20 if it does lie on the seam.

        s: The x-coordinate on the skin.

        t: The y-coordinate on the skin.
    """

    __slots__ = (
        'on_seam',
        's',
        't'
    )

    def __init__(self):
        self.on_seam = 0
        self.s = None
        self.t = None

    def __getitem__(self, key):
        if type(key) is int:
            return [self.s, self.t][key]

        elif type(key) is slice:
            start = key.start or 0
            stop = key.stop or 2

            return [self.s, self.t][start:stop]

    def __setitem__(self, key, value):
        if type(key) is int:
            if key == 0:
                self.s = value
            elif key == 1:
                self.t = value
            else:
                raise IndexError('stvertex assignment index out of range')

        elif type(key) is slice:
            start = key.start or 0
            stop = key.stop or 2

            for i in range(start, stop):
                self[i] = value[i]

    @staticmethod
    def write(file, st_vertex):
        st_vertex_data = struct.pack(st_vertex_format,
                                     st_vertex.on_seam,
                                     st_vertex.s,
                                     st_vertex.t)

        file.write(st_vertex_data)

    @staticmethod
    def read(file):
        st_vertex = StVertex()
        st_vertex_data = file.read(st_vertex_size)
        st_vertex_struct = struct.unpack(st_vertex_format, st_vertex_data)

        st_vertex.on_seam = st_vertex_struct[_ST_VERTEX_ON_SEAM]
        st_vertex.s = st_vertex_struct[_ST_VERTEX_S]
        st_vertex.t = st_vertex_struct[_ST_VERTEX_T]

        return st_vertex


class Triangle:
    """Class for representing a triangle

    Note:
        The triangle winding direction is clockwise.

    Attributes:
        faces_front: Indicates if the triangle faces the front of the model, or
            towards the back. The value will be 0 for back-facing and 0x10 for
            front-facing.

        vertices: A triple of vertex indexes. XYZ data can be obtained by
            indexing into the frame.vertices attribute.
    """

    __slots__ = (
        'faces_front',
        'vertices'
    )

    def __init__(self):
        self.faces_front = 0x10
        self.vertices = []

    def __getitem__(self, key):
        return self.vertices[key]

    def __setitem__(self, key, value):
        self.vertices[key] = value

    @staticmethod
    def write(file, triangle):
        triangle_data = struct.pack(triangle_format,
                                    triangle.faces_front,
                                    *triangle.vertices)

        file.write(triangle_data)

    @staticmethod
    def read(file):
        triangle = Triangle()
        triangle_data = file.read(triangle_size)
        triangle_struct = struct.unpack(triangle_format, triangle_data)

        triangle.faces_front = triangle_struct[_TRIANGLE_FACES_FRONT]
        triangle.vertices = triangle_struct[_TRIANGLE_VERTICES:]

        return triangle


class TriVertex:
    """Class for representing a trivertex

    A TriVertex is a set of XYZ coordinates and a light normal index.

    Note:
        The XYZ coordinates are packed into a (0, 0, 0) to (255, 255, 255)
        local space. The actual position can be calculated:

        position = (packed_vertex * mdl.scale) + mdl.offset

    Note:
        The light normal index is an index into a set of pre-calculated normal
        vectors. These can be found in the anorms attribute of the quake
        module.

    Attributes:
        x: The x-coordinate

        y: The y-coordinate

        z: The z-coordinate

        light_normal_index: The index for the pre-calculated normal vector of
            this vertex used for lighting.
    """

    __slots__ = (
        'x',
        'y',
        'z',
        'light_normal_index'
    )

    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.light_normal_index = None

    def __getitem__(self, key):
        if type(key) is int:
            return [self.x, self.y, self.z][key]

        elif type(key) is slice:
            start = key.start or 0
            stop = key.stop or 3

            return [self.x, self.y, self.z][start:stop]

    def __setitem__(self, key, value):
        if type(key) is int:
            if key == 0:
                self.x = value
            elif key == 1:
                self.y = value
            elif key == 2:
                self.z = value
            else:
                raise IndexError('trivertex assignment index out of range')

        elif type(key) is slice:
            start = key.start or 0
            stop = key.stop or 3

            for i in range(start, stop):
                self[i] = value[i]

    @staticmethod
    def write(file, tri_vertex):
        tri_vertex_data = struct.pack(trivertex_format,
                                      tri_vertex.x,
                                      tri_vertex.y,
                                      tri_vertex.z,
                                      tri_vertex.light_normal_index)

        file.write(tri_vertex_data)

    @staticmethod
    def read(file):
        tri_vertex = TriVertex()
        tri_vertex_data = file.read(trivertex_size)
        tri_vertex_struct = struct.unpack(trivertex_format, tri_vertex_data)

        tri_vertex.x = tri_vertex_struct[_TRIVERTEX_X]
        tri_vertex.y = tri_vertex_struct[_TRIVERTEX_Y]
        tri_vertex.z = tri_vertex_struct[_TRIVERTEX_Z]
        tri_vertex.light_normal_index = tri_vertex_struct[_TRIVERTEX_LIGHT_NORMAL_INDEX]

        return tri_vertex


class Frame:
    """Class for representing a frame

    A Frame is a set of vertices that represent the state of the model at
    a single frame of animation.

    Note:
        The TriVertices that describe the bounding box do not use their
        light_normal_index attribute.

    Attributes:
        type: The FrameType of the frame. For a Frame object the type
            must be SINGLE

        bounding_box_min: The minimum coordinate of the bounding box containing
            the vertices in this frame.

        bounding_box_max: The maximum coordinate of the bounding box containing
            all the vertices in this frame.

        name: The name of the frame.

        vertices: A list of TriVertex objects.
    """

    __slots__ = (
        'type',
        'bounding_box_min',
        'bounding_box_max',
        'name',
        'vertices'
    )

    def __init__(self):
        self.type = SINGLE
        self.bounding_box_min = None
        self.bounding_box_max = None
        self.name = None
        self.vertices = []

    @staticmethod
    def write(file, frame, number_of_vertexes):
        TriVertex.write(file, frame.bounding_box_min)
        TriVertex.write(file, frame.bounding_box_max)
        file.write(struct.pack('<16s', frame.name.encode('ascii')))
        for vertex in frame.vertices:
            TriVertex.write(file, vertex)

    @staticmethod
    def read(file, number_of_vertexes):
        frame = Frame()
        frame.bounding_box_min = TriVertex.read(file)
        frame.bounding_box_max = TriVertex.read(file)
        frame.name = struct.unpack('<16s', file.read(struct.calcsize('<16s')))[0].split(b'\00')[0].decode('ascii')
        frame.vertices = [TriVertex.read(file) for _ in range(number_of_vertexes)]

        return frame


class FrameGroup:
    """Class for representing a frame group

    Attributes:
        type: The FrameType of the frame group. For a Frame object the
            type must be GROUP

        bounding_box_min: The minimum coordinate of the bounding box containing
            the vertices of all frames in this group.

        bounding_box_max: The maximum coordinate of the bounding box containing
            the vertices of all the frames in this group.

        number_of_frames: The number of frames in this group.

        intervals: A sequence of timings for each frame.

        frames: A list of Frame objects.
    """

    __slots__ = (
        'type',
        'bounding_box_min',
        'bounding_box_max',
        'number_of_frames',
        'intervals',
        'frames'
    )

    def __init__(self):
        self.type = GROUP
        self.number_of_frames = None
        self.bounding_box_min = None
        self.bounding_box_max = None
        self.intervals = None
        self.frames = None

    @staticmethod
    def write(file, frame_group, number_of_vertexes):
        file.write(struct.pack('<l', frame_group.number_of_frames))
        TriVertex.write(file, frame_group.bounding_box_min)
        TriVertex.write(file, frame_group.bounding_box_max)
        intervals_data = struct.pack('<%if' % frame_group.number_of_frames, *frame_group.intervals)
        file.write(intervals_data)
        for frame in frame_group.frames:
            Frame.write(file, frame, number_of_vertexes)

    @staticmethod
    def read(file, number_of_vertexes):
        frame_group = FrameGroup()
        frame_group.number_of_frames = struct.unpack('<l', file.read(4))[0]
        frame_group.bounding_box_min = TriVertex.read(file)
        frame_group.bounding_box_max = TriVertex.read(file)
        intervals_data = file.read(4 * frame_group.number_of_frames)
        frame_group.intervals = struct.unpack('<%if' % frame_group.number_of_frames, intervals_data)
        frame_group.frames = [Frame.read(file, number_of_vertexes) for _ in range(frame_group.number_of_frames)]

        return frame_group


SYNC = 0
RAND = 1

ROCKET = 1      # leave a trail
GRENADE = 2     # leave a trail
GIB = 4         # leave a trail
ROTATE = 8      # rotate (bonus items)
TRACER = 16     # green split trail
ZOMGIB = 32     # small blood trail
TRACER2 = 64    # orange split trail + rotate
TRACER3 = 128   # purple trail


class Mesh:
    """Class for representing mesh data

    Attributes:
        vertices: A list of vertex data represented as XYZ three-tuples.

        triangles: A list of triangle data represented by a three-tuple of
            vertex indexes.

        uvs: A list of uv coordinates represented as UV tuples.

        normals: A list of vertex normal data represented as XYZ three-tuples.
    """

    __slots = (
        'vertices',
        'triangles',
        'uvs',
        'normals'
    )

    def __init__(self):
        self.vertices = []
        self.triangles = []
        self.uvs = []
        self.normals = []


class Image:
    """Class for representing pixel data

    Attributes:
        width: The width of the image.

        height: The height of the image.

        format: A string describing the format of the color data. Usually 'RGB'
            or 'RGBA'

        pixels: The raw pixel data of the image.
            The length of this attribute is:

            width * height * len(format)
    """

    __slots__ = (
        'width',
        'height',
        'format',
        'pixels'
    )

    def __init__(self):
        self.width = 0
        self.height = 0
        self.format = 'RGBA'
        self.pixels = None


class Mdl(ReadWriteFile):
    """Class for working with Mdl files

    Example:
        m = Mdl.open(file)

    Attributes:
        identity: The magic number of the model, must be IDENTITY

        version: The version of the model, should be 6.

        scale: The scale of the model. Used to correctly resize the model as
            the frame vertices are packed into a (0, 0, 0) to (255, 255, 255)
            local space.

        origin: The offset of the model. Used to correctly position the model.

            Note: The frame vertices are packed into a (0, 0, 0) to
            (255, 255, 255) local space.

        bounding_radius: The bounding radius of the model.

        eye_position: The eye position for the model.

        number_of_skins: The number of skins contained inside the model.

        skin_width: The pixel width of the skin texture.

        skin_height: The pixel height of the skin texture.

        number_of_vertexes: The number of vertices for the model.

        number_of_triangles: The number of triangles for the model.

        number_of_frames: The number of frames for the model.

        sync_type: The synchronization type for the model. It is either
            SYNC or RAND.

        flags: A bit field of entity effects.

        size: The average size of the triangles.


        skins: The list of Skin or SkinGroup objects. Use the type
            attribute to identify the object. The type is either
            SINGLE or GROUP.

        st_vertices: The list of StVertex objects.

        triangles: The list of Triangle objects.

        frames: The list of Frame or FrameGroup objects. Use the type
            attribute to identify the object. The type is either
            SINGLE or GROUP.


        fp: The file-like object to read data from.

        mode: The file mode for the file-like object.
    """

    def __init__(self):
        super().__init__()

        self.identity = IDENTITY
        self.version = VERSION
        self.scale = 1, 1, 1
        self.origin = 0, 0, 0
        self.bounding_radius = 0
        self.eye_position = 0, 0, 0
        self.number_of_skins = 0
        self.skin_width = 0
        self.skin_height = 0
        self.number_of_vertexes = 0
        self.number_of_triangles = 0
        self.number_of_frames = 0
        self.sync_type = SYNC
        self.flags = 0
        self.size = 0

        self.skins = []
        self.st_vertices = []
        self.triangles = []
        self.frames = []

        self.factory = SimpleNamespace(
            Header=Header,
            Skin=Skin,
            SkinGroup=SkinGroup,
            StVertex=StVertex,
            Triangle=Triangle,
            TriVertex=TriVertex,
            Frame=Frame,
            FrameGroup=FrameGroup
        )

    @staticmethod
    def _read_file(file, mode):
        mdl = Mdl()
        mdl.fp = file
        mdl.mode = mode

        factory = mdl.factory

        header = factory.Header.read(file)

        if header.identity != IDENTITY:
            raise BadMdlFile(f'Bad magic number: {header.identity}')

        if header.version != VERSION:
            raise BadMdlFile(f'Bad version number: {header.version}')

        factory.Skin = Skin.create_class(header.skin_width, header.skin_height)

        mdl.identity = header.identity
        mdl.version = header.version
        mdl.scale = header.scale
        mdl.origin = header.origin
        mdl.bounding_radius = header.radius
        mdl.eye_position = header.eye_position
        mdl.number_of_skins = header.number_of_skins
        mdl.skin_width = header.skin_width
        mdl.skin_height = header.skin_height
        mdl.number_of_vertexes = header.number_of_vertexes
        mdl.number_of_triangles = header.number_of_triangles
        mdl.number_of_frames = header.number_of_frames
        mdl.sync_type = header.sync_type
        mdl.flags = header.flags
        mdl.size = header.size

        mdl.skins = []
        mdl.st_vertices = []
        mdl.triangles = []
        mdl.frames = []

        # Skins
        for _ in range(mdl.number_of_skins):
            pos = file.tell()
            group = struct.unpack('<i', file.read(4))[0]
            file.seek(pos)

            if group == 0:
                skin = factory.Skin.read(file, (mdl.skin_width, mdl.skin_height))
                mdl.skins.append(skin)

            else:
                skin_group = factory.SkinGroup.read(file, (mdl.skin_width, mdl.skin_height))
                mdl.skins.append(skin_group)

        # St Vertexes
        for _ in range(mdl.number_of_vertexes):
            mdl.st_vertices.append(mdl.factory.StVertex.read(file))

        # Triangles
        for _ in range(mdl.number_of_triangles):
            mdl.triangles.append(mdl.factory.Triangle.read(file))

        # Frames
        for _ in range(mdl.number_of_frames):
            frame_type = struct.unpack('<i', file.read(4))[0]

            if frame_type == SINGLE:
                mdl.frames.append(factory.Frame.read(file, mdl.number_of_vertexes))

            else:
                mdl.frames.append(factory.FrameGroup.read(file, mdl.number_of_vertexes))

        return mdl

    @staticmethod
    def _write_file(file, mdl):
        # Validate mdl data
        mdl.validate()

        # Header
        header = Header(
            mdl.identity,
            mdl.version,
            *mdl.scale,
            *mdl.origin,
            mdl.bounding_radius,
            *mdl.eye_position,
            mdl.number_of_skins,
            mdl.skin_width,
            mdl.skin_height,
            mdl.number_of_vertexes,
            mdl.number_of_triangles,
            mdl.number_of_frames,
            mdl.synctype,
            mdl.flags,
            mdl.size
        )

        Header.write(file, header)

        # Skins
        for skin in mdl.skins:
            if skin.type == SINGLE:
                mdl.factory.Skin.write(file, skin, (mdl.skin_width, mdl.skin_height))

            else:
                mdl.factory.SkinGroup.write(file, skin, (mdl.skin_width, mdl.skin_height))

        # St Vertexes
        for st_vertex in mdl.st_vertices:
            mdl.factory.StVertex.write(file, st_vertex)

        # Triangles
        for triangle in mdl.triangles:
            mdl.factory.Triangle.write(file, triangle)

        # Frames
        for frame in mdl.frames:
            if frame.type == SINGLE:
                file.write(struct.pack('<l', SINGLE))
                mdl.factory.Frame.write(file, frame, mdl.number_of_vertexes)

            else:
                file.write(struct.pack('<l', GROUP))
                mdl.factory.FrameGroup.write(file, frame, mdl.number_of_vertexes)

    @property
    def identifier(self):
        return self.identity

    @property
    def number_of_vertices(self):
        return self.number_of_vertexes

    @property
    def synctype(self):
        return self.sync_type

    def validate(self):
        """Verifies correctness of Mdl data.

        Raises:
            BadMdlFile: If a discrepancy is found.
        """

        if self.identity != IDENTITY:
            raise BadMdlFile('Bad magic number: %r' % self.identity)

        if self.version != VERSION:
            raise BadMdlFile('Bad version number: %r' % self.version)

        if self.number_of_triangles != len(self.triangles):
            raise BadMdlFile('Incorrect number of triangles. Expected: %r Actual: %r' % (self.number_of_triangles, len(self.triangles)))

        for triangle in self.triangles:
            for vertex in triangle.vertices:
                if vertex < 0 or vertex > self.number_of_vertexes:
                    raise BadMdlFile('Bad vertex index: %r' % vertex)

        if self.number_of_skins != len(self.skins):
            raise BadMdlFile('Incorrect number of skins. Expected: %r Actual: %r' % (self.number_of_skins, len(self.skins)))

        for skin in self.skins:
            if skin.type == SINGLE and len(skin.pixels) != self.skin_width * self.skin_height:
                raise BadMdlFile('Incorrect number of pixels. Expected: %r Actual: %r' % (self.skin_width * self.skin_height, len(skin.pixels)))

            elif skin.type == GROUP and len(skin.pixels) != self.skin_width * self.skin_height * skin.number_of_skins:
                raise BadMdlFile('Incorrect number of pixels. Expected: %r Actual: %r' % (self.skin_width * self.skin_height * skin.number_of_skins, len(skin.pixels)))

        if self.number_of_vertexes != len(self.st_vertices):
            raise BadMdlFile('Incorrect number of st vertices. Expected: %r Actual: %r' % (self.number_of_vertexes, len(self.st_vertices)))

        if self.number_of_frames != len(self.frames):
            raise BadMdlFile('Incorrect number of frames. Expected: %r Actual: %r' % (self.number_of_frames, len(self.frames)))

        for frame in self.frames:
            if frame.type == SINGLE and len(frame.vertices) != self.number_of_vertexes:
                raise BadMdlFile('Incorrect number of vertices. Expected: %r Actual: %r' % (self.number_of_vertexes, len(frame.vertices)))

            elif frame.type == GROUP:
                for sub_frame in frame.frames:
                    if len(sub_frame.vertices) != self.number_of_vertexes:
                        raise BadMdlFile('Incorrect number of vertices. Expected: %r Actual: %r' % (self.number_of_vertexes, len(sub_frame.vertices)))

    def mesh(self, frame=0, subframe=0):
        """Returns a Mesh object

        Args:
            frame: The index of the frame to get mesh data for.

            subframe: If the frame is a FrameGroup, a subframe index is needed
                to get the mesh data.

        Returns:
            A Mesh object
        """

        mesh = Mesh()

        frame = self.frames[frame]

        if frame.type == SINGLE:
            mesh.vertices = [(v.x, v.y, v.z) for v in frame.vertices]
            mesh.normals = [quake.anorms[v.light_normal_index] for v in frame.vertices]
        else:
            mesh.vertices = [(v.x, v.y, v.z) for v in frame.frames[subframe].vertices]
            mesh.normals = [quake.anorms[v.light_normal_index] for v in frame.frames[subframe].vertices]

        triangles = self.triangles[:]

        mesh.uvs = [None for _ in range(len(mesh.vertices))]

        for tri_index, triangle in enumerate(triangles):
            temp_triangle = Triangle()
            temp_triangle.faces_front = triangle.faces_front
            temp_triangle.vertices = triangle.vertices
            for vert_index, vertex in enumerate(temp_triangle.vertices):
                st_vertex = self.st_vertices[vertex]
                s, t = st_vertex

                if st_vertex.on_seam and not temp_triangle.faces_front:
                    s += self.skin_width / 2

                uv_coord = s / self.skin_width, 1 - t / self.skin_height

                if not mesh.uvs[vertex]:
                    mesh.uvs[vertex] = uv_coord

                elif mesh.uvs[vertex] != uv_coord:
                    # Duplicate this vertex to accommodate new uv coordinate
                    duplicated_vertex = mesh.vertices[vertex]
                    mesh.vertices.append(duplicated_vertex)
                    duplicated_vertex_index = len(mesh.vertices) - 1

                    duplicated_normal = mesh.normals[vertex]
                    mesh.normals.append(duplicated_normal)

                    temp_triangle.vertices = list(temp_triangle.vertices)
                    temp_triangle.vertices[vert_index] = duplicated_vertex_index
                    temp_triangle.vertices = tuple(temp_triangle.vertices)

                    mesh.uvs.append(uv_coord)

            mesh.triangles.append(tuple(reversed(temp_triangle.vertices)))

        return mesh

    def image(self, index=0, palette=quake.palette):
        """Returns an Image object.

        Args:
            index: The index of the skin to get image data for.

            palette: A 256 color palette to use for converted index color data to
                RGB data.

        Returns:
            An Image object.
        """

        if index > len(self.skins):
            raise IndexError('list index out of range')

        image = Image()
        image.width = self.skin_width
        image.height = self.skin_height
        image.pixels = self.skins[index].pixels

        p = []
        for row in reversed(range(image.height)):
            p += image.pixels[row * image.width:(row + 1) * image.width]

        d = []

        for i in p:
            d += palette[i]
            d += [255] if i != 255 else [0]

        image.pixels = d

        return image
