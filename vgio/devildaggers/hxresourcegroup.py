"""This module provides file I/O for Devil Daggers resource group archive files.

Example:
    dd_file = dd.HxResourceGroupFile.open('dd')

"""

import io
import os
import shutil
import struct

from vgio._core import ArchiveFile, _ArchiveWriteFile


class BadResourceGroupFile(Exception):
    pass


class io_:
    class read:
        @staticmethod
        def string(file):
            result = b''

            char = file.read(1)
            while char and char != b'\x00':
                result += char
                char = file.read(1)

            return result.decode('ascii')

    class write:
        @staticmethod
        def string(file, string):
            file.write(string.encode())
            file.write(b'\x00')


class PeekableBytesIO(io.BytesIO):
    def peek(self, size=1):
        position = self.tell()
        result = self.read(size)
        self.seek(position)

        return result


class Header:
    format = '<8si'
    size = struct.calcsize(format)

    __slots__ = (
        'signature',
        'size_of_directory'
    )

    def __init__(self,
                 signature,
                 size_of_directory):
        self.signature = signature
        self.size_of_directory = size_of_directory

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.signature,
            header.size_of_directory
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Entry:
    format = '<h8s2i'
    size = struct.calcsize(format)

    __slots__ = (
        'type',
        'filename',
        'file_offset',
        'file_size',
        'date_time'
    )

    def __init__(self,
                 type_,
                 filename,
                 file_offset,
                 file_size,
                 date_time):
        self.type = type_
        self.filename = filename
        self.file_offset = file_offset
        self.file_size = file_size
        self.date_time = date_time

    @classmethod
    def write(cls, file, entry):
        type_data = struct.pack('<h', entry.type)
        file.write(type_data)
        io_.write.string(file, entry.name)

        infos_data = struct.pack(
            '<3i',
            entry.file_offset,
            entry.file_size,
            entry.date_time
        )
        file.write(infos_data)

    @classmethod
    def read(cls, file):
        type_format = '<h'
        type_data = file.read(struct.calcsize(type_format))
        type_struct = struct.unpack(type_format, type_data)
        type_ = type_struct[0]

        name = io_.read.string(file)

        infos_format = '<3i'
        infos_data = file.read(struct.calcsize(infos_format))
        offset, size, date_time = struct.unpack(infos_format, infos_data)

        return Entry(type_, name, offset, size, date_time)


class ResourceGroupInfo:
    """Instances of the ResourceGroupInfo class are returned by the
    getinfo() and infolist() methods of HxResourceGroupFile objects. Each object
    stores information about a single member of the HxResourceGroupFile archive.

    Attributes:
        type: Type of the file.

        filename: Name of the file in the archive.

        file_offset:

        file_size: Size of file in bytes.

        date_time: Last modified date as Unix timestamp.
    """

    __slots__ = (
        'type',
        'filename',
        'file_offset',
        'file_size',
        'date_time'
    )

    def __init__(self,
                 type_,
                 filename,
                 file_offset=0,
                 file_size=0,
                 date_time=0):
        """Constructs a ResourceGroupInfo object."""

        self.type = type_
        self.filename = filename
        self.file_offset = file_offset
        self.file_size = file_size
        self.date_time = date_time

    @classmethod
    def from_file(cls, filename):
        """Construct an ResourceGroupInfo instance for a file on the filesystem,
        in preparation for adding it to an archive file. filename should be the
        path to a file or directory on the filesystem.

        Args:
            filename: A path to a file or directory.

        Returns:
            A ResourceGroupInfo object.
        """
        st = os.stat(filename)
        isdir = os.stat.S_ISDIR(st.st_mode)
        arcname = os.path.normpath(os.path.splitdrive(filename)[1])[-12:]

        while arcname[0] in (os.sep, os.altsep):
            arcname = arcname[1:]

        if isdir:
            raise RuntimeError('GrpFile expects a file, got a directory')

        info = cls(arcname)
        info.file_size = st.st_size
        info.filename = os.path.basename(arcname)[-12:]
        info.type = 0
        info.date_time = 0

        return info


class _ResourceGroupWriteFile(_ArchiveWriteFile):
    def __init__(self, archive_file, archive_info):
        super().__init__(archive_file, archive_info)

    @property
    def _fileobj(self):
        return self._archive_file.data_buffer


class ResourceType:
    MESH = 0x01
    TEXTURE = 0x02
    SHADER = 0x10
    AUDIO = 0x20
    MATERIAL = 0x80


class HxResourceGroupFile(ArchiveFile):
    """Class with methods to open, read, close, and list resource group files.

    Example:
        Print out file name and type of all entries in a resource group::

            from vgio.devildaggers.hxresourcegroup import HxResourceGroupFile
            with HxResourceGroupFile('dd') as resource_group:
                for info in resource_group.infolist():
                    print(f'{info.filename}: {info.type}')

    Attributes:
       file: Either the path to the file, or a file-like object. If it is a path,
           the file will be opened and closed by HxResourceGroupFile.

       mode: The file mode for the file-like object.
    """

    class factory(ArchiveFile.factory):
        ArchiveInfo = ResourceGroupInfo
        ArchiveWriteFile = _ResourceGroupWriteFile

    def __init__(self, file, mode='r'):
        """Open an HxResourceGroup file, where *file* can be a path to a file (a
        string), or a file-like object.

        The mode parameter should be 'r' to read an existing file, 'w' to
        truncate and write a new file, or 'a' to append to an existing file.

        Args:
            file: A path or a file-like object.

            mode: File mode for the file-like object.
        """
        self.end_of_data = 0
        self.data_buffer = io.BytesIO()

        super().__init__(file, mode)

    def _read_file(self, mode='r'):
        """Read in the directory information for the grp file."""
        self.fp.seek(0)
        header = Header.read(self.fp)

        if header.signature != b':hx:rg:\x01':
            raise BadResourceGroupFile(f'Bad magic number: {header.signature}')

        data = PeekableBytesIO(self.fp.read(header.size_of_directory))

        while data.peek() != b'\x00':
            entry = Entry.read(data)
            info = ResourceGroupInfo(entry.type, entry.filename, entry.file_offset, entry.file_size, entry.date_time)
            self.file_list.append(info)
            self.NameToInfo[info.filename] = info

        if mode == 'a':
            self.data_buffer = io.BytesIO(self.fp.read())

    def _write_directory(self):
        self.fp.seek(0)

        directory_data = io.BytesIO()
        for info in self.file_list:
            Entry.write(directory_data, info)

        directory_data.write(b'\x00')

        header = Header(b':hx:rg:\x01', directory_data.tell())
        Header.write(self.fp, header)

        directory_data.seek(0)
        self.fp.write(directory_data.read())

        self._write_data()

    def _write_data(self):
        self.data_buffer.seek(0)
        self.fp.write(self.data_buffer.read())

    def _extract_member(self, info, target_path):
        """Extract the ArchiveInfo object 'member' to a physical file on the path
        target_path.
        """

        # Ignore directories
        if info.type == 17:
            return ''

        # Build the destination pathname, replacing forward slashes to
        # platform specific separators.
        archive_name = info.filename.replace('/', os.path.sep)

        if os.path.altsep:
            archive_name = archive_name.replace(os.path.altsep, os.path.sep)

        # Interpret absolute pathname as relative, remove drive letter or
        # UNC path, redundant separators, "." and ".." components.
        archive_name = os.path.splitdrive(archive_name)[1]
        invalid_path_parts = ('', os.path.curdir, os.path.pardir)
        archive_name = os.path.sep.join(x for x in archive_name.split(os.path.sep)
                                   if x not in invalid_path_parts)
        if os.path.sep == '\\':
            # Filter illegal characters on Windows
            archive_name = self._sanitize_windows_name(archive_name, os.path.sep)

        extension = {
            ResourceType.MESH: '.mesh',
            ResourceType.TEXTURE: '.texture',
            ResourceType.SHADER: '.shader',
            ResourceType.AUDIO: '.wav',
            ResourceType.MATERIAL: '.material'
        }.get(info.type, '')

        target_path = os.path.join(target_path, f'{archive_name}{extension}')
        target_path = os.path.normpath(target_path)

        # Create all upper directories if necessary.
        upperdirs = os.path.dirname(target_path)
        if upperdirs and not os.path.exists(upperdirs):
            os.makedirs(upperdirs)

        if info.filename[-1] == '/':
            if not os.path.isdir(target_path):
                os.mkdir(target_path)
            return target_path

        with self.open(info) as source, open(target_path, "wb") as target:
            shutil.copyfileobj(source, target)

        return target_path
