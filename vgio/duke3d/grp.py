"""This module provides file I/O for Duke3D GRP archive files.

Example:
    grp_file = grp.GrpFile.open('duke3d.grp')

"""

import io
import os
import stat
import struct

from vgio._core import ArchiveFile, _ArchiveWriteFile


__all__ = ['BadGrpFile', 'is_grpfile', 'GrpInfo', 'GrpFile']


IDENTITY = b'KenSilverman'


class BadGrpFile(Exception):
    pass


def _check_grpfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<12s'))

    return data == IDENTITY


def is_grpfile(filename):
    """Quickly see if a file is a grp file by checking the magic number.

    The filename argument may be a file for file-like object.

    Args:
        filename: File to check as string or file-like object.

    Returns:
        True if given file's magic number is correct.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_grpfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_grpfile(fp)

    except Exception:
        return False


class Header:
    format = '<12sl'
    size = struct.calcsize(format)

    __slots__ = (
        'signature',
        'number_of_entries'
    )

    def __init__(self,
                 signature,
                 number_of_entries):
        self.signature = signature
        self.number_of_entries = number_of_entries

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(cls.format,
                                  header.signature,
                                  header.number_of_entries)

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Entry:
    format = '<12sl'
    size = struct.calcsize(format)

    __slots__ = (
        'filename',
        'file_size'
    )

    def __init__(self,
                 filename,
                 file_size):
        self.filename = filename.split(b'\x00')[0].decode('ascii') if type(filename) is bytes else filename
        self.file_size = file_size

    @classmethod
    def write(cls, file, entry):
        entry_data = struct.pack(cls.format,
                                 entry.filename.encode('ascii'),
                                 entry.file_size)

        file.write(entry_data)

    @classmethod
    def read(cls, file):
        entry_data = file.read(cls.size)
        entry_struct = struct.unpack(cls.format, entry_data)

        return Entry(*entry_struct)


class GrpInfo:
    """Instances of the GrpInfo class are returned by the getinfo() and
    infolist() methods of GrpFile objects. Each object stores information about
    a single member of the GrpFile archive.

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

    def __init__(self,
                 filename,
                 file_offset=0,
                 file_size=0):
        """Constructs a GrpInfo object."""

        self.filename = filename
        self.file_offset = file_offset
        self.file_size = file_size

    @classmethod
    def from_file(cls, filename):
        st = os.stat(filename)
        isdir = stat.S_ISDIR(st.st_mode)
        arcname = os.path.normpath(os.path.splitdrive(filename)[1])[-12:]

        while arcname[0] in (os.sep, os.altsep):
            arcname = arcname[1:]

        if isdir:
            raise RuntimeError('GrpFile expects a file, got a directory')

        info = cls(arcname)
        info.file_size = st.st_size
        info.filename = os.path.basename(arcname)[-12:]

        return info


class _GrpWriteFile(_ArchiveWriteFile):
    def __init__(self, archive_file, archive_info):
        super().__init__(archive_file, archive_info)

    @property
    def _fileobj(self):
        return self._archive_file.data_buffer


class GrpFile(ArchiveFile):
    """Class with methods to open, read, close, and list grp files.

    Example:
        Basic usage::

            from vgio.duke3d.grp import GrpFile
            grp_file = GrpFile(file, mode='r')

    Attributes:
        file: Either the path to the file, or a file-like object. If it is a path,
            the file will be opened and closed by GrpFile.

        mode: The file mode for the file-like object.
    """

    class factory(ArchiveFile.factory):
        ArchiveInfo = GrpInfo
        ArchiveWriteFile = _GrpWriteFile

    def __init__(self, file, mode='r'):
        """Open an Grp file, where *file* can be a path to a file (a string), or
        a file-like object.

        The mode parameter should be 'r' to read an existing file, 'w' to
        truncate and write a new file, or 'a' to append to an existing file.
        """

        self.end_of_data = 0
        self.data_buffer = io.BytesIO()

        super().__init__(file, mode)

    def _read_file(self, mode='r'):
        """Read in the directory information for the grp file."""
        self.fp.seek(0)
        header = Header.read(self.fp)

        if header.signature != IDENTITY:
            raise BadGrpFile(f'Bad magic number: {header.signature}')

        size_of_directory = header.number_of_entries * Entry.size
        data = self.fp.read(size_of_directory)

        entries = [Entry(*e) for e in struct.iter_unpack(Entry.format, data)]
        offset = Header.size + size_of_directory

        for entry in entries:
            info = GrpInfo(entry.filename, offset, entry.file_size)
            offset += info.file_size
            self.file_list.append(info)
            self.NameToInfo[info.filename] = info

        if mode == 'a':
            self.data_buffer = io.BytesIO(self.fp.read())

    def _write_directory(self):
        self.fp.seek(0)

        header = Header(IDENTITY, len(self.file_list))
        Header.write(self.fp, header)

        for info in self.file_list:
            Entry.write(self.fp, info)

        self._write_data()

    def _write_data(self):
        self.data_buffer.seek(0)
        self.fp.write(self.data_buffer.read())
