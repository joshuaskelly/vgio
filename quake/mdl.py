"""Module for working with id Software style MDL files

Supported games:
    - QUAKE
"""

import enum
import io
import struct

__all__ = ['BadMdlFile', 'is_mdlfile', 'BadMdlFile', 'MdlSkin', 'MdlSkinGroup',
           'MdlStVertex', 'MdlTriangle', 'MdlTriVertex', 'MdlFrame',
           'MdlFrameGroup', 'Mesh', 'Image', 'Mdl']


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

def _calculate_frame_format(numverts):
    return '<4B4B16s%iB' % (numverts * 4)

frame_format = None
frame_size = None

_FRAME_MIN = 0
_FRAME_MAX = 4
_FRAME_NAME = 8
_FRAME_VERTS = 9

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

class MdlSkinType(enum.Enum):
    SINGLE = 0
    GROUP = 1


class MdlSkin(object):
    """Class for representing an mdl skin

    A skin is an indexed image embedded within the model. Models may contain
    more than one skin, and there may be as many skins as are there are
    separate parts in the model.

    Attributes:
        type: The MdlSkinType for the skin. For an MdlSkin object the type must
            be MdlSkinType.SINGLE

        skin: A tuple of unstructured indexed pixel data represented as
            integers. A palette must be used to obtain RGB data.
            The size of this tuple is:

            mdl.skin_width * mdl.skin_height.
    """

    __slots__ = (
        'type',
        'skin'
    )

    def __init__(self, skin_struct):
        self.type = MdlSkinType.SINGLE
        self.skin = skin_struct[1:]


class MdlSkinGroup(object):
    """Class for representing an mdl skin group

    A skin group is a sequence of indexed images embedded within the model.

    Attributes:
        type: The MdlSkinType for the skin group. For an MdlSkinGroup the type
            must be MdlSkinType.GROUP

        number_of_skins: The number of skins contain within this MdlSkinGroup.

        intervals: The time intervals between skin.

        skins: A tuple of unstructured indexed pixel data represented as
            integers. A palette must be used to obtain RGB data.
            This size of this tuple is:

            mdl.skin_width * mdl.skin_height * number_of_frames
    """

    __slots__ = (
        'type',
        'number_of_skins',
        'intervals',
        'skins'
    )

    def __init__(self, skingroup_struct):
        self.type = MdlSkinType.GROUP
        self.number_of_skins = skingroup_struct[1]
        self.intervals = skingroup_struct[2:self.number_of_skins + 2]
        self.skins = skingroup_struct[self.number_of_skins + 2:]


class MdlStVertex(object):
    """Class for representing an mdl st vertex

    MdlStVertices are basically UV coordinates with the following caveat:

    Note:
        If an MdlStVertex lies on a seam and belongs to a back facing triangle,
        the s-component must be incremented by half of the skin width.

    Attributes:
        on_seam: Indicates if the MdlStVertex is on a skin boundary. The value
            will be 0 if not on the seam and 0x20 if it does lie on the seam.

        s: The x-coordinate on the skin.

        t: The y-coordinate on the skin.
    """

    __slots__ = (
        'on_seam',
        's',
        't'
    )

    def __init__(self, st_vertex_struct):
        self.on_seam = st_vertex_struct[_ST_VERTEX_ON_SEAM]
        self.s = st_vertex_struct[_ST_VERTEX_S]
        self.t = st_vertex_struct[_ST_VERTEX_T]

    def __getitem__(self, item):
        if item > 1:
            raise IndexError('list index of out of range')

        return self.s if item == 0 else self.t


class MdlTriangle(object):
    """Class for representing an mdl triangle

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

    def __init__(self, triangle_struct):
        self.faces_front = triangle_struct[_TRIANGLE_FACES_FRONT]
        self.vertices = triangle_struct[_TRIANGLE_VERTICES:]

    def __getitem__(self, item):
        return self.vertices[item]


class MdlTriVertex(object):
    """Class for representing an mdl trivertex

    An MdlTriVertex is a set of XYZ coordinates and a light normal index.

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


class MdlFrameType(enum.Enum):
    SINGLE = 0
    GROUP = 1


class MdlFrame(object):
    """Class for representing an mdl frame

    An MdlFrame is a set of vertices that represent the state of the model at
    a single frame of animation.

    Note:
        The MdlTriVertices that describe the bounding box do not use their
        light_normal_index attribute.

    Attributes:
        type: The MdlFrameType of the frame. For an MdlFrame object the type
            must be MdlFrameType.SINGLE

        bounding_box_min: The minimum coordinate of the bounding box containing
            the vertices in this frame.

        bounding_box_max: The maximum coordinate of the bounding box containing
            all the vertices in this frame.

        name: The name of the frame.

        vertices: A list of MdlTriVertex objects.
    """

    __slots__ = (
        'type',
        'bounding_box_min',
        'bounding_box_max',
        'name',
        'vertices'
    )

    def __init__(self, frame_struct):
        self.type = MdlFrameType.SINGLE
        self.bounding_box_min = MdlTriVertex(frame_struct[_FRAME_MIN:_FRAME_MAX])
        self.bounding_box_max = MdlTriVertex(frame_struct[_FRAME_MAX:_FRAME_NAME])
        self.name = frame_struct[_FRAME_NAME].split(b'\00')[0].decode('ascii')

        vs = frame_struct[_FRAME_VERTS:]
        self.vertices = [MdlTriVertex((vs[i], vs[i + 1], vs[i + 2], vs[i + 3])) for i in range(0, len(vs), 4)]


class MdlFrameGroup(object):
    """Class for representing an mdl frame group

    Attributes:
        type: The MdlFrameType of the frame group. For an MdlFrame object the
            type must be MdlFrameType.GROUP

        bounding_box_min: The minimum coordinate of the bounding box containing
            the vertices of all frames in this group.

        bounding_box_max: The maximum coordinate of the bounding box containing
            the vertices of all the frames in this group.

        number_of_frames: The number of frames in this group.

        intervals: A sequence of timings for each frame.

        frames: A list of MdlFrame objects.
    """

    __slots__ = (
        'type',
        'bounding_box_min',
        'bounding_box_max',
        'number_of_frames',
        'intervals',
        'frames'
    )

    def __init__(self, framegroup_struct):
        self.type = MdlFrameType.GROUP
        self.number_of_frames = framegroup_struct[_FRAMEGROUP_NUMBER_OF_FRAMES]
        self.bounding_box_min = MdlTriVertex(framegroup_struct[_FRAMEGROUP_MIN])
        self.bounding_box_max = MdlTriVertex(framegroup_struct[_FRAMEGROUP_MAX])
        self.intervals = framegroup_struct[_FRAMEGROUP_INTERVALS]
        self.frames = [MdlFrame(f) for f in framegroup_struct[_FRAMEGROUP_FRAMES]]



class SyncType(enum.Enum):
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
        self.format = 'RGB'
        self.pixels = None


class Mdl(object):
    """Class for working with Mdl files

    Example:
        m = MdlFile()
        m.open(file)

    Attributes:
        identifier: The magic number of the model, must be b'IDPO'

        version: The version of the model, should be 6.

        scale: The scale of the model. Used to correctly resize the model as
            the frame vertices are packed into a (0, 0, 0) to (255, 255, 255)
            local space.

        origin: The offset of the model. Used to correctly position the model
            as the frame vertices are packed into a (0, 0, 0) to
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
            MdlSyncType.SYNC or MdlSyncType.RAND.

        flags: A bit field of entity effects.

        size: The average size of the triangles.


        skins: The list of MdlSkin or MdlSkinGroup objects. Use the type
            attribute to identify the object. The type is either
            MdlSkinType.SINGLE or MdlSkinType.GROUP.

        st_vertices: The list of MdlStVertex objects.

        triangles: The list of MdlTriangle objects.

        frames: The list of MdlFrame or MdlFrameGroup objects. Use the type
            attribute to identify the object. The type is either
            MdlFrameType.SINGLE or MdlFrameType.GROUP.


        fp: The file-like object to read data from.

        mode: The file mode for the file-like object.
    """

    def __init__(self):
        self.fp = None
        self.mode = None

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
        self.synctype = 0
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

            mode: Currently the only supported mode is 'r'

        Returns:
            An Mdl object constructed from the information read from the
            file-like object.
        """

        if mode not in ['r']:
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

        frame_format = _calculate_frame_format(mdl.number_of_vertices)
        frame_size = struct.calcsize(frame_format)

        for _ in range(mdl.number_of_frames):
            frame_type = file.read(4)
            frame_type = struct.unpack('<l', frame_type)[0]
            frame_type = MdlFrameType(frame_type)

            if frame_type is MdlFrameType.SINGLE:
                data = file.read(frame_size)
                data = struct.unpack(frame_format, data)

                mdl.frames.append(MdlFrame(data))

            else:
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

        if frame.type is MdlFrameType.SINGLE:
            mesh.vertices = [(v.x, v.y, v.z) for v in frame.vertices]
        else:
            mesh.vertices = [(v.x, v.y, v.z) for v in frame.frames[subframe].vertices]

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
