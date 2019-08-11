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

from vgio._core import ReadWriteFile
from vgio import quake

__all__ = ['BadMdlFile', 'is_mdlfile', 'Mdl']


VERSION = 6
IDENTITY = b'IDPO'


class BadMdlFile(Exception):
    pass


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
    format = '<4si10f8if'
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'version',
        'scale',
        'origin',
        'radius',
        'offsets',
        'number_of_skins',
        'skin_width',
        'skin_height',
        'number_of_vertexes',
        'number_of_triangles',
        'number_of_frames',
        'sync_type',
        'flags',
        'size_'
    )

    def __init__(self,
                 identity,
                 version,
                 scale_0,
                 scale_1,
                 scale_2,
                 origin_0,
                 origin_1,
                 origin_2,
                 radius,
                 offsets_0,
                 offsets_1,
                 offsets_2,
                 number_of_skins,
                 skin_width,
                 skin_height,
                 number_of_vertexes,
                 number_of_triangles,
                 number_of_frames,
                 sync_type,
                 flags,
                 size):
        self.identity = identity
        self.version = version
        self.scale = scale_0, scale_1, scale_2
        self.origin = origin_0, origin_1, origin_2
        self.radius = radius
        self.offsets = offsets_0, offsets_1, offsets_2
        self.number_of_skins = number_of_skins
        self.skin_width = skin_width
        self.skin_height = skin_height
        self.number_of_vertexes = number_of_vertexes
        self.number_of_triangles = number_of_triangles
        self.number_of_frames = number_of_frames
        self.sync_type = sync_type
        self.flags = flags
        self.size_ = size

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.identity,
            header.version,
            *header.scale,
            *header.origin,
            header.radius,
            *header.offsets,
            header.number_of_skins,
            header.skin_width,
            header.skin_height,
            header.number_of_vertexes,
            header.number_of_triangles,
            header.number_of_frames,
            header.sync_type,
            header.flags,
            header.size_
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

    __slots__ = (
        'type',
        'pixels'
    )

    def __init__(self):
        self.type = SINGLE
        self.pixels = None

    @staticmethod
    def write(file, skin, size):
        skin_format = _calculate_skin_format(size)
        skin_data = struct.pack(
            skin_format,
            skin.type,
            *skin.pixels
        )

        file.write(skin_data)

    @staticmethod
    def read(file, size):
        skin = Skin()
        skin_format = _calculate_skin_format(size)
        skin_size = struct.calcsize(skin_format)
        skin_data = file.read(skin_size)
        skin_struct = struct.unpack(skin_format, skin_data)

        skin.type = skin_struct[_SKIN_TYPE]
        skin.pixels = skin_struct[_SKIN_PIXELS:]

        return skin


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
        skin_group_data = struct.pack(
            skin_group_format,
            *skin_group.intervals,
            *skin_group.pixels
        )

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
        on_seam:  Indicates if the StVertex is on a skin boundary. The value
            will be 0 if not on the seam and 0x20 if it does lie on the seam.

        s:  The s-coordinate on the skin.

        t:  The t-coordinate on the skin.
    """

    format = '<3i'
    size = struct.calcsize(format)

    __slots__ = (
        'on_seam',
        's',
        't'
    )

    def __init__(self,
                 on_seam,
                 s,
                 t):
        self.on_seam = on_seam
        self.s = s
        self.t = t

    @classmethod
    def write(cls, file, stvertex):
        stvertex_data = struct.pack(
            cls.format,
            stvertex.on_seam,
            stvertex.s,
            stvertex.t
        )

        file.write(stvertex_data)

    @classmethod
    def read(cls, file):
        stvertex_data = file.read(cls.size)
        stvertex_struct = struct.unpack(cls.format, stvertex_data)

        return StVertex(*stvertex_struct)

    def __getitem__(self, key):
        return (self.s, self.t)[key]

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


class Triangle:
    """Class for representing a triangle

    Note:
        The triangle winding direction is clockwise.


    Attributes:
        faces_front: Indicates if the triangle faces the front of the model, or
            towards the back. The value will be 0 for back-facing and 0x10 for
            front-facing.

        vertexes:  A triple of vertex indices.
    """

    format = '<4i'
    size = struct.calcsize(format)

    __slots__ = (
        'faces_front',
        'vertexes'
    )

    def __init__(self,
                 faces_front,
                 vertexes_0,
                 vertexes_1,
                 vertexes_2):
        self.faces_front = faces_front
        self.vertexes = [vertexes_0, vertexes_1, vertexes_2]

    def __getitem__(self, key):
        return self.vertexes[key]

    def __setitem__(self, key, value):
        self.vertexes[key] = value

    @classmethod
    def write(cls, file, triangle):
        triangle_data = struct.pack(
            cls.format,
            triangle.faces_front,
            *triangle.vertexes
        )

        file.write(triangle_data)

    @classmethod
    def read(cls, file):
        triangle_data = file.read(cls.size)
        triangle_struct = struct.unpack(cls.format, triangle_data)

        return Triangle(*triangle_struct)


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
        x:  The x-coordinate.

        y:  The y-coordinate.

        z:  The z-coordinate.

        light_normal_index:  The index for the pre-calculated normal vector of
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

    @classmethod
    def write(cls, file, trivertex):
        trivertex_data = struct.pack(
            cls.format,
            trivertex.x,
            trivertex.y,
            trivertex.z,
            trivertex.light_normal_index
        )

        file.write(trivertex_data)

    @classmethod
    def read(cls, file):
        trivertex_data = file.read(cls.size)
        trivertex_struct = struct.unpack(cls.format, trivertex_data)

        return TriVertex(*trivertex_struct)

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
                raise IndexError('trivertex assignment index out of range')

        elif type(key) is slice:
            start = key.start or 0
            stop = key.stop or 3

            for i in range(start, stop):
                self[i] = value[i]


class Frame:
    """Class for representing a frame

    A Frame is a set of vertexes that represent the state of the model at
    a single frame of animation.

    Note:
        The TriVertices that describe the bounding box do not use their
        light_normal_index attribute.

    Attributes:
        type: The FrameType of the frame. For a Frame object the type
            must be SINGLE

        bounding_box_min: The minimum coordinate of the bounding box containing
            the vertexes in this frame.

        bounding_box_max: The maximum coordinate of the bounding box containing
            all the vertexes in this frame.

        name: The name of the frame.

        vertexes: A list of TriVertex objects.
    """

    __slots__ = (
        'type',
        'bounding_box_min',
        'bounding_box_max',
        'name',
        'vertexes'
    )

    def __init__(self):
        self.type = SINGLE
        self.bounding_box_min = None
        self.bounding_box_max = None
        self.name = None
        self.vertexes = []

    @staticmethod
    def write(file, frame, number_of_vertexes):
        TriVertex.write(file, frame.bounding_box_min)
        TriVertex.write(file, frame.bounding_box_max)
        file.write(struct.pack('<16s', frame.name.encode('ascii')))
        for vertex in frame.vertexes:
            TriVertex.write(file, vertex)

    @staticmethod
    def read(file, number_of_vertexes):
        frame = Frame()
        frame.bounding_box_min = TriVertex.read(file)
        frame.bounding_box_max = TriVertex.read(file)
        frame.name = struct.unpack('<16s', file.read(struct.calcsize('<16s')))[0].split(b'\00')[0].decode('ascii')
        frame.vertexes = [TriVertex.read(file) for _ in range(number_of_vertexes)]

        return frame


class FrameGroup:
    """Class for representing a frame group

    Attributes:
        type: The FrameType of the frame group. For a Frame object the
            type must be GROUP

        bounding_box_min: The minimum coordinate of the bounding box containing
            the vertexes of all frames in this group.

        bounding_box_max: The maximum coordinate of the bounding box containing
            the vertexes of all the frames in this group.

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
        vertexes: A list of vertex data represented as XYZ three-tuples.

        triangles: A list of triangle data represented by a three-tuple of
            vertex indexes.

        uvs: A list of uv coordinates represented as UV tuples.

        normals: A list of vertex normal data represented as XYZ three-tuples.
    """

    __slots = (
        'vertexes',
        'triangles',
        'uvs',
        'normals'
    )

    def __init__(self):
        self.vertexes = []
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
        identifier: The magic number of the model, must be b'IDPO'

        version: The version of the model, should be 6.

        scale: The scale of the model. Used to correctly resize the model as
            the frame vertexes are packed into a (0, 0, 0) to (255, 255, 255)
            local space.

        origin: The offset of the model. Used to correctly position the model.

            Note: The frame vertexes are packed into a (0, 0, 0) to
            (255, 255, 255) local space.

        bounding_radius: The bounding radius of the model.

        eye_position: The eye position for the model.

        number_of_skins: The number of skins contained inside the model.

        skin_width: The pixel width of the skin texture.

        skin_height: The pixel height of the skin texture.

        number_of_vertexes: The number of vertexes for the model.

        number_of_triangles: The number of triangles for the model.

        number_of_frames: The number of frames for the model.

        synctype: The synchronization type for the model. It is either
            SYNC or RAND.

        flags: A bit field of entity effects.

        size: The average size of the triangles.

        skins: The list of Skin or SkinGroup objects. Use the type
            attribute to identify the object. The type is either
            SINGLE or GROUP.

        st_vertexes: The list of StVertex objects.

        triangles: The list of Triangle objects.

        frames: The list of Frame or FrameGroup objects. Use the type
            attribute to identify the object. The type is either
            SINGLE or GROUP.


        fp: The file-like object to read data from.

        mode: The file mode for the file-like object.
    """
    class factory:
        Header = Header
        Skin = Skin
        SkinGroup = SkinGroup
        StVertex = StVertex
        Triangle = Triangle
        TriVertex = TriVertex
        Frame = Frame
        FrameGroup = FrameGroup

    def __init__(self):
        super().__init__()

        self.identifier = IDENTITY
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
        self.synctype = SYNC
        self.flags = 0
        self.size = 0

        self.skins = []
        self.st_vertexes = []
        self.triangles = []
        self.frames = []

    @classmethod
    def _read_file(cls, file, mode):
        mdl = cls()
        mdl.mode = mode
        mdl.fp = file

        # Header
        header = cls.factory.Header.read(file)

        if header.identity != IDENTITY:
            raise BadMdlFile(f'Bad magic number: {header.identity}')

        if header.version != VERSION:
            raise BadMdlFile(f'Bad version number: {header.version}')

        mdl.identifier = header.identity
        mdl.version = header.version
        mdl.scale = header.scale
        mdl.origin = header.origin
        mdl.bounding_radius = header.radius
        mdl.eye_position = header.offsets
        mdl.number_of_skins = header.number_of_skins
        mdl.skin_width = header.skin_width
        mdl.skin_height = header.skin_height
        mdl.number_of_vertexes = header.number_of_vertexes
        mdl.number_of_triangles = header.number_of_triangles
        mdl.number_of_frames = header.number_of_frames
        mdl.synctype = header.sync_type
        mdl.flags = header.flags
        mdl.size = header.size_

        # Skins
        for _ in range(mdl.number_of_skins):
            pos = file.tell()
            group = struct.unpack('<i', file.read(4))[0]
            file.seek(pos)

            class_ = (cls.factory.Skin, cls.factory.SkinGroup)[group]
            skin = class_.read(file, (mdl.skin_width, mdl.skin_height))
            mdl.skins.append(skin)

        # St Vertexes
        for _ in range(mdl.number_of_vertexes):
            mdl.st_vertexes.append(cls.factory.StVertex.read(file))

        # Triangles
        for _ in range(mdl.number_of_triangles):
            mdl.triangles.append(cls.factory.Triangle.read(file))

        # Frames
        for _ in range(mdl.number_of_frames):
            frame_type = struct.unpack('<i', file.read(4))[0]
            class_ = (cls.factory.Frame, cls.factory.FrameGroup)[frame_type]
            frame = class_.read(file, mdl.number_of_vertexes)
            mdl.frames.append(frame)

        return mdl

    @classmethod
    def _write_file(cls, file, mdl):
        # Validate mdl data
        mdl.validate()

        # Header
        header = cls.factory.Header(
            mdl.identifier,
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

        cls.factory.Header.write(file, header)

        # Skins
        for skin in mdl.skins:
            class_ = (cls.factory.Skin, cls.factory.SkinGroup)[skin.type]
            class_.write(file, skin, (mdl.skin_width, mdl.skin_height))

        # St Vertexes
        for st_vertex in mdl.st_vertexes:
            cls.factory.StVertex.write(file, st_vertex)

        # Triangles
        for triangle in mdl.triangles:
            cls.factory.Triangle.write(file, triangle)

        # Frames
        for frame in mdl.frames:
            class_ = (cls.factory.Frame, cls.factory.FrameGroup)[frame.type]
            file.write(struct.pack('<l', frame.type))
            class_.write(file, frame, mdl.number_of_vertexes)

    def validate(self):
        """Verifies correctness of Mdl data.

        Raises:
            BadMdlFile: If a discrepancy is found.
        """

        if self.identifier != IDENTITY:
            raise BadMdlFile('Bad magic number: %r' % self.identifier)

        if self.version != VERSION:
            raise BadMdlFile('Bad version number: %r' % self.version)

        if self.number_of_triangles != len(self.triangles):
            raise BadMdlFile('Incorrect number of triangles. Expected: %r Actual: %r' % (self.number_of_triangles, len(self.triangles)))

        for triangle in self.triangles:
            for vertex in triangle.vertexes:
                if vertex < 0 or vertex > self.number_of_vertexes:
                    raise BadMdlFile('Bad vertex index: %r' % vertex)

        if self.number_of_skins != len(self.skins):
            raise BadMdlFile('Incorrect number of skins. Expected: %r Actual: %r' % (self.number_of_skins, len(self.skins)))

        for skin in self.skins:
            if skin.type == SINGLE and len(skin.pixels) != self.skin_width * self.skin_height:
                raise BadMdlFile('Incorrect number of pixels. Expected: %r Actual: %r' % (self.skin_width * self.skin_height, len(skin.pixels)))

            elif skin.type == GROUP and len(skin.pixels) != self.skin_width * self.skin_height * skin.number_of_skins:
                raise BadMdlFile('Incorrect number of pixels. Expected: %r Actual: %r' % (self.skin_width * self.skin_height * skin.number_of_skins, len(skin.pixels)))

        if self.number_of_vertexes != len(self.st_vertexes):
            raise BadMdlFile('Incorrect number of st vertexes. Expected: %r Actual: %r' % (self.number_of_vertexes, len(self.st_vertexes)))

        if self.number_of_frames != len(self.frames):
            raise BadMdlFile('Incorrect number of frames. Expected: %r Actual: %r' % (self.number_of_frames, len(self.frames)))

        for frame in self.frames:
            if frame.type == SINGLE and len(frame.vertexes) != self.number_of_vertexes:
                raise BadMdlFile('Incorrect number of vertexes. Expected: %r Actual: %r' % (self.number_of_vertexes, len(frame.vertexes)))

            elif frame.type == GROUP:
                for sub_frame in frame.frames:
                    if len(sub_frame.vertexes) != self.number_of_vertexes:
                        raise BadMdlFile('Incorrect number of vertexes. Expected: %r Actual: %r' % (self.number_of_vertexes, len(sub_frame.vertexes)))


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
            mesh.vertexes = [(v.x, v.y, v.z) for v in frame.vertexes]
            mesh.normals = [quake.anorms[v.light_normal_index] for v in frame.vertexes]
        else:
            mesh.vertexes = [(v.x, v.y, v.z) for v in frame.frames[subframe].vertexes]
            mesh.normals = [quake.anorms[v.light_normal_index] for v in frame.frames[subframe].vertexes]

        triangles = self.triangles[:]

        mesh.uvs = [None for _ in range(len(mesh.vertexes))]

        for tri_index, triangle in enumerate(triangles):
            temp_triangle = Triangle(triangle.faces_front, *triangle.vertexes)
            for vert_index, vertex in enumerate(temp_triangle.vertexes):
                st_vertex = self.st_vertexes[vertex]
                s, t = st_vertex

                if st_vertex.on_seam and not temp_triangle.faces_front:
                    s += self.skin_width / 2

                uv_coord = s / self.skin_width, 1 - t / self.skin_height

                if not mesh.uvs[vertex]:
                    mesh.uvs[vertex] = uv_coord

                elif mesh.uvs[vertex] != uv_coord:
                    # Duplicate this vertex to accommodate new uv coordinate
                    duplicated_vertex = mesh.vertexes[vertex]
                    mesh.vertexes.append(duplicated_vertex)
                    duplicated_vertex_index = len(mesh.vertexes) - 1

                    duplicated_normal = mesh.normals[vertex]
                    mesh.normals.append(duplicated_normal)

                    temp_triangle.vertexes = list(temp_triangle.vertexes)
                    temp_triangle.vertexes[vert_index] = duplicated_vertex_index
                    temp_triangle.vertexes = tuple(temp_triangle.vertexes)

                    mesh.uvs.append(uv_coord)

            mesh.triangles.append(tuple(reversed(temp_triangle.vertexes)))

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
