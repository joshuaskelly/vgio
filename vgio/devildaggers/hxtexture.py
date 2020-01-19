"""This module provides file I/O for Devil Daggers texture files.

Example:
    hxtex_file = hxtexture.HxTexture.open('blood')
"""

import struct

from vgio._core import ReadWriteFile


class Header:
    """Class for representing a HxTexture file header.

    Attributes:
        texture_format:  Texture format. Should be 0x4011

        width:  Width of the texture at mip level 0.

        height:  Height of the texture at mip level 0.

        mip_level_count:  Number of mip levels.
    """

    format = '<h2iB'
    size = struct.calcsize(format)

    __slots__ = (
        'texture_format',
        'width',
        'height',
        'mip_level_count'
    )

    def __init__(self,
                 texture_format,
                 width,
                 height,
                 mip_level_count):
        self.texture_format = texture_format
        self.width = width
        self.height = height
        self.mip_level_count = mip_level_count

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.texture_format,
            header.width,
            header.height,
            header.mip_level_count
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class HxTexture(ReadWriteFile):
    """Class for working with HxTextures.

    Attributes:
        texture_format: Likely a texture format?

        width: Texture width at mip level 0.

        height: Texture height at mip level 0.

        mip_level_count: Number of mip levels

        pixels: An unstructured sequence of interleaved RGBA data as bytes.
    """
    def __init__(self):
        """Constructs an HxTexture object."""

        super().__init__()

        self.texture_format = 0x4011
        self.width = 0
        self.height = 0
        self.mip_level_count = 0
        self.pixels = None

    @classmethod
    def _read_file(cls, file, mode):
        ht = HxTexture()
        ht.fp = file
        ht.mode = mode

        header = Header.read(file)

        ht.texture_format = header.texture_format
        ht.width = header.width
        ht.height = header.height
        ht.mip_level_count = header.mip_level_count
        ht.pixels = file.read()

        return ht

    @classmethod
    def _write_file(cls, file, hxtex):
        header = Header(
            hxtex.texture_format,
            hxtex.width,
            hxtex.height,
            hxtex.mip_level_count
        )
        Header.write(file, header)

        file.write(hxtex.pixels)
