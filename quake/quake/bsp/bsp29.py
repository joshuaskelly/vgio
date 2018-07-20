"""This module provides file I/O for Quake BSP map files.

Example:
    bsp_file = bsp.Bsp.open('e1m1.bsp')

References:
    Quake Source
    - id Software
    - https://github.com/id-Software/Quake

    Quake Documentation Version 3.4
    - Olivier Montanuy, et al.
    - http://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_4.htm
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


# Visibility structure
def _calculate_visibility_format(size):
    return '<%dB' % size

visibility_format = None
visibility_size = None


# Lighting structure
def _calculate_lighting_format(size):
    return '<%dB' % size

lighting_format = None
lighting_size = None


# Mark Surface structure
def _calculate_mark_surface_format(size):
    return '<%dB' % size

mark_surface_format = None
mark_surface_size = None


# Surf Edge structure
def _calculate_surf_edge_format(size):
    return '<%di' % (size // 4)

surf_edge_format = None
surf_edge_size = None


def _check_bspfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<1l'))
    version = struct.unpack('<1l', data)[0]

    return version == header_version


def is_bspfile(filename):
    """Quickly see if a file is a bsp file by checking the magic number.

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

    format = '<4fi'
    size = struct.calcsize(format)

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
        plane_data = struct.pack(cls.format,
                                 *plane.normal,
                                 plane.distance,
                                 plane.type)

        file.write(plane_data)

    @classmethod
    def read(cls, file):
        plane = Plane()
        plane_data = file.read(cls.size)
        plane_struct = struct.unpack(cls.format, plane_data)
        plane.normal = plane_struct[0:3]
        plane.distance = plane_struct[3]
        plane.type = plane_struct[4]

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

    format = '<16s6I'
    size = struct.calcsize(format)

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
        miptexture_data = struct.pack(cls.format,
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
        miptexture_data = file.read(cls.size)
        miptexture_struct = struct.unpack(cls.format, miptexture_data)
        miptexture.name = miptexture_struct[0].split(b'\00')[0].decode('ascii')
        miptexture.width = miptexture_struct[1]
        miptexture.height = miptexture_struct[2]
        miptexture.offsets = miptexture_struct[3:]

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

    format = '<3f'
    size = struct.calcsize(format)

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
        vertex_data = struct.pack(cls.format,
                                  vertex.x,
                                  vertex.y,
                                  vertex.z)

        file.write(vertex_data)

    @classmethod
    def read(cls, file):
        vertex = Vertex()
        vertex_data = file.read(cls.size)
        vertex_struct = struct.unpack(cls.format, vertex_data)

        vertex.x = vertex_struct[0]
        vertex.y = vertex_struct[1]
        vertex.z = vertex_struct[2]

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

    format = '<i8h2H'
    size = struct.calcsize(format)

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
        node_data = struct.pack(cls.format,
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
        node_data = file.read(cls.size)
        node_struct = struct.unpack(cls.format, node_data)

        node.plane_number = node_struct[0]
        node.children = node_struct[1:3]
        node.bounding_box_min = node_struct[3:6]
        node.bounding_box_max = node_struct[6:9]
        node.first_face = node_struct[9]
        node.number_of_faces = node_struct[10]

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

    format = '<8f2i'
    size = struct.calcsize(format)

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
        texture_info_data = struct.pack(cls.format,
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
        texture_info_data = file.read(cls.size)
        texture_info_struct = struct.unpack(cls.format, texture_info_data)

        texture_info.s = texture_info_struct[0:3]
        texture_info.s_offset = texture_info_struct[3]
        texture_info.t = texture_info_struct[4:7]
        texture_info.t_offset = texture_info_struct[7]
        texture_info.miptexture_number = texture_info_struct[8]
        texture_info.flags = texture_info_struct[9]

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

    format = '<2hi2h4Bi'
    size = struct.calcsize(format)

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
        face_data = struct.pack(cls.format,
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
        face_data = file.read(cls.size)
        face_struct = struct.unpack(cls.format, face_data)

        face.plane_number = face_struct[0]
        face.side = face_struct[1]
        face.first_edge = face_struct[2]
        face.number_of_edges = face_struct[3]
        face.texture_info = face_struct[4]
        face.styles = face_struct[5:9]
        face.light_offset = face_struct[9]

        return face


class ClipNode(object):
    """Class for representing a clip node

    Attributes:
        plane_number: The number of the plane that partitions the node.

        children: A two-tuple of the two sub-spaces formed by the partitioning
            plane.

            Note: Child 0 is the front sub-space, and 1 is the back sub-space.
    """

    format = '<i2h'
    size = struct.calcsize(format)

    __slots__ = (
        'plane_number',
        'children'
    )

    def __init__(self):
        self.plane_number = None
        self.children = None

    @classmethod
    def write(cls, file, clip_node):
        clip_node_data = struct.pack(cls.format,
                                     clip_node.plane_number,
                                     *clip_node.children)

        file.write(clip_node_data)

    @classmethod
    def read(cls, file):
        clip_node = ClipNode()
        clip_node_data = file.read(cls.size)
        clip_node_struct = struct.unpack(cls.format, clip_node_data)

        clip_node.plane_number = clip_node_struct[0]
        clip_node.children = clip_node_struct[1:]

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

    format = '<2i6h2H4B'
    size = struct.calcsize(format)

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
        leaf_data = struct.pack(cls.format,
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
        leaf_data = file.read(cls.size)
        leaf_struct = struct.unpack(cls.format, leaf_data)

        leaf.contents = leaf_struct[0]
        leaf.visibilitiy_offset = leaf_struct[1]
        leaf.bounding_box_min = leaf_struct[2:5]
        leaf.bounding_box_max = leaf_struct[5:8]
        leaf.first_mark_surface = leaf_struct[8]
        leaf.number_of_marked_surfaces = leaf_struct[9]
        leaf.ambient_level = leaf_struct[10:]

        return leaf


class Edge(object):
    """Class for representing a edge

    Attributes:
        vertexes: A two-tuple of vertexes that form the edge. Vertex 0 is the
            start vertex, and 1 is the end vertex.
    """

    format = '<2H'
    size = struct.calcsize(format)

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
        edge_data = struct.pack(cls.format,
                                *edge.vertexes)

        file.write(edge_data)

    @classmethod
    def read(cls, file):
        edge = Edge()
        edge_data = file.read(cls.size)
        edge_struct = struct.unpack(cls.format, edge_data)

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

    format = '<9f7i'
    size = struct.calcsize(format)

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
        model_data = struct.pack(cls.format,
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
        model_data = file.read(cls.size)
        model_struct = struct.unpack(cls.format, model_data)

        model.bounding_box_min = model_struct[0:3]
        model.bounding_box_max = model_struct[3:6]
        model.origin = model_struct[6:9]
        model.head_node = model_struct[9:13]
        model.visleafs = model_struct[13]
        model.first_face = model_struct[14]
        model.number_of_faces = model_struct[15]

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
        self.entities = ""
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

    @staticmethod
    def open(file, mode='r'):
        """Returns a Bsp object

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file

        Returns:
            An Bsp object constructed from the information read from the
            file-like object.

        Raises:
            ValueError: If an invalid file mode is given.

            RuntimeError: If the file argument is not a file-like object.
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

        # Read
        if mode == 'r':
            return Bsp._read_file(file, mode)

        # Write
        elif mode == 'w':
            bsp = Bsp()
            bsp.fp = file
            bsp.mode = 'w'
            bsp._did_modify = True

            return bsp

        # Append
        else:
            bsp = Bsp._read_file(file, mode)
            bsp._did_modify = True

            return bsp

    @staticmethod
    def _read_file(file, mode):
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
        entities_data = file.read(entities_size)

        # Sanitize any Quake color codes
        entities_data = bytearray(entities_data)
        entities_data = bytes(map(lambda x: x % 128, entities_data))

        entities = struct.unpack('<{}s'.format(entities_size), entities_data)[0].decode('ascii').strip('\x00')
        bsp.entities = entities

        # Planes
        planes_entry = bsp_struct[_HEADER_PLANES_OFFSET], bsp_struct[_HEADER_PLANES_SIZE]
        bsp.planes = Bsp._read_chunk(file, planes_entry, Plane)

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
        vertexes_entry = bsp_struct[_HEADER_VERTEXES_OFFSET], bsp_struct[_HEADER_VERTEXES_SIZE]
        bsp.vertexes = Bsp._read_chunk(file, vertexes_entry, Vertex)

        # Visibilities
        visibilities_offset = bsp_struct[_HEADER_VISIBILITIES_OFFSET]
        visibilities_size = bsp_struct[_HEADER_VISIBILITIES_SIZE]
        visibility_format = _calculate_visibility_format(visibilities_size)

        file.seek(visibilities_offset)
        visibilities_data = file.read(visibilities_size)
        bsp.visibilities = struct.unpack(visibility_format, visibilities_data)

        # Nodes
        nodes_entry = bsp_struct[_HEADER_NODES_OFFSET], bsp_struct[_HEADER_NODES_SIZE]
        bsp.nodes = Bsp._read_chunk(file, nodes_entry, Node)

        # Texture Infos
        texture_infos_entry = bsp_struct[_HEADER_TEXTURE_INFOS_OFFSET], bsp_struct[_HEADER_TEXTURE_INFOS_SIZE]
        bsp.texture_infos = Bsp._read_chunk(file, texture_infos_entry, TextureInfo)

        # Faces
        faces_entry = bsp_struct[_HEADER_FACES_OFFSET], bsp_struct[_HEADER_FACES_SIZE]
        bsp.faces = Bsp._read_chunk(file, faces_entry, Face)

        # Lighting
        lighting_offset = bsp_struct[_HEADER_LIGHTING_OFFSET]
        lighting_size = bsp_struct[_HEADER_LIGHTING_SIZE]
        lighting_format = _calculate_lighting_format(lighting_size)

        file.seek(lighting_offset)
        lighting_data = file.read(lighting_size)
        bsp.lighting = struct.unpack(lighting_format, lighting_data)

        # Clip Nodes
        clip_nodes_entry = bsp_struct[_HEADER_CLIP_NODES_OFFSET], bsp_struct[_HEADER_CLIP_NODES_SIZE]
        bsp.clip_nodes = Bsp._read_chunk(file, clip_nodes_entry, ClipNode)

        # Leafs
        leafs_entry = bsp_struct[_HEADER_LEAFS_OFFSET], bsp_struct[_HEADER_LEAFS_SIZE]
        bsp.leafs = Bsp._read_chunk(file, leafs_entry, Leaf)

        # Mark Surfaces
        mark_surfaces_offset = bsp_struct[_HEADER_MARK_SURFACES_OFFSET]
        mark_surfaces_size = bsp_struct[_HEADER_MARK_SURFACES_SIZE]
        mark_surfaces_format = _calculate_mark_surface_format(mark_surfaces_size)

        file.seek(mark_surfaces_offset)
        mark_surfaces_data = file.read(mark_surfaces_size)
        bsp.mark_surfaces = struct.unpack(mark_surfaces_format,
                                          mark_surfaces_data)

        # Edges
        edges_entry = bsp_struct[_HEADER_EDGES_OFFSET], bsp_struct[_HEADER_EDGES_SIZE]
        bsp.edges = Bsp._read_chunk(file, edges_entry, Edge)

        # Surf Edges
        surf_edges_offset = bsp_struct[_HEADER_SURF_EDGES_OFFSET]
        surf_edges_size = bsp_struct[_HEADER_SURF_EDGES_SIZE]
        surf_edges_format = _calculate_surf_edge_format(surf_edges_size)

        file.seek(surf_edges_offset)
        surf_edges_data = file.read(surf_edges_size)
        bsp.surf_edges = struct.unpack(surf_edges_format, surf_edges_data)

        # Models
        models_entry = bsp_struct[_HEADER_MODELS_OFFSET], bsp_struct[_HEADER_MODELS_SIZE]
        bsp.models = Bsp._read_chunk(file, models_entry, Model)

        return bsp

    @staticmethod
    def _read_chunk(file, chunk_entry, cls):
        chunk_offset, chunk_size = chunk_entry
        count = chunk_size // cls.size
        result = []
        file.seek(chunk_offset)

        for _ in range(count):
            result.append(cls.read(file))

        return result

    @staticmethod
    def _write_file(file, bsp):
        # Stub out header info
        header_data = struct.pack(header_format,
                                  bsp.version,
                                  *([0]*30))

        file.write(header_data)

        # Entities
        entities_offset = file.tell()
        file.write(str.encode(bsp.entities))
        entities_size = file.tell() - entities_offset

        # Planes
        planes_entry = Bsp._write_chunk(file, bsp.planes)

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
        vertexes_entry = Bsp._write_chunk(file, bsp.vertexes)

        # Visibilities
        visibilities_offset = file.tell()
        visibilities_format = _calculate_visibility_format(len(bsp.visibilities))
        file.write(struct.pack(visibilities_format, *bsp.visibilities))
        visibilities_size = file.tell() - visibilities_offset

        # Nodes
        nodes_entry = Bsp._write_chunk(file, bsp.nodes)

        # Texture Infos
        texture_infos_entry = Bsp._write_chunk(file, bsp.texture_infos)

        # Faces
        faces_entry = Bsp._write_chunk(file, bsp.faces)

        # Lighting
        lighting_offset = file.tell()
        lighting_format = _calculate_lighting_format(len(bsp.lighting))
        file.write(struct.pack(lighting_format, *bsp.lighting))
        lighting_size = file.tell() - lighting_offset

        # Clip Nodes
        clip_nodes_entry = Bsp._write_chunk(file, bsp.clip_nodes)

        # Leafs
        leafs_entry = Bsp._write_chunk(file, bsp.leafs)

        # Mark Surfaces
        mark_surfaces_offset = file.tell()
        mark_surface_format = _calculate_mark_surface_format(len(bsp.mark_surfaces))
        file.write(struct.pack(mark_surface_format, *bsp.mark_surfaces))
        mark_surfaces_size = file.tell() - mark_surfaces_offset

        # Edges
        edges_entry = Bsp._write_chunk(file, bsp.edges)

        # Surf Edges
        surf_edges_offset = file.tell()

        number_of_surf_edges = len(bsp.surf_edges)
        surf_edge_format = _calculate_surf_edge_format(number_of_surf_edges * 4)
        file.write(struct.pack(surf_edge_format, *bsp.surf_edges))
        surf_edges_size = file.tell() - surf_edges_offset

        # Models
        models_entry = Bsp._write_chunk(file, bsp.models)

        end_of_file = file.tell()

        # Write header info
        file.seek(0)
        header_data = struct.pack(header_format,
                                  bsp.version,
                                  entities_offset,
                                  entities_size,
                                  *planes_entry,
                                  miptextures_offset,
                                  miptextures_size,
                                  *vertexes_entry,
                                  visibilities_offset,
                                  visibilities_size,
                                  *nodes_entry,
                                  *texture_infos_entry,
                                  *faces_entry,
                                  lighting_offset,
                                  lighting_size,
                                  *clip_nodes_entry,
                                  *leafs_entry,
                                  mark_surfaces_offset,
                                  mark_surfaces_size,
                                  *edges_entry,
                                  surf_edges_offset,
                                  surf_edges_size,
                                  *models_entry)

        file.write(header_data)
        file.seek(end_of_file)

    @staticmethod
    def _write_chunk(file, data):
        offset = file.tell()

        if data:
            Class = data[0].__class__

            for datum in data:
                Class.write(file, datum)

        size = file.tell() - offset

        return offset, size

    def save(self, file):
        """Writes Bsp data to file

            Args:
                file: Either the path to the file, or a file-like object, or bytes.

            Raises:
                RuntimeError: If the file argument is not a file-like object.
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
        """Closes the file pointer if possible. If mode is 'w' or 'a', the file
        will be written to.
        """

        if self.fp:
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

            # Ignore degenerate faces
            if len(verts) < 3:
                continue

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
