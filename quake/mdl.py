"""Module for working with id Software style MDL files

Supported games:
    - QUAKE
"""

import io
import struct

__all__ = ['BadMdlFile', 'is_mdlfile', 'BadMdlFile', 'Skin', 'SkinGroup',
           'StVertex', 'Triangle', 'TriVertex', 'Frame',
           'FrameGroup', 'Mesh', 'Image', 'Mdl']


class BadMdlFile(Exception):
    pass


# The mdl header structure
header_format = '<4sl10f8lf'
header_magic_number = b'IDPO'
header_version = 6
header_size = struct.calcsize(header_format)

# Indexes of the header structure
_HEADER_SIGNATURE = 0
_HEADER_VERSION = 1
_HEADER_SCALE = 2
_HEADER_ORIGIN = 5
_HEADER_RADIUS = 8
_HEADER_OFFSETS = 9
_HEADER_NUMSKINS = 12
_HEADER_SKINWIDTH = 13
_HEADER_SKINHEIGHT = 14
_HEADER_NUMVERTS = 15
_HEADER_NUMTRIS = 16
_HEADER_NUMFRAMES = 17
_HEADER_SYNCTYPE = 18
_HEADER_FLAGS = 19
_HEADER_SIZE = 20

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

vertex_normals = (
    (-0.525731, 0.000000, 0.850651), (-0.442863, 0.238856, 0.864188),
    (-0.295242, 0.000000, 0.955423), (-0.309017, 0.500000, 0.809017),
    (-0.162460, 0.262866, 0.951056), (0.000000, 0.000000, 1.000000),
    (0.000000, 0.850651, 0.525731), (-0.147621, 0.716567, 0.681718),
    (0.147621, 0.716567, 0.681718), (0.000000, 0.525731, 0.850651),
    (0.309017, 0.500000, 0.809017), (0.525731, 0.000000, 0.850651),
    (0.295242, 0.000000, 0.955423), (0.442863, 0.238856, 0.864188),
    (0.162460, 0.262866, 0.951056), (-0.681718, 0.147621, 0.716567),
    (-0.809017, 0.309017, 0.500000), (-0.587785, 0.425325, 0.688191),
    (-0.850651, 0.525731, 0.000000), (-0.864188, 0.442863, 0.238856),
    (-0.716567, 0.681718, 0.147621), (-0.688191, 0.587785, 0.425325),
    (-0.500000, 0.809017, 0.309017), (-0.238856, 0.864188, 0.442863),
    (-0.425325, 0.688191, 0.587785), (-0.716567, 0.681718, -0.147621),
    (-0.500000, 0.809017, -0.309017), (-0.525731, 0.850651, 0.000000),
    (0.000000, 0.850651, -0.525731), (-0.238856, 0.864188, -0.442863),
    (0.000000, 0.955423, -0.295242), (-0.262866, 0.951056, -0.162460),
    (0.000000, 1.000000, 0.000000), (0.000000, 0.955423, 0.295242),
    (-0.262866, 0.951056, 0.162460), (0.238856, 0.864188, 0.442863),
    (0.262866, 0.951056, 0.162460), (0.500000, 0.809017, 0.309017),
    (0.238856, 0.864188, -0.442863), (0.262866, 0.951056, -0.162460),
    (0.500000, 0.809017, -0.309017), (0.850651, 0.525731, 0.000000),
    (0.716567, 0.681718, 0.147621), (0.716567, 0.681718, -0.147621),
    (0.525731, 0.850651, 0.000000), (0.425325, 0.688191, 0.587785),
    (0.864188, 0.442863, 0.238856), (0.688191, 0.587785, 0.425325),
    (0.809017, 0.309017, 0.500000), (0.681718, 0.147621, 0.716567),
    (0.587785, 0.425325, 0.688191), (0.955423, 0.295242, 0.000000),
    (1.000000, 0.000000, 0.000000), (0.951056, 0.162460, 0.262866),
    (0.850651, -0.525731, 0.000000), (0.955423, -0.295242, 0.000000),
    (0.864188, -0.442863, 0.238856), (0.951056, -0.162460, 0.262866),
    (0.809017, -0.309017, 0.500000), (0.681718, -0.147621, 0.716567),
    (0.850651, 0.000000, 0.525731), (0.864188, 0.442863, -0.238856),
    (0.809017, 0.309017, -0.500000), (0.951056, 0.162460, -0.262866),
    (0.525731, 0.000000, -0.850651), (0.681718, 0.147621, -0.716567),
    (0.681718, -0.147621, -0.716567), (0.850651, 0.000000, -0.525731),
    (0.809017, -0.309017, -0.500000), (0.864188, -0.442863, -0.238856),
    (0.951056, -0.162460, -0.262866), (0.147621, 0.716567, -0.681718),
    (0.309017, 0.500000, -0.809017), (0.425325, 0.688191, -0.587785),
    (0.442863, 0.238856, -0.864188), (0.587785, 0.425325, -0.688191),
    (0.688191, 0.587785, -0.425325), (-0.147621, 0.716567, -0.681718),
    (-0.309017, 0.500000, -0.809017), (0.000000, 0.525731, -0.850651),
    (-0.525731, 0.000000, -0.850651), (-0.442863, 0.238856, -0.864188),
    (-0.295242, 0.000000, -0.955423), (-0.162460, 0.262866, -0.951056),
    (0.000000, 0.000000, -1.000000), (0.295242, 0.000000, -0.955423),
    (0.162460, 0.262866, -0.951056), (-0.442863, -0.238856, -0.864188),
    (-0.309017, -0.500000, -0.809017), (-0.162460, -0.262866, -0.951056),
    (0.000000, -0.850651, -0.525731), (-0.147621, -0.716567, -0.681718),
    (0.147621, -0.716567, -0.681718), (0.000000, -0.525731, -0.850651),
    (0.309017, -0.500000, -0.809017), (0.442863, -0.238856, -0.864188),
    (0.162460, -0.262866, -0.951056), (0.238856, -0.864188, -0.442863),
    (0.500000, -0.809017, -0.309017), (0.425325, -0.688191, -0.587785),
    (0.716567, -0.681718, -0.147621), (0.688191, -0.587785, -0.425325),
    (0.587785, -0.425325, -0.688191), (0.000000, -0.955423, -0.295242),
    (0.000000, -1.000000, 0.000000), (0.262866, -0.951056, -0.162460),
    (0.000000, -0.850651, 0.525731), (0.000000, -0.955423, 0.295242),
    (0.238856, -0.864188, 0.442863), (0.262866, -0.951056, 0.162460),
    (0.500000, -0.809017, 0.309017), (0.716567, -0.681718, 0.147621),
    (0.525731, -0.850651, 0.000000), (-0.238856, -0.864188, -0.442863),
    (-0.500000, -0.809017, -0.309017), (-0.262866, -0.951056, -0.162460),
    (-0.850651, -0.525731, 0.000000), (-0.716567, -0.681718, -0.147621),
    (-0.716567, -0.681718, 0.147621), (-0.525731, -0.850651, 0.000000),
    (-0.500000, -0.809017, 0.309017), (-0.238856, -0.864188, 0.442863),
    (-0.262866, -0.951056, 0.162460), (-0.864188, -0.442863, 0.238856),
    (-0.809017, -0.309017, 0.500000), (-0.688191, -0.587785, 0.425325),
    (-0.681718, -0.147621, 0.716567), (-0.442863, -0.238856, 0.864188),
    (-0.587785, -0.425325, 0.688191), (-0.309017, -0.500000, 0.809017),
    (-0.147621, -0.716567, 0.681718), (-0.425325, -0.688191, 0.587785),
    (-0.162460, -0.262866, 0.951056), (0.442863, -0.238856, 0.864188),
    (0.162460, -0.262866, 0.951056), (0.309017, -0.500000, 0.809017),
    (0.147621, -0.716567, 0.681718), (0.000000, -0.525731, 0.850651),
    (0.425325, -0.688191, 0.587785), (0.587785, -0.425325, 0.688191),
    (0.688191, -0.587785, 0.425325), (-0.955423, 0.295242, 0.000000),
    (-0.951056, 0.162460, 0.262866), (-1.000000, 0.000000, 0.000000),
    (-0.850651, 0.000000, 0.525731), (-0.955423, -0.295242, 0.000000),
    (-0.951056, -0.162460, 0.262866), (-0.864188, 0.442863, -0.238856),
    (-0.951056, 0.162460, -0.262866), (-0.809017, 0.309017, -0.500000),
    (-0.864188, -0.442863, -0.238856), (-0.951056, -0.162460, -0.262866),
    (-0.809017, -0.309017, -0.500000), (-0.681718, 0.147621, -0.716567),
    (-0.681718, -0.147621, -0.716567), (-0.850651, 0.000000, -0.525731),
    (-0.688191, 0.587785, -0.425325), (-0.587785, 0.425325, -0.688191),
    (-0.425325, 0.688191, -0.587785), (-0.425325, -0.688191, -0.587785),
    (-0.587785, -0.425325, -0.688191), (-0.688191, -0.587785, -0.425325),
)

SINGLE = 0
GROUP = 1


class Skin(object):
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

    @classmethod
    def write(cls, file, skin, size):
        width, height = size
        skin_format = _calculate_skin_format(size)
        skin_data = struct.pack(skin_format,
                                skin.type,
                                *skin.pixels)

        file.write(skin_data)

    @classmethod
    def read(cls, file, size):
        skin = Skin()
        skin_format = _calculate_skin_format(size)
        skin_size = struct.calcsize(skin_format)
        skin_data = file.read(skin_size)
        skin_struct = struct.unpack(skin_format, skin_data)

        skin.type = skin_struct[_SKIN_TYPE]
        skin.pixels = skin_struct[_SKIN_PIXELS:]

        return skin


class SkinGroup(object):
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

    @classmethod
    def write(cls, file, skin_group, size):
        group = struct.pack('<l', skin_group.type)
        file.write(group)
        number_of_skins = struct.pack('<l', skin_group.number_of_skins)
        file.write(number_of_skins)
        skin_group_format = _calculate_skin_group_format(skin_group.number_of_skins, size)
        skin_group_data = struct.pack(skin_group_format,
                                      *skin_group.intervals,
                                      *skin_group.pixels)

        file.write(skin_group_data)


    @classmethod
    def read(cls, file, size):
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


class StVertex(object):
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
        self.on_seam = None
        self.s = None
        self.t = None

    def __getitem__(self, item):
        if item > 1:
            raise IndexError('list index of out of range')

        return self.s if item == 0 else self.t

    @classmethod
    def write(cls, file, st_vertex):
        st_vertex_data = struct.pack(st_vertex_format,
                                     st_vertex.on_seam,
                                     st_vertex.s,
                                     st_vertex.t)

        file.write(st_vertex_data)

    @classmethod
    def read(cls, file):
        st_vertex = StVertex()
        st_vertex_data = file.read(st_vertex_size)
        st_vertex_struct = struct.unpack(st_vertex_format, st_vertex_data)

        st_vertex.on_seam = st_vertex_struct[_ST_VERTEX_ON_SEAM]
        st_vertex.s = st_vertex_struct[_ST_VERTEX_S]
        st_vertex.t = st_vertex_struct[_ST_VERTEX_T]

        return st_vertex


class Triangle(object):
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
        self.faces_front = None
        self.vertices = None

    def __getitem__(self, item):
        return self.vertices[item]

    @classmethod
    def write(cls, file, triangle):
        triangle_data = struct.pack(triangle_format,
                                    triangle.faces_front,
                                    *triangle.vertices)

        file.write(triangle_data)

    @classmethod
    def read(cls, file):
        triangle = Triangle()
        triangle_data = file.read(triangle_size)
        triangle_struct = struct.unpack(triangle_format, triangle_data)

        triangle.faces_front = triangle_struct[_TRIANGLE_FACES_FRONT]
        triangle.vertices = triangle_struct[_TRIANGLE_VERTICES:]

        return triangle


class TriVertex(object):
    """Class for representing a trivertex

    A TriVertex is a set of XYZ coordinates and a light normal index.

    Note:
        The XYZ coordinates are packed into a (0, 0, 0) to (255, 255, 255)
        local space. The actual position can be calculated:

        position = (packed_vertex * mdl.scale) + mdl.offset

    Note:
        The light normal index is an index into a set of pre-calculated normal
        vectors. These can be found in the vertex_normals attribute of this
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

    def __getitem__(self, item):
        if item > 2:
            raise IndexError('list index of out of range')

        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z

    @classmethod
    def write(cls, file, tri_vertex):
        tri_vertex_data = struct.pack(trivertex_format,
                                      tri_vertex.x,
                                      tri_vertex.y,
                                      tri_vertex.z,
                                      tri_vertex.light_normal_index)

        file.write(tri_vertex_data)

    @classmethod
    def read(cls, file):
        tri_vertex = TriVertex()
        tri_vertex_data = file.read(trivertex_size)
        tri_vertex_struct = struct.unpack(trivertex_format, tri_vertex_data)

        tri_vertex.x = tri_vertex_struct[_TRIVERTEX_X]
        tri_vertex.y = tri_vertex_struct[_TRIVERTEX_Y]
        tri_vertex.z = tri_vertex_struct[_TRIVERTEX_Z]
        tri_vertex.light_normal_index = tri_vertex_struct[_TRIVERTEX_LIGHT_NORMAL_INDEX]

        return tri_vertex


class Frame(object):
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
        self.vertices = None

    @classmethod
    def write(cls, file, frame, number_of_vertices):
        TriVertex.write(file, frame.bounding_box_min)
        TriVertex.write(file, frame.bounding_box_max)
        file.write(struct.pack('<16s', frame.name.encode('ascii')))
        for vertex in frame.vertices:
            TriVertex.write(file, vertex)

    @classmethod
    def read(cls, file, number_of_vertices):
        frame = Frame()
        frame.bounding_box_min = TriVertex.read(file)
        frame.bounding_box_max = TriVertex.read(file)
        frame.name = struct.unpack('<16s', file.read(struct.calcsize('<16s')))[0].split(b'\00')[0].decode('ascii')
        frame.vertices = [TriVertex.read(file) for _ in range(number_of_vertices)]

        return frame


class FrameGroup(object):
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

    @classmethod
    def write(cls, file, frame_group, number_of_vertices):
        file.write(struct.pack('<l', frame_group.number_of_frames))
        TriVertex.write(file, frame_group.bounding_box_min)
        TriVertex.write(file, frame_group.bounding_box_max)
        intervals_data = struct.pack('<%if' % frame_group.number_of_frames, *frame_group.intervals)
        file.write(intervals_data)
        for frame in frame_group.frames:
            Frame.write(file, frame, number_of_vertices)

    @classmethod
    def read(cls, file, number_of_vertices):
        frame_group = FrameGroup()
        frame_group.number_of_frames = struct.unpack('<l', file.read(4))[0]
        frame_group.bounding_box_min = TriVertex.read(file)
        frame_group.bounding_box_max = TriVertex.read(file)
        intervals_data = file.read(4 * frame_group.number_of_frames)
        frame_group.intervals = struct.unpack('<%if' % frame_group.number_of_frames, intervals_data)
        frame_group.frames = [Frame.read(file, number_of_vertices) for _ in range(frame_group.number_of_frames)]

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


class Mesh(object):
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


class Image(object):
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


class Mdl(object):
    """Class for working with Mdl files

    Example:
        m = Mdl.open(file)

    Attributes:
        identifier: The magic number of the model, must be b'IDPO'

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

        number_of_vertices: The number of vertices for the model.

        number_of_triangles: The number of triangles for the model.

        number_of_frames: The number of frames for the model.

        synctype: The synchronization type for the model. It is either
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
        self.fp = None
        self.mode = None
        self._did_modify = False

        self.identifier = header_magic_number
        self.version = header_version
        self.scale = 1, 1, 1
        self.origin = 0, 0, 0
        self.bounding_radius = 0
        self.eye_position = 0, 0, 0
        self.number_of_skins = 0
        self.skin_width = 0
        self.skin_height = 0
        self.number_of_vertices = 0
        self.number_of_triangles = 0
        self.number_of_frames = 0
        self.synctype = SYNC
        self.flags = 0
        self.size = 0

        self.skins = []
        self.st_vertices = []
        self.triangles = []
        self.frames = []

    @staticmethod
    def open(file, mode='r'):
        """Returns an Mdl object

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file

        Returns:
            An Mdl object constructed from the information read from the
            file-like object.

        Raises:
            ValueError: If an invalid file mode is given.

            RuntimeError: If the file argument is not a file-like object.

            BadMdlFile: If the file opened is not recognized as an Mdl file.
        """

        if mode not in ('r', 'w', 'a'):
            raise ValueError("invalid mode: '%s'" % mode)

        filemode = {'r': 'rb', 'w': 'w+b', 'a': 'r+b'}[mode]

        if isinstance(file, str):
            file = io.open(file, filemode)

        elif isinstance(file, bytes):
            file = io.BytesIO(file)

        elif not hasattr(file, 'read'):
            raise RuntimeError(
                "Mdl.open() requires 'file' to be a path, a file-like object, or bytes")

        # Read
        if mode == 'r':
            return Mdl._read_file(file, mode)

        # Write
        elif mode == 'w':
            mdl = Mdl()
            mdl.fp = file
            mdl.mode = 'w'
            mdl._did_modify = True

            return mdl

        # Append
        else:
            mdl = Mdl._read_file(file, mode)
            mdl._did_modify = True

            return mdl

    @classmethod
    def _read_file(cls, file, mode):
        mdl = Mdl()
        mdl.mode = mode
        mdl.fp = file

        # Header
        data = file.read(header_size)
        data = struct.unpack(header_format, data)

        if data[_HEADER_SIGNATURE] != header_magic_number:
            raise BadMdlFile('Bad magic number: %r' % data[_HEADER_SIGNATURE])

        if data[_HEADER_VERSION] != header_version:
            raise BadMdlFile('Bad version number: %r' % data[_HEADER_VERSION])

        mdl.identifier = data[_HEADER_SIGNATURE]
        mdl.version = data[_HEADER_VERSION]
        mdl.scale = data[_HEADER_SCALE:_HEADER_ORIGIN]
        mdl.origin = data[_HEADER_ORIGIN:_HEADER_RADIUS]
        mdl.bounding_radius = data[_HEADER_RADIUS]
        mdl.eye_position = data[_HEADER_OFFSETS:_HEADER_NUMSKINS]
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

        # Skins
        for _ in range(mdl.number_of_skins):
            pos = file.tell()
            group = struct.unpack('<i', file.read(4))[0]
            file.seek(pos)

            if group == 0:
                skin = Skin.read(file, (mdl.skin_width, mdl.skin_height))
                mdl.skins.append(skin)

            else:
                skin_group = SkinGroup.read(file, (mdl.skin_width, mdl.skin_height))
                mdl.skins.append(skin_group)

        # St Vertexes
        for _ in range(mdl.number_of_vertices):
            mdl.st_vertices.append(StVertex.read(file))

        # Triangles
        for _ in range(mdl.number_of_triangles):
            mdl.triangles.append(Triangle.read(file))

        # Frames
        for _ in range(mdl.number_of_frames):
            frame_type = struct.unpack('<i', file.read(4))[0]

            if frame_type == SINGLE:
                mdl.frames.append(Frame.read(file, mdl.number_of_vertices))

            else:
                mdl.frames.append(FrameGroup.read(file, mdl.number_of_vertices))

        return mdl

    @classmethod
    def _write_file(cls, file, mdl):
        # Validate mdl data
        mdl.validate()

        # Header
        header_data = struct.pack(header_format,
                                  mdl.identifier,
                                  mdl.version,
                                  *mdl.scale,
                                  *mdl.origin,
                                  mdl.bounding_radius,
                                  *mdl.eye_position,
                                  mdl.number_of_skins,
                                  mdl.skin_width,
                                  mdl.skin_height,
                                  mdl.number_of_vertices,
                                  mdl.number_of_triangles,
                                  mdl.number_of_frames,
                                  mdl.synctype,
                                  mdl.flags,
                                  mdl.size)

        file.write(header_data)

        # Skins
        for skin in mdl.skins:
            if skin.type == SINGLE:
                Skin.write(file, skin, (mdl.skin_width, mdl.skin_height))

            else:
                SkinGroup.write(file, skin, (mdl.skin_width, mdl.skin_height))

        # St Vertexes
        for st_vertex in mdl.st_vertices:
            StVertex.write(file, st_vertex)

        # Triangles
        for triangle in mdl.triangles:
            Triangle.write(file, triangle)

        # Frames
        for frame in mdl.frames:
            if frame.type == SINGLE:
                file.write(struct.pack('<l', SINGLE))
                Frame.write(file, frame, mdl.number_of_vertices)

            else:
                file.write(struct.pack('<l', GROUP))
                FrameGroup.write(file, frame, mdl.number_of_vertices)

    def validate(self):
        """Verifies correctness of Mdl data.

        Raises:
            BadMdlFile: If a discrepancy is found.
        """

        if self.identifier != header_magic_number:
            raise BadMdlFile('Bad magic number: %r' % self.identifier)

        if self.version != header_version:
            raise BadMdlFile('Bad version number: %r' % self.version)

        if self.number_of_triangles != len(self.triangles):
            raise BadMdlFile('Incorrect number of triangles. Expected: %r Actual: %r' % (self.number_of_triangles, len(self.triangles)))

        for triangle in self.triangles:
            for vertex in triangle.vertices:
                if vertex < 0 or vertex > self.number_of_vertices:
                    raise BadMdlFile('Bad vertex index: %r' % vertex)

        if self.number_of_skins != len(self.skins):
            raise BadMdlFile('Incorrect number of skins. Expected: %r Actual: %r' % (self.number_of_skins, len(self.skins)))

        for skin in self.skins:
            if skin.type == SINGLE and len(skin.pixels) != self.skin_width * self.skin_height:
                raise BadMdlFile('Incorrect number of pixels. Expected: %r Actual: %r' % (self.skin_width * self.skin_height, len(skin.pixels)))

            elif skin.type == GROUP and len(skin.pixels) != self.skin_width * self.skin_height * skin.number_of_skins:
                raise BadMdlFile('Incorrect number of pixels. Expected: %r Actual: %r' % (self.skin_width * self.skin_height * skin.number_of_skins, len(skin.pixels)))

        if self.number_of_frames != len(self.frames):
            raise BadMdlFile('Incorrect number of frames. Expected: %r Actual: %r' % (self.number_of_frames, len(self.frames)))

        for frame in self.frames:
            if frame.type == SINGLE and len(frame.vertices) != self.number_of_vertices:
                raise BadMdlFile('Incorrect number of vertices. Expected: %r Actual: %r' % (self.number_of_vertices, len(frame.vertices)))

            elif frame.type == GROUP:
                for sub_frame in frame.frames:
                    if len(sub_frame.vertices) != self.number_of_vertices:
                        raise BadMdlFile('Incorrect number of vertices. Expected: %r Actual: %r' % (self.number_of_vertices, len(sub_frame.vertices)))

    def save(self, file):
        """Writes Mdl data to file

        Args:
            file: Either the path to the file, or a file-like object, or bytes.

        Raises:
            RuntimeError: If file argument is not a file-like object.

            BadMdlFile: If the internal Mdl data is not invalid.
        """

        should_close = False

        if isinstance(file, str):
            file = io.open(file, 'r+b')
            should_close = True

        elif isinstance(file, bytes):
            file = io.BytesIO(file)
            should_close = True

        elif not hasattr(file, 'write'):
            raise RuntimeError(
                "Mdl.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        Mdl._write_file(file, self)

        if should_close:
            file.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Closes the file pointer if possible. If mode is 'w' or 'a', the file
        will be written to.

        Raises:
            BadMdlFile: If the internal Mdl data is not invalid.
        """

        if self.fp:
            if self.mode in ('w', 'a') and self._did_modify:
                self.fp.seek(0)
                Mdl._write_file(self.fp, self)
                self.fp.truncate()

            file_object = self.fp
            self.fp = None
            file_object.close()

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
            mesh.normals = [vertex_normals[v.light_normal_index] for v in frame.vertices]
        else:
            mesh.vertices = [(v.x, v.y, v.z) for v in frame.frames[subframe].vertices]
            mesh.normals = [vertex_normals[v.light_normal_index] for v in frame.frames[subframe].vertices]

        triangles = self.triangles[:]

        mesh.uvs = [None for _ in range(len(mesh.vertices))]

        for tri_index, triangle in enumerate(triangles):
            for vert_index, vertex in enumerate(triangle.vertices):
                st_vertex = self.st_vertices[vertex]
                s, t = st_vertex

                if st_vertex.on_seam and not triangle.faces_front:
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

                    updated_triangle = list(triangles[tri_index].vertices)
                    updated_triangle[vert_index] = duplicated_vertex_index
                    triangle.vertices = tuple(updated_triangle)

                    mesh.uvs.append(uv_coord)

            mesh.triangles.append(tuple(reversed(triangle.vertices)))

        return mesh

    def image(self, index=0, palette=default_palette):
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
