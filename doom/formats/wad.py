"""Module for working with id Software style WAD files

Supported Games:
    - DOOM
    - DOOM2
"""

import struct
from collections import namedtuple

from doom.formats import datastructures
from doom.formats.datastructures import Header, header_format

def load(file_path):
    """Creates a dictionary representation of a wad file.

    Args:
        file_path (string): The pathn to the wad file.

    Returns:
        (Wad): Wad file of parsed data.
    """

    with open(file_path, 'rb') as file:
        def read_struct(file, tup, format):
            read_data = file.read(struct.calcsize(format))
            unpacked_tuple = struct.unpack(format, read_data)
            args = list(map(lambda s: s.decode('ascii').strip('\x00') if hasattr(s, 'decode') else s, unpacked_tuple))
            return tup._make(args)

        header = read_struct(file, Header, header_format)
        file.seek(header.directory_pointer)
        lumps = LumpList()

        for _ in range(header.directory_size):
            lump = read_struct(file, Lump, '<2i8s')

            def read_entry_callback(entry):
                if entry.size == 0:
                    return None

                with open(file_path, 'rb') as file:
                    file.seek(entry.pointer)

                    # See if we have a definition for the lump data structure
                    if entry.name in datastructures.__dict__:
                        lump_info = datastructures.__dict__[entry.name]
                        number_of_definitions = entry.size // struct.calcsize(lump_info['format'])
                        
                        return [read_struct(file, lump_info['typename'], lump_info['format']) for _ in range(number_of_definitions)]
                    else:
                        return file.read(entry.size)

            lump.callback = read_entry_callback
            lumps.append(lump)

        return Wad(header.type, lumps)

class Wad:
    def __init__(self, type, lumps):
        self.type = type
        self.lumps = lumps

class Lump:
    def __init__(self, pointer, size, name):
        self.__data = None
        self.name = name
        self.size = size
        self.pointer = pointer
        self.callback = None

    def __repr__(self):
        return '<{0} name={1}>'.format(self.__class__.__name__, self.name)

    @property
    def data(self):
        if (self.__data is None and self.callback is not None):
            self.__data = self.callback(self)

        return self.__data

    @staticmethod
    def _make(args):
        return Lump(args[0], args[1], args[2])

class LumpList(list):
    def __getitem__(self, key):
        if type(key) is str:
            return next((i for i in self if i.name == key), None)
        else:
            return list.__getitem__(self, key)

    def __contains__(self, key):
        return self[key] is not None

    def index(self, key):
        if type(key) is str:
            return next((i for i in range(len(self)) if self[i].name == key), None)
        else:
            return list.index(self, key)