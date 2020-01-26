"""This module provides file I/O for Half-Life BSP map files.

Example:
    bsp_file = bsp.Bsp.open('snarkpit.bsp')

References:
    Unofficial BSP v30 File Spec
    - http://hlbsp.sourceforge.net/index.php?content=bspdef

    Half-Life SDK Source
    - Valve Software
    - https://github.com/ValveSoftware/halflife/tree/master/dmc/cl_dll/DMC_BSPFile.h
"""

import struct

from vgio._core import ReadWriteFile


__all__ = ['BadBspFile', 'is_bspfile', 'Bsp']


VERSION = 30


class BadBspFile(Exception):
    pass


def _check_bspfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<1l'))
    version = struct.unpack('<1l', data)[0]

    return version == VERSION


def is_bspfile(filename):
    """Quickly see if a file is a bsp file by checking the magic number.

    The filename argument may be a file for file-like object.

    Args:
        filename: File to check as string or file-like object.

    Returns:
        True if given file's magic number is correct.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_bspfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_bspfile(fp)

    except Exception:
        return False


class Lump:
    """Class for representing a lump.

    A lump is a section of data that typically contains a sequence of data
    structures.

    Attributes:
        offset: The offset of the lump entry from the start of the file.

        length: The length of the lump entry.
    """

    format = '<2i'
    size = struct.calcsize(format)

    __slots__ = (
        'offset',
        'length'
    )

    def __init__(self, offset, length):
        self.offset = offset
        self.length = length

    @classmethod
    def write(cls, file, lump):
        lump_data = struct.pack(
            cls.format,
            lump.offset,
            lump.length
        )

        file.write(lump_data)

    @classmethod
    def read(cls, file):
        lump_data = file.read(cls.size)
        lump_struct = struct.unpack(cls.format, lump_data)

        return Lump(*lump_struct)


class Header:
    """Class for representing a Bsp file header

    Attributes:
        version: The file version. Should be 30.

        lumps: A sequence of fifteen Lump objects
    """

    format = '<i{}'.format(Lump.format[1:] * 15)
    size = struct.calcsize(format)

    __slots__ = (
        'version',
        '_lumps'
    )

    def __init__(self,
                 version,
                 lumps):
        self.version = version
        self._lumps = lumps

        if len(lumps) != 15:
            raise Exception

    @property
    def entities(self):
        return self._lumps[0]

    @entities.setter
    def entities(self, value):
        self._lumps[0] = value

    @property
    def planes(self):
        return self._lumps[1]

    @planes.setter
    def planes(self, value):
        self._lumps[1] = value

    @property
    def textures(self):
        return self._lumps[2]

    @textures.setter
    def textures(self, value):
        self._lumps[2] = value

    @property
    def vertexes(self):
        return self._lumps[3]

    @vertexes.setter
    def vertexes(self, value):
        self._lumps[3] = value

    @property
    def visibilities(self):
        return self._lumps[4]

    @visibilities.setter
    def visibilities(self, value):
        self._lumps[4] = value

    @property
    def nodes(self):
        return self._lumps[5]

    @nodes.setter
    def nodes(self, value):
        self._lumps[5] = value

    @property
    def texture_infos(self):
        return self._lumps[6]

    @texture_infos.setter
    def texture_infos(self, value):
        self._lumps[6] = value

    @property
    def faces(self):
        return self._lumps[7]

    @faces.setter
    def faces(self, value):
        self._lumps[7] = value

    @property
    def lighting(self):
        return self._lumps[8]

    @lighting.setter
    def lighting(self, value):
        self._lumps[8] = value

    @property
    def clip_nodes(self):
        return self._lumps[9]

    @clip_nodes.setter
    def clip_nodes(self, value):
        self._lumps[9] = value

    @property
    def leafs(self):
        return self._lumps[10]

    @leafs.setter
    def leafs(self, value):
        self._lumps[10] = value

    @property
    def mark_surfaces(self):
        return self._lumps[11]

    @mark_surfaces.setter
    def mark_surfaces(self, value):
        self._lumps[11] = value

    @property
    def edges(self):
        return self._lumps[12]

    @edges.setter
    def edges(self, value):
        self._lumps[12] = value

    @property
    def surf_edges(self):
        return self._lumps[13]

    @surf_edges.setter
    def surf_edges(self, value):
        self._lumps[13] = value

    @property
    def models(self):
        return self._lumps[14]

    @models.setter
    def models(self, value):
        self._lumps[14] = value

    @classmethod
    def write(cls, file, header):
        lump_values = []
        for lump in header._lumps:
            lump_values += lump.offset, lump.length

        header_data = struct.pack(
            cls.format,
            header.version,
            *lump_values
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        data = file.read(cls.size)
        lumps_start = struct.calcsize('<i')

        header_data = data[:lumps_start]
        header_struct = struct.unpack('<i', header_data)
        version = header_struct[0]

        lumps_data = data[lumps_start:]
        lumps = [Lump(*l) for l in struct.iter_unpack(Lump.format, lumps_data)]

        return Header(version, lumps)


class _Entities:
    """Helper class for working with the entities lump"""
    @staticmethod
    def write(file, entities):
        entities_data = entities.encode('cp437')
        file.write(entities_data)

    @staticmethod
    def read(file, size=-1):
        entities_data = file.read(size)
        return entities_data.decode('cp437').strip('\x00')


class Plane:
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

    def __init__(self,
                 normal_x,
                 normal_y,
                 normal_z,
                 distance,
                 type):

        self.normal = normal_x, normal_y, normal_z
        self.distance = distance
        self.type = type

    @classmethod
    def write(cls, file, plane):
        plane_data = struct.pack(
            cls.format,
            *plane.normal,
            plane.distance,
            plane.type
        )

        file.write(plane_data)

    @classmethod
    def read(cls, file):
        plane_data = file.read(cls.size)
        plane_struct = struct.unpack(cls.format, plane_data)

        return Plane(*plane_struct)


class Miptexture:
    """Class for representing a miptexture

    A miptexture is an indexed image mip map embedded within the map. Maps
    usually have many miptextures, and the miptexture lump is treated like a
    small wad file.

    Attributes:
        name: The name of the miptexture.

        width: The width of the miptexture.
            Note:
                This is the width at mipmap level 0.

        height: The height of the miptexture.
            Note:
                This is the height at mipmap level 0.

        offsets: The offsets for each of the mipmaps. This is a tuple of size
            four (this is the number of mipmap levels).

        pixels: Unstructured pixel data represented as bytes. A
            palette must be used to obtain RGB data.

            Note:
                This is the pixel data for all four mip levels. The size is
                calculated using the simplified form of the geometric series where
                r = 1/4 and n = 4.

            The size of this tuple is:

                miptexture.width * miptexture.height * 85 / 64

        palette: A sequence of 768 bytes representing a 256 RGB color palette.
    """

    format = '<16s6I'
    size = struct.calcsize(format)

    __slots__ = (
        'name',
        'width',
        'height',
        'offsets',
        'pixels',
        'palette'
    )

    def __init__(self,
                 name,
                 width,
                 height,
                 offsets=(0, 0, 0, 0),
                 pixels=b'',
                 palette=b''):
        """Constructs a MipTexture object."""

        self.name = name
        self.width = width
        self.height = height
        self.offsets = offsets
        self.pixels = pixels
        self.palette = palette

    @classmethod
    def write(cls, file, miptexture):
        miptexture_data = struct.pack(
            cls.format,
            miptexture.name.encode('ascii'),
            miptexture.width,
            miptexture.height,
            *miptexture.offsets
        )

        file.write(miptexture_data)

        if any(miptexture.offsets):
            file.write(miptexture.pixels)
            file.write(struct.pack('<H', len(miptexture.palette // 3)))
            file.write(miptexture.palette)
            file.write(b'\x00\x00')

    @classmethod
    def read(cls, file):
        miptexture_data = file.read(cls.size)
        miptexture_struct = struct.unpack(cls.format, miptexture_data)

        name = miptexture_struct[0].split(b'\00')[0].decode('ascii')
        width = miptexture_struct[1]
        height = miptexture_struct[2]
        offsets = miptexture_struct[3:]
        pixels = b''
        palette = b''

        if any(offsets):
            pixels_size = width * height * 85 // 64
            pixels = file.read(pixels_size)
            palette_size = struct.unpack('<H', file.read(2))[0]
            palette = file.read(struct.calcsize(f'<{palette_size * 3}B'))
            file.read(2)

        return Miptexture(
            name,
            width,
            height,
            offsets,
            pixels,
            palette
        )


class _Textures:
    """Helper class for working with the textures lump"""
    @staticmethod
    def write(file, miptextures):
        offset = file.tell()
        number_of_miptextures = len(miptextures)
        file.write(struct.pack('<i', number_of_miptextures))
        offset_format = f'<{number_of_miptextures}i'

        # Stub out directory info
        miptexture_offsets = [0] * number_of_miptextures
        file.write(struct.pack(offset_format, *miptexture_offsets))

        for i, miptex in enumerate(miptextures):
            if not miptex:
                miptexture_offsets[i] = -1
                continue

            miptexture_offsets[i] = file.tell() - offset
            Miptexture.write(file, miptex)

        # Write directory info
        end_offset = file.tell()
        file.seek(offset + 4)
        file.write(struct.pack(offset_format, *miptexture_offsets))
        file.seek(end_offset)

    @staticmethod
    def read(file, size=-1):
        result = []

        miptextures_offset = file.tell()
        number_of_miptextures = struct.unpack('<i', file.read(4))[0]
        offset_format = f'<{number_of_miptextures}i'
        offset_data = file.read(4 * number_of_miptextures)
        miptexture_offsets = struct.unpack(offset_format, offset_data)

        for miptexture_id in range(number_of_miptextures):
            if miptexture_offsets[miptexture_id] == -1:
                result.append(None)
                continue

            offset = miptextures_offset + miptexture_offsets[miptexture_id]
            file.seek(offset)

            result.append(Miptexture.read(file))

        return result


class Vertex:
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

    def __init__(self, x, y, z):
        """Constructs a Vertex object."""

        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, item):
        return (self.x, self.y, self.z)[item]

    @classmethod
    def write(cls, file, vertex):
        vertex_data = struct.pack(
            cls.format,
            vertex.x,
            vertex.y,
            vertex.z
        )

        file.write(vertex_data)

    @classmethod
    def read(cls, file):
        vertex_data = file.read(cls.size)
        vertex_struct = struct.unpack(cls.format, vertex_data)

        return Vertex(*vertex_struct)


class _Visibilities:
    """Helper class for working with the visibilities lump"""
    @staticmethod
    def write(file, visibilities):
        file.write(visibilities)

    @staticmethod
    def read(file, size=-1):
        return file.read(size)


class Node:
    """Class for representing a node

    A Node is a data structure used to compose a bsp tree data structure. A
    child may be a Node or a Leaf.

    Attributes:
        plane_number: The number of the plane that partitions the node.

        children: A two-tuple of the two sub-spaces formed by the partitioning
            plane.

            Note:
                Child 0 is the front sub-space, and 1 is the back sub-space.

            Note:
                If bit 15 is set, the child is a leaf.

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

    def __init__(self,
                 plane_number,
                 child_front,
                 child_back,
                 bounding_box_min_x,
                 bounding_box_min_y,
                 bounding_box_min_z,
                 bounding_box_max_x,
                 bounding_box_max_y,
                 bounding_box_max_z,
                 first_face,
                 number_of_faces):
        """Constructs a Node object."""

        self.plane_number = plane_number
        self.children = child_front, child_back
        self.bounding_box_min = bounding_box_min_x, bounding_box_min_y, bounding_box_min_z
        self.bounding_box_max = bounding_box_max_x, bounding_box_max_y, bounding_box_max_z
        self.first_face = first_face
        self.number_of_faces = number_of_faces

    @classmethod
    def write(cls, file, node):
        node_data = struct.pack(
            cls.format,
            node.plane_number,
            *node.children,
            *node.bounding_box_min,
            *node.bounding_box_max,
            node.first_face,
            node.number_of_faces
        )

        file.write(node_data)

    @classmethod
    def read(cls, file):
        node_data = file.read(cls.size)
        node_struct = struct.unpack(cls.format, node_data)

        return Node(*node_struct)


class TextureInfo:
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

    def __init__(self,
                 s_x,
                 s_y,
                 s_z,
                 s_offset,
                 t_x,
                 t_y,
                 t_z,
                 t_offset,
                 miptexture_number,
                 flags):
        """Constructs a TextureInfo object"""

        self.s = s_x, s_y, s_z
        self.s_offset = s_offset
        self.t = t_x, t_y, t_z
        self.t_offset = t_offset
        self.miptexture_number = miptexture_number
        self.flags = flags

    @classmethod
    def write(cls, file, texture_info):
        texture_info_data = struct.pack(
            cls.format,
            *texture_info.s,
            texture_info.s_offset,
            *texture_info.t,
            texture_info.t_offset,
            texture_info.miptexture_number,
            texture_info.flags
        )

        file.write(texture_info_data)

    @classmethod
    def read(cls, file):
        texture_info_data = file.read(cls.size)
        texture_info_struct = struct.unpack(cls.format, texture_info_data)

        return TextureInfo(*texture_info_struct)


class Face:
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

    def __init__(self,
                 plane_number,
                 side,
                 first_edge,
                 number_of_edges,
                 texture_info,
                 style_0,
                 style_1,
                 style_2,
                 style_3,
                 light_offset):
        """Constructs a Face object."""

        self.plane_number = plane_number
        self.side = side
        self.first_edge = first_edge
        self.number_of_edges = number_of_edges
        self.texture_info = texture_info
        self.styles = style_0, style_1, style_2, style_3
        self.light_offset = light_offset

    @classmethod
    def write(cls, file, plane):
        face_data = struct.pack(
            cls.format,
            plane.plane_number,
            plane.side,
            plane.first_edge,
            plane.number_of_edges,
            plane.texture_info,
            *plane.styles,
            plane.light_offset
        )

        file.write(face_data)

    @classmethod
    def read(cls, file):
        face_data = file.read(cls.size)
        face_struct = struct.unpack(cls.format, face_data)

        return Face(*face_struct)


class _Lighting:
    """Helper class for working with the lighting lump"""
    @staticmethod
    def write(file, lighting):
        file.write(lighting)

    @staticmethod
    def read(file, size=-1):
        return file.read(size)


class ClipNode:
    """Class for representing a clip node

    Attributes:
        plane_number: The number of the plane that partitions the node.

        children: A two-tuple of the two sub-spaces formed by the partitioning
            plane.

            Note:
                Child 0 is the front sub-space, and 1 is the back sub-space.
    """

    format = '<i2h'
    size = struct.calcsize(format)

    __slots__ = (
        'plane_number',
        'children'
    )

    def __init__(self,
                 plane_number,
                 child_front,
                 child_back):
        """Constructs a ClipNode object."""

        self.plane_number = plane_number
        self.children = child_front, child_back

    @classmethod
    def write(cls, file, clip_node):
        clip_node_data = struct.pack(
            cls.format,
            clip_node.plane_number,
            *clip_node.children
        )

        file.write(clip_node_data)

    @classmethod
    def read(cls, file):
        clip_node_data = file.read(cls.size)
        clip_node_struct = struct.unpack(cls.format, clip_node_data)

        return ClipNode(*clip_node_struct)


class Leaf:
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

    def __init__(self,
                 contents,
                 visibilitiy_offset,
                 bounding_box_min_x,
                 bounding_box_min_y,
                 bounding_box_min_z,
                 bounding_box_max_x,
                 bounding_box_max_y,
                 bounding_box_max_z,
                 first_mark_surface,
                 number_of_marked_surfaces,
                 ambient_level_0,
                 ambient_level_1,
                 ambient_level_2,
                 ambient_level_3):
        """Constructs a Leaf object."""

        self.contents = contents
        self.visibilitiy_offset = visibilitiy_offset
        self.bounding_box_min = bounding_box_min_x, bounding_box_min_y, bounding_box_min_z
        self.bounding_box_max = bounding_box_max_x, bounding_box_max_y, bounding_box_max_z
        self.first_mark_surface = first_mark_surface
        self.number_of_marked_surfaces = number_of_marked_surfaces
        self.ambient_level = ambient_level_0, ambient_level_1, ambient_level_2, ambient_level_3

    @classmethod
    def write(cls, file, leaf):
        leaf_data = struct.pack(
            cls.format,
            leaf.contents,
            leaf.visibilitiy_offset,
            *leaf.bounding_box_min,
            *leaf.bounding_box_max,
            leaf.first_mark_surface,
            leaf.number_of_marked_surfaces,
            *leaf.ambient_level
        )

        file.write(leaf_data)

    @classmethod
    def read(cls, file):
        leaf_data = file.read(cls.size)
        leaf_struct = struct.unpack(cls.format, leaf_data)

        return Leaf(*leaf_struct)


class _MarkSurfaces:
    """Helper class for working with the mark surfaces lump"""
    @staticmethod
    def write(file, surfaces):
        file.write(surfaces)

    @staticmethod
    def read(file, size=-1):
        return file.read(size)


class Edge:
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

    def __init__(self, vertex_0, vertex_1):
        """Constructs an Edge object."""

        self.vertexes = vertex_0, vertex_1

    def __getitem__(self, item):
        return self.vertexes[item]

    @classmethod
    def write(cls, file, edge):
        edge_data = struct.pack(cls.format, *edge.vertexes)

        file.write(edge_data)

    @classmethod
    def read(cls, file):
        edge_data = file.read(cls.size)
        edge_struct = struct.unpack(cls.format, edge_data)

        return Edge(*edge_struct)


class _SurfEdges:
    """Helper class for working with the surfedges lump"""
    @staticmethod
    def write(file, surfedges):
        data = struct.pack(f'<{len(surfedges)}i', *surfedges)
        file.write(data)

    @staticmethod
    def read(file, size=-1):
        data = file.read(size)
        return struct.unpack(f'<{len(data) // 4}i', data)


class Model:
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

    def __init__(self,
                 bounding_box_min_x,
                 bounding_box_min_y,
                 bounding_box_min_z,
                 bounding_box_max_x,
                 bounding_box_max_y,
                 bounding_box_max_z,
                 origin_x,
                 origin_y,
                 origin_z,
                 head_node_0,
                 head_node_1,
                 head_node_2,
                 head_node_3,
                 visleafs,
                 first_face,
                 number_of_faces):
        """Constructs a Model object."""

        self.bounding_box_min = bounding_box_min_x, bounding_box_min_y, bounding_box_min_z
        self.bounding_box_max = bounding_box_max_x, bounding_box_max_y, bounding_box_max_z
        self.origin = origin_x, origin_y, origin_z
        self.head_node = head_node_0, head_node_1, head_node_2, head_node_3
        self.visleafs = visleafs
        self.first_face = first_face
        self.number_of_faces = number_of_faces

    @classmethod
    def write(cls, file, model):
        model_data = struct.pack(
            cls.format,
            *model.bounding_box_min,
            *model.bounding_box_max,
            *model.origin,
            *model.head_node,
            model.visleafs,
            model.first_face,
            model.number_of_faces
        )

        file.write(model_data)

    @classmethod
    def read(cls, file):
        model_data = file.read(cls.size)
        model_struct = struct.unpack(cls.format, model_data)

        return Model(*model_struct)


class Bsp(ReadWriteFile):
    """Class for working with Bsp file

    Example:
        Basic usage::

            from vgio.halflife.bsp import Bsp
            b = Bsp.open('bounce.bsp')

    Attributes:
        version: Version of the map file. Vanilla Quake is 29.

        entities: A string containing the entity definitions.

        planes: A sequence of Planes used by the bsp tree data structure.

        textures: A sequence of Miptextures.

        vertexes: A sequence of Vertexes.

        visibilities: A sequence of ints representing visibility data.

        nodes: A sequence of Nodes used by the bsp tree data structure.

        texture_infos: A sequence of TextureInfo objects.

        faces: A sequence of Faces.

        lighting: A sequence of ints representing lighting data.

        clip_nodes: A sequence of ClipNodes used by the bsp tree data structure.

        leafs: A sequence of Leafs used by the bsp tree data structure.

        mark_surfaces: A sequence of ints representing lists of consecutive faces
            used by the Node objects.

        edges: A sequence of Edges.

        surf_edges: A sequence of ints representing  list of consecutive edges used
            by the Face objects.

        models: A sequence of Models.

            Note:
                The first model is the entire level.
    """

    class factory:
        Header = Header
        Plane = Plane
        Miptexture = Miptexture
        Vertex = Vertex
        Node = Node
        TextureInfo = TextureInfo
        Face = Face
        ClipNode = ClipNode
        Leaf = Leaf
        Edge = Edge
        Model = Model

    def __init__(self,
                 entities,
                 planes,
                 textures,
                 vertexes,
                 visibilities,
                 nodes,
                 texture_infos,
                 faces,
                 lighting,
                 clip_nodes,
                 leafs,
                 mark_surfaces,
                 edges,
                 surf_edges,
                 models):
        """Constructs a Bsp object"""
        super().__init__()

        self.version = VERSION
        self.entities = entities
        self.planes = planes
        self.textures = textures
        self.vertexes = vertexes
        self.visibilities = visibilities
        self.nodes = nodes
        self.texture_infos = texture_infos
        self.faces = faces
        self.lighting = lighting
        self.clip_nodes = clip_nodes
        self.leafs = leafs
        self.mark_surfaces = mark_surfaces
        self.edges = edges
        self.surf_edges = surf_edges
        self.models = models

    @classmethod
    def _read_file(cls, file, mode):
        def _read_iter_lump(lump, class_):
            """Read iteratively from file unpacking according to format
            class attribute on the class_ object"""
            offset, size = lump.offset, lump.length
            file.seek(offset)

            return [class_(*s) for s in
                    struct.iter_unpack(class_.format, file.read(size))]

        def _read_lump(lump, reader):
            """Read from file using the provided reader object"""
            file.seek(lump.offset)
            return reader.read(file, lump.length)

        factory = cls.factory

        header = factory.Header.read(file)

        entities = _read_lump(header.entities, _Entities)
        planes = _read_iter_lump(header.planes, factory.Plane)
        textures = _read_lump(header.textures, _Textures)
        vertexes = _read_iter_lump(header.vertexes, factory.Vertex)
        visibilities = _read_lump(header.visibilities, _Visibilities)
        nodes = _read_iter_lump(header.nodes, factory.Node)
        texture_infos = _read_iter_lump(header.texture_infos, factory.TextureInfo)
        faces = _read_iter_lump(header.faces, factory.Face)
        lighting = _read_lump(header.lighting, _Lighting)
        clip_nodes = _read_iter_lump(header.clip_nodes, factory.ClipNode)
        leafs = _read_iter_lump(header.leafs, factory.Leaf)
        mark_surfaces = _read_lump(header.mark_surfaces, _MarkSurfaces)
        edges = _read_iter_lump(header.edges, factory.Edge)
        surf_edges = _read_lump(header.surf_edges, _SurfEdges)
        models = _read_iter_lump(header.models, factory.Model)

        return cls(
            entities,
            planes,
            textures,
            vertexes,
            visibilities,
            nodes,
            texture_infos,
            faces,
            lighting,
            clip_nodes,
            leafs,
            mark_surfaces,
            edges,
            surf_edges,
            models
        )

    @classmethod
    def _write_file(cls, file, bsp):
        factory = cls.factory

        def _write_iter_lump(data):
            offset = file.tell()

            if data:
                class_ = data[0].__class__

                for datum in data:
                    class_.write(file, datum)

            length = file.tell() - offset

            return Lump(offset, length)

        def _write_lump(data, writer):
            """Write to file using the provided writer object"""
            offset = file.tell()
            writer.write(file, data)
            length = file.tell() - offset

            return Lump(offset, length)

        start_of_file = file.tell()

        lumps = [Lump(0, 0) for _ in range(15)]
        header = factory.Header(bsp.version, lumps)
        factory.Header.write(file, header)

        header.entities = _write_lump(bsp.entities, _Entities)
        header.planes = _write_iter_lump(bsp.planes)
        header.textures = _write_lump(bsp.textures, _Textures)
        header.vertexes = _write_iter_lump(bsp.vertexes)
        header.visibilities = _write_lump(bsp.visibilities, _Visibilities)
        header.nodes = _write_iter_lump(bsp.nodes)
        header.texture_infos = _write_iter_lump(bsp.texture_infos)
        header.faces = _write_iter_lump(bsp.faces)
        header.lighting = _write_lump(bsp.lighting, _Lighting)
        header.clip_nodes = _write_iter_lump(bsp.clip_nodes)
        header.leafs = _write_iter_lump(bsp.leafs)
        header.mark_surfaces = _write_lump(bsp.mark_surfaces, _MarkSurfaces)
        header.edges = _write_iter_lump(bsp.edges)
        header.surf_edges = _write_lump(bsp.surf_edges, _SurfEdges)
        header.models = _write_iter_lump(bsp.models)

        end_of_file = file.tell()

        # Finalize header
        file.seek(start_of_file)
        factory.Header.write(file, header)
        file.seek(end_of_file)