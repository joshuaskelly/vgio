"""This module provides file I/O for Quake BSP2 map files.

Example:
    bsp_file = bsp.Bsp.open('ad_sepulcher.bsp')
"""

import struct

from vgio.quake.bsp import bsp29


__all__ = ['is_bspfile', 'Bsp']


def is_bspfile(filename):
    """Quickly see if a file is a bsp file by checking the magic number.

    The filename argument may be a file for file-like object.

    Args:
        filename: File to check as string or file-like object.

    Returns:
        True if given file's magic number is correct.
    """
    return bsp29.is_bspfile(filename)


class Model(bsp29.Bsp.factory.Model):
    """Class for representing a model

    Attributes:
        bounding_box_min: The minimum coordinate of the bounding box containing
            the model.

        bounding_box_max: The maximum coordinate of the bounding box containing
            the model.

        origin: The origin of the model.

        head_node: An eight-tuple of indexes. Corresponds to number of map hulls.

        visleafs: The number of leaves in the bsp tree?

        first_face: The number of the first face in Bsp.mark_surfaces.

        number_of_faces: The number of faces contained in the node. These
            are stored in consecutive order in Bsp.mark_surfaces starting at
            Model.first_face.
    """

    format = '<9f11i'
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
                 head_node_4,
                 head_node_5,
                 head_node_6,
                 head_node_7,
                 visleafs,
                 first_face,
                 number_of_faces):
        """Constructs a Model object."""

        self.bounding_box_min = bounding_box_min_x, bounding_box_min_y, bounding_box_min_z
        self.bounding_box_max = bounding_box_max_x, bounding_box_max_y, bounding_box_max_z
        self.origin = origin_x, origin_y, origin_z
        self.head_node = head_node_0, head_node_1, head_node_2, head_node_3, head_node_4, head_node_5, head_node_6, head_node_7
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


class Bsp(bsp29.Bsp):
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
    class factory(bsp29.Bsp.factory):
        Model = Model
