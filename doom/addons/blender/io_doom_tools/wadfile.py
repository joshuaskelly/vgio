"""Module for working with id Software style WAD files

Supported Games:
    - DOOM
    - DOOM2
"""

from os import path
from struct import unpack


def load(name):
    """Creates a dictionary representation of a wad file.

    Args:
        name (string): The pathname of the wad file to open.

    Returns:
        WadFile (dictionary): Wad file of parsed data.

    """

    with open(name, "rb") as f:
        if not is_wadfile(f):
            return None

        def read_string(length):
            """Return a string of length bytes"""
            return unpack("{}s".format(length), f.read(length))[0].partition(b"\0")[0].decode("ascii")

        def read_int():
            """Returns a little-endian signed integer"""
            return unpack("<i", f.read(4))[0]

        def read_unsigned_char():
            """Returns a little-endian unsigned integer"""
            return unpack("<B", f.read(1))[0]

        def read_short():
            """Returns a little-endian signed short"""
            return unpack("<h", f.read(2))[0]

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
        for entry in directory:
            name = entry["name"]
            f.seek(entry["file_position"])

            if name == "LINEDEFS":
                data = []

                while f.tell() < entry["file_position"] + entry["size"]:
                    data.append({
                        "vertex_1": read_short(),
                        "vertex_2": read_short(),
                        "flags": read_short(),
                        "specials": read_short(),
                        "tag": read_short(),
                        "front_side": read_short(),
                        "back_side": read_short()
                    })

            elif name == "NODES":
                data = []

                while f.tell() < entry["file_position"] + entry["size"]:
                    data.append({
                        "x": read_short(),
                        "y": read_short(),
                        "dx": read_short(),
                        "dy": read_short(),
                        "right_bounding_box": {
                            "top": read_short(),
                            "bottom": read_short(),
                            "left": read_short(),
                            "right": read_short()
                        },
                        "left_bounding_box": {
                            "top": read_short(),
                            "bottom": read_short(),
                            "left": read_short(),
                            "right": read_short()
                        },
                        "right_child": read_short(),
                        "left_child": read_short()
                    })

            elif name == "PLAYPAL":
                data = []

                while f.tell() < entry["file_position"] + entry["size"]:
                    for palette in range(14):
                        data.append([{
                            "r": read_unsigned_char(),
                            "g": read_unsigned_char(),
                            "b": read_unsigned_char()
                        } for color in range(256)])

            elif name == "SIDEDEFS":
                data = []

                while f.tell() < entry["file_position"] + entry["size"]:
                    data.append({
                        "x_offset": read_short(),
                        "y_offset": read_short(),
                        "top_texture": read_string(8),
                        "bottom_texture": read_string(8),
                        "middle_texture": read_string(8),
                        "sector": read_short()
                    })

            elif name == "SECTORS":
                data = []

                while f.tell() < entry["file_position"] + entry["size"]:
                    data.append({
                        "floor_height": read_short(),
                        "ceiling_height": read_short(),
                        "floor_texture": read_string(8),
                        "ceiling_texture": read_string(8),
                        "light_level": read_short(),
                        "special": read_short(),
                        "tag": read_short()
                    })

            elif name == "SEGS":
                data = []

                while f.tell() < entry["file_position"] + entry["size"]:
                    data.append({
                        "vertex_1": read_short(),
                        "vertex_2": read_short(),
                        "angle": read_short(),
                        "linedef": read_short(),
                        "side": read_short(),
                        "offset": read_short()
                    })

            elif name == "SSECTORS":
                data = []

                while f.tell() < entry["file_position"] + entry["size"]:
                    data.append({
                        "number_of_segs": read_short(),
                        "first_seg": read_short()
                    })

            elif name == "THINGS":
                data = []

                while f.tell() < entry["file_position"] + entry["size"]:
                    data.append({
                        "x": read_short(),
                        "y": read_short(),
                        "angle": read_short(),
                        "type": read_short(),
                        "options": read_short()
                    })

            elif name == "VERTEXES":
                data = []

                while f.tell() < entry["file_position"] + entry["size"]:
                    data.append({
                        "x": read_short(),
                        "y": read_short()
                    })

            else:
                data = {}#f.read(entry["size"])

            lumps.append({"name": name, "value": data})

    return {"lumps": lumps}


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

    class Map:

        class BlockMap:
            def __init__(self):
                pass

        class Line:
            def __init__(self):
                pass

        class Node:
            def __init__(self):
                pass

        class Reject:
            def __init__(self):
                pass

        class Sector:
            def __init__(self):
                pass

        class Seg:
            def __init__(self):
                pass

        class Side:
            def __init__(self):
                pass

        class SubSector:
            def __init__(self):
                pass

        class Thing:
            def __init__(self):
                pass

        class Vertex:
            def __init__(self):
                pass

        def __init__(self):
            pass
    def __init__(self, name):
        self.name = name
