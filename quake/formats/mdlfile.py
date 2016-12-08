"""Module for working with id Software style MDL files

Supported games:
    - QUAKE
"""

import io
import struct

__all__ = ['BadMdlFile', 'is_mdlfile', 'MdlFile']


class BadMdlFile(Exception):
    pass


# The mdl header structure
header_format = '<4sl10f8lf'
header_magic_number = b'IDPO'
header_size = struct.calcsize(header_format)

# Indexes of the header structure
_HEADER_SIGNATURE = 0
_HEADER_VERSION = 1
_HEADER_SCALE = 2#slice(2,5)
_HEADER_ORIGIN = 5#slice(5,8)
_HEADER_RADIUS = 8
_HEADER_OFFSETS = 9#slice(9,12) 9:12
_HEADER_NUMSKINS = 12
_HEADER_SKINWIDTH = 13
_HEADER_SKINHEIGHT = 14
_HEADER_NUMVERTS = 15
_HEADER_NUMTRIS = 16
_HEADER_NUMFRAMES = 17
_HEADER_SYNCTYPE = 18
_HEADER_FLAGS = 19
_HEADER_SIZE = 20

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

def calculate_frame_format(numverts):
    return '<4B4B16s%iB' % (numverts * 4)

frame_format = None
frame_size = None

_FRAME_MIN = 0
_FRAME_MAX = 4
_FRAME_NAME = 8
_FRAME_VERTS = 9

def calculate_framegroup_format(numverts, numframes):
    fs = calculate_frame_format(numverts).lstrip('<')
    return '<8B%if%s' % (numframes, fs * numframes)

framegroup_format = None
framegroup_size = None

_FRAMEGROUP_NUMBER_OF_FRAMES = 0
_FRAMEGROUP_MIN = 1
_FRAMEGROUP_MAX = 2
_FRAMEGROUP_INTERVALS = 3
_FRAMEGROUP_FRAMES = 4


def _check_mdlfile(fp):
    fp.seek(0)
    data = fp.read(header_size)

    return data == header_magic_number


def is_mdlfile(filename):
    """Quickly see if a file is a mdl file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    result = False

    try:
        if hasattr(filename, 'read'):
            return _check_mdlfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_mdlfile(fp)

    except:
        pass

    return result


default_palette = (
    (0x00,0x00,0x00),(0x0f,0x0f,0x0f),(0x1f,0x1f,0x1f),(0x2f,0x2f,0x2f),
    (0x3f,0x3f,0x3f),(0x4b,0x4b,0x4b),(0x5b,0x5b,0x5b),(0x6b,0x6b,0x6b),
    (0x7b,0x7b,0x7b),(0x8b,0x8b,0x8b),(0x9b,0x9b,0x9b),(0xab,0xab,0xab),
    (0xbb,0xbb,0xbb),(0xcb,0xcb,0xcb),(0xdb,0xdb,0xdb),(0xeb,0xeb,0xeb),
    (0x0f,0x0b,0x07),(0x17,0x0f,0x0b),(0x1f,0x17,0x0b),(0x27,0x1b,0x0f),
    (0x2f,0x23,0x13),(0x37,0x2b,0x17),(0x3f,0x2f,0x17),(0x4b,0x37,0x1b),
    (0x53,0x3b,0x1b),(0x5b,0x43,0x1f),(0x63,0x4b,0x1f),(0x6b,0x53,0x1f),
    (0x73,0x57,0x1f),(0x7b,0x5f,0x23),(0x83,0x67,0x23),(0x8f,0x6f,0x23),
    (0x0b,0x0b,0x0f),(0x13,0x13,0x1b),(0x1b,0x1b,0x27),(0x27,0x27,0x33),
    (0x2f,0x2f,0x3f),(0x37,0x37,0x4b),(0x3f,0x3f,0x57),(0x47,0x47,0x67),
    (0x4f,0x4f,0x73),(0x5b,0x5b,0x7f),(0x63,0x63,0x8b),(0x6b,0x6b,0x97),
    (0x73,0x73,0xa3),(0x7b,0x7b,0xaf),(0x83,0x83,0xbb),(0x8b,0x8b,0xcb),
    (0x00,0x00,0x00),(0x07,0x07,0x00),(0x0b,0x0b,0x00),(0x13,0x13,0x00),
    (0x1b,0x1b,0x00),(0x23,0x23,0x00),(0x2b,0x2b,0x07),(0x2f,0x2f,0x07),
    (0x37,0x37,0x07),(0x3f,0x3f,0x07),(0x47,0x47,0x07),(0x4b,0x4b,0x0b),
    (0x53,0x53,0x0b),(0x5b,0x5b,0x0b),(0x63,0x63,0x0b),(0x6b,0x6b,0x0f),
    (0x07,0x00,0x00),(0x0f,0x00,0x00),(0x17,0x00,0x00),(0x1f,0x00,0x00),
    (0x27,0x00,0x00),(0x2f,0x00,0x00),(0x37,0x00,0x00),(0x3f,0x00,0x00),
    (0x47,0x00,0x00),(0x4f,0x00,0x00),(0x57,0x00,0x00),(0x5f,0x00,0x00),
    (0x67,0x00,0x00),(0x6f,0x00,0x00),(0x77,0x00,0x00),(0x7f,0x00,0x00),
    (0x13,0x13,0x00),(0x1b,0x1b,0x00),(0x23,0x23,0x00),(0x2f,0x2b,0x00),
    (0x37,0x2f,0x00),(0x43,0x37,0x00),(0x4b,0x3b,0x07),(0x57,0x43,0x07),
    (0x5f,0x47,0x07),(0x6b,0x4b,0x0b),(0x77,0x53,0x0f),(0x83,0x57,0x13),
    (0x8b,0x5b,0x13),(0x97,0x5f,0x1b),(0xa3,0x63,0x1f),(0xaf,0x67,0x23),
    (0x23,0x13,0x07),(0x2f,0x17,0x0b),(0x3b,0x1f,0x0f),(0x4b,0x23,0x13),
    (0x57,0x2b,0x17),(0x63,0x2f,0x1f),(0x73,0x37,0x23),(0x7f,0x3b,0x2b),
    (0x8f,0x43,0x33),(0x9f,0x4f,0x33),(0xaf,0x63,0x2f),(0xbf,0x77,0x2f),
    (0xcf,0x8f,0x2b),(0xdf,0xab,0x27),(0xef,0xcb,0x1f),(0xff,0xf3,0x1b),
    (0x0b,0x07,0x00),(0x1b,0x13,0x00),(0x2b,0x23,0x0f),(0x37,0x2b,0x13),
    (0x47,0x33,0x1b),(0x53,0x37,0x23),(0x63,0x3f,0x2b),(0x6f,0x47,0x33),
    (0x7f,0x53,0x3f),(0x8b,0x5f,0x47),(0x9b,0x6b,0x53),(0xa7,0x7b,0x5f),
    (0xb7,0x87,0x6b),(0xc3,0x93,0x7b),(0xd3,0xa3,0x8b),(0xe3,0xb3,0x97),
    (0xab,0x8b,0xa3),(0x9f,0x7f,0x97),(0x93,0x73,0x87),(0x8b,0x67,0x7b),
    (0x7f,0x5b,0x6f),(0x77,0x53,0x63),(0x6b,0x4b,0x57),(0x5f,0x3f,0x4b),
    (0x57,0x37,0x43),(0x4b,0x2f,0x37),(0x43,0x27,0x2f),(0x37,0x1f,0x23),
    (0x2b,0x17,0x1b),(0x23,0x13,0x13),(0x17,0x0b,0x0b),(0x0f,0x07,0x07),
    (0xbb,0x73,0x9f),(0xaf,0x6b,0x8f),(0xa3,0x5f,0x83),(0x97,0x57,0x77),
    (0x8b,0x4f,0x6b),(0x7f,0x4b,0x5f),(0x73,0x43,0x53),(0x6b,0x3b,0x4b),
    (0x5f,0x33,0x3f),(0x53,0x2b,0x37),(0x47,0x23,0x2b),(0x3b,0x1f,0x23),
    (0x2f,0x17,0x1b),(0x23,0x13,0x13),(0x17,0x0b,0x0b),(0x0f,0x07,0x07),
    (0xdb,0xc3,0xbb),(0xcb,0xb3,0xa7),(0xbf,0xa3,0x9b),(0xaf,0x97,0x8b),
    (0xa3,0x87,0x7b),(0x97,0x7b,0x6f),(0x87,0x6f,0x5f),(0x7b,0x63,0x53),
    (0x6b,0x57,0x47),(0x5f,0x4b,0x3b),(0x53,0x3f,0x33),(0x43,0x33,0x27),
    (0x37,0x2b,0x1f),(0x27,0x1f,0x17),(0x1b,0x13,0x0f),(0x0f,0x0b,0x07),
    (0x6f,0x83,0x7b),(0x67,0x7b,0x6f),(0x5f,0x73,0x67),(0x57,0x6b,0x5f),
    (0x4f,0x63,0x57),(0x47,0x5b,0x4f),(0x3f,0x53,0x47),(0x37,0x4b,0x3f),
    (0x2f,0x43,0x37),(0x2b,0x3b,0x2f),(0x23,0x33,0x27),(0x1f,0x2b,0x1f),
    (0x17,0x23,0x17),(0x0f,0x1b,0x13),(0x0b,0x13,0x0b),(0x07,0x0b,0x07),
    (0xff,0xf3,0x1b),(0xef,0xdf,0x17),(0xdb,0xcb,0x13),(0xcb,0xb7,0x0f),
    (0xbb,0xa7,0x0f),(0xab,0x97,0x0b),(0x9b,0x83,0x07),(0x8b,0x73,0x07),
    (0x7b,0x63,0x07),(0x6b,0x53,0x00),(0x5b,0x47,0x00),(0x4b,0x37,0x00),
    (0x3b,0x2b,0x00),(0x2b,0x1f,0x00),(0x1b,0x0f,0x00),(0x0b,0x07,0x00),
    (0x00,0x00,0xff),(0x0b,0x0b,0xef),(0x13,0x13,0xdf),(0x1b,0x1b,0xcf),
    (0x23,0x23,0xbf),(0x2b,0x2b,0xaf),(0x2f,0x2f,0x9f),(0x2f,0x2f,0x8f),
    (0x2f,0x2f,0x7f),(0x2f,0x2f,0x6f),(0x2f,0x2f,0x5f),(0x2b,0x2b,0x4f),
    (0x23,0x23,0x3f),(0x1b,0x1b,0x2f),(0x13,0x13,0x1f),(0x0b,0x0b,0x0f),
    (0x2b,0x00,0x00),(0x3b,0x00,0x00),(0x4b,0x07,0x00),(0x5f,0x07,0x00),
    (0x6f,0x0f,0x00),(0x7f,0x17,0x07),(0x93,0x1f,0x07),(0xa3,0x27,0x0b),
    (0xb7,0x33,0x0f),(0xc3,0x4b,0x1b),(0xcf,0x63,0x2b),(0xdb,0x7f,0x3b),
    (0xe3,0x97,0x4f),(0xe7,0xab,0x5f),(0xef,0xbf,0x77),(0xf7,0xd3,0x8b),
    (0xa7,0x7b,0x3b),(0xb7,0x9b,0x37),(0xc7,0xc3,0x37),(0xe7,0xe3,0x57),
    (0x7f,0xbf,0xff),(0xab,0xe7,0xff),(0xd7,0xff,0xff),(0x67,0x00,0x00),
    (0x8b,0x00,0x00),(0xb3,0x00,0x00),(0xd7,0x00,0x00),(0xff,0x00,0x00),
    (0xff,0xf3,0x93),(0xff,0xf7,0xc7),(0xff,0xff,0xff),(0x9f,0x5b,0x53),
)


class MdlSkin(object):
    """ """

    __slots__ = (
        'group',
        'skin'
    )

    def __init__(self, skin_struct):
        self.group = skin_struct[0]
        self.skin = skin_struct[1:]


class MdlSkinGroup(object):
    """ """

    __slots__ = (
        'group',
        'number_of_skins',
        'intervals',
        'skins'
    )

    def __init__(self, skingroup_struct):
        self.group = skingroup_struct[0]
        self.number_of_skins = skingroup_struct[1]
        self.intervals = skingroup_struct[2:self.number_of_skins + 2]
        self.skins = skingroup_struct[self.number_of_skins + 2:]


class MdlStVertex(object):
    """ """

    __slots__ = (
        'on_seam',
        's',
        't'
    )

    def __init__(self, st_vertex_struct):
        self.on_seam = st_vertex_struct[_ST_VERTEX_ON_SEAM]
        self.s = st_vertex_struct[_ST_VERTEX_S]
        self.t = st_vertex_struct[_ST_VERTEX_T]


class MdlTriangle(object):
    """ """

    __slots__ = (
        'faces_front',
        'vertices'
    )

    def __init__(self, triangle_struct):
        self.faces_front = triangle_struct[_TRIANGLE_FACES_FRONT]
        self.vertices = triangle_struct[_TRIANGLE_VERTICES:]

    def __getitem__(self, item):
        if item > 2:
            raise IndexError('list index out of range')

        return self.vertices[item]


class MdlTriVertex(object):
    """ """

    __slots__ = (
        'x',
        'y',
        'z',
        'light_normal_index'
    )

    def __init__(self, trivertex_struct):
        self.x = trivertex_struct[_TRIVERTEX_X]
        self.y = trivertex_struct[_TRIVERTEX_Y]
        self.z = trivertex_struct[_TRIVERTEX_Z]
        self.light_normal_index = trivertex_struct[_TRIVERTEX_LIGHT_NORMAL_INDEX]

    def __getitem__(self, item):
        if item > 2:
            raise IndexError('list index of out of range')

        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z


class MdlFrame(object):
    """ """

    __slots__ = (
        'type',
        'min',
        'max',
        'name',
        'vertices'
    )

    def __init__(self, frame_struct):
        self.type = 0
        self.min = MdlTriVertex(frame_struct[_FRAME_MIN:_FRAME_MAX])
        self.max = MdlTriVertex(frame_struct[_FRAME_MAX:_FRAME_NAME])
        self.name = frame_struct[_FRAME_NAME].split(b'\00')[0].decode('ascii')

        vs = frame_struct[_FRAME_VERTS:]
        self.vertices = [MdlTriVertex((vs[4*i], vs[4*i + 1], vs[4*i + 2], vs[4*i + 3])) for i in range(len(vs) // 4)]


class MdlFrameGroup(object):
    """ """

    __slots__ = (
        'number_of_frames',
        'type',
        'min',
        'max',
        'intervals',
        'frames'
    )

    def __init__(self, framegroup_struct):
        self.type = 1
        self.number_of_frames = framegroup_struct[_FRAMEGROUP_NUMBER_OF_FRAMES]
        self.min = MdlTriVertex(framegroup_struct[_FRAMEGROUP_MIN])
        self.max = MdlTriVertex(framegroup_struct[_FRAMEGROUP_MAX])
        self.intervals = framegroup_struct[_FRAMEGROUP_INTERVALS]
        self.frames = [MdlFrame(f) for f in framegroup_struct[_FRAMEGROUP_FRAMES]]


class Mesh(object):
    """Class for representing mesh data"""

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


class Image(object):
    """Class for representing pixel data"""

    __slots__ = (
        'width',
        'height',
        'format',
        'pixels'
    )

    def __init__(self):
        self.width = 0
        self.height = 0
        self.format = 'RGB'
        self.pixels = None


class Mdl(object):
    """Class for working with Mdl files.

    m = MdlFile()
    m.open(file)

    """

    def __init__(self):
        self.fp = None
        self.mode = None

        self.signature = header_magic_number
        self.version = 6
        self.scale = 1, 1, 1
        self.origin = 0, 0, 0
        self.radius = 0
        self.offsets = 0, 0, 0
        self.number_of_skins = 0
        self.skin_width = 0
        self.skin_height = 0
        self.number_of_vertices = 0
        self.number_of_triangles = 0
        self.number_of_frames = 0
        self.synctype = 0
        self.flags = 0
        self.size = 0

        self.skins = []
        self.st_vertices = []
        self.triangles = []
        self.frames = []

    @staticmethod
    def open(file, mode='r'):
        """Returns an Mdl object"""

        if mode not in ['r', 'w']:
            raise ValueError("invalid mode: '%s'" % mode)

        mdl = Mdl()

        mdl.mode = mode

        if isinstance(file, str):
            file = io.open(file, 'rb')

        elif isinstance(file, bytes):
            file = io.BytesIO(file)

        elif not hasattr(file, 'read'):
            raise RuntimeError(
                "MdlFile requires 'file' to be a path, a file-like object, or bytes")

        mdl.fp = file

        data = file.read(header_size)
        data = struct.unpack(header_format, data)

        if data[_HEADER_SIGNATURE] != header_magic_number:
            raise BadMdlFile('Bad magic number: %r' % mdl.signature)

        mdl.signature = data[_HEADER_SIGNATURE]
        mdl.version = data[_HEADER_VERSION]
        mdl.scale = data[_HEADER_SCALE:_HEADER_ORIGIN]
        mdl.origin = data[_HEADER_ORIGIN:_HEADER_RADIUS]
        mdl.radius = data[_HEADER_RADIUS]
        mdl.offsets = data[_HEADER_OFFSETS:_HEADER_NUMSKINS]
        mdl.number_of_skins = data[_HEADER_NUMSKINS]
        mdl.skin_width = data[_HEADER_SKINWIDTH]
        mdl.skin_height = data[_HEADER_SKINHEIGHT]
        mdl.number_of_vertices = data[_HEADER_NUMVERTS]
        mdl.number_of_triangles = data[_HEADER_NUMTRIS]
        mdl.number_of_frames = data[_HEADER_NUMFRAMES]
        mdl.synctype = data[_HEADER_SYNCTYPE]
        mdl.flags = data[_HEADER_FLAGS]
        mdl.size = data[_HEADER_SIZE]

        mdl.skins = []
        mdl.st_vertices = []
        mdl.triangles = []
        mdl.frames = []

        for _ in range(mdl.number_of_skins):
            group = file.read(4)
            group = struct.unpack('<l', group)[0]

            if group == 0:
                skin_format = '<%iB' % (mdl.skin_width * mdl.skin_height)
                skin_size = struct.calcsize(skin_format)

                data = file.read(skin_size)
                data = struct.unpack(skin_format, data)
                skin_struct = (group,) + data

                mdl.skins.append(MdlSkin(skin_struct))

            else:
                number_of_pictures = file.read(4)
                number_of_pictures = struct.unpack('<l', number_of_pictures)[0]

                skingroup_format = '<%if%iB' % (number_of_pictures, (mdl.skin_width * mdl.skin_height * number_of_pictures))
                skingroup_size = struct.calcsize(skingroup_format)

                data = file.read(skingroup_size)
                data = struct.unpack(skingroup_format, data)
                skingroup_struct = (group, number_of_pictures) + data

                mdl.skins.append(MdlSkinGroup(skingroup_struct))

        for _ in range(mdl.number_of_vertices):
            data = file.read(st_vertex_size)
            data = struct.unpack(st_vertex_format, data)

            mdl.st_vertices.append(MdlStVertex(data))

        for _ in range(mdl.number_of_triangles):
            data = file.read(triangle_size)
            data = struct.unpack(triangle_format, data)

            mdl.triangles.append(MdlTriangle(data))

        frame_format = calculate_frame_format(mdl.number_of_vertices)
        frame_size = struct.calcsize(frame_format)

        for _ in range(mdl.number_of_frames):
            frame_type = file.read(4)
            frame_type = struct.unpack('<l', frame_type)[0]

            if frame_type == 0:
                data = file.read(frame_size)
                data = struct.unpack(frame_format, data)

                mdl.frames.append(MdlFrame(data))

            else:
                """
                framegroup_struct = calculate_framegroup_struct(self.numverts, self.numframes)
                framegroup_size = struct.calcsize(framegroup_struct)

                data = fp.read(framegroup_size)
                unpacked_data = struct.unpack(framegroup_struct, data)
                framegroup_struct = unpacked_data

                self.frames.append(MdlFrameGroup(framegroup_struct))
                """

                number_of_frames = file.read(4)
                number_of_frames = struct.unpack('<l', number_of_frames)[0]

                min = file.read(trivertex_size)
                min = struct.unpack(trivertex_format, min)

                max = file.read(trivertex_size)
                max = struct.unpack(trivertex_format, max)

                intervals = file.read(4 * number_of_frames)
                intervals = struct.unpack('<%if' % number_of_frames, intervals)

                frame_structs = []

                for _ in range(number_of_frames):
                    data = file.read(frame_size)
                    data = struct.unpack(frame_format, data)

                    frame_structs.append(data)

                framegroup_struct = number_of_frames, min, max, intervals, frame_structs

                mdl.frames.append(MdlFrameGroup(framegroup_struct))

        return mdl

    def close(self):
        self.fp.close()

    def mesh(self, frame=0, subframe=0):
        mesh = Mesh()

        frame = self.frames[frame]

        if isinstance(frame, MdlFrame):
            mesh.vertices = [(v.x, v.y, v.z) for v in frame.vertices]
        else:
            mesh.vertices = [(v.x, v.y, v.z) for v in frame.frames[subframe].vertices]

        mesh.triangles = [list(reversed(t.vertices)) for t in self.triangles]

        mesh.uvs = [None for _ in range(len(mesh.vertices))]

        for tri_index, triangle in enumerate(self.triangles):
            for vert_index, vertex in enumerate(list(reversed(triangle.vertices))):
                st_vertex = self.st_vertices[vertex]
                s = st_vertex.s
                t = st_vertex.t

                if st_vertex.on_seam  and not triangle.faces_front:
                    s += self.skin_width / 2

                uv_coord = s / self.skin_width, 1 - t / self.skin_height

                if not mesh.uvs[vertex]:
                    mesh.uvs[vertex] = uv_coord

                elif mesh.uvs[vertex] != uv_coord:
                    # Split this vertex
                    vert = mesh.vertices[vertex]
                    mesh.vertices.append(vert)
                    vertex = len(mesh.vertices) - 1
                    mesh.triangles[tri_index][vert_index] = vertex
                    mesh.uvs.append(uv_coord)

        return mesh

    def image(self, index=0, palette=default_palette):
        if index > len(self.skins):
            raise IndexError('list index out of range')

        image = Image()
        image.width = self.skin_width
        image.height = self.skin_height
        image.format = 'RGBA'
        image.pixels = self.skins[index].skin

        p = []

        for row in reversed(range(image.height)):
            p += image.pixels[row * image.width:(row + 1) * image.width]

        d = []

        for i in p:
            d += palette[i]
            d += [255]

        image.pixels = d

        return image


