"""This module provides file I/O for Quake BSP2 map files.

Example:
    bsp_file = bsp.Bsp.open('ad_sepulcher.bsp')
"""

import struct

from .bsp29 import Bsp as Bsp29


__all__ = ['is_bspfile', 'Bsp']


IDENTITY = b'BSP2'


def _check_bspfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4s'))
    identity = struct.unpack('<4s', data)[0]

    return identity == IDENTITY


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


class Node(Bsp29.factory.Node):
    format = '<i8i2I'
    size = struct.calcsize(format)


class Face(Bsp29.factory.Face):
    format = '<2ii2i4Bi'
    size = struct.calcsize(format)


class ClipNode(Bsp29.factory.ClipNode):
    format = '<i2i'
    size = struct.calcsize(format)


class Leaf(Bsp29.factory.Leaf):
    format = '<2i6i2I4B'
    size = struct.calcsize(format)


class Edge(Bsp29.factory.Edge):
    format = '<2I'
    size = struct.calcsize(format)


class Bsp(Bsp29):
    """Class for working with Bsp files

    Example:
        Basic usage::

            from vgio.quake.bsp.bsp29a import Bsp
            b = Bsp.open('ad_sepulcher.bsp')

    Attributes:
        version: Version of the map file. Vanilla Quake is 29.

        entities: A string containing the entity definitions.

        planes: A sequence of Planes used by the bsp tree data structure.

        miptextures: A sequence of Miptextures.

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

        fp: The file-like object to read data from.

        mode: The file mode for the file-like object.
    """
    class factory(Bsp29.factory):
        Node = Node
        Face = Face
        ClipNode = ClipNode
        Leaf = Leaf
        Edge = Edge
