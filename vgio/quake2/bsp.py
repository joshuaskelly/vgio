"""This module provides file I/O for Quake 2 BSP map files.

Example:
    bsp_file = bsp.Bsp.open('base1.bsp')

References:
    Quake 2 Source
    - id Software
    - https://github.com/id-Software/Quake-2

    Quake 2 BSP File Format
    - Max McGuire
    - http://www.flipcode.com/archives/Quake_2_BSP_File_Format.shtml
"""

import io
import struct

from vgio._core import ReadWriteFile

__all__ = ['BadBspFile', 'is_bspfile', 'Bsp']


VERSION = 38
IDENTITY = b'IBSP'


class BadBspFile(Exception):
    pass


def _check_bspfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4si'))
    identity, version = struct.unpack('<4si', data)[0]

    return identity is IDENTITY and version is VERSION


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

    format = '<3i6h2H'
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


class SurfaceFlag:
    LIGHT = 0x1
    SLICK = 0x2
    SKY = 0x4
    WARP = 0x8
    TRANS33 = 0x10
    TRANS66 = 0x20
    FLOWING = 0x40
    NODRAW = 0x80


class TextureInfo:
    """Class for representing a texture info

    Attributes:
        s: The s vector in texture space represented as an XYZ three-tuple.

        s_offset: Horizontal offset in texture space.

        t: The t vector in texture space represented as an XYZ three-tuple.

        t_offset: Vertical offset in texture space.

        flags: A bitfield of surface behaviors.

        value:

        texture_name: The path of the texture.

        next_texture_info: For animated textures. Sequence will be terminated
            with a value of -1

    """

    format = '<8f2i32si'
    size = struct.calcsize(format)

    __slots__ = (
        's',
        's_offset',
        't',
        't_offset',
        'flags',
        'value',
        'texture_name',
        'next_texture_info'
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
                 flags,
                 value,
                 texture_name,
                 next_texture_info):

        self.s = s_x, s_y, s_z
        self.s_offset = s_offset
        self.t = t_x, t_y, t_z
        self.t_offset = t_offset
        self.flags = flags
        self.value = value

        if type(texture_name) == bytes:
            self.texture_name = texture_name.split(b'\00')[0].decode('ascii')
        else:
            self.texture_name = texture_name

        self.next_texture_info = next_texture_info

    @classmethod
    def write(cls, file, texture_info):
        texture_info_data = struct.pack(
            cls.format,
            *texture_info.s,
            texture_info.s_offset,
            *texture_info.t,
            texture_info.t_offset,
            texture_info.flags,
            texture_info.value,
            texture_info.texture_name.encode('ascii'),
            texture_info.next_texture_info
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

    format = '<Hhi2h4Bi'
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


class Contents:
    SOLID = 1
    WINDOW = 2
    AUX = 4
    LAVA = 8
    SLIME = 16
    WATER = 32
    MIST = 64
    LAST_VISIBLE = 64
    AREAPORTAL = 0x8000
    PLAYERCLIP = 0x10000
    MONSTERCLIP = 0x20000
    CURRENT_0 = 0x40000
    CURRENT_90 = 0x80000
    CURRENT_180 = 0x100000
    CURRENT_270 = 0x200000
    CURRENT_UP = 0x400000
    CURRENT_DOWN = 0x800000
    ORIGIN = 0x1000000
    MONSTER = 0x2000000
    DEADMONSTER = 0x4000000
    DETAIL = 0x8000000
    TRANSLUCENT = 0x10000000
    LADDER = 0x20000000


class Leaf:
    """Class for representing a leaf

    Attributes:
        contents: The content of the leaf. Affect the player's view.

        cluster: The cluster containing this leaf. -1 for no visibility info.

        area: The area containing this leaf.

        bounding_box_min: The minimum coordinate of the bounding box containing
            this node.

        bounding_box_max: The maximum coordinate of the bounding box containing
            this node.

        first_leaf_face: The number of the first face in Bsp.faces

        number_of_leaf_faces: The number of faces contained within the leaf.
            These are stored in consecutive order in Bsp.faces at
            Leaf.first_leaf_face.

        first_leaf_brush: The number of the first brush in Bsp.brushes

        number_of_leaf_brushes: The number of brushes contained within the
            leaf. These are stored in consecutive order in Bsp.brushes at
            Leaf.first_leaf_brush.
    """

    format = '<i8h4H'
    size = struct.calcsize(format)

    __slots__ = (
        'contents',
        'cluster',
        'area',
        'bounding_box_min',
        'bounding_box_max',
        'first_leaf_face',
        'number_of_leaf_faces',
        'first_leaf_brush',
        'number_of_leaf_brushes'
    )

    def __init__(self,
                 contents,
                 cluster,
                 area,
                 bounding_box_min_x,
                 bounding_box_min_y,
                 bounding_box_min_z,
                 bounding_box_max_x,
                 bounding_box_max_y,
                 bounding_box_max_z,
                 first_leaf_face,
                 number_of_leaf_faces,
                 first_leaf_brush,
                 number_of_leaf_brushes):

        self.contents = contents
        self.cluster = cluster
        self.area = area
        self.bounding_box_min = bounding_box_min_x, bounding_box_min_y, bounding_box_min_z
        self.bounding_box_max = bounding_box_max_x, bounding_box_max_y, bounding_box_max_z
        self.first_leaf_face = first_leaf_face
        self.number_of_leaf_faces = number_of_leaf_faces
        self.first_leaf_brush = first_leaf_brush
        self.number_of_leaf_brushes = number_of_leaf_brushes

    @classmethod
    def write(cls, file, leaf):
        leaf_data = struct.pack(
            cls.format,
            leaf.contents,
            leaf.cluster,
            leaf.area,
            *leaf.bounding_box_min,
            *leaf.bounding_box_max,
            leaf.first_leaf_face,
            leaf.number_of_leaf_faces,
            leaf.first_leaf_brush,
            leaf.number_of_leaf_brushes
        )

        file.write(leaf_data)

    @classmethod
    def read(cls, file):
        leaf_data = file.read(cls.size)
        leaf_struct = struct.unpack(cls.format, leaf_data)

        return Leaf(*leaf_struct)


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
        self.vertexes = vertex_0, vertex_1

    def __getitem__(self, item):
        return self.vertexes[item]

    @classmethod
    def write(cls, file, edge):
        edge_data = struct.pack(
            cls.format,
            *edge.vertexes
        )

        file.write(edge_data)

    @classmethod
    def read(cls, file):
        edge_data = file.read(cls.size)
        edge_struct = struct.unpack(cls.format, edge_data)

        return Edge(*edge_struct)


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

    format = '<9f3i'
    size = struct.calcsize(format)

    __slots__ = (
        'bounding_box_min',
        'bounding_box_max',
        'origin',
        'head_node',
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
                 head_node,
                 first_face,
                 number_of_faces):

        self.bounding_box_min = bounding_box_min_x, bounding_box_min_y, bounding_box_min_z
        self.bounding_box_max = bounding_box_max_x, bounding_box_max_y, bounding_box_max_z
        self.origin = origin_x, origin_y, origin_z
        self.head_node = head_node
        self.first_face = first_face
        self.number_of_faces = number_of_faces

    @classmethod
    def write(cls, file, model):
        model_data = struct.pack(
            cls.format,
            *model.bounding_box_min,
            *model.bounding_box_max,
            *model.origin,
            model.head_node,
            model.first_face,
            model.number_of_faces
        )

        file.write(model_data)

    @classmethod
    def read(cls, file):
        model_data = file.read(cls.size)
        model_struct = struct.unpack(cls.format, model_data)

        return Model(*model_struct)


class Brush:
    format = '<3i'
    size = struct.calcsize(format)

    __slots__ = (
        'first_side',
        'number_of_sides',
        'contents'
    )

    def __init__(self,
                 first_side,
                 number_of_sides,
                 contents):

        self.first_side = first_side
        self.number_of_sides = number_of_sides
        self.contents = contents

    @classmethod
    def write(cls, file, brush):
        brush_data = struct.pack(
            cls.format,
            brush.first_side,
            brush.number_of_sides,
            brush.contents
        )

        file.write(brush_data)

    @classmethod
    def read(cls, file):
        brush_data = file.read(cls.size)
        brush_struct = struct.unpack(cls.format, brush_data)

        return Brush(*brush_struct)


class BrushSide:
    format = '<Hh'
    size = struct.calcsize(format)

    __slots__ = (
        'plane_number',
        'texture_info'
    )

    def __init__(self,
                 plane_number,
                 texture_info):

        self.plane_number = plane_number
        self.texture_info = texture_info

    @classmethod
    def write(cls, file, brush_side):
        brush_side_data = struct.pack(
            cls.format,
            brush_side.plane_number,
            brush_side.texture_info
        )

        file.write(brush_side_data)

    @classmethod
    def read(cls, file):
        brush_side_data = file.read(cls.size)
        brush_side_struct = struct.unpack(cls.format, brush_side_data)

        return BrushSide(*brush_side_struct)


class Area:
    format = '<2i'
    size = struct.calcsize(format)

    __slots__ = (
        'number_of_area_portals',
        'first_area_portal'
    )

    def __init__(self,
                 number_of_area_portals,
                 first_area_portal):

        self.number_of_area_portals = number_of_area_portals
        self.first_area_portal = first_area_portal

    @classmethod
    def write(cls, file, area):
        area_data = struct.pack(
            cls.format,
            area.number_of_area_portals,
            area.first_area_portal
        )

        file.write(area_data)

    @classmethod
    def read(cls, file):
        area_data = file.read(cls.size)
        area_struct = struct.unpack(cls.format, area_data)

        return Area(*area_struct)


class AreaPortal:
    format = '<2i'
    size = struct.calcsize(format)

    __slots__ = (
        'portal_number',
        'other_area'
    )

    def __init__(self,
                 portal_number,
                 other_area):
        self.portal_number = portal_number
        self.other_area = other_area

    @classmethod
    def write(cls, file, area):
        area_data = struct.pack(
            cls.format,
            area.portal_number,
            area.other_area
        )

        file.write(area_data)

    @classmethod
    def read(cls, file):
        area_data = file.read(cls.size)
        area_struct = struct.unpack(cls.format, area_data)

        return AreaPortal(*area_struct)


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


class _Visibilities:
    """Helper class for working with the visibilities lump"""
    @staticmethod
    def write(file, structures):
        file.write(structures)

    @staticmethod
    def read(file, size=-1):
        return file.read(size)


class _Lighting:
    """Helper class for working with the lighting lump"""
    @staticmethod
    def write(file, lighting):
        file.write(lighting)

    @staticmethod
    def read(file, size=-1):
        return file.read(size)


class _LeafFaces:
    """Helper class for working with the leaf faces lump"""
    @staticmethod
    def write(file, leaf_faces):
        leaf_faces_format = '<{}H'.format(len(leaf_faces))
        leaf_faces_data = struct.pack(leaf_faces_format, *leaf_faces)

        file.write(leaf_faces_data)

    @staticmethod
    def read(file, size=-1):
        return [lf[0] for lf in struct.iter_unpack('<H', file.read(size))]


class _LeafBrushes:
    """Helper class for working with the leaf brushes lump"""
    @staticmethod
    def write(file, leaf_brushes):
        leaf_brushes_format = '<{}H'.format(len(leaf_brushes))
        leaf_brushes_data = struct.pack(leaf_brushes_format, *leaf_brushes)

        file.write(leaf_brushes_data)

    @staticmethod
    def read(file, size=-1):
        return [lb[0] for lb in struct.iter_unpack('<H', file.read(size))]


class _SurfEdges:
    """Helper class for working with the surfedges lump"""
    @staticmethod
    def write(file, surf_edges):
        surf_edges_format = '<{}H'.format(len(surf_edges))
        surf_edges_data = struct.pack(surf_edges_format, *surf_edges)

        file.write(surf_edges_data)

    @staticmethod
    def read(file, size=-1):
        return [se[0] for se in struct.iter_unpack('<H', file.read(size))]


class _Pop:
    @staticmethod
    def write(file, structures):
        file.write(structures)

    @staticmethod
    def read(file, size=-1):
        return file.read(size)


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
        identity: The file identity. Should be b'IBSP'.

        version: The file version. Should be 38.

        lumps: A sequence of nineteen Lump objects
    """

    format = '<4si{}'.format(Lump.format[1:] * 19)
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'version',
        '_lumps'
    )

    def __init__(self,
                 identity,
                 version,
                 lumps):
        self.identity = identity
        self.version = version
        self._lumps = lumps

        if len(lumps) != 19:
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
    def vertexes(self):
        return self._lumps[2]

    @vertexes.setter
    def vertexes(self, value):
        self._lumps[2] = value

    @property
    def visibilities(self):
        return self._lumps[3]

    @visibilities.setter
    def visibilities(self, value):
        self._lumps[3] = value

    @property
    def nodes(self):
        return self._lumps[4]

    @nodes.setter
    def nodes(self, value):
        self._lumps[4] = value

    @property
    def texture_infos(self):
        return self._lumps[5]

    @texture_infos.setter
    def texture_infos(self, value):
        self._lumps[5] = value

    @property
    def faces(self):
        return self._lumps[6]

    @faces.setter
    def faces(self, value):
        self._lumps[6] = value

    @property
    def lighting(self):
        return self._lumps[7]

    @lighting.setter
    def lighting(self, value):
        self._lumps[7] = value

    @property
    def leafs(self):
        return self._lumps[8]

    @leafs.setter
    def leafs(self, value):
        self._lumps[8] = value

    @property
    def leaf_faces(self):
        return self._lumps[9]

    @leaf_faces.setter
    def leaf_faces(self, value):
        self._lumps[9] = value

    @property
    def leaf_brushes(self):
        return self._lumps[10]

    @leaf_brushes.setter
    def leaf_brushes(self, value):
        self._lumps[10] = value

    @property
    def edges(self):
        return self._lumps[11]

    @edges.setter
    def edges(self, value):
        self._lumps[11] = value

    @property
    def surf_edges(self):
        return self._lumps[12]

    @surf_edges.setter
    def surf_edges(self, value):
        self._lumps[12] = value

    @property
    def models(self):
        return self._lumps[13]

    @models.setter
    def models(self, value):
        self._lumps[13] = value

    @property
    def brushes(self):
        return self._lumps[14]

    @brushes.setter
    def brushes(self, value):
        self._lumps[14] = value

    @property
    def brush_sides(self):
        return self._lumps[15]

    @brush_sides.setter
    def brush_sides(self, value):
        self._lumps[15] = value

    @property
    def pop(self):
        return self._lumps[16]

    @pop.setter
    def pop(self, value):
        self._lumps[16] = value

    @property
    def areas(self):
        return self._lumps[17]

    @areas.setter
    def areas(self, value):
        self._lumps[17] = value

    @property
    def area_portals(self):
        return self._lumps[18]

    @area_portals.setter
    def area_portals(self, value):
        self._lumps[18] = value

    @classmethod
    def write(cls, file, header):
        lump_values = []
        for lump in header._lumps:
            lump_values += lump.offset, lump.length

        header_data = struct.pack(
            cls.format,
            header.identity,
            header.version,
            *lump_values
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        data = file.read(cls.size)
        lumps_start = struct.calcsize('<4si')

        header_data = data[:lumps_start]
        header_struct = struct.unpack('<4si', header_data)
        ident = header_struct[0]
        version = header_struct[1]

        lumps_data = data[lumps_start:]
        lumps = [Lump(*l) for l in struct.iter_unpack(Lump.format, lumps_data)]

        return Header(ident, version, lumps)


class Bsp(ReadWriteFile):
    """Class for working with Bsp files

    Example:
        Basic usage::

            from vgio.quake2.bsp import Bsp
            b = Bsp.open(file)

    Attributes:
        identity: Identity of the Bsp file. Should be b'IBSP'

        version: Version of the Bsp file. Should be 38

        entities: A string containing the entity definitions.

        planes: A list of Plane objects used by the bsp tree data structure.

        vertexes: A list of Vertex objects.

        visibilities: A list of integers representing visibility data.

        nodes: A list of Node objects used by the bsp tree data structure.

        texture_infos: A list of TextureInfo objects.

        faces: A list of Face objects.

        lighting: A list of ints representing lighting data.

        leafs: A list of Leaf objects used by the bsp tree data structure.

        leaf_faces: A list of ints representing a consecutive list of faces
            used by the Leaf objects.

        leaf_brushes: A list of ints representing a consecutive list of edges
            used by the Leaf objects.

        edges: A list of Edge objects.

        surf_edges: A list of ints representing a consecutive list of edges
            used by the Face objects.

        models: A list of Model objects.

        brushes: A list of Brush objects.

        brush_sides: A list of BrushSide objects.

        pop: Proof of purchase? Always 256 bytes of null data if present.

        areas: A list of Area objects.

        area_portals: A list of AreaPortal objects.
    """
    class factory:
        Lump = Lump
        Header = Header
        Plane = Plane
        Vertex = Vertex
        Node = Node
        TextureInfo = TextureInfo
        Face = Face
        Leaf = Leaf
        Edge = Edge
        Model = Model
        Brush = Brush
        BrushSide = BrushSide
        Pop = _Pop
        Area = Area
        AreaPortal = AreaPortal

    def __init__(self):
        """Constructs a Bsp object."""

        super().__init__()

        self.identity = IDENTITY
        self.version = VERSION
        self.entities = ''
        self.planes = []
        self.vertexes = []
        self.visibilities = []
        self.nodes = []
        self.texture_infos = []
        self.faces = []
        self.lighting = b''
        self.leafs = []
        self.leaf_faces = []
        self.leaf_brushes = []
        self.edges = []
        self.surf_edges = []
        self.models = []
        self.brushes = []
        self.brush_sides = []
        self.pop = []
        self.areas = []
        self.area_portals = []

    @classmethod
    def _read_file(cls, file, mode):
        def _read_iter_lump(lump, class_):
            """Read iteratively from file unpacking according to format
            class attribute on the class_ object"""
            file.seek(lump.offset)

            return [class_(*s) for s in struct.iter_unpack(class_.format, file.read(lump.length))]

        def _read_lump(lump, reader):
            """Read from file using the provided reader object"""
            file.seek(lump.offset)
            return reader.read(file, lump.length)

        bsp = cls()
        bsp.mode = mode
        bsp.fp = file

        factory = cls.factory

        # Header
        header = factory.Header.read(file)
        bsp.identity = header.identity
        bsp.version = header.version

        bsp.entities = _read_lump(header.entities, _Entities)
        bsp.planes = _read_iter_lump(header.planes, factory.Plane)
        bsp.vertexes = _read_iter_lump(header.vertexes, factory.Vertex)
        bsp.visibilities = _read_lump(header.visibilities, _Visibilities)
        bsp.nodes = _read_iter_lump(header.nodes, factory.Node)
        bsp.texture_infos = _read_iter_lump(header.texture_infos, factory.TextureInfo)
        bsp.faces = _read_iter_lump(header.faces, factory.Face)
        bsp.lighting = _read_lump(header.lighting, _Lighting)
        bsp.leafs = _read_iter_lump(header.leafs, factory.Leaf)
        bsp.leaf_faces = _read_lump(header.leaf_faces, _LeafFaces)
        bsp.leaf_brushes = _read_lump(header.leaf_brushes, _LeafBrushes)
        bsp.edges = _read_iter_lump(header.edges, factory.Edge)
        bsp.surf_edges = _read_lump(header.surf_edges, _SurfEdges)
        bsp.models = _read_iter_lump(header.models, factory.Model)
        bsp.brushes = _read_iter_lump(header.brushes, factory.Brush)
        bsp.brush_sides = _read_iter_lump(header.brush_sides, factory.BrushSide)
        bsp.pop = _read_lump(header.pop, _Pop)
        bsp.areas = _read_iter_lump(header.areas, factory.Area)
        bsp.area_portals = _read_iter_lump(header.area_portals, factory.AreaPortal)

        return bsp

    @classmethod
    def _write_file(cls, file, bsp):
        factory = cls.factory

        def _write_iter_lump(data):
            """Write iteratively to file unpacking according to format
            class attribute on the class_ object"""
            offset = file.tell()

            if data:
                class_ = data[0].__class__

                for datum in data:
                    class_.write(file, datum)

            length = file.tell() - offset

            return factory.Lump(offset, length)

        def _write_lump(data, writer):
            """Write to file using the provided writer object"""
            offset = file.tell()
            writer.write(file, data)
            length = file.tell() - offset

            return factory.Lump(offset, length)

        start_of_file = file.tell()

        lumps = [factory.Lump(0, 0) for _ in range(19)]
        header = factory.Header(bsp.identity, bsp.version, lumps)
        factory.Header.write(file, header)

        header.entities = _write_lump(bsp.entities, _Entities)
        header.planes = _write_iter_lump(bsp.planes)
        header.vertexes = _write_iter_lump(bsp.vertexes)
        header.visibilities = _write_lump(bsp.visibilities, _Visibilities)
        header.nodes = _write_iter_lump(bsp.nodes)
        header.texture_infos = _write_iter_lump(bsp.texture_infos)
        header.faces = _write_iter_lump(bsp.faces)
        header.lighting = _write_lump(bsp.lighting, _Lighting)
        header.leafs = _write_iter_lump(bsp.leafs)
        header.leaf_faces = _write_lump(bsp.leaf_faces, _LeafFaces)
        header.leaf_brushes = _write_lump(bsp.leaf_brushes, _LeafBrushes)
        header.edges = _write_iter_lump(bsp.edges)
        header.surf_edges = _write_lump(bsp.surf_edges, _SurfEdges)
        header.models = _write_iter_lump(bsp.models)
        header.brushes = _write_iter_lump(bsp.brushes)
        header.brush_sides = _write_iter_lump(bsp.brush_sides)
        header.pop = _write_lump(bsp.pop, _Pop)
        header.areas = _write_iter_lump(bsp.areas)
        header.area_portals = _write_iter_lump(bsp.area_portals)

        end_of_file = file.tell()

        # Finalize header
        file.seek(start_of_file)
        factory.Header.write(file, header)
        file.seek(end_of_file)
