"""This module provides file I/O for Duke3D Art archive files.

Example:
    art_file = art.ArtFile.open('tiles001.art')

References:
    "Build Engine & Tools"
    - Ken Silverman
    - http://fabiensanglard.net/duke3d/BUILDINF.TXT
"""

import io
import struct

from vgio._core import ArchiveFile, _ArchiveWriteFile


__all__ = ['BadArtFile', 'is_artfile', 'ArtInfo', 'ArtFile']


VERSION = 1


class BadArtFile(Exception):
    pass


def _check_artfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<l'))
    data = struct.unpack('<l', data)[0]

    return data == 1


def is_artfile(filename):
    """Quickly see if a file is a art file by checking the magic number.

    The filename argument may be a file for file-like object.

    Args:
        filename: File to check as string or file-like object.

    Returns:
        True if given file's magic number is correct.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_artfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_artfile(fp)

    except Exception:
        return False


class Header:
    format = '<4l'
    size = struct.calcsize(format)

    __slots__ = (
        'version',
        'number_of_tiles',
        'local_tiles_start_id',
        'local_tiles_end_id'
    )

    def __init__(self,
                 version,
                 number_of_tiles,
                 local_tiles_start_id,
                 local_tiles_end_id):
        self.version = version
        self.number_of_tiles = number_of_tiles
        self.local_tiles_start_id = local_tiles_start_id
        self.local_tiles_end_id = local_tiles_end_id

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(cls.format,
                                  header.version,
                                  header.number_of_tiles,
                                  header.local_tiles_start_id,
                                  header.local_tiles_end_id)

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class ArtInfo:
    """Instances of the ArtInfo class are returned by the getinfo() and
    infolist() methods of ArtFile objects. Each object stores information about
    a single member of the ArtFile archive.

    Attributes:
        tile_index: Index of the tile in the archive.

        tile_dimensions: The size of the tile.

        picanim: A sequence of bitmasked tile attributes.

        file_offset: Offset of file in bytes.

        file_size: Size of the file in bytes.
    """

    __slots__ = (
        'tile_index',
        'tile_dimensions',
        'picanim',
        'file_offset',
        'file_size'
    )

    def __init__(self,
                 tile_index,
                 tile_dimensions=(0, 0),
                 file_offset=0,
                 file_size=0):
        """Constructs an ArtInfo object."""

        self.tile_index = tile_index
        self.tile_dimensions = tile_dimensions
        self.picanim = 0
        self.file_offset = file_offset
        self.file_size = file_size

    @property
    def filename(self):
        return self.tile_index


class _ArtWriteFile(_ArchiveWriteFile):
    def __init__(self, archive_file, archive_info):
        super().__init__(archive_file, archive_info)

    @property
    def _fileobj(self):
        return self._archive_file.data_buffer

    def close(self):
        super().close()

        self._archive_file.tile_x_dimensions.append(self._archive_info.tile_dimensions[0])
        self._archive_file.tile_y_dimensions.append(self._archive_info.tile_dimensions[1])
        self._archive_file.picanims.append(self._archive_info.picanim)
        self._archive_file.local_tile_end += 1


class ArtFile(ArchiveFile):
    """Class with methods to open, read, close, and list art files.

    Example:
        Basic usage::

            from vgio.duke3d.art import ArtFile
            art_file = ArtFile(file, mode='r')

    Attributes:
        file: Either the path to the file, or a file-like object. If it is a
            path, the file will be opened and closed by ArtFile.

        mode: The file mode for the file-like object.
    """

    class factory(ArchiveFile.factory):
        ArchiveInfo = ArtInfo
        ArchiveWriteFile = _ArtWriteFile

    def __init__(self, file, mode='r'):
        """Open an Art file, where *file* can be a path to a file (a string), or
        a file-like object.

        The mode parameter should be 'r' to read an existing file, 'w' to
        truncate and write a new file, or 'a' to append to an existing file.

        Args:
            file: A path or a file-like object.

            mode: File mode for the file-like object.
        """
        self.end_of_data = 0

        self.data_buffer = io.BytesIO()
        self.version = VERSION
        self.number_of_tiles = 0
        self.local_tile_start = 0
        self.local_tile_end = -1
        self.tile_x_dimensions = []
        self.tile_y_dimensions = []
        self.picanims = []

        super().__init__(file, mode)

    def _read_file(self, mode='r'):
        """Read in the directory information for the art file."""
        self.fp.seek(0)
        header = Header.read(self.fp)

        if header.version != VERSION:
            raise BadArtFile(f'Bad version number: {header.version}')

        self.local_tile_start = header.local_tiles_start_id
        self.local_tile_end = header.local_tiles_end_id
        self.number_of_tiles = self.local_tile_end - self.local_tile_start + 1

        # Read in tile dimensions data
        tile_dimensions_format = f'<{2 * self.number_of_tiles}h'
        tile_dimensions_size = struct.calcsize(tile_dimensions_format)
        tile_dimensions = self.fp.read(tile_dimensions_size)
        tile_dimensions = struct.unpack(tile_dimensions_format, tile_dimensions)
        self.tile_x_dimensions = list(tile_dimensions[:self.number_of_tiles])
        self.tile_y_dimensions = list(tile_dimensions[self.number_of_tiles:])
        tile_dimensions = tuple(zip(self.tile_x_dimensions, self.tile_y_dimensions))

        # Read in picanim data
        picanims_format = f'<{self.number_of_tiles}l'
        picanims_size = struct.calcsize(picanims_format)
        picanims = self.fp.read(picanims_size)
        picanims = list(struct.unpack(picanims_format, picanims))
        self.picanims = picanims

        start_of_data = self.fp.tell()

        local_file_sizes = list(map(lambda x: x[0] * x[1], tile_dimensions))
        size_of_data = sum(local_file_sizes)
        data = self.fp.read(size_of_data)

        if size_of_data != len(data):
            raise BadArtFile('Expected: %i bytes, actual: %i bytes') % (size_of_data, len(data))

        local_file_offset = start_of_data

        for index, dimensions in enumerate(tile_dimensions):
            local_file_size = local_file_sizes[index]
            local_tile_index = self.local_tile_start + index
            info = ArtInfo(local_tile_index, dimensions, local_file_offset, local_file_size)
            local_file_offset += local_file_size

            self.file_list.append(info)
            self.NameToInfo[info.tile_index] = info

        if mode == 'a':
            self.data_buffer = io.BytesIO(self.fp.read())

    def _write_directory(self):
        self.fp.seek(0)

        count = len(self.file_list)
        header = Header(1, count, self.local_tile_start, self.local_tile_end)
        Header.write(self.fp, header)

        # Write tile dimensions
        tile_dimensions_data = struct.pack(
            f'<{2 * count}h',
            *(self.tile_x_dimensions + self.tile_y_dimensions)
        )

        self.fp.write(tile_dimensions_data)

        # Write picanim data
        picanims_data = struct.pack(
            f'<{count}l',
            *self.picanims
        )

        self.fp.write(picanims_data)

        self._write_data()

    def _write_data(self):
        self.data_buffer.seek(0)
        self.fp.write(self.data_buffer.read())
