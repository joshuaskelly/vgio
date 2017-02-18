"""Module for working with id Software style BSP files

Supported games:
    - QUAKE
"""

import io
import struct

__all__ = ['BadBspFile', 'is_bspfile', 'BspPlane', 'BspMiptexture',
           'BspVertex', 'BspNode', 'BspTextureInfo', 'BspFace', 'BspClipNode',
           'BspLeaf', 'BspEdge', 'BspModel', 'Bsp']

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
    return '<%dh' % (size // 2)

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

    return data == header_version


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


class BspPlane(object):
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

    def __init__(self, plane_struct):
        self.normal = plane_struct[_PLANE_NORMAL:_PLANE_DISTANCE]
        self.distance = plane_struct[_PLANE_DISTANCE]
        self.type = plane_struct[_PLANE_TYPE]


class BspMiptexture(object):
    """Class for representing a bsp miptexture

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
            palette must be used to obtain RGB data. Note: this is the pixel
            data for all four mip levels.
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

    def __init__(self, miptexture_struct):
        self.name = miptexture_struct[_MIPTEXTURE_NAME].split(b'\00')[0].decode('ascii')
        self.width = miptexture_struct[_MIPTEXTURE_WIDTH]
        self.height = miptexture_struct[_MIPTEXTURE_HEIGHT]
        self.offsets = miptexture_struct[_MIPTEXTURE_OFFSETS:]
        self.pixels = None


class BspVertex(object):
    """Class for representing a bsp vertex

    A BspVertex is an XYZ triple.

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

    def __init__(self, vertex_struct):
        self.x = vertex_struct[_VERTEX_X]
        self.y = vertex_struct[_VERTEX_Y]
        self.z = vertex_struct[_VERTEX_Z]

    def __getitem__(self, item):
        if item > 2:
            raise IndexError('list index of out of range')

        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z


class BspNode(object):
    """Class for representing a bsp node

    A BspNode is a data structure used to compose a bsp tree data structure. A
    child may be a BspNode or a BspLeaf.

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
            BspNode.first_face.
    """

    __slots__ = (
        'plane_number',
        'children',
        'bounding_box_min',
        'bounding_box_max',
        'first_face',
        'number_of_faces'
    )

    def __init__(self, node_struct):
        self.plane_number = node_struct[_NODE_PLANE_NUMBER]
        self.children = node_struct[_NODE_CHILDREN:_NODE_BOUNDING_BOX_MIN]
        self.bounding_box_min = node_struct[_NODE_BOUNDING_BOX_MIN:_NODE_BOUNDING_BOX_MAX]
        self.bounding_box_max = node_struct[_NODE_BOUNDING_BOX_MAX:_NODE_FIRST_FACE]
        self.first_face = node_struct[_NODE_FIRST_FACE]
        self.number_of_faces = node_struct[_NODE_NUMBER_OF_FACES]


class BspTextureInfo(object):
    """Class for representing a bsp texture info

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

    def __init__(self, texture_info_struct):
        self.s = texture_info_struct[_TEXTURE_INFO_S:_TEXTURE_INFO_S_OFFSET]
        self.s_offset = texture_info_struct[_TEXTURE_INFO_S_OFFSET]
        self.t = texture_info_struct[_TEXTURE_INFO_T:_TEXTURE_INFO_T_OFFSET]
        self.t_offset = texture_info_struct[_TEXTURE_INFO_T_OFFSET]
        self.miptexture_number = texture_info_struct[_TEXTURE_INFO_MIPTEXTURE_NUMBER]
        self.flags = texture_info_struct[_TEXTURE_INFO_FLAGS]


class BspFace(object):
    """Class for representing a bsp face

    Attributes:
        plane_number: The plane in which the face lies.

        side: Which side of the plane the face lies. 0 is the front, 1 is the
            back.

        first_edge: The number of the first edge in Bsp.surf_edges.

        number_of_edges: The number of edges contained within the face. These
            are stored in consecutive order in Bsp.surf_edges starting at
            BspFace.first_edge.

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

    def __init__(self, face_struct):
        self.plane_number = face_struct[_FACE_PLANE_NUMBER]
        self.side = face_struct[_FACE_SIDE]
        self.first_edge = face_struct[_FACE_FIRST_EDGE]
        self.number_of_edges = face_struct[_FACE_NUMBER_OF_EDGES]
        self.texture_info = face_struct[_FACE_TEXTURE_INFO]
        self.styles = face_struct[_FACE_STYLES:_FACE_LIGHT_OFFSET]
        self.light_offset = face_struct[_FACE_LIGHT_OFFSET]


class BspClipNode(object):
    """Class for representing a bsp clip node

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

    def __init__(self, clip_node_struct):
        self.plane_number = clip_node_struct[_CLIP_NODE_PLANE_NUMBER]
        self.children = clip_node_struct[_CLIP_NODE_CHILDREN:]


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


class BspLeaf(object):
    """Class for representing a bsp leaf

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
            starting at BspLeaf.first_mark_surface.

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

    def __init__(self, leaf_struct):
        self.contents = leaf_struct[_LEAF_CONTENTS]
        self.visibilitiy_offset = leaf_struct[_LEAF_VISIBILITIY_OFFSET]
        self.bounding_box_min = leaf_struct[_LEAF_BOUNDING_BOX_MIN:_LEAF_BOUNDING_BOX_MAX]
        self.bounding_box_max = leaf_struct[_LEAF_BOUNDING_BOX_MAX:_LEAF_FIRST_MARK_SURFACE]
        self.first_mark_surface = leaf_struct[_LEAF_FIRST_MARK_SURFACE]
        self.number_of_marked_surfaces = leaf_struct[_LEAF_NUMBER_OF_MARKED_SURFACES]
        self.ambient_level = leaf_struct[_LEAF_AMBIENT_LEVEL:]


class BspEdge(object):
    """Class for representing a bsp edge

    Attributes:
        vertexes: A two-tuple of vertexes that form the edge. Vertex 0 is the
            start vertex, and 1 is the end vertex.
    """

    __slots__ = (
        'vertexes'
    )

    def __init__(self, edge_struct):
        self.vertexes = edge_struct[:]

    def __getitem__(self, item):
        if item > 1:
            raise IndexError('list index of out of range')

        return self.vertexes[item]


class BspModel(object):
    """Class for representing a bsp model

    Attributes:
        bounding_box_min: The minimum coordinate of the bounding box containing
            the model.

        bounding_box_max: The maximum coordinate of the bounding box containing
            the model.

        origin: The origin of the model.

        head_node: A four-tuple of

        visleafs: The number of leaves in the bsp tree?

        first_face: The number of the first face in Bsp.mark_surfaces.

        number_of_faces: The number of faces contained in the node. These
            are stored in consecutive order in Bsp.mark_surfaces starting at
            BspModel.first_face.
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

    def __init__(self, model_struct):
        self.bounding_box_min = model_struct[_MODEL_BOUNDING_BOX_MIN:_MODEL_BOUNDING_BOX_MAX]
        self.bounding_box_max = model_struct[_MODEL_BOUNDING_BOX_MAX:_MODEL_ORIGIN]
        self.origin = model_struct[_MODEL_ORIGIN:_MODEL_HEAD_NODE]
        self.head_node = model_struct[_MODEL_HEAD_NODE:_MODEL_VISLEAFS]
        self.visleafs = model_struct[_MODEL_VISLEAFS]
        self.first_face = model_struct[_MODEL_FIRST_FACE]
        self.number_of_faces = model_struct[_MODEL_NUMBER_OF_FACES]


class Bsp(object):
    """Class for working with Bsp files

    Example:
        b = Bsp.open(file)

    Attributes:
        version: Version of the map file. Vanilla Quake is 29.

        entities: A string containing the entity definitions.

        planes: A list of BspPlanes used by the bsp tree data structure.

        miptextures: A list of BspMiptextures.

        vertexes: A list of BspVertexes.

        visibilities: A list of ints representing visibility data.

        nodes: A list of BspNodes used by the bsp tree data structure.

        texture_infos: A list of BspTextureInfo objects.

        faces: A list of BspFaces.

        lighting: A list of ints representing lighting data.

        clip_nodes: A list of BspClipNodes used by the bsp tree data structure.

        leafs: A list of BspLeafs used by the bsp tree data structure.

        mark_surfaces: A list of ints representing lists of consecutive faces
            used by the BspNode objects.

        edges: A list of BspEdges.

        surf_edges: A list of ints representing  list of consecutive edges used
            by the BspFace objects.

        models: A list of BspModels.

            Note: The first model is the entire level.

        fp: The file-like object to read data from.

        mode: The file mode for the file-like object.
    """

    def __init__(self):
        self.fp = None
        self.mode = None

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

            mode: Currently the only supported mode is 'r'

        Returns:
            An Bsp object constructed from the information read from the
            file-like object.
        """

        if mode not in ['r']:
            raise ValueError("invalid mode: '%s'" % mode)

        bsp = Bsp()
        bsp.mode = mode

        if isinstance(file, str):
            file = io.open(file, 'rb')

        elif isinstance(file, bytes):
            file = io.BytesIO(file)

        elif not hasattr(file, 'read'):
            raise RuntimeError(
                "Bsp.open() requires 'file' to be a path, a file-like object, or bytes")

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
            plane_data = file.read(plane_size)
            plane_struct = struct.unpack(plane_format, plane_data)

            bsp.planes.append(BspPlane(plane_struct))

        # Miptextures
        miptextures_offset = bsp_struct[_HEADER_MIPTEXTURES_OFFSET]

        # Miptexture directory
        file.seek(miptextures_offset)
        number_of_miptextures = struct.unpack('<i', file.read(4))[0]
        offset_format = '<%di' % number_of_miptextures
        offset_data = file.read(4 * number_of_miptextures)
        miptexture_offsets = struct.unpack(offset_format, offset_data)

        for miptexture_id in range(number_of_miptextures):
            offset = miptextures_offset + miptexture_offsets[miptexture_id]
            file.seek(offset)

            miptexture_data = file.read(miptexture_size)
            miptexture_struct = struct.unpack(miptexture_format, miptexture_data)

            miptexture = BspMiptexture(miptexture_struct)

            # Calculate miptexture size using the simplified form of the
            # geometric series where r = 1/4 and n = 4
            pixels_size = miptexture.width * miptexture.height * 85 // 64
            pixels_format = '<%dB' % pixels_size
            pixels_data = struct.unpack(pixels_format, file.read(pixels_size))

            miptexture.pixels = pixels_data

            bsp.miptextures.append(miptexture)

        # Vertexes
        vertexes_offset = bsp_struct[_HEADER_VERTEXES_OFFSET]
        vertexes_size = bsp_struct[_HEADER_VERTEXES_SIZE]
        number_of_vertexes = vertexes_size // vertex_size

        file.seek(vertexes_offset)
        for _ in range(number_of_vertexes):
            vertex_data = file.read(vertex_size)
            vertex_struct = struct.unpack(vertex_format, vertex_data)

            bsp.vertexes.append(BspVertex(vertex_struct))

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
            node_data = file.read(node_size)
            node_struct = struct.unpack(node_format, node_data)

            bsp.nodes.append(BspNode(node_struct))

        # Texture Infos
        texture_infos_offset = bsp_struct[_HEADER_TEXTURE_INFOS_OFFSET]
        texture_infos_size = bsp_struct[_HEADER_TEXTURE_INFOS_SIZE]
        number_of_texture_infos = texture_infos_size // texture_info_size

        file.seek(texture_infos_offset)
        for _ in range(number_of_texture_infos):
            texture_info_data = file.read(texture_info_size)
            texture_info_struct = struct.unpack(texture_info_format, texture_info_data)

            bsp.texture_infos.append(BspTextureInfo(texture_info_struct))

        # Faces
        faces_offset = bsp_struct[_HEADER_FACES_OFFSET]
        faces_size = bsp_struct[_HEADER_FACES_SIZE]
        number_of_faces = faces_size // face_size

        file.seek(faces_offset)
        for _ in range(number_of_faces):
            face_data = file.read(face_size)
            face_struct = struct.unpack(face_format, face_data)

            bsp.faces.append(BspFace(face_struct))

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
            clip_node_data = file.read(clip_node_size)
            clip_node_struct = struct.unpack(clip_node_format, clip_node_data)

            bsp.clip_nodes.append(BspClipNode(clip_node_struct))

        # Leafs
        leafs_offset = bsp_struct[_HEADER_LEAFS_OFFSET]
        leafs_size = bsp_struct[_HEADER_LEAFS_SIZE]
        number_of_leafs = leafs_size // leaf_size

        file.seek(leafs_offset)
        for _ in range(number_of_leafs):
            leaf_data = file.read(leaf_size)
            leaf_struct = struct.unpack(leaf_format, leaf_data)

            bsp.leafs.append(BspLeaf(leaf_struct))

        # Mark Surfaces
        mark_surfaces_offset = bsp_struct[_HEADER_MARK_SURFACES_OFFSET]
        mark_surfaces_size = bsp_struct[_HEADER_MARK_SURFACES_SIZE]
        mark_surfaces_format = _calculate_mark_surface_format(mark_surfaces_size)

        file.seek(mark_surfaces_offset)
        mark_surfaces_data = file.read(mark_surfaces_size)
        bsp.mark_surfaces = struct.unpack(mark_surfaces_format, mark_surfaces_data)

        # Edges
        edges_offset = bsp_struct[_HEADER_EDGES_OFFSET]
        edges_size = bsp_struct[_HEADER_EDGES_SIZE]
        number_of_edges = edges_size // edge_size

        file.seek(edges_offset)
        for _ in range(number_of_edges):
            edge_data = file.read(edge_size)
            edge_struct = struct.unpack(edge_format, edge_data)

            bsp.edges.append(BspEdge(edge_struct))

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
            model_data = file.read(model_size)
            model_struct = struct.unpack(model_format, model_data)

            bsp.models.append(BspModel(model_struct))

        return bsp
