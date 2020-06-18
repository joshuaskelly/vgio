"""This module provides file I/O for HROT PAK archive files."""

import os
import stat
import struct

from vgio._core import ArchiveFile

IDENTITY = b'HROT'

class BadPakFile(Exception):
    pass


def _check_pakfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4s'))

    return data == IDENTITY


def is_pakfile(filename):
    """Quickly see if a file is a pak file by checking the magic number.

    The filename argument may be a file for file-like object.

    Args:
        filename: File to check as string or file-like object.

    Returns:
        True if given file's magic number is correct.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_pakfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_pakfile(fp)

    except Exception:
        return False


class Header:
    format = '<4s2i'
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'directory_offset',
        'directory_size'
    )

    def __init__(self,
                 identity,
                 directory_offset,
                 directory_size):
        self.identity = identity
        self.directory_offset = directory_offset
        self.directory_size = directory_size

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.identity,
            header.directory_offset,
            header.directory_size
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Entry:
    format = '<120s2i'
    size = struct.calcsize(format)

    __slots__ = (
        'filename',
        'file_offset',
        'file_size'
    )

    def __init__(self,
                 filename,
                 file_offset,
                 file_size):
        self.filename = filename.split(b'\x00')[0].decode('ascii') if type(filename) is bytes else filename
        self.file_offset = file_offset
        self.file_size = file_size

    @classmethod
    def write(cls, file, entry):
        entry_data = struct.pack(
            cls.format,
            entry.filename.encode('ascii'),
            entry.file_offset,
            entry.file_size
        )

        file.write(entry_data)

    @classmethod
    def read(cls, file):
        entry_data = file.read(cls.size)
        entry_struct = struct.unpack(cls.format, entry_data)

        return Entry(*entry_struct)


class PakInfo:
    """Instances of the PakInfo class are returned by the getinfo() and
    infolist() methods of PakFile objects. Each object stores information about
    a single member of the PakFile archive.

    Attributes:
        filename: Name of file.

        file_offset: Offset of file in bytes.

        file_size: Size of the file in bytes.
    """

    __slots__ = (
        'filename',
        'file_offset',
        'file_size'
    )

    def __init__(self, filename, file_offset=0, file_size=0):
        self.filename = filename
        self.file_offset = file_offset
        self.file_size = file_size

    @classmethod
    def from_file(cls, filename):
        st = os.stat(filename)
        isdir = stat.S_ISDIR(st.st_mode)

        if len(filename) > 120:
            raise BadPakFile('PakFile filename must be 56 characters or less')

        if isdir:
            raise RuntimeError('PakFile expects a file, got a directory')

        info = cls(filename)
        info.file_size = st.st_size

        return info


class PakFile(ArchiveFile):
    """Class with methods to open, read, close, and list pak files.

    Example:
        Basic usage::

            from vgio.quake.pak import PakFile
            p = PakFile(file, mode='r')

    Args:
        file: Either the path to the file, or a file-like object. If it is a path,
            the file will be opened and closed by PakFile.

        mode: The file mode for the file-like object.
    """

    class factory(ArchiveFile.factory):
        ArchiveInfo = PakInfo

    def __init__(self, file, mode='r'):
        super().__init__(file, mode)

    def _read_file(self, mode='r'):
        """Read in the directory information for the pak file."""
        self.fp.seek(0)
        header = Header.read(self.fp)

        if header.identity != IDENTITY:
            raise BadPakFile(f'Bad magic number: {header.identity}')

        self.end_of_data = header.directory_offset
        size_of_directory = header.directory_size

        self.fp.seek(self.end_of_data)
        data = self.fp.read(size_of_directory)
        entries = [Entry(*e) for e in struct.iter_unpack(Entry.format, data)]

        for entry in entries:
            info = PakInfo(entry.filename, entry.file_offset, entry.file_size)
            self.file_list.append(info)
            self.NameToInfo[info.filename] = info

    def _write_directory(self):
        for info in self.file_list:
            Entry.write(self.fp, info)

        self.fp.seek(0)
        end = self.end_of_data if hasattr(self, 'end_of_data') else Header.size
        directory_size = len(self.file_list) * Entry.size

        header = Header(IDENTITY, end, directory_size)
        Header.write(self.fp, header)
