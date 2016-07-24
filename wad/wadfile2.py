"""Module for working with id Software style WAD files

Supported Games:
    - DOOM
    - DOOM2
"""

import sys

from os import path
import re
from struct import unpack

PYTHON_3 = sys.version[0] == '3'

def load(name):
    """Creates a dictionary representation of a wad file.

    Args:
        name (string): The pathname of the wad file to open.

    Returns:
        WadFile (dictionary): Wad file of parsed data.

    """

    with open(name, "rb") as f:
        if not is_wadfile(f):
            print("I think it is not a wad file")
            return None

        def read_string(length):
            """Return a string of length bytes"""
            result = unpack("{}s".format(length), f.read(length))[0].partition(b"\0")[0]
            if PYTHON_3:
                return result

            return result.encode("utf-8")

        def read_int():
            """Returns a little-endian signed integer"""
            return unpack("<i", f.read(4))[0]

        def read_unsigned_char():
            """Returns a little-endian unsigned integer"""
            return unpack("<B", f.read(1))[0]

        def read_short():
            """Returns a little-endian signed short"""
            return unpack("<h", f.read(2))[0]

        def read_unsigned_short():
            """Returns a little-endian unsigned short"""
            return unpack("<H", f.read(2))[0]

        def read_directory_entry():
            return {"file_position": read_int(), "size": read_int(), "name": read_string(8)}



        # Read header
        file_signature = read_string(4)
        num_lumps = read_int()
        directory_offset = read_int()

        # Read directory entries
        f.seek(directory_offset)
        directory = [read_directory_entry() for _ in range(num_lumps)]

        # Process the data lumps
        lumps = []
        markers = []

        def is_map():
            if not markers:
                return False

            index = [e["name"] for e in directory].index(markers[-1])
            last_index = min(index + 11, len(directory))
            following_entries = [e["name"] for e in directory[index:last_index]]
            required_entries = ["THINGS", "LINEDEFS", "SIDEDEFS", "VERTEXES", "SECTORS"]
            common = set(following_entries).intersection(required_entries)

            return len(common) == len(required_entries)

        def is_sprite():
            if not markers:
                return False

            return markers[-1] == "S_START"

        def is_patch():
            if not markers:
                return False

            return re.match('P\d*_START', markers[-1]) is not None

        def is_flat():
            if not markers:
                return False

            return re.match('F\d*_START', markers[-1]) is not None

        for entry in directory:
            name = entry["name"]
            index = directory.index(entry)
            f.seek(entry["file_position"])

            if entry["size"] == 0:
                markers.append(entry["name"])
                continue

            if is_map():
                if name == "LINEDEFS":
                    data = []

                    while f.tell() < entry["file_position"] + entry["size"]:
                        l = WadFile.Map.Line(vertex_1=read_short(),
                                             vertex_2=read_short(),
                                             flags=read_short(),
                                             specials=read_short(),
                                             tag=read_short(),
                                             front_side=read_short(),
                                             back_side=read_short())
                        data.append(l)

                elif name == "NODES":
                    data = []

                    while f.tell() < entry["file_position"] + entry["size"]:
                        n = WadFile.Map.Node(x=read_short(),
                                             y=read_short(),
                                             dx=read_short(),
                                             dy=read_short(),
                                             right_bounding_box_top=read_short(),
                                             right_bounding_box_bottom=read_short(),
                                             right_bounding_box_left=read_short(),
                                             right_bounding_box_right=read_short(),
                                             left_bounding_box_top=read_short(),
                                             left_bounding_box_bottom=read_short(),
                                             left_bounding_box_left=read_short(),
                                             left_bounding_box_right=read_short(),
                                             right_child=read_unsigned_short(),
                                             left_child=read_unsigned_short())
                        data.append(n)

                elif name == "SIDEDEFS":
                    data = []

                    while f.tell() < entry["file_position"] + entry["size"]:
                        s = WadFile.Map.Side(x_offset=read_short(),
                                             y_offset=read_short(),
                                             top_texture=read_string(8),
                                             bottom_texture=read_string(8),
                                             middle_texture=read_string(8),
                                             sector=read_short())
                        data.append(s)

                elif name == "SECTORS":
                    data = []

                    while f.tell() < entry["file_position"] + entry["size"]:
                        s = WadFile.Map.Sector(floor_height=read_short(),
                                               ceiling_height=read_short(),
                                               floor_texture=read_string(8),
                                               ceiling_texture=read_string(8),
                                               light_level=read_short(),
                                               special=read_short(),
                                               tag=read_short())
                        data.append(s)

                elif name == "SEGS":
                    data = []

                    while f.tell() < entry["file_position"] + entry["size"]:
                        s = WadFile.Map.Seg(vertex_1=read_short(),
                                            vertex_2=read_short(),
                                            angle=read_short(),
                                            linedef=read_short(),
                                            side=read_short(),
                                            offset=read_short())
                        data.append(s)

                elif name == "SSECTORS":
                    data = []

                    while f.tell() < entry["file_position"] + entry["size"]:
                        s = WadFile.Map.SubSector(seg_count=read_short(),
                                                  first_seg=read_short())
                        data.append(s)

                elif name == "THINGS":
                    data = []

                    while f.tell() < entry["file_position"] + entry["size"]:
                        t = WadFile.Map.Thing(x=read_short(),
                                              y=read_short(),
                                              direction=read_short(),
                                              type=read_short(),
                                              flags=read_short())
                        data.append(t)

                elif name == "VERTEXES":
                    data = []

                    while f.tell() < entry["file_position"] + entry["size"]:
                        v = WadFile.Map.Vertex(x=read_short(),
                                               y=read_short())
                        data.append(v)

            elif is_sprite():
                pass
            elif is_patch():
                data = {}
                data["width"] = read_unsigned_short()
                data["height"] = read_unsigned_short()
                data["x_offset"] = read_short()
                data["y_offset"] = read_short()
                column_pointers = [read_int() for _ in range(data["width"])]

                # Read spans
                for pointer in column_pointers:
                    f.seek(pointer)
                    # Read header
                    offset = read_unsigned_char()
                    number_pixels = read_unsigned_char()
                    ignore = read_unsigned_char()


            elif is_flat():
                data = {}
                data["width"] = 64
                data["height"] = 64
                data["pixels"] = [read_unsigned_char() for _ in range(4096)]

            else:
                if name == "PLAYPAL":
                    data = []

                    while f.tell() < entry["file_position"] + entry["size"]:
                        for palette in range(14):
                            data.append([{
                                "r": read_unsigned_char(),
                                "g": read_unsigned_char(),
                                "b": read_unsigned_char()
                            } for color in range(256)])
                else:
                    data = f.read(entry["size"])

            lumps.append({"name": name, "value": data})

    return WadFile(lumps)


def is_wadfile(name):
    """Returns if the given path or file is a wad file

    Note:
        If the passed arg is a file object, the current position will be
        preserved and assumes the caller will handle closing the file.

    Args:
        name (string or File Object): The object to determine if a wad file
    """

    # Handle File Objects
    if hasattr(name, "read"):
        f = name
        current_position = f.tell()

        # Read file signature
        f.seek(0)
        file_signature = unpack("4s", f.read(4))[0]

        # Restore position
        f.seek(current_position)

    # Handle file path
    else:
        if not path.exists(name):
            return False

        with open(name, "rb") as f:
            file_signature = unpack("4s", f.read(4))[0]

    file_signature= file_signature.decode("ascii")

    return file_signature == "IWAD" or file_signature == "PWAD"


class WadFile:
    """ Class that represents data stored in the WAD file format.
    """
    class Lump:
        """ Class that represents a named chunk of data

        Attributes:
            name (string): Name of the lump
            value (object): The data
        """
        def __init__(self, name, value=None):
            self.name = name
            self.value = value

        def __repr__(self):
            return "Lump: %r" % self.name

    class Map:
        class BlockMap:
            def __init__(self):
                pass

        class Line:
            def __init__(self, vertex_1, vertex_2, flags, specials, tag, front_side, back_side):
                self.vertex_1 = vertex_1
                self.vertex_2 = vertex_2
                self.flags = flags
                self.specials = specials
                self.tag = tag
                self.front_side = front_side
                self.back_side = back_side

        class Node:
            class BoundingBox:
                def __init__(self, top, bottom, left, right):
                    self.top = top
                    self.bottom = bottom
                    self.left = left
                    self.right = right

            def __init__(self,
                         x,
                         y,
                         dx,
                         dy,
                         right_bounding_box_top,
                         right_bounding_box_bottom,
                         right_bounding_box_left,
                         right_bounding_box_right,
                         left_bounding_box_top,
                         left_bounding_box_bottom,
                         left_bounding_box_left,
                         left_bounding_box_right,
                         right_child,
                         left_child
                         ):
                BoundingBox = WadFile.Map.Node.BoundingBox

                self.x = x
                self.y = y
                self.dx = dx
                self.dy = dy

                self.right_bounding_box = BoundingBox(right_bounding_box_top,
                                                      right_bounding_box_bottom,
                                                      right_bounding_box_left,
                                                      right_bounding_box_right)

                self.left_bounding_box = BoundingBox(left_bounding_box_top,
                                                     left_bounding_box_bottom,
                                                     left_bounding_box_left,
                                                     left_bounding_box_right)

                self.right_child = right_child
                self.left_child = left_child

        class Reject:
            def __init__(self):
                pass

        class Sector:
            def __init__(self, floor_height, ceiling_height, floor_texture, ceiling_texture, light_level, special, tag):
                self.floor_height = floor_height
                self.ceiling_height = ceiling_height
                self.floor_texture = floor_texture
                self.ceiling_texture = ceiling_texture
                self.light_level = light_level
                self.special = special
                self.tag = tag

        class Seg:
            def __init__(self, vertex_1, vertex_2, angle, linedef, side, offset):
                self.vertex_1 = vertex_1
                self.vertex_2 = vertex_2
                self.angle = angle
                self.linedef = linedef
                self.side = side
                self.offset = offset

        class Side:
            def __init__(self, x_offset, y_offset, top_texture, bottom_texture, middle_texture, sector):
                self.x_offset = x_offset
                self.y_offset = y_offset
                self.top_texture = top_texture
                self.bottom_texture = bottom_texture
                self.middle_texture = middle_texture
                self.sector = sector

        class SubSector:
            def __init__(self, seg_count, first_seg):
                self.seg_count = seg_count
                self.first_seg = first_seg

        class Thing:
            def __init__(self, x, y, direction, type, flags):
                self.x = x
                self.y = y
                self.direction =  direction
                self.type = type
                self.flags = flags

        class Vertex:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __getitem__(self, index):
                if index == 0:
                    return self.x
                elif index == 1:
                    return self.y
                else:
                    raise "IndexError: range object index out of range"

        def __init__(self, name):
            """ Constructor for Map class
            """
            self.name = name

    def __init__(self, lumps=[]):
        """ Constructor for WadFile class
        """
        self.lumps = lumps

