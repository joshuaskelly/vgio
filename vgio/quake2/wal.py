"""This module provides file I/O for Quake 2 WAL texture files.

Example:
    with open('arrow0.wal') as file:
        wal_file = wal.Wal.read(file)

References:
    Quake 2 Source
    - id Software
    - https://github.com/id-Software/Quake-2
"""

import struct

from vgio._core import ReadWriteFile

__all__ = ['Wal']


class Header:
    """Class for representing a Wal file header

    Attributes:
        name:  Name of the wal texture.

        width:  Width of the wal texture at mip level 0.

        height:  Height of the wal texture at mip level 0.

        offsets:  The offsets for each of the mipmaps.

        animation_name:  The name of the next wal texture in the animation

        flags:  A bitfield of surface behaviors.

        contents:

        value:
    """

    format = '<32s6I32s3i'
    size = struct.calcsize(format)

    __slots__ = (
        'name',
        'width',
        'height',
        'offsets',
        'animation_name',
        'flags',
        'contents',
        'value'
    )

    def __init__(self,
                 name,
                 width,
                 height,
                 offsets_0,
                 offsets_1,
                 offsets_2,
                 offsets_3,
                 animation_name,
                 flags,
                 contents,
                 value):
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name
        self.width = width
        self.height = height
        self.offsets = offsets_0, offsets_1, offsets_2, offsets_3
        self.animation_name = animation_name.split(b'\x00')[0].decode('ascii') if type(animation_name) is bytes else animation_name
        self.flags = flags
        self.contents = contents
        self.value = value

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.name.encode('ascii'),
            header.width,
            header.height,
            *header.offsets,
            header.animation_name.encode('ascii'),
            header.flags,
            header.contents,
            header.value
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Wal(ReadWriteFile):
    """Class for working with Wal files

    Example:
        with open(path) as file:
            w = wal.Wal.read(file)

    Attributes:
        name: The name of the wal texture.

        width: The width of the wal texture.
            Note: This is the width at mipmap level 0.

        height: The height of the wal texture.
            Note: This is the height at mipmap level 0.

        offsets: The offsets for each of the mipmaps. This is a tuple of size
            four (this is the number of mipmap levels).

        animation_name: The name of the next wal texture in the animation
            sequence.

        flags: A bitfield of surface behaviors.

        contents:

        value:

        pixels: A bytes object of unstructured indexed color data. A
            palette must be used to obtain RGB data.

            Note: this is the pixel data for all four mip levels. The size is
            calculated using the simplified form of the geometric series where
            r = 1/4 and n = 4.

            The size of this tuple is:

            wal.width * wal.height * 85 / 64
    """

    class factory:
        Header = Header

    def __init__(self):
        super().__init__()

        self.name = ''
        self.width = 0
        self.height = 0
        self.offsets = 0, 0, 0, 0
        self.animation_name = ''
        self.flags = 0
        self.contents = 0
        self.value = 0
        self.pixels = None

    @classmethod
    def _read_file(cls, file, mode):
        wal = Wal()
        wal.fp = file
        wal.mode = mode

        header = Header.read(file)

        wal.name = header.name
        wal.width = header.width
        wal.height = header.height
        wal.offsets = header.offsets
        wal.animation_name = header.animation_name
        wal.flags = header.flags
        wal.contents = header.contents
        wal.value = header.value

        pixels_size = wal.width * wal.height * 85 // 64
        wal.pixels = file.read(pixels_size)

        return wal

    @classmethod
    def _write_file(cls, file, wal):
        header = wal.factory.Header(
            wal.name,
            wal.width,
            wal.height,
            *wal.offsets,
            wal.animation_name,
            wal.flags,
            wal.contents,
            wal.value
        )

        wal.factory.Header.write(file, header)
        file.write(wal.pixels)
