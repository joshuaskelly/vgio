"""Module for working with id Software style BSP files

Supported games:
    - QUAKE
"""

import io
import struct

__all__ = ['BadBspFile', 'is_bspfile', 'Plane', 'Miptexture',
           'Vertex', 'Node', 'TextureInfo', 'Face', 'ClipNode',
           'Leaf', 'Edge', 'Model', 'Bsp']


class BadBspFile(Exception):
    pass


# The bsp header structure
header_format = '<31l'
header_version = 29
header_size = struct.calcsize(header_format)

# Indexes of header structure
_HEADER_VERSION = 0
_HEADER_ENTITIES_OFFSET = 1
_HEADER_ENTITIES_SIZE = 2
_HEADER_PLANES_OFFSET = 3
_HEADER_PLANES_SIZE = 4
_HEADER_MIPTEXTURES_OFFSET = 5
_HEADER_MIPTEXTURES_SIZE = 6
_HEADER_VERTEXES_OFFSET = 7
_HEADER_VERTEXES_SIZE = 8
_HEADER_VISIBILITIES_OFFSET = 9
_HEADER_VISIBILITIES_SIZE = 10
_HEADER_NODES_OFFSET = 11
_HEADER_NODES_SIZE = 12
_HEADER_TEXTURE_INFOS_OFFSET = 13
_HEADER_TEXTURE_INFOS_SIZE = 14
_HEADER_FACES_OFFSET = 15
_HEADER_FACES_SIZE = 16
_HEADER_LIGHTING_OFFSET = 17
_HEADER_LIGHTING_SIZE = 18
_HEADER_CLIP_NODES_OFFSET = 19
_HEADER_CLIP_NODES_SIZE = 20
_HEADER_LEAFS_OFFSET = 21
_HEADER_LEAFS_SIZE = 22
_HEADER_MARK_SURFACES_OFFSET = 23
_HEADER_MARK_SURFACES_SIZE = 24
_HEADER_EDGES_OFFSET = 25
_HEADER_EDGES_SIZE = 26
_HEADER_SURF_EDGES_OFFSET = 27
_HEADER_SURF_EDGES_SIZE = 28
_HEADER_MODELS_OFFSET = 29
_HEADER_MODELS_SIZE = 30

# Plane structure
plane_format = '<4fi'
plane_size = struct.calcsize(plane_format)

# Indexes of Plane structure
_PLANE_NORMAL = 0
_PLANE_DISTANCE = 3
_PLANE_TYPE = 4

# Miptexture structure
miptexture_format = '<16s6I'
miptexture_size = struct.calcsize(miptexture_format)

# Indexes of Miptexture structure
_MIPTEXTURE_NAME = 0
_MIPTEXTURE_WIDTH = 1
_MIPTEXTURE_HEIGHT = 2
_MIPTEXTURE_OFFSETS = 3

# Vertex structure
vertex_format = '<3f'
vertex_size = struct.calcsize(vertex_format)

# Indexes of Vertex structure
_VERTEX_X = 0
_VERTEX_Y = 1
_VERTEX_Z = 2


# Visibility structure
def _calculate_visibility_format(size):
    return '<%dB' % size


visibility_format = None
visibility_size = None

# Node structure
node_format = '<i8h2H'
node_size = struct.calcsize(node_format)

# Indexes of Node structure
_NODE_PLANE_NUMBER = 0
_NODE_CHILDREN = 1
_NODE_BOUNDING_BOX_MIN = 3
_NODE_BOUNDING_BOX_MAX = 6
_NODE_FIRST_FACE = 9
_NODE_NUMBER_OF_FACES = 10

# Texture Info structure
texture_info_format = '<8f2i'
texture_info_size = struct.calcsize(texture_info_format)

# Indexes of Texture Info structure
_TEXTURE_INFO_S = 0
_TEXTURE_INFO_S_OFFSET = 3
_TEXTURE_INFO_T = 4
_TEXTURE_INFO_T_OFFSET = 7
_TEXTURE_INFO_MIPTEXTURE_NUMBER = 8
_TEXTURE_INFO_FLAGS = 9

# Face structure
face_format = '<2hi2h4Bi'
face_size = struct.calcsize(face_format)

# Indexes of Face structure
_FACE_PLANE_NUMBER = 0
_FACE_SIDE = 1
_FACE_FIRST_EDGE = 2
_FACE_NUMBER_OF_EDGES = 3
_FACE_TEXTURE_INFO = 4
_FACE_STYLES = 5
_FACE_LIGHT_OFFSET = 9


# Lighting structure
def _calculate_lighting_format(size):
    return '<%dB' % size


lighting_format = None
lighting_size = None

# Clip_node structure
clip_node_format = '<i2h'
clip_node_size = struct.calcsize(clip_node_format)

# Indexes of Clip_node structure
_CLIP_NODE_PLANE_NUMBER = 0
_CLIP_NODE_CHILDREN = 1

# Leaf structure
leaf_format = '<2i6h2H4B'
leaf_size = struct.calcsize(leaf_format)

# Indexes of Leaf structure
_LEAF_CONTENTS = 0
_LEAF_VISIBILITIY_OFFSET = 1
_LEAF_BOUNDING_BOX_MIN = 2
_LEAF_BOUNDING_BOX_MAX = 5
_LEAF_FIRST_MARK_SURFACE = 8
_LEAF_NUMBER_OF_MARKED_SURFACES = 9
_LEAF_AMBIENT_LEVEL = 10


# Mark Surface structure
def _calculate_mark_surface_format(size):
    return '<%dB' % size


mark_surface_format = None
mark_surface_size = None

# Edge structure
edge_format = '<2H'
edge_size = struct.calcsize(edge_format)


# Surf Edge structure
def _calculate_surf_edge_format(size):
    return '<%di' % (size // 4)


surf_edge_format = None
surf_edge_size = None

# Model structure
model_format = '<9f7i'
model_size = struct.calcsize(model_format)

# Indexes of Model structure
_MODEL_BOUNDING_BOX_MIN = 0
_MODEL_BOUNDING_BOX_MAX = 3
_MODEL_ORIGIN = 6
_MODEL_HEAD_NODE = 9
_MODEL_VISLEAFS = 13
_MODEL_FIRST_FACE = 14
_MODEL_NUMBER_OF_FACES = 15


def _check_bspfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<1l'))
    version = struct.unpack('<1l', data)[0]

    return version == header_version


def is_bspfile(filename):
    """Quickly see if a file is a mdl file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    result = False

    try:
        if hasattr(filename, 'read'):
            return _check_bspfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_bspfile(fp)

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


class Plane(object):
    """Class for representing a bsp plane

    Attributes:
        normal: The normal vector to the plane.

        distance: The distance from world (0, 0, 0) to a point on the plane

        type: Planes are classified as follows:
            0: Axial plane aligned to the x-axis.
            1: Axial plane aligned to the y-axis.
            2: Axial plane aligned to the z-axis.
            3: Non-axial plane roughly aligned to the x-axis.
            4: Non-axial plane roughly aligned to the y-axis.
            5: Non-axial plane roughly aligned to the z-axis.
    """

    __slots__ = (
        'normal',
        'distance',
        'type'
    )

    def __init__(self):
        self.normal = None
        self.distance = None
        self.type = None

    @classmethod
    def write(cls, file, plane):
        plane_data = struct.pack(plane_format,
                                 *plane.normal,
                                 plane.distance,
                                 plane.type)

        file.write(plane_data)

    @classmethod
    def read(cls, file):
        plane = Plane()
        plane_data = file.read(plane_size)
        plane_struct = struct.unpack(plane_format, plane_data)
        plane.normal = plane_struct[_PLANE_NORMAL:_PLANE_DISTANCE]
        plane.distance = plane_struct[_PLANE_DISTANCE]
        plane.type = plane_struct[_PLANE_TYPE]

        return plane


class Miptexture(object):
    """Class for representing a miptexture

    A miptexture is an indexed image mip map embedded within the map. Maps
    usually have many miptextures, and the miptexture lump is treated like a
    small wad file.

    Attributes:
        name: The name of the miptexture.

        width: The width of the miptexture.
            Note: this is the width at mipmap level 0.

        height: The height of the miptexture.
            Note: this is the height at mipmap level 0.

        offsets: The offsets for each of the mipmaps. This is a tuple of size
            four (this is the number of mipmap levels).

        pixels: A tuple of unstructured pixel data represented as integers. A
            palette must be used to obtain RGB data.

            Note: this is the pixel data for all four mip levels. The size is
            calculated using the simplified form of the geometric series where
            r = 1/4 and n = 4.

            The size of this tuple is:

            miptexture.width * miptexture.height * 85 / 64
    """

    __slots__ = (
        'name',
        'width',
        'height',
        'offsets',
        'pixels'
    )

    def __init__(self):
        self.name = None
        self.width = None
        self.height = None
        self.offsets = None
        self.pixels = None

    @classmethod
    def write(cls, file, miptexture):
        miptexture_data = struct.pack(miptexture_format,
                                      miptexture.name.encode('ascii'),
                                      miptexture.width,
                                      miptexture.height,
                                      *miptexture.offsets)

        pixels_size = miptexture.width * miptexture.height * 85 // 64
        pixels_format = '<%dB' % pixels_size
        pixels_data = struct.pack(pixels_format, *miptexture.pixels)

        file.write(miptexture_data)
        file.write(pixels_data)

    @classmethod
    def read(cls, file):
        miptexture = Miptexture()
        miptexture_data = file.read(miptexture_size)
        miptexture_struct = struct.unpack(miptexture_format, miptexture_data)
        miptexture.name = miptexture_struct[_MIPTEXTURE_NAME].split(b'\00')[0].decode('ascii')
        miptexture.width = miptexture_struct[_MIPTEXTURE_WIDTH]
        miptexture.height = miptexture_struct[_MIPTEXTURE_HEIGHT]
        miptexture.offsets = miptexture_struct[_MIPTEXTURE_OFFSETS:]

        pixels_size = miptexture.width * miptexture.height * 85 // 64
        pixels_format = '<%dB' % pixels_size
        pixels_data = struct.unpack(pixels_format, file.read(pixels_size))

        miptexture.pixels = pixels_data

        return miptexture


class Vertex(object):
    """Class for representing a vertex

    A Vertex is an XYZ triple.

    Attributes:
        x: The x-coordinate

        y: The y-coordinate

        z: The z-coordinate
    """

    __slots__ = (
        'x',
        'y',
        'z'
    )

    def __init__(self):
        self.x = None
        self.y = None
        self.z = None

    def __getitem__(self, item):
        if type(item) is int:
            return [self.x, self.y, self.z][item]

        elif type(item) is slice:
            start = item.start or 0
            stop = item.stop or 3

            return [self.x, self.y, self.z][start:stop]

    @classmethod
    def write(cls, file, vertex):
        vertex_data = struct.pack(vertex_format,
                                  vertex.x,
                                  vertex.y,
                                  vertex.z)

        file.write(vertex_data)

    @classmethod
    def read(cls, file):
        vertex = Vertex()
        vertex_data = file.read(vertex_size)
        vertex_struct = struct.unpack(vertex_format, vertex_data)

        vertex.x = vertex_struct[_VERTEX_X]
        vertex.y = vertex_struct[_VERTEX_Y]
        vertex.z = vertex_struct[_VERTEX_Z]

        return vertex


class Node(object):
    """Class for representing a node

    A Node is a data structure used to compose a bsp tree data structure. A
    child may be a Node or a Leaf.

    Attributes:
        plane_number: The number of the plane that partitions the node.

        children: A two-tuple of the two sub-spaces formed by the partitioning
            plane.

            Note: Child 0 is the front sub-space, and 1 is the back sub-space.

            Note: If bit 15 is set, the child is a leaf.

        bounding_box_min: The minimum coordinate of the bounding box containing
            this node and all of its children.

        bounding_box_max: The maximum coordinate of the bounding box containing
            this node and all of its children.

        first_face: The number of the first face in Bsp.mark_surfaces.

        number_of_faces: The number of faces contained in the node. These
            are stored in consecutive order in Bsp.mark_surfaces starting at
            Node.first_face.
    """

    __slots__ = (
        'plane_number',
        'children',
        'bounding_box_min',
        'bounding_box_max',
        'first_face',
        'number_of_faces'
    )

    def __init__(self):
        self.plane_number = None
        self.children = None
        self.bounding_box_min = None
        self.bounding_box_max = None
        self.first_face = None
        self.number_of_faces = None

    @classmethod
    def write(cls, file, node):
        node_data = struct.pack(node_format,
                                node.plane_number,
                                *node.children,
                                *node.bounding_box_min,
                                *node.bounding_box_max,
                                node.first_face,
                                node.number_of_faces)

        file.write(node_data)

    @classmethod
    def read(cls, file):
        node = Node()
        node_data = file.read(node_size)
        node_struct = struct.unpack(node_format, node_data)

        node.plane_number = node_struct[_NODE_PLANE_NUMBER]
        node.children = node_struct[_NODE_CHILDREN:_NODE_BOUNDING_BOX_MIN]
        node.bounding_box_min = node_struct[_NODE_BOUNDING_BOX_MIN:_NODE_BOUNDING_BOX_MAX]
        node.bounding_box_max = node_struct[_NODE_BOUNDING_BOX_MAX:_NODE_FIRST_FACE]
        node.first_face = node_struct[_NODE_FIRST_FACE]
        node.number_of_faces = node_struct[_NODE_NUMBER_OF_FACES]

        return node


class TextureInfo(object):
    """Class for representing a texture info

    Attributes:
        s: The s vector in texture space represented as an XYZ three-tuple.

        s_offset: Horizontal offset in texture space.

        t: The t vector in texture space represented as an XYZ three-tuple.

        t_offset: Vertical offset in texture space.

        miptexture_number: The index of the miptexture.

        flags: If set to 1 the texture will be animated like water.
    """

    __slots__ = (
        's',
        's_offset',
        't',
        't_offset',
        'miptexture_number',
        'flags'
    )

    def __init__(self):
        self.s = None
        self.s_offset = None
        self.t = None
        self.t_offset = None
        self.miptexture_number = None
        self.flags = None

    @classmethod
    def write(cls, file, texture_info):
        texture_info_data = struct.pack(texture_info_format,
                                        *texture_info.s,
                                        texture_info.s_offset,
                                        *texture_info.t,
                                        texture_info.t_offset,
                                        texture_info.miptexture_number,
                                        texture_info.flags)
        file.write(texture_info_data)

    @classmethod
    def read(cls, file):
        texture_info = TextureInfo()
        texture_info_data = file.read(texture_info_size)
        texture_info_struct = struct.unpack(texture_info_format, texture_info_data)

        texture_info.s = texture_info_struct[_TEXTURE_INFO_S:_TEXTURE_INFO_S_OFFSET]
        texture_info.s_offset = texture_info_struct[_TEXTURE_INFO_S_OFFSET]
        texture_info.t = texture_info_struct[_TEXTURE_INFO_T:_TEXTURE_INFO_T_OFFSET]
        texture_info.t_offset = texture_info_struct[_TEXTURE_INFO_T_OFFSET]
        texture_info.miptexture_number = texture_info_struct[_TEXTURE_INFO_MIPTEXTURE_NUMBER]
        texture_info.flags = texture_info_struct[_TEXTURE_INFO_FLAGS]

        return texture_info


class Face(object):
    """Class for representing a face

    Attributes:
        plane_number: The plane in which the face lies.

        side: Which side of the plane the face lies. 0 is the front, 1 is the
            back.

        first_edge: The number of the first edge in Bsp.surf_edges.

        number_of_edges: The number of edges contained within the face. These
            are stored in consecutive order in Bsp.surf_edges starting at
            Face.first_edge.

        texture_info: The number of the texture info for this face.

        styles: A four-tuple of lightmap styles.

        light_offset: The offset into the lighting data.
    """

    __slots__ = (
        'plane_number',
        'side',
        'first_edge',
        'number_of_edges',
        'texture_info',
        'styles',
        'light_offset'
    )

    def __init__(self):
        self.plane_number = None
        self.side = None
        self.first_edge = None
        self.number_of_edges = None
        self.texture_info = None
        self.styles = None
        self.light_offset = None

    @classmethod
    def write(cls, file, plane):
        face_data = struct.pack(face_format,
                                plane.plane_number,
                                plane.side,
                                plane.first_edge,
                                plane.number_of_edges,
                                plane.texture_info,
                                *plane.styles,
                                plane.light_offset)

        file.write(face_data)

    @classmethod
    def read(cls, file):
        face = Face()
        face_data = file.read(face_size)
        face_struct = struct.unpack(face_format, face_data)

        face.plane_number = face_struct[_FACE_PLANE_NUMBER]
        face.side = face_struct[_FACE_SIDE]
        face.first_edge = face_struct[_FACE_FIRST_EDGE]
        face.number_of_edges = face_struct[_FACE_NUMBER_OF_EDGES]
        face.texture_info = face_struct[_FACE_TEXTURE_INFO]
        face.styles = face_struct[_FACE_STYLES:_FACE_LIGHT_OFFSET]
        face.light_offset = face_struct[_FACE_LIGHT_OFFSET]

        return face


class ClipNode(object):
    """Class for representing a clip node

    Attributes:
        plane_number: The number of the plane that partitions the node.

        children: A two-tuple of the two sub-spaces formed by the partitioning
            plane.

            Note: Child 0 is the front sub-space, and 1 is the back sub-space.
    """

    __slots__ = (
        'plane_number',
        'children'
    )

    def __init__(self):
        self.plane_number = None
        self.children = None

    @classmethod
    def write(cls, file, clip_node):
        clip_node_data = struct.pack(clip_node_format,
                                     clip_node.plane_number,
                                     *clip_node.children)

        file.write(clip_node_data)

    @classmethod
    def read(cls, file):
        clip_node = ClipNode()
        clip_node_data = file.read(clip_node_size)
        clip_node_struct = struct.unpack(clip_node_format, clip_node_data)

        clip_node.plane_number = clip_node_struct[_CLIP_NODE_PLANE_NUMBER]
        clip_node.children = clip_node_struct[_CLIP_NODE_CHILDREN:]

        return clip_node


CONTENTS_EMPTY = -1
CONTENTS_SOLID = -2
CONTENTS_WATER = -3
CONTENTS_SLIME = -4
CONTENTS_LAVA = -5
CONTENTS_SKY = -6

AMBIENT_WATER = 0
AMBIENT_SKY = 1
AMBIENT_SLIME = 2
AMBIENT_LAVA = 3


class Leaf(object):
    """Class for representing a leaf

    Attributes:
        contents: The content of the leaf. Affect the player's view.

        visibilitiy_offset: The offset into the visibility data.

        bounding_box_min: The minimum coordinate of the bounding box containing
            this node.

        bounding_box_max: The maximum coordinate of the bounding box containing
            this node.

        first_mark_surface: The number of the first face in Bsp.mark_surfaces.

        number_of_marked_surfaces: The number of surfaces contained within the
            leaf. These are stored in consecutive order in Bsp.mark_surfaces
            starting at Leaf.first_mark_surface.

        ambient_level: A four-tuple that represent the volume of the four
            ambient sounds.
    """

    __slots__ = (
        'contents',
        'visibilitiy_offset',
        'bounding_box_min',
        'bounding_box_max',
        'first_mark_surface',
        'number_of_marked_surfaces',
        'ambient_level'
    )

    def __init__(self):
        self.contents = None
        self.visibilitiy_offset = None
        self.bounding_box_min = None
        self.bounding_box_max = None
        self.first_mark_surface = None
        self.number_of_marked_surfaces = None
        self.ambient_level = None

    @classmethod
    def write(cls, file, leaf):
        leaf_data = struct.pack(leaf_format,
                                    leaf.contents,
                                    leaf.visibilitiy_offset,
                                    *leaf.bounding_box_min,
                                    *leaf.bounding_box_max,
                                    leaf.first_mark_surface,
                                    leaf.number_of_marked_surfaces,
                                    *leaf.ambient_level)

        file.write(leaf_data)

    @classmethod
    def read(cls, file):
        leaf = Leaf()
        leaf_data = file.read(leaf_size)
        leaf_struct = struct.unpack(leaf_format, leaf_data)

        leaf.contents = leaf_struct[_LEAF_CONTENTS]
        leaf.visibilitiy_offset = leaf_struct[_LEAF_VISIBILITIY_OFFSET]
        leaf.bounding_box_min = leaf_struct[_LEAF_BOUNDING_BOX_MIN:_LEAF_BOUNDING_BOX_MAX]
        leaf.bounding_box_max = leaf_struct[_LEAF_BOUNDING_BOX_MAX:_LEAF_FIRST_MARK_SURFACE]
        leaf.first_mark_surface = leaf_struct[_LEAF_FIRST_MARK_SURFACE]
        leaf.number_of_marked_surfaces = leaf_struct[_LEAF_NUMBER_OF_MARKED_SURFACES]
        leaf.ambient_level = leaf_struct[_LEAF_AMBIENT_LEVEL:]

        return leaf


class Edge(object):
    """Class for representing a edge

    Attributes:
        vertexes: A two-tuple of vertexes that form the edge. Vertex 0 is the
            start vertex, and 1 is the end vertex.
    """

    __slots__ = (
        'vertexes'
    )

    def __init__(self):
        self.vertexes = None

    def __getitem__(self, item):
        if item > 1:
            raise IndexError('list index of out of range')

        return self.vertexes[item]

    @classmethod
    def write(cls, file, edge):
        edge_data = struct.pack(edge_format,
                                *edge.vertexes)

        file.write(edge_data)

    @classmethod
    def read(cls, file):
        edge = Edge()
        edge_data = file.read(edge_size)
        edge_struct = struct.unpack(edge_format, edge_data)

        edge.vertexes = edge_struct[:]

        return edge


class Model(object):
    """Class for representing a model

    Attributes:
        bounding_box_min: The minimum coordinate of the bounding box containing
            the model.

        bounding_box_max: The maximum coordinate of the bounding box containing
            the model.

        origin: The origin of the model.

        head_node: A four-tuple of indexes. Corresponds to number of map hulls.

        visleafs: The number of leaves in the bsp tree?

        first_face: The number of the first face in Bsp.mark_surfaces.

        number_of_faces: The number of faces contained in the node. These
            are stored in consecutive order in Bsp.mark_surfaces starting at
            Model.first_face.
    """

    __slots__ = (
        'bounding_box_min',
        'bounding_box_max',
        'origin',
        'head_node',
        'visleafs',
        'first_face',
        'number_of_faces'
    )

    def __init__(self):
        self.bounding_box_min = None
        self.bounding_box_max = None
        self.origin = None
        self.head_node = None
        self.visleafs = None
        self.first_face = None
        self.number_of_faces = None

    @classmethod
    def write(cls, file, model):
        model_data = struct.pack(model_format,
                                 *model.bounding_box_min,
                                 *model.bounding_box_max,
                                 *model.origin,
                                 *model.head_node,
                                 model.visleafs,
                                 model.first_face,
                                 model.number_of_faces)

        file.write(model_data)

    @classmethod
    def read(cls, file):
        model = Model()
        model_data = file.read(model_size)
        model_struct = struct.unpack(model_format, model_data)

        model.bounding_box_min = model_struct[_MODEL_BOUNDING_BOX_MIN:_MODEL_BOUNDING_BOX_MAX]
        model.bounding_box_max = model_struct[_MODEL_BOUNDING_BOX_MAX:_MODEL_ORIGIN]
        model.origin = model_struct[_MODEL_ORIGIN:_MODEL_HEAD_NODE]
        model.head_node = model_struct[_MODEL_HEAD_NODE:_MODEL_VISLEAFS]
        model.visleafs = model_struct[_MODEL_VISLEAFS]
        model.first_face = model_struct[_MODEL_FIRST_FACE]
        model.number_of_faces = model_struct[_MODEL_NUMBER_OF_FACES]

        return model


class Mesh(object):
    """Class for representing mesh data

    Attributes:
        vertices: A list of vertex data represented as XYZ three-tuples.

        triangles: A list of triangle data represented by a three-tuple of
            vertex indexes.

        uvs: A list of uv coordinates represented as UV tuples.

        normals: A list of vertex normal data represented as XYZ three-tuples.

        sub_meshes: A list of triangle index lists.
    """

    __slots = (
        'vertices',
        'triangles',
        'uvs',
        'normals',
        'sub_meshes'
    )

    def __init__(self):
        self.vertices = []
        self.triangles = []
        self.uvs = []
        self.normals = []
        self.sub_meshes = []


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


class Bsp(object):
    """Class for working with Bsp files

    Example:
        b = Bsp.open(file)

    Attributes:
        version: Version of the map file. Vanilla Quake is 29.

        entities: A string containing the entity definitions.

        planes: A list of Planes used by the bsp tree data structure.

        miptextures: A list of Miptextures.

        vertexes: A list of Vertexes.

        visibilities: A list of ints representing visibility data.

        nodes: A list of Nodes used by the bsp tree data structure.

        texture_infos: A list of TextureInfo objects.

        faces: A list of Faces.

        lighting: A list of ints representing lighting data.

        clip_nodes: A list of ClipNodes used by the bsp tree data structure.

        leafs: A list of Leafs used by the bsp tree data structure.

        mark_surfaces: A list of ints representing lists of consecutive faces
            used by the Node objects.

        edges: A list of Edges.

        surf_edges: A list of ints representing  list of consecutive edges used
            by the Face objects.

        models: A list of Models.

            Note: The first model is the entire level.

        fp: The file-like object to read data from.

        mode: The file mode for the file-like object.
    """

    def __init__(self):
        self.fp = None
        self.mode = None
        self._did_modify = False

        self.version = header_version
        self.entities = b""
        self.planes = []
        self.miptextures = []
        self.vertexes = []
        self.visibilities = []
        self.nodes = []
        self.texture_infos = []
        self.faces = []
        self.lighting = []
        self.clip_nodes = []
        self.leafs = []
        self.mark_surfaces = []
        self.edges = []
        self.surf_edges = []
        self.models = []

    @classmethod
    def open(cls, file, mode='r'):
        """Returns a Bsp object

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: Currently the only supported mode is 'r'

        Returns:
            An Bsp object constructed from the information read from the
            file-like object.
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
                "Bsp.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        if mode == 'r':
            bsp = Bsp._read_file(file, mode)

            return bsp

        elif mode == 'w':
            bsp = Bsp()
            bsp.fp = file
            bsp.mode = 'w'
            bsp._did_modify = True

            return bsp

        elif mode == 'a':
            bsp = Bsp._read_file(file, mode)
            bsp._did_modify = True

            return bsp

    @classmethod
    def _read_file(cls, file, mode):
        bsp = Bsp()
        bsp.mode = mode
        bsp.fp = file

        # Header
        bsp_data = file.read(header_size)
        bsp_struct = struct.unpack(header_format, bsp_data)

        bsp.version = bsp_struct[_HEADER_VERSION]

        # Entities
        entities_offset = bsp_struct[_HEADER_ENTITIES_OFFSET]
        entities_size = bsp_struct[_HEADER_ENTITIES_SIZE]

        file.seek(entities_offset)
        bsp.entities = file.read(entities_size)

        # Planes
        planes_offset = bsp_struct[_HEADER_PLANES_OFFSET]
        planes_size = bsp_struct[_HEADER_PLANES_SIZE]
        number_of_planes = planes_size // plane_size

        file.seek(planes_offset)
        for _ in range(number_of_planes):
            plane = Plane.read(file)
            bsp.planes.append(plane)

        # Miptextures
        miptextures_offset = bsp_struct[_HEADER_MIPTEXTURES_OFFSET]

        # Miptexture directory
        file.seek(miptextures_offset)
        number_of_miptextures = struct.unpack('<i', file.read(4))[0]
        offset_format = '<%di' % number_of_miptextures
        offset_data = file.read(4 * number_of_miptextures)
        miptexture_offsets = struct.unpack(offset_format, offset_data)

        for miptexture_id in range(number_of_miptextures):
            if miptexture_offsets[miptexture_id] == -1:
                bsp.miptextures.append(None)
                continue

            offset = miptextures_offset + miptexture_offsets[miptexture_id]
            file.seek(offset)

            bsp.miptextures.append(Miptexture.read(file))

        # Vertexes
        vertexes_offset = bsp_struct[_HEADER_VERTEXES_OFFSET]
        vertexes_size = bsp_struct[_HEADER_VERTEXES_SIZE]
        number_of_vertexes = vertexes_size // vertex_size

        file.seek(vertexes_offset)
        for _ in range(number_of_vertexes):
            bsp.vertexes.append(Vertex.read(file))

        # Visibilities
        visibilities_offset = bsp_struct[_HEADER_VISIBILITIES_OFFSET]
        visibilities_size = bsp_struct[_HEADER_VISIBILITIES_SIZE]
        visibility_format = _calculate_visibility_format(visibilities_size)

        file.seek(visibilities_offset)
        visibilities_data = file.read(visibilities_size)
        bsp.visibilities = struct.unpack(visibility_format, visibilities_data)

        # Nodes
        nodes_offset = bsp_struct[_HEADER_NODES_OFFSET]
        nodes_size = bsp_struct[_HEADER_NODES_SIZE]
        number_of_nodes = nodes_size // node_size

        file.seek(nodes_offset)
        for _ in range(number_of_nodes):
            bsp.nodes.append(Node.read(file))

        # Texture Infos
        texture_infos_offset = bsp_struct[_HEADER_TEXTURE_INFOS_OFFSET]
        texture_infos_size = bsp_struct[_HEADER_TEXTURE_INFOS_SIZE]
        number_of_texture_infos = texture_infos_size // texture_info_size

        file.seek(texture_infos_offset)
        for _ in range(number_of_texture_infos):
            bsp.texture_infos.append(TextureInfo.read(file))

        # Faces
        faces_offset = bsp_struct[_HEADER_FACES_OFFSET]
        faces_size = bsp_struct[_HEADER_FACES_SIZE]
        number_of_faces = faces_size // face_size

        file.seek(faces_offset)
        for _ in range(number_of_faces):
            bsp.faces.append(Face.read(file))

        # Lighting
        lighting_offset = bsp_struct[_HEADER_LIGHTING_OFFSET]
        lighting_size = bsp_struct[_HEADER_LIGHTING_SIZE]
        lighting_format = _calculate_lighting_format(lighting_size)

        file.seek(lighting_offset)
        lighting_data = file.read(lighting_size)
        bsp.lighting = struct.unpack(lighting_format, lighting_data)

        # Clip Nodes
        clip_nodes_offset = bsp_struct[_HEADER_CLIP_NODES_OFFSET]
        clip_nodes_size = bsp_struct[_HEADER_CLIP_NODES_SIZE]
        number_of_clip_nodes = clip_nodes_size // clip_node_size

        file.seek(clip_nodes_offset)
        for _ in range(number_of_clip_nodes):
            bsp.clip_nodes.append(ClipNode.read(file))

        # Leafs
        leafs_offset = bsp_struct[_HEADER_LEAFS_OFFSET]
        leafs_size = bsp_struct[_HEADER_LEAFS_SIZE]
        number_of_leafs = leafs_size // leaf_size

        file.seek(leafs_offset)
        for _ in range(number_of_leafs):
            bsp.leafs.append(Leaf.read(file))

        # Mark Surfaces
        mark_surfaces_offset = bsp_struct[_HEADER_MARK_SURFACES_OFFSET]
        mark_surfaces_size = bsp_struct[_HEADER_MARK_SURFACES_SIZE]
        mark_surfaces_format = _calculate_mark_surface_format(mark_surfaces_size)

        file.seek(mark_surfaces_offset)
        mark_surfaces_data = file.read(mark_surfaces_size)
        bsp.mark_surfaces = struct.unpack(mark_surfaces_format,
                                          mark_surfaces_data)

        # Edges
        edges_offset = bsp_struct[_HEADER_EDGES_OFFSET]
        edges_size = bsp_struct[_HEADER_EDGES_SIZE]
        number_of_edges = edges_size // edge_size

        file.seek(edges_offset)
        for _ in range(number_of_edges):
            bsp.edges.append(Edge.read(file))

        # Surf Edges
        surf_edges_offset = bsp_struct[_HEADER_SURF_EDGES_OFFSET]
        surf_edges_size = bsp_struct[_HEADER_SURF_EDGES_SIZE]
        surf_edges_format = _calculate_surf_edge_format(surf_edges_size)

        file.seek(surf_edges_offset)
        surf_edges_data = file.read(surf_edges_size)
        bsp.surf_edges = struct.unpack(surf_edges_format, surf_edges_data)

        # Models
        models_offset = bsp_struct[_HEADER_MODELS_OFFSET]
        models_size = bsp_struct[_HEADER_MODELS_SIZE]
        number_of_models = models_size // model_size

        file.seek(models_offset)
        for _ in range(number_of_models):
            bsp.models.append(Model.read(file))

        return bsp

    @classmethod
    def _write_file(cls, file, bsp):
        # Stub out header info
        header_data = struct.pack(header_format,
                                  bsp.version,
                                  *([0]*30))

        file.write(header_data)

        # Entities
        entities_offset = file.tell()
        file.write(bsp.entities)
        entities_size = file.tell() - entities_offset

        # Planes
        planes_offset = file.tell()

        for plane in bsp.planes:
            Plane.write(file, plane)

        planes_size = file.tell() - planes_offset

        # Miptextures
        miptextures_offset = file.tell()

        # Miptexture directory
        number_of_miptextures = len(bsp.miptextures)
        file.write(struct.pack('<i', number_of_miptextures))
        offset_format = '<%di' % number_of_miptextures

        # Stub out directory info
        miptexture_offsets = [0] * number_of_miptextures
        file.write(struct.pack(offset_format, *miptexture_offsets))

        for i, miptex in enumerate(bsp.miptextures):
            if not miptex:
                miptexture_offsets[i] = -1
                continue

            miptexture_offsets[i] = file.tell() - miptextures_offset
            Miptexture.write(file, miptex)

        # Write directory info
        vertexes_offset = file.tell()
        file.seek(miptextures_offset + 4)
        file.write(struct.pack(offset_format, *miptexture_offsets))
        file.seek(vertexes_offset)

        miptextures_size = file.tell() - miptextures_offset

        # Vertexes
        for vertex in bsp.vertexes:
            Vertex.write(file, vertex)

        vertexes_size = file.tell() - vertexes_offset

        # Visibilities
        visibilities_offset = file.tell()
        visibilities_format = _calculate_visibility_format(len(bsp.visibilities))
        file.write(struct.pack(visibilities_format, *bsp.visibilities))
        visibilities_size = file.tell() - visibilities_offset

        # Nodes
        nodes_offset = file.tell()

        for node in bsp.nodes:
            Node.write(file, node)

        nodes_size = file.tell() - nodes_offset

        # Texture Infos
        texture_infos_offset = file.tell()

        for tex_info in bsp.texture_infos:
            TextureInfo.write(file, tex_info)

        texture_infos_size = file.tell() - texture_infos_offset

        # Faces
        faces_offset = file.tell()

        for face in bsp.faces:
            Face.write(file, face)

        faces_size = file.tell() - faces_offset

        # Lighting
        lighting_offset = file.tell()
        lighting_format = _calculate_lighting_format(len(bsp.lighting))
        file.write(struct.pack(lighting_format, *bsp.lighting))
        lighting_size = file.tell() - lighting_offset

        # Clip Nodes
        clip_nodes_offset = file.tell()

        for clip_node in bsp.clip_nodes:
            ClipNode.write(file, clip_node)

        clip_nodes_size = file.tell() - clip_nodes_offset

        # Leafs
        leafs_offset = file.tell()

        for leaf in bsp.leafs:
            Leaf.write(file, leaf)

        leafs_size = file.tell() - leafs_offset

        # Mark Surfaces
        mark_surfaces_offset = file.tell()
        mark_surface_format = _calculate_mark_surface_format(len(bsp.mark_surfaces))
        file.write(struct.pack(mark_surface_format, *bsp.mark_surfaces))
        mark_surfaces_size = file.tell() - mark_surfaces_offset

        # Edges
        edges_offset = file.tell()

        for edge in bsp.edges:
            Edge.write(file, edge)

        edges_size = file.tell() - edges_offset

        # Surf Edges
        surf_edges_offset = file.tell()

        number_of_surf_edges = len(bsp.surf_edges)
        surf_edge_format = _calculate_surf_edge_format(number_of_surf_edges * 4)
        file.write(struct.pack(surf_edge_format, *bsp.surf_edges))
        surf_edges_size = file.tell() - surf_edges_offset

        # Models
        models_offset = file.tell()

        for model in bsp.models:
            Model.write(file, model)

        models_size = file.tell() - models_offset
        end_of_file = file.tell()

        # Write header info
        file.seek(0)
        header_data = struct.pack(header_format,
                                  bsp.version,
                                  entities_offset,
                                  entities_size,
                                  planes_offset,
                                  planes_size,
                                  miptextures_offset,
                                  miptextures_size,
                                  vertexes_offset,
                                  vertexes_size,
                                  visibilities_offset,
                                  visibilities_size,
                                  nodes_offset,
                                  nodes_size,
                                  texture_infos_offset,
                                  texture_infos_size,
                                  faces_offset,
                                  faces_size,
                                  lighting_offset,
                                  lighting_size,
                                  clip_nodes_offset,
                                  clip_nodes_size,
                                  leafs_offset,
                                  leafs_size,
                                  mark_surfaces_offset,
                                  mark_surfaces_size,
                                  edges_offset,
                                  edges_size,
                                  surf_edges_offset,
                                  surf_edges_size,
                                  models_offset,
                                  models_size)

        file.write(header_data)
        file.seek(end_of_file)

    def save(self, file):
        should_close = False

        if isinstance(file, str):
            file = io.open(file, 'r+b')
            should_close = True

        elif isinstance(file, bytes):
            file = io.BytesIO(file)
            should_close = True

        elif not hasattr(file, 'write'):
            raise RuntimeError(
                "Bsp.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        Bsp._write_file(file, self)

        if should_close:
            file.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if self.mode in ('w', 'a') and self._did_modify:
            self.fp.seek(0)
            Bsp._write_file(self.fp, self)
            self.fp.truncate()

        file_object = self.fp
        self.fp = None
        file_object.close()

    def mesh(self, model=0):
        """Returns a Mesh object

        Args:
            model: The index of the model to get mesh data for.

        Returns:
            A Mesh object
        """

        def dot(v0, v1):
            return v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]

        def cross(v0, v1):
            return v0[1] * v1[2] - v0[2] * v1[1], \
                   v0[2] * v1[0] - v0[0] * v1[2], \
                   v0[0] * v1[1] - v0[1] * v1[0]

        def sub(v0, v1):
            return v0[0] - v1[0], v0[1] - v1[1], v0[2] - v1[2]

        if model > len(self.models):
            raise IndexError('list index out of range')

        model = self.models[model]

        mesh = Mesh()
        mesh.sub_meshes = [[] for _ in range(len(self.miptextures))]

        faces = self.faces[model.first_face:model.first_face + model.number_of_faces]

        for face in faces:
            texture_info = self.texture_infos[face.texture_info]
            miptex = self.miptextures[texture_info.miptexture_number]

            s = texture_info.s
            ds = texture_info.s_offset
            t = texture_info.t
            dt = texture_info.t_offset

            w = miptex.width
            h = miptex.height

            edges = self.surf_edges[face.first_edge:face.first_edge + face.number_of_edges]

            verts = []
            for edge in edges:
                v = self.edges[abs(edge)].vertexes

                # Flip edges with negative ids
                v0, v1 = v if edge > 0 else reversed(v)

                if len(verts) == 0:
                    verts.append(v0)

                if v1 != verts[0]:
                    verts.append(v1)

            # Convert Vertexes to three-tuples and reverse their order
            verts = [tuple(self.vertexes[i][:]) for i in reversed(verts)]

            # Convert ST coordinate space to UV coordinate space
            uvs = [((dot(v, s) + ds) / w, -(dot(v, t) + dt) / h) for v in verts]

            # Calculate face normal
            normal = cross(sub(verts[0], verts[1]), sub(verts[0], verts[2]))

            # Determine indices of vertices added
            start_index = len(mesh.vertices)
            stop_index = start_index + len(verts)
            vert_indices = list(range(start_index, stop_index))

            # Simple convex polygon triangulation
            tris = []
            v0 = vert_indices[0]
            for i in range(1, len(vert_indices) - 1):
                v1 = vert_indices[i]
                v2 = vert_indices[i+1]
                tris.append((v0, v1, v2))

            # Determine indices of triangles added
            tri_start = len(mesh.triangles)
            tri_stop = tri_start + len(tris)
            tri_indices = list(range(tri_start, tri_stop))

            mesh.vertices += verts
            mesh.uvs += uvs
            mesh.normals += (normal,) * len(verts)
            mesh.triangles += tris
            mesh.sub_meshes[texture_info.miptexture_number] += tri_indices

        return mesh

    def meshes(self):
        return [self.mesh(i) for i in range(len(self.models))]

    def image(self, index=0, palette=default_palette):
        """Returns an Image object.

        Args:
            index: The index of the skin to get image data for.

            palette: A 256 color palette to use for converted index color data to
                RGB data.

        Returns:
            An Image object or None.

            Note: Not all indices are valid miptextures.
        """

        if index > len(self.miptextures):
            raise IndexError('list index out of range')

        miptex = self.miptextures[index]
        if miptex is None:
            return None

        image = Image()
        image.width = miptex.width
        image.height = miptex.height
        image.pixels = miptex.pixels[:miptex.width * miptex.height]

        p = []
        for row in reversed(range(image.height)):
            p += image.pixels[row * image.width:(row + 1) * image.width]

        d = []

        for i in p:
            d += palette[i]
            d += [255] if i is not 255 else [0]

        image.pixels = d

        return image

    def images(self):
        return [self.image(i) for i in range(len(self.miptextures))]
