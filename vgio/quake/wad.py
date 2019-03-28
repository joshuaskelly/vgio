"""This module provides file I/O for Quake WAD archive files.

Example:
    wad_file = wad.Wad.open('gfx.wad')

References:
    Quake Source
    - id Software
    - https://github.com/id-Software/Quake

    Quake Documentation Version 3.4
    - Olivier Montanuy, et al.
    - http://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_7.htm
"""

import os
import stat
import struct

from vgio._core import ArchiveFile


__all__ = ['BadWadFile', 'is_wadfile', 'WadInfo', 'WadFile']


class BadWadFile(Exception):
    pass


def _check_wadfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4s'))

    return data == b'WAD2'


def is_wadfile(filename):
    """Quickly see if a file is a wad file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_wadfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_wadfile(fp)

    except Exception:
        return False


class Miptexture:
    """Class for representing a miptexture

    A miptexture is an indexed image mip map embedded within the map. Maps
    usually have many miptextures, and the miptexture lump is treated like a
    small wad file.

    Attributes:
        name: The name of the miptexture.

        width: The width of the miptexture.
            Note: this is the width at mipmap level 0.

        height: The height of the miptexture.
            Note: this is the height at mipmap level 0.

        offsets: The offsets for each of the mipmaps. This is a tuple of size
            four (this is the number of mipmap levels).

        pixels: A tuple of unstructured pixel data represented as integers. A
            palette must be used to obtain RGB data.

            Note: this is the pixel data for all four mip levels. The size is
            calculated using the simplified form of the geometric series where
            r = 1/4 and n = 4.

            The size of this tuple is:

            miptexture.width * miptexture.height * 85 / 64
    """

    format = '<16s6I'
    size = struct.calcsize(format)

    __slots__ = (
        'name',
        'width',
        'height',
        'offsets',
        'pixels'
    )

    def __init__(self):
        self.name = None
        self.width = None
        self.height = None
        self.offsets = None
        self.pixels = None

    @classmethod
    def write(cls, file, miptexture):
        miptexture_data = struct.pack(cls.format,
                                      miptexture.name.encode('ascii'),
                                      miptexture.width,
                                      miptexture.height,
                                      *miptexture.offsets)

        pixels_size = miptexture.width * miptexture.height * 85 // 64
        pixels_format = f'<{pixels_size}B'
        pixels_data = struct.pack(pixels_format, *miptexture.pixels)

        file.write(miptexture_data)
        file.write(pixels_data)

    @classmethod
    def read(cls, file):
        miptexture = Miptexture()
        miptexture_data = file.read(cls.size)
        miptexture_struct = struct.unpack(cls.format, miptexture_data)
        miptexture.name = miptexture_struct[0].split(b'\00')[0].decode('ascii')
        miptexture.width = miptexture_struct[1]
        miptexture.height = miptexture_struct[2]
        miptexture.offsets = miptexture_struct[3:]

        pixels_size = miptexture.width * miptexture.height * 85 // 64
        pixels_format = f'<{pixels_size}B'
        pixels_data = struct.unpack(pixels_format, file.read(pixels_size))

        miptexture.pixels = pixels_data

        return miptexture


class CompressionType:
    NONE = 0
    LZSS = 1


class LumpType:
    NONE = 0
    LABEL = 1
    LUMP = 64
    PALETTE = 64
    QTEX = 65
    QPIC = 66
    SOUND = 67
    MIPTEX = 68


class Header:
    format = '<4s2i'
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'lump_count',
        'directory_offset'
    )

    def __init__(self, identity, lump_count, directory_offset):
        self.identity = identity
        self.lump_count = lump_count
        self.directory_offset = directory_offset

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.identity,
            header.lump_count,
            header.directory_offset
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Entry:
    format = '<3i2B2x16s'
    size = struct.calcsize(format)

    __slots__ = (
        'file_offset',
        'disk_size',
        'file_size',
        'type',
        'compression',
        'filename'
    )

    def __init__(self,
                 file_offset,
                 disk_size,
                 file_size,
                 type_,
                 compression,
                 filename):
        self.file_offset = file_offset
        self.disk_size = disk_size
        self.file_size = file_size
        self.type = type_
        self.compression = compression
        self.filename = filename.split(b'\x00')[0].decode('ascii') if type(filename) is bytes else filename

    @classmethod
    def write(cls, file, entry):
        entry_data = struct.pack(
            cls.format,
            entry.file_offset,
            entry.disk_size,
            entry.file_size,
            entry.type,
            entry.compression,
            entry.filename.encode('ascii')
        )

        file.write(entry_data)

    @classmethod
    def read(cls, file):
        entry_data = file.read(cls.size)
        entry_struct = struct.unpack(cls.format, entry_data)

        return Entry(*entry_struct)


class WadInfo:
    """Class with attributes describing each entry in the wad file archive."""

    __slots__ = (
        'filename',
        'file_offset',
        'file_size',
        'compression',
        'disk_size',
        'type'
    )

    def __init__(self, filename, file_offset=0, file_size=0):
        self.filename = filename
        self.file_offset = file_offset
        self.file_size = file_size
        self.compression = CompressionType.NONE
        self.disk_size = file_size
        self.type = LumpType.NONE

    @classmethod
    def from_file(cls, filename):
        st = os.stat(filename)
        isdir = stat.S_ISDIR(st.st_mode)
        arcname = os.path.normpath(os.path.splitdrive(filename)[1])[-16:]

        while arcname[0] in (os.sep, os.altsep):
            arcname = arcname[1:]

        if isdir:
            raise RuntimeError('WadFile expects a file, got a directory')

        info = cls(arcname)
        info.type = LumpType.LUMP
        info.file_size = st.st_size
        info.disk_size = st.st_size
        info.filename = os.path.basename(arcname)[-16:]

        return info


class WadFile(ArchiveFile):
    """Class with methods to open, read, close, and list wad files.

     p = WadFile(file, mode='r')

    file: Either the path to the file, or a file-like object. If it is a path,
        the file will be opened and closed by WadFile.

    mode: The file mode for the file-like object.
    """

    class factory(ArchiveFile.factory):
        ArchiveInfo = WadInfo

    def __init__(self, file, mode='r'):
        super().__init__(file, mode)

    def _read_file(self, mode='r'):
        """Read in the directory information for the wad file."""
        self.fp.seek(0)
        header = Header.read(self.fp)

        if header.identity != b'WAD2':
            raise BadWadFile(f'Bad magic number: {header.identity}')

        self.end_of_data = header.directory_offset
        size_of_directory = header.lump_count * Entry.size

        self.fp.seek(self.end_of_data)
        data = self.fp.read(size_of_directory)
        entries = [Entry(*e) for e in struct.iter_unpack(Entry.format, data)]

        for entry in entries:
            info = WadInfo(entry.filename, entry.file_offset, entry.file_size)
            info.compression = entry.compression
            info.disk_size = entry.disk_size
            info.type = entry.type

            self.file_list.append(info)
            self.NameToInfo[info.filename] = info

    def _write_directory(self):
        for info in self.file_list:
            Entry.write(self.fp, info)

        self.fp.seek(0)
        end = self.end_of_data if hasattr(self, 'end_of_data') else Header.size

        header = Header(b'WAD2', len(self.file_list), end)
        Header.write(self.fp, header)
