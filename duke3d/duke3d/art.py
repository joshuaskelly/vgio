"""This module provides file I/O for Duke3D Art archive files.

Example:
    art_file = art.ArtFile.open('tiles001.art')

References:
    "Build Engine & Tools"
    - Ken Silverman
    - http://fabiensanglard.net/duke3d/BUILDINF.TXT
"""

import io
import os
import shutil
import stat
import struct

try:
    import threading
except ImportError:
    import dummy_threading as threading


__all__ = []


class BadArtFile(Exception):
    pass


# The main ART file structure
header_struct = '<4l'
header_version = 1
header_size = struct.calcsize(header_struct)

_HEADER_VERSION = 0
_HEADER_NUMBER_OF_TILES = 1
_HEADER_LOCAL_TILES_START_ID = 2
_HEADER_LOCAL_TILES_END_ID = 3


def _calculate_tile_dimensions_format(number_of_tiles):
    return '<%ih' % (2 * number_of_tiles)


def _calculate_picanim_format(number_of_tiles):
    return '<%il' % (number_of_tiles)


def _check_artfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<l'))
    data = struct.unpack('<l', data)[0]

    return data == header_version


def is_artfile(filename):
    """Quickly see if a file is a art file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    result = False

    try:
        if hasattr(filename, 'read'):
            return _check_artfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_artfile(fp)

    except:
        pass

    return result


default_palette = (
    (0x00,0x00,0x00),(0x04,0x04,0x04),(0x10,0x0c,0x10),(0x18,0x18,0x18),
    (0x24,0x20,0x20),(0x2c,0x28,0x2c),(0x38,0x34,0x34),(0x40,0x3c,0x3c),
    (0x4c,0x48,0x48),(0x59,0x50,0x50),(0x61,0x59,0x5d),(0x6d,0x61,0x65),
    (0x75,0x6d,0x71),(0x81,0x75,0x79),(0x89,0x7d,0x81),(0x95,0x89,0x8d),
    (0x99,0x8d,0x91),(0xa1,0x95,0x99),(0xaa,0x9d,0xa1),(0xae,0xa5,0xaa),
    (0xb2,0xae,0xae),(0xba,0xb2,0xb6),(0xc2,0xba,0xba),(0xca,0xbe,0xc2),
    (0xce,0xc6,0xca),(0xd6,0xce,0xd2),(0xda,0xd6,0xda),(0xe2,0xda,0xde),
    (0xe6,0xe2,0xe6),(0xee,0xea,0xee),(0xf6,0xf2,0xf6),(0xff,0xff,0xff),
    (0x00,0x00,0x00),(0x04,0x04,0x00),(0x0c,0x04,0x04),(0x18,0x0c,0x04),
    (0x20,0x10,0x08),(0x28,0x14,0x0c),(0x30,0x1c,0x10),(0x3c,0x20,0x14),
    (0x44,0x24,0x18),(0x4c,0x2c,0x18),(0x55,0x30,0x1c),(0x61,0x34,0x20),
    (0x69,0x3c,0x24),(0x71,0x40,0x28),(0x79,0x44,0x2c),(0x85,0x4c,0x30),
    (0x8d,0x55,0x38),(0x91,0x5d,0x3c),(0x99,0x65,0x44),(0xa1,0x6d,0x48),
    (0xaa,0x75,0x50),(0xae,0x7d,0x59),(0xb2,0x85,0x61),(0xba,0x91,0x69),
    (0xbe,0x99,0x71),(0xc6,0xa1,0x79),(0xce,0xae,0x81),(0xd6,0xb2,0x8d),
    (0xda,0xba,0x95),(0xde,0xc6,0x9d),(0xe6,0xce,0xaa),(0xee,0xda,0xb2),
    (0x50,0x61,0x95),(0x55,0x69,0x99),(0x5d,0x71,0xa1),(0x61,0x79,0xaa),
    (0x69,0x81,0xae),(0x71,0x89,0xb6),(0x79,0x91,0xbe),(0x7d,0x99,0xc6),
    (0x85,0xa5,0xce),(0x8d,0xae,0xd2),(0x95,0xb2,0xda),(0x9d,0xba,0xde),
    (0xa5,0xc6,0xe6),(0xae,0xce,0xee),(0xb6,0xd6,0xf6),(0xbe,0xde,0xff),
    (0x00,0x00,0x00),(0x04,0x04,0x04),(0x04,0x08,0x10),(0x0c,0x0c,0x18),
    (0x10,0x14,0x20),(0x14,0x18,0x2c),(0x18,0x20,0x34),(0x20,0x28,0x40),
    (0x24,0x2c,0x48),(0x28,0x34,0x50),(0x2c,0x38,0x5d),(0x34,0x40,0x65),
    (0x38,0x44,0x6d),(0x3c,0x4c,0x79),(0x40,0x50,0x81),(0x48,0x59,0x8d),
    (0x00,0x00,0x00),(0x04,0x04,0x04),(0x0c,0x0c,0x08),(0x18,0x14,0x0c),
    (0x20,0x20,0x10),(0x28,0x28,0x18),(0x30,0x30,0x1c),(0x3c,0x38,0x24),
    (0x44,0x40,0x28),(0x4c,0x4c,0x2c),(0x55,0x55,0x34),(0x61,0x5d,0x38),
    (0x69,0x65,0x40),(0x71,0x6d,0x44),(0x79,0x75,0x48),(0x85,0x81,0x50),
    (0x8d,0x89,0x55),(0x95,0x95,0x55),(0x99,0x9d,0x59),(0x9d,0xa5,0x5d),
    (0xa1,0xae,0x61),(0xa5,0xb2,0x61),(0xaa,0xba,0x65),(0xae,0xc2,0x69),
    (0xae,0xca,0x69),(0xae,0xd2,0x6d),(0xb2,0xda,0x6d),(0xb2,0xde,0x71),
    (0xb2,0xe6,0x71),(0xb2,0xee,0x75),(0xb2,0xf6,0x75),(0xb2,0xff,0x79),
    (0x00,0x00,0x00),(0x0c,0x00,0x00),(0x18,0x04,0x00),(0x28,0x04,0x00),
    (0x34,0x08,0x04),(0x44,0x0c,0x04),(0x55,0x10,0x04),(0x61,0x14,0x04),
    (0x71,0x18,0x08),(0x81,0x1c,0x08),(0x8d,0x20,0x0c),(0x9d,0x24,0x0c),
    (0xae,0x28,0x0c),(0xba,0x2c,0x10),(0xca,0x30,0x10),(0xda,0x34,0x14),
    (0x65,0x44,0x18),(0x69,0x50,0x04),(0x75,0x59,0x04),(0x81,0x65,0x04),
    (0x8d,0x6d,0x08),(0x95,0x79,0x08),(0xa1,0x81,0x08),(0xae,0x8d,0x08),
    (0xb2,0x95,0x10),(0xbe,0xa1,0x10),(0xca,0xae,0x10),(0xd6,0xb6,0x14),
    (0xda,0xc2,0x14),(0xe6,0xca,0x14),(0xf2,0xda,0x14),(0xff,0xe2,0x18),
    (0x00,0x00,0x00),(0x04,0x04,0x00),(0x08,0x08,0x04),(0x10,0x0c,0x08),
    (0x14,0x10,0x10),(0x1c,0x14,0x14),(0x20,0x1c,0x18),(0x28,0x20,0x1c),
    (0x30,0x24,0x20),(0x34,0x2c,0x28),(0x3c,0x30,0x2c),(0x40,0x34,0x30),
    (0x48,0x3c,0x34),(0x4c,0x40,0x38),(0x55,0x44,0x40),(0x5d,0x4c,0x44),
    (0x65,0x55,0x4c),(0x6d,0x5d,0x50),(0x79,0x65,0x59),(0x81,0x6d,0x61),
    (0x8d,0x75,0x69),(0x95,0x7d,0x71),(0x9d,0x85,0x79),(0xaa,0x8d,0x7d),
    (0xae,0x95,0x85),(0xb6,0x9d,0x8d),(0xc2,0xa5,0x95),(0xca,0xae,0x9d),
    (0xd6,0xb2,0xa5),(0xda,0xba,0xae),(0xe2,0xc6,0xb2),(0xee,0xce,0xba),
    (0x34,0x1c,0x00),(0x44,0x28,0x00),(0x59,0x30,0x00),(0x6d,0x38,0x00),
    (0x81,0x40,0x00),(0x91,0x48,0x00),(0xa5,0x50,0x00),(0xb6,0x55,0x04),
    (0xca,0x5d,0x04),(0xce,0x69,0x18),(0xd6,0x75,0x30),(0xda,0x85,0x44),
    (0xde,0x91,0x59),(0xe6,0xa1,0x71),(0xee,0xae,0x89),(0xf6,0xc2,0xa1),
    (0xda,0x40,0x18),(0xda,0x4c,0x1c),(0xde,0x5d,0x28),(0xe2,0x69,0x30),
    (0xe6,0x79,0x38),(0xea,0x85,0x40),(0xee,0x91,0x48),(0xf2,0xa1,0x50),
    (0xf2,0xae,0x5d),(0xf2,0xba,0x65),(0xf6,0xc6,0x75),(0xf6,0xd2,0x7d),
    (0xfa,0xda,0x8d),(0xfa,0xe2,0x95),(0xfa,0xea,0xa5),(0xff,0xf2,0xae),
    (0x08,0x10,0x34),(0x08,0x08,0x40),(0x14,0x08,0x4c),(0x1c,0x08,0x59),
    (0x30,0x08,0x5d),(0x40,0x10,0x65),(0x55,0x14,0x69),(0x69,0x18,0x71),
    (0x7d,0x18,0x79),(0x89,0x20,0x75),(0x99,0x20,0x6d),(0xa5,0x18,0x61),
    (0xb2,0x28,0x4c),(0xbe,0x2c,0x38),(0xce,0x30,0x18),(0xda,0x34,0x14),
    (0x44,0x44,0x00),(0xa5,0xa5,0x00),(0xff,0xff,0x00),(0x44,0x00,0x44),
    (0xa5,0x00,0xa5),(0xff,0x00,0xff),(0x59,0x00,0x00),(0xae,0x00,0x00),
    (0xff,0x00,0x00),(0x00,0x44,0x00),(0x00,0xa5,0x00),(0x00,0xff,0x00),
    (0x00,0x00,0x44),(0x00,0x00,0xa5),(0x00,0x00,0xff),(0xff,0x00,0xff)
)


class ArtInfo(object):
    """Class with attributes describing each entry in the art file archive."""

    __slots__ = (
        'tile_index',
        'tile_dimensions',
        'picanim',
        'file_offset',
        'file_size'
    )

    def __init__(self, tile_index, tile_dimensions=(0, 0), file_offset=0, file_size=0):
        self.tile_index = tile_index
        self.tile_dimensions = tile_dimensions
        self.picanim = 0
        self.file_offset = file_offset
        self.file_size = file_size


class _SharedFile:
    def __init__(self, file, position, size, close, lock):
        self._file = file
        self._position = position
        self._start = position
        self._end = position + size
        self._close = close
        self._lock = lock

    def read(self, n=-1):
        with self._lock:
            self._file.seek(self._position)

            if n < 0 or n > self._end:
                n = self._end - self._position

            data = self._file.read(n)
            self._position = self._file.tell()
            return data

    def close(self):
        if self._file is not None:
            file_object = self._file
            self._file = None
            self._close(file_object)

    def seek(self, n):
        n = min(self._start + n, self._end)
        self._file.seek(n)
        self._position = self._file.tell()


class ArtExtFile(io.BufferedIOBase):
    """A file-like object for reading an entry.

    It is returned by ArtFile.open()
    """

    MAX_N = 1 << 31 - 1
    MIN_READ_SIZE = 4096

    def __init__(self, file_object, mode, art_info, close_file_object=False):
        self._file_object = file_object
        self._close_file_object = close_file_object
        self._bytes_left = art_info.file_size

        self._eof = False
        self._readbuffer = b''
        self._offset = 0
        self._size = art_info.file_size

        self.mode = mode
        self.name = art_info.tile_index

    def read(self, n=-1):
        """Read and return up to n bytes.

        If the argument n is omitted, None, or negative, data will be read
        until EOF.
        """

        if n is None or n < 0:
            buffer = self._readbuffer[self._offset:]
            self._readbuffer = b''
            self._offset = 0

            while not self._eof:
                buffer += self._read_internal(self.MAX_N)

            return buffer

        end = n + self._offset

        if end < len(self._readbuffer):
            buffer = self._readbuffer[self._offset:end]
            self._offset = end

            return buffer

        n = end - len(self._readbuffer)
        buffer = self._readbuffer[self._offset:]
        self._readbuffer = b''
        self._offset = 0

        while n > 0 and not self._eof:
            data = self._read_internal(n)

            if n < len(data):
                self._readbuffer = data
                self._offset = n
                buffer += data[:n]
                break

            buffer += data
            n -= len(data)

        return buffer

    def _read_internal(self, n):
        """Read up to n bytes with at most one read() system call"""

        if self._eof or n <= 0:
            return b''

        # Read from file.
        n = max(n, self.MIN_READ_SIZE)
        data = self._file_object.read(n)

        if not data:
            raise EOFError

        data = data[:self._bytes_left]
        self._bytes_left -= len(data)

        if self._bytes_left <= 0:
            self._eof = True

        return data

    def peek(self, n=1):
        """Returns buffered bytes without advancing the position."""

        if n > len(self._readbuffer) - self._offset:
            chunk = self.read(n)
            if len(chunk) > self._offset:
                self._readbuffer = chunk + self._readbuffer[self._offset:]
                self._offset = 0
            else:
                self._offset -= len(chunk)

        # Return up to 512 bytes to reduce allocation overhead for tight loops.
        return self._readbuffer[self._offset: self._offset + 512]

    def seek(self, n):
        self._file_object.seek(n)
        self._readbuffer = b''
        self._offset = 0

    def close(self):
        try:
            if self._close_file_object:
                self._file_object.close()
        finally:
            super().close()


class _ArtWriteFile(io.BufferedIOBase):
    def __init__(self, art_file, art_info):
        self._art_info = art_info
        self._art_file = art_file
        self._file_size = 0

    @property
    def _fileobj(self):
        return self._art_file.data_buffer

    def writable(self):
        return True

    def write(self, data):
        number_of_bytes = len(data)
        self._file_size += number_of_bytes
        self._fileobj.write(data)

        return number_of_bytes

    def close(self):
        super().close()

        self._art_file._writing = False
        self._art_file.file_list.append(self._art_info)
        self._art_file.NameToInfo[self._art_info.tile_index] = self._art_info
        self._art_file.tile_x_dimensions.append(self._art_info.tile_dimensions[0])
        self._art_file.tile_y_dimensions.append(self._art_info.tile_dimensions[1])
        self._art_file.picanims.append(self._art_info.picanim)
        self._art_file.local_tile_end += 1


class ArtFile(object):
    """Class with methods to open, read, close, and list art files.

     p = ArtFile(file, mode='r')

    file: Either the path to the file, or a file-like object. If it is a path,
        the file will be opened and closed by ArtFile.

    mode: Currently the only supported mode is 'r'
    """

    fp = None
    _windows_illegal_name_trans_table = None

    def __init__(self, file, mode='r'):
        if mode not in ('r', 'w', 'a'):
            raise RuntimeError("ArtFile requires mode 'r', 'w', or 'a'")

        self.NameToInfo = {}
        self.file_list = []
        self.mode = mode
        self.data_buffer = io.BytesIO()

        self.version = 7
        self.number_of_tiles = 0
        self.local_tile_start = 0
        self.local_tile_end = -1
        self.tile_x_dimensions = []
        self.tile_y_dimensions = []
        self.picanims = []

        self._did_modify = False
        self._file_reference_count = 1
        self._lock = threading.RLock()
        self._writing = False

        filemode = {'r': 'rb', 'w': 'w+b', 'a': 'r+b'}[mode]

        if isinstance(file, str):
            self.filename = file
            self.fp = io.open(file, filemode)
            self._file_passed = 0

        else:
            self.fp = file
            self.filename = getattr(file, 'name', None)
            self._file_passed = 1

        try:
            if mode == 'r':
                self._read_archive_content()

            elif mode == 'w':
                self._did_modify = True

                data = struct.pack(header_struct,
                                   header_version,
                                   len(self.file_list),
                                   self.local_tile_start,
                                   self.local_tile_end)

                self.fp.write(data)

                if self.file_list:
                    data = struct.pack(_calculate_tile_dimensions_format(len(self.file_list)),
                                       self.tile_x_dimensions + self.tile_y_dimensions)

                    self.fp.write(data)

                    data = struct.pack(_calculate_picanim_format(len(self.file_list)),
                                       self.picanims)

                    self.fp.write(data)

            elif mode == 'a':
                try:
                    self._read_archive_content(mode)

                except BadArtFile:
                    # Don't support appending to non-art file
                    raise
            else:
                raise ValueError("Mode must be 'r', 'w', 'x', or 'a'")

        except:
            fp = self.fp
            self.fp = None
            self._fpclose(fp)
            raise

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _read_archive_content(self, mode='r'):
        """Read in the directory information for the art file."""

        fp = self.fp
        _windows_illegal_name_trans_table = None

        fp.seek(0)
        header = fp.read(header_size)
        header = struct.unpack(header_struct, header)

        if header[_HEADER_VERSION] != header_version:
            raise BadArtFile('Bad version number: %r' % header[_HEADER_VERSION])

        self.local_tile_start = header[_HEADER_LOCAL_TILES_START_ID]
        self.local_tile_end = header[_HEADER_LOCAL_TILES_END_ID]
        self.number_of_tiles = self.local_tile_end - self.local_tile_start + 1

        # Read in tile dimensions data
        tile_dimensions_format = _calculate_tile_dimensions_format(self.number_of_tiles)
        tile_dimensions_size = struct.calcsize(tile_dimensions_format)
        tile_dimensions = fp.read(tile_dimensions_size)
        tile_dimensions = struct.unpack(tile_dimensions_format, tile_dimensions)
        self.tile_x_dimensions = list(tile_dimensions[:self.number_of_tiles])
        self.tile_y_dimensions = list(tile_dimensions[self.number_of_tiles:])
        tile_dimensions = tuple(zip(self.tile_x_dimensions, self.tile_y_dimensions))

        if self.number_of_tiles != len(tile_dimensions):
            raise BadArtFile('Found: %i tiles, expected: %i') % (len(tile_dimensions), self.number_of_tilesJ)

        # Read in picanim data
        picanims_format = _calculate_picanim_format(self.number_of_tiles)
        picanims_size = struct.calcsize(picanims_format)
        picanims = fp.read(picanims_size)
        picanims = list(struct.unpack(picanims_format, picanims))
        self.picanims = picanims

        self.start_of_data = fp.tell()

        local_file_sizes = list(map(lambda x: x[0] * x[1], tile_dimensions))
        size_of_data = sum(local_file_sizes)
        data = fp.read(size_of_data)

        if size_of_data != len(data):
            raise BadArtFile('Expected: %i bytes, actual: %i bytes') % (size_of_data, len(data))

        local_file_offset = self.start_of_data

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
        count = len(self.file_list)

        # Write header
        header_data = struct.pack(header_struct,
                                  header_version,
                                  count,
                                  self.local_tile_start,
                                  self.local_tile_end)

        self.fp.seek(0)
        self.fp.write(header_data)

        # Write tile dimensions
        tile_dimensions_format = _calculate_tile_dimensions_format(count)
        tile_dimensions_data = struct.pack(tile_dimensions_format,
                                           *(self.tile_x_dimensions + self.tile_y_dimensions))

        self.fp.write(tile_dimensions_data)

        # Write picanim data
        picanims_format = _calculate_picanim_format(count)
        picanims_data = struct.pack(picanims_format,
                                    *self.picanims)

        self.fp.write(picanims_data)

    def namelist(self):
        """Return a list of file names in the art file."""

        return [data.tile_index for data in self.file_list]

    def infolist(self):
        """Return a list of ArtInfo instances for all of the files in the
        art file."""

        return self.file_list

    def getinfo(self, name):
        """Return an instance of ArtInfo given 'name'."""

        info = self.NameToInfo.get(name)

        if info is None:
            raise KeyError('There is no item named %r in the art file' % name)

        return info

    def read(self, index):
        """Return file bytes (as a string) for index."""

        info = self.getinfo(index)

        with self.open(index, 'r') as fp:
            return fp.read(info.file_size)

    def open(self, index, mode='r'):
        """Return a file-like object for index."""

        if mode not in ('r', 'w'):
            raise ValueError("open() requires mode 'r' or 'w'")

        if not self.fp:
            raise RuntimeError('Attempt to read ART archive that was already closed')

        if isinstance(index, ArtInfo):
            info = index

        elif mode == 'w':
            info = ArtInfo.from_file(index)

        else:
            info = self.getinfo(index)

        if mode == 'w':
            return self._open_to_write(info)

        self._file_reference_count += 1
        shared_file = _SharedFile(self.fp, info.file_offset, info.file_size, self._fpclose, self._lock)

        try:
            return ArtExtFile(shared_file, mode, info, True)

        except:
            shared_file.close()
            raise

    def _open_to_write(self, art_info):
        if self._writing:
            raise ValueError("Can't write to the ART file while there is "
                             "another write handle open on it. Close the first"
                             " handle before opening another.")

        self._did_modify = True
        self._writing = True

        return _ArtWriteFile(self, art_info)

    def extract(self, member, path=None):
        """Extract a member from the art file to the current working directory
        using its full name. Note: art files do not store file metadata.

        member: Either the name of the member to extract or a ArtInfo instance.

        path: The directory to extract to. The current working directory will
        be used if None.
        """

        if not isinstance(member, ArtInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        return self._extract_member(member, path)

    def extractall(self, path=None, members=None):
        """Extract all members from the art file to the current working
        directory.

        path: The directory to extract to. The current working directory will
            be used if None.

        members: The names of the members to extract. This must be a subset of
            the list returned by namelist(). All members will be extracted if
            None.
        """

        if members is None:
            members = self.namelist()

        for ArtInfo in members:
            self.extract(ArtInfo, path)

    @classmethod
    def _sanitize_windows_name(cls, archive_name, path_separator):
        """Replace bad characters and remove trailing dots from parts."""

        table = cls._windows_illegal_name_trans_table

        if not table:
            illegal = ':<>|"?*'
            table = str.maketrans(illegal, '_' * len(illegal))
            cls._windows_illegal_name_trans_table = table

        archive_name = archive_name.translate(table)

        # Remove trailing dots
        archive_name = (x.rstrip('.') for x in archive_name.split(path_separator))

        # Rejoin, removing empty parts.
        archive_name = path_separator.join(x for x in archive_name if x)

        return archive_name

    def _extract_member(self, member, target_path):
        """Extract the ArtInfo object 'member' to a physical file on the path
        target_path.
        """

        # Build the destination pathname, replacing forward slashes to
        # platform specific separators.
        archive_name = member.filename.replace('/', os.path.sep)

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

        target_path = os.path.join(target_path, archive_name)
        target_path = os.path.normpath(target_path)

        # Create all upper directories if necessary.
        upperdirs = os.path.dirname(target_path)
        if upperdirs and not os.path.exists(upperdirs):
            os.makedirs(upperdirs)

        if member.filename[-1] == '/':
            if not os.path.isdir(target_path):
                os.mkdir(target_path)
            return target_path

        with self.open(member) as source, open(target_path, "wb") as target:
            shutil.copyfileobj(source, target)

        return target_path

    def writebytes(self, info_or_dimensions, data):
        """Puts bytes from data into the art file.

        Args:
            info_or_dimensions: Either an ArtInfo object or Tile dimensions as
                a two-tuple.

            data: Pixel data as unstructured bytes in column major order.
        """
        if not self.fp:
            raise ValueError('Attempting to write to ART archive that was'
                             ' already closed')
        if self._writing:
            raise ValueError("Can't write to ART archive while an open writing"
                             " handle exists")

        tile_index = self.local_tile_start + len(self.file_list)

        if not isinstance(info_or_dimensions, ArtInfo):
            info = ArtInfo(tile_index, tile_dimensions=info_or_dimensions)

        else:
            info = info_or_dimensions
            info.tile_index = tile_index

        info.file_offset = self.fp.tell()

        if not info.file_size:
            if isinstance(data, io.BytesIO):
                info.file_size = data.getbuffer().nbytes

            else:
                info.file_size = len(data)

        should_close = False

        if isinstance(data, str):
            data = data.encode('ascii')

        if isinstance(data, bytes):
            data = io.BytesIO(data)
            should_close = True

        if not hasattr(data, 'read'):
            raise BadArtFile('Invalid data type. Art.writebytes expects a string or bytes')

        with data as src, self.open(info, 'w') as dest:
            shutil.copyfileobj(src, dest, 8*1024)

        if should_close:
            data.close()

    def close(self):
        """Close the file."""

        if self.fp is None:
            return

        if self._writing:
            raise ValueError("Can't close ART file while there is an open"
                             "writing handle on it. Close the writing handle"
                             "before closing the art.")

        try:
            if self.mode in ('w', 'x', 'a') and self._did_modify:
                with self._lock:
                    self._write_directory()

                    if self.data_buffer is not None:
                        self.data_buffer.seek(0)
                        self.fp.write(self.data_buffer.read())
                        self.fp.flush()

        finally:
            fp = self.fp
            self.fp = None
            self._fpclose(fp)

    def _fpclose(self, fp):
        assert self._file_reference_count > 0
        self._file_reference_count -= 1

        if not self._file_reference_count and not self._file_passed:
            fp.close()
