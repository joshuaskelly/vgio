"""This module provides file I/O for Quake LMP lump files.

Example:
    lmp_file = lmp.Lmp.open('palette.lmp')

References:
    Quake Source
    - id Software
    - https://github.com/id-Software/Quake

    Quake Documentation Version 3.4
    - Olivier Montanuy, et al.
    - http://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_7.htm#CWADS
"""

import io
import struct

from vgio import quake

__all__ = ['BadLmpFile', 'Lmp']


class BadLmpFile(Exception):
    pass


# The header structure for 2D lumps
header_format = '<2l'
header_size = struct.calcsize(header_format)

# The data structure for palette lumps
palette_format = '<768B'
palette_size = struct.calcsize(palette_format)

# The data structure for colormap lumps
colormap_format = '<16384B'
colormap_size = struct.calcsize(colormap_format)

# For some reason the colormap shipped with Quake has one extra byte
quake_colormap_size = struct.calcsize('<16385B')


class Image(object):
    """Class for representing pixel data

    Attributes:
        width: The width of the image.

        height: The height of the image.

        format: A string describing the format of the color data. Usually 'RGB'
            or 'RGBA'

        pixels: The raw pixel data of the image.
            The length of this attribute is:

            width * height * len(format)
    """

    __slots__ = (
        'width',
        'height',
        'format',
        'pixels'
    )

    def __init__(self):
        self.width = 0
        self.height = 0
        self.format = 'RGBA'
        self.pixels = None


class Lmp(object):
    """Class for working with Lmp files

    There are three different types of lump files:
        1. 2D image - The majority of the lump files are 2D images. If a lump 
            is a 2D image it will have width, height, and pixels attributes.

        2. Palette - The palette lump has the palette attribute which is a 
            list of 256 RGB tuples. This is used to map color indexes to 
            actual RGB triples.

        3. Colormap - The colormap lump has the colormap attribute which is a
            list of 16384 color indexes. It functions as a 256 x 64 table for 
            mapping colors to different values for lighting.
    
    Example:
        l = Lmp.open(file)

    Attributes:
        width: (2D image lump only) The width of the lump.

        height: (2D image lump only) The height of the lump.

        pixels: (2D image lump only) The raw pixel data.

        palette: (Palette lump only) A list of 256 RGB tuples.

        colormap: (Color Map lump only) A list of 16384 color indexes.
    """

    def __init__(self):
        self.fp = None
        self.mode = None
        self._did_modify = False

    @staticmethod
    def open(file, mode='r'):
        """Returns an Lmp object
        
        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file

        Returns:
            An Lmp object constructed from the information read from the
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
            raise RuntimeError("Lmp.open() requires 'file' to be a path, a file-like object, or bytes")

        # Read
        if mode == 'r':
            return Lmp._read_file(file, mode)

        # Write
        elif mode == 'w':
            lmp = Lmp()
            lmp.fp = file
            lmp.mode = 'w'
            lmp._did_modify = True

            return lmp

        # Append
        else:
            lmp = Lmp._read_file(file, mode)
            lmp._did_modify = True

            return lmp

    @staticmethod
    def _read_file(file, mode):
        data = file.read(-1)
        data_size = len(data)

        width, height = struct.unpack(header_format, data[0:8])

        # Determine which kind of lump we are working with
        if width * height + header_size == data_size:
            lump = Lmp._read_lmp(data)

        elif data_size == palette_size:
            lump = Lmp._read_palette(data)

        elif data_size == colormap_size or data_size == quake_colormap_size:
            lump = Lmp._read_colormap(data)

        else:
            raise BadLmpFile("unable to determine format of lump file")

        lump.fp = file
        lump.mode = mode

        return lump

    @staticmethod
    def _read_lmp(data):
        """Returns a 2D image lump.
        
        Args:
            data: A byte array
        """

        width, height = struct.unpack(header_format, data[:header_size])

        pixels_format = '<%iB' % (width * height)
        pixels_size = struct.calcsize(pixels_format)

        pixels = data[header_size:pixels_size + header_size]
        pixels = struct.unpack(pixels_format, pixels)

        lmp = Lmp()
        lmp.width = width
        lmp.height = height
        lmp.pixels = pixels

        return lmp

    @staticmethod
    def _read_palette(data):
        """Returns a palette lump
        
        Args:
            data: A byte array.
        """

        data = struct.unpack(palette_format, data)

        pixels = []
        i = 0

        while i < 768:
            pixels.append((data[i], data[i + 1], data[i + 2]))
            i += 3

        lmp = Lmp()
        lmp.palette = pixels

        return lmp

    @staticmethod
    def _read_colormap(data):
        """Returns a colormap lump
        
        Args:
            data: A byte array.
        """

        data = struct.unpack(colormap_format, data[:colormap_size])

        lmp = Lmp()
        lmp.colormap = data

        return lmp

    @staticmethod
    def _write_lmp(file, lmp):
        header_data = struct.pack(header_format,
                                  lmp.width,
                                  lmp.height)

        pixels_format = '<%iB' % (lmp.width * lmp.height)
        pixels_data = struct.pack(pixels_format,
                                  *lmp.pixels)

        file.write(header_data)
        file.write(pixels_data)

    @staticmethod
    def _write_palette(file, lmp):
        # Flatten out palette
        palette = []

        for i in lmp.palette:
            palette.append(i[0])
            palette.append(i[1])
            palette.append(i[2])

        if len(palette) != 768:
            raise BadLmpFile

        palette_data = struct.pack(palette_format,
                                   *palette)

        file.write(palette_data)

    @staticmethod
    def _write_colormap(file, lmp):
        if len(lmp.colormap) != colormap_size:
            raise BadLmpFile

        colormap_data = struct.pack(colormap_format,
                                    *lmp.colormap)

        file.write(colormap_data)

    @staticmethod
    def _write_file(file, lmp):
        if hasattr(lmp, 'width') and hasattr(lmp, 'width'):
            Lmp._write_lmp(file, lmp)

        elif hasattr(lmp, 'palette'):
            Lmp._write_palette(file, lmp)

        elif hasattr(lmp, 'colormap'):
            Lmp._write_colormap(file, lmp)

        else:
            raise BadLmpFile('Unable to determine type of Lmp file to write')

    @staticmethod
    def write(file, lmp):
        Lmp._write_file(file, lmp)

    def save(self, file):
        """Writes Lmp data to file

        Args:
            file: Either the path to the file, or a file-like object, or bytes.

        Raises:
            RuntimeError: If file argument is not a file-like object.

            BadLmpFile: If unable to determine type of Lmp to write.
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
                "Lmp.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        Lmp._write_file(file, self)

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
                Lmp._write_file(self.fp, self)
                self.fp.truncate()

        file_object = self.fp
        self.fp = None
        file_object.close()

    def image(self, palette=quake.palette):
        """Returns an Image object.

        Args:
            palette: A 256 color palette to use for converted index color data
            to RGBA data.

        Returns:
            An Image object.
        """

        image = Image()

        if hasattr(self, 'palette'):
            image.width = 16
            image.height = 16
            
            p = []
            for i, entry in enumerate(self.palette):
                p += (entry)
                p += [255] if i is not 255 else [0]

            image.pixels = p

        elif hasattr(self, 'colormap'):
            image.width = 256
            image.height = 64
            
            p = []
            for index in self.colormap:
                p += palette[index]
                p += [255] if index is not 255 else [0]

            image.pixels = p

        else:
            image.width = self.width
            image.height = self.height
            
            p = []
            for index in self.pixels:
                p += palette[index]
                p += [255] if index is not 255 else [0]

            image.pixels = p

        d = []
        for row in reversed(range(image.height)):
            d += image.pixels[row * image.width * 4:(row + 1) * image.width * 4]

        image.pixels = d

        return image
