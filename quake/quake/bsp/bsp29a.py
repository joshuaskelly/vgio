"""This module provides file I/O for Quake BSP2 map files.

Example:
    bsp_file = bsp.Bsp.open('e1m1.bsp')
"""

import io
import struct

from .bsp29 import (
    default_palette,
    Plane,
    Miptexture,
    Vertex,
    Node,
    TextureInfo,
    Face,
    ClipNode,
    Leaf,
    Edge,
    Model,
    Mesh,
    Image
)

__all__ = ['BadBspFile', 'is_bspfile', 'Plane', 'Miptexture',
           'Vertex', 'Node', 'TextureInfo', 'Face', 'ClipNode',
           'Leaf', 'Edge', 'Model', 'Bsp']


class BadBspFile(Exception):
    pass


# The bsp header structure
header_format = '<31l'
header_version = b'BSP2'
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
    data = fp.read(struct.calcsize('<4s'))
    version = struct.unpack('<4s', data)[0]

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


class Node(Node):
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

    format = '<i8i2I'
    size = struct.calcsize(format)


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

    format = '<2ii2i4Bi'
    size = struct.calcsize(format)


class ClipNode(object):
    """Class for representing a clip node

    Attributes:
        plane_number: The number of the plane that partitions the node.

        children: A two-tuple of the two sub-spaces formed by the partitioning
            plane.

            Note: Child 0 is the front sub-space, and 1 is the back sub-space.
    """

    format = '<i2i'
    size = struct.calcsize(format)


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

    format = '<2i6i2I4B'
    size = struct.calcsize(format)


class Edge(object):
    """Class for representing a edge

    Attributes:
        vertexes: A two-tuple of vertexes that form the edge. Vertex 0 is the
            start vertex, and 1 is the end vertex.
    """

    format = '<2I'
    size = struct.calcsize(format)


class Bsp(object):
    """Class for working with Bsp2 files

    Example:
        b = Bsp.open(file)

    Attributes:
        version: Version of the map file. Bsp2 is b'BSP2'

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
        planes_offset = bsp_struct[_HEADER_PLANES_OFFSET]
        planes_size = bsp_struct[_HEADER_PLANES_SIZE]
        number_of_planes = planes_size // Plane.size

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
        number_of_vertexes = vertexes_size // Vertex.size

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
        number_of_nodes = nodes_size // Node.size

        file.seek(nodes_offset)
        for _ in range(number_of_nodes):
            bsp.nodes.append(Node.read(file))

        # Texture Infos
        texture_infos_offset = bsp_struct[_HEADER_TEXTURE_INFOS_OFFSET]
        texture_infos_size = bsp_struct[_HEADER_TEXTURE_INFOS_SIZE]
        number_of_texture_infos = texture_infos_size // TextureInfo.size

        file.seek(texture_infos_offset)
        for _ in range(number_of_texture_infos):
            bsp.texture_infos.append(TextureInfo.read(file))

        # Faces
        faces_offset = bsp_struct[_HEADER_FACES_OFFSET]
        faces_size = bsp_struct[_HEADER_FACES_SIZE]
        number_of_faces = faces_size // Face.size

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
        number_of_clip_nodes = clip_nodes_size // ClipNode.size

        file.seek(clip_nodes_offset)
        for _ in range(number_of_clip_nodes):
            bsp.clip_nodes.append(ClipNode.read(file))

        # Leafs
        leafs_offset = bsp_struct[_HEADER_LEAFS_OFFSET]
        leafs_size = bsp_struct[_HEADER_LEAFS_SIZE]
        number_of_leafs = leafs_size // Leaf.size

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
        number_of_edges = edges_size // Edge.size

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
        number_of_models = models_size // Model.size

        file.seek(models_offset)
        for _ in range(number_of_models):
            bsp.models.append(Model.read(file))

        return bsp

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
