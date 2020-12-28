"""The _core module provides several base classes for creating binary
serialization classes.

Note:
    These classes must be subclassed as the don't do anything useful on
    their own.
"""

import io
import os
import shutil
import stat

try:
    import threading

except ImportError:
    import dummy_threading as threading

from types import SimpleNamespace


__all__ = ['ReadWriteFile', 'ArchiveInfo', 'ArchiveFile']


class ReadWriteFile(object):
    """ReadWriteFile serves as base class for serializing/deserialing
    binary data.

    Attributes:
        fp: The handle to the open file. Will be None if file closed.

        mode: File mode. Is one of 'r', 'w', or 'a'.
    """
    def __init__(self):
        """Initializes a ReadWriteFile object. Derving classes must call this."""

        self.fp = None
        self.mode = None
        self._did_modify = False

    @classmethod
    def open(cls, file, mode='r'):
        """Open a ReadWriteFile object where file can be a path to a file (a
        string), or a file-like object.

        The mode parameter should be ‘r’ to read an existing file, ‘w’ to
        truncate and write a new file, or ‘a’ to append to an existing file.

        open() is also a context manager and supports the with statement::

            with ReadWriteFile.open('file.ext') as file:
                file.save('file2.ext')

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file

        Returns:
            An ReadWriteFile object constructed from the information read from
            the file-like object.

        Raises:
            ValueError: If an invalid file mode is given.

            TypeError: If attempting to write to a bytes object.

            OSError: If the file argument is not a file-like object.
        """

        if mode not in ('r', 'w', 'a'):
            raise ValueError(f"invalid mode: '{mode}'")

        filemode = {'r': 'rb', 'w': 'w+b', 'a': 'r+b'}[mode]

        if isinstance(file, str):
            file = io.open(file, filemode)

        elif isinstance(file, bytes):
            if mode != 'r':
                raise TypeError('Unable to write to bytes object')

            file = io.BytesIO(file)

        elif not hasattr(file, 'read'):
            raise OSError('Bad file descriptor')

        # Read
        if mode == 'r':
            read_file = cls._read_file(file, mode)
            read_file.fp = file
            read_file.mode = 'r'

            return read_file

        # Write
        elif mode == 'w':
            write_file = cls()
            write_file.fp = file
            write_file.mode = 'w'
            write_file._did_modify = True

            return write_file

        # Append
        else:
            append_file = cls._read_file(file, mode)
            append_file.fp = file
            append_file.mode = 'a'
            append_file._did_modify = True

            return append_file

    @staticmethod
    def _read_file(file, mode):
        raise NotImplementedError

    @staticmethod
    def _write_file(file, object_):
        raise NotImplementedError

    def save(self, file):
        """Writes data to file.

        Args:
            file: Either the path to the file, or a file-like object.

        Raises:
            OSError: If file argument is not a file-like object.
        """

        should_close = False

        if isinstance(file, str):
            file = io.open(file, 'r+b')
            should_close = True

        elif not hasattr(file, 'write'):
            raise OSError('Bad file descriptor')

        self.__class__._write_file(file, self)

        if should_close:
            file.close()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def close(self):
        """Closes the file pointer if possible. If mode is 'w' or 'a', the file
        will be written to.
        """

        if self.fp:
            if self.mode in ('w', 'a') and self._did_modify:
                self.fp.seek(0)
                self.__class__._write_file(self.fp, self)
                self.fp.truncate()

            file_object = self.fp
            self.fp = None
            file_object.close()


class ArchiveInfo:
    """ArchiveInfo objects store information about a single entry in the
    ArchiveFile archive. Instances of the ArchiveInfo class are returned by the getinfo() and
    infolist() methods of ArchiveFile objects.

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
        raise NotImplementedError

    @classmethod
    def from_file(cls, filename):
        """Construct an ArchiveInfo instance for a file on the filesystem, in
        preparation for adding it to an archive file. filename should be the
        path to a file or directory on the filesystem.

        Args:
            filename: A path to a file or directory.

        Returns:
            An ArchiveInfo object.
        """
        raise NotImplementedError


class _SharedFile:
    def __init__(self, file, position, size, close, lock, writing):
        self._file = file
        self._position = position
        self._start = position
        self._end = position + size
        self._close = close
        self._lock = lock
        self._writing = writing

    def seek(self, offset, whence=0):
        with self._lock:
            if self._writing():
                raise ValueError(
                    "Can't reposition in the archive file while there is an "
                    "open writing handle on it. Close the writing handle "
                    "before trying to read."
                )

            self._file.seek(offset, whence)
            self._position = self._file.tell()

    def read(self, n=-1):
        with self._lock:
            self._file.seek(self._position)

            if n < 0 or n > self._end:
                n = self._end - self._position

            data = self._file.read(n)
            self._position = self._file.tell()
            return data

    def tell(self):
        return self._file.tell()

    def close(self):
        if self._file is not None:
            file_object = self._file
            self._file = None
            self._close(file_object)


class ArchiveExtFile(io.BufferedIOBase):
    """A file-like object for reading an entry.

    It is returned by ArchiveFile.open()
    """

    MAX_N = 1 << 31 - 1
    MIN_READ_SIZE = 4096
    MAX_SEEK_READ = 1 << 24

    def __init__(self, file_object, mode, archive_info, close_file_object=False):
        self._file_object = file_object
        self._close_file_object = close_file_object
        self._bytes_left = archive_info.file_size
        self._original_size = archive_info.file_size
        self._original_start = file_object.tell()

        self._eof = False
        self._readbuffer = b''
        self._offset = 0
        self._size = archive_info.file_size

        self.mode = mode
        self.name = archive_info.filename

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

    def seek(self, offset, whence=0):
        current_position = self.tell()

        if whence == 0:
            new_position = offset

        elif whence == 1:
            new_position = current_position + offset

        elif whence == 2:
            new_position = self._original_size + offset

        else:
            raise ValueError("whence must be os.SEEK_SET (0), os.SEEK_CUR (1), or os.SEEK_END (2)")

        if new_position > self._original_size:
            new_position = self._original_size

        if new_position < 0:
            new_position = 0

        read_offset = new_position - current_position
        buff_offset = read_offset + self._offset

        if buff_offset >= 0 and buff_offset < len(self._readbuffer):
            self._offset = buff_offset
            read_offset = 0

        elif read_offset < 0:
            self._file_object.seek(self._original_start)
            self._bytes_left = self._original_size
            self._readbuffer = b''
            self._offset = 0
            self._eof = False
            read_offset = new_position

        while read_offset > 0:
            read_length = min(self.MAX_SEEK_READ, read_offset)
            self.read(read_length)
            read_offset -= read_length

    def tell(self):
        filepos = self._original_size - self._bytes_left - len(self._readbuffer) + self._offset

        return filepos

    def close(self):
        try:
            if self._close_file_object:
                self._file_object.close()
        finally:
            super().close()


class _ArchiveWriteFile(io.BufferedIOBase):
    def __init__(self, archive_file, archive_info):
        self._archive_info = archive_info
        self._archive_file = archive_file
        self._file_size = 0
        self._start_of_file = self._fileobj.tell()

    @property
    def _fileobj(self):
        return self._archive_file.fp

    def writable(self):
        return True

    def write(self, data):
        number_of_bytes = len(data)
        relative_offset = self.tell()
        self._file_size = max(self._file_size, relative_offset + number_of_bytes)
        self._fileobj.write(data)

        return number_of_bytes

    def peek(self, n=1):
        return self._fileobj.peek(n)

    def seek(self, offset, whence=0):
        self._fileobj.seek(offset + self._start_of_file, whence)

    def tell(self):
        return self._fileobj.tell() - self._start_of_file

    def close(self):
        super().close()

        self._archive_info.file_size = self._file_size
        self._archive_file.end_of_data = self._fileobj.tell()
        self._archive_file._writing = False
        self._archive_file.file_list.append(self._archive_info)
        self._archive_file.NameToInfo[self._archive_info.filename] = self._archive_info


class ArchiveFile:
    """ArchiveFile serves as base class for working with binary archive data.

    Attributes:
        file: Either the path to the file, or a file-like object. If it is a path,
            the file will be opened and closed by ArchiveFile.

        mode: File mode. Is one of 'r', 'w', or 'a'.
    """

    fp = None
    _windows_illegal_name_trans_table = None

    class factory:
        ArchiveExtFile = ArchiveExtFile
        ArchiveInfo = ArchiveInfo
        ArchiveWriteFile = _ArchiveWriteFile
        SharedFile = _SharedFile

    def __init__(self, file, mode='r'):
        if mode not in ('r', 'w', 'a'):
            raise RuntimeError("ArchiveFile requires mode 'r', 'w', or 'a'")

        self.NameToInfo = {}
        self.file_list = []
        self.mode = mode

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
                self._read_file(mode)

            elif mode == 'w':
                self._did_modify = True
                self._write_directory()
                self.end_of_data = self.fp.tell()

            elif mode == 'a':
                self._read_file(mode)
                self.fp.seek(self.end_of_data)

            else:
                raise ValueError("Mode must be 'r', 'w', or 'a'")

        except Exception as e:
            fp = self.fp
            self.fp = None
            self._fpclose(fp)

            raise e

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _read_file(self, mode='r'):
        raise NotImplementedError

    def _write_directory(self):
        raise NotImplementedError

    def namelist(self):
        """Return a list of archive members by name.

        Returns:
            A sequence of filenames.
        """

        return [data.filename for data in self.file_list]

    def infolist(self):
        """Return a list containing an ArchiveInfo object for each member of the
        archive. The objects are in the same order as their entries in the
        actual archive file on disk if an existing archive was opened.

        Returns:
            A sequence of ArchiveInfo objects.
        """

        return self.file_list

    def getinfo(self, name):
        """Return a ArchiveInfo object with information about the archive member
        name. Calling getinfo() for a name not currently contained in the
        archive will raise a KeyError.

        Args:
            name: AchiveInfo name.

        Returns:
            An ArchiveInfo object.

        Raises:
            KeyError: If no archive item exists for the given name.
        """

        info = self.NameToInfo.get(name)

        if info is None:
            raise KeyError('There is no item named %r in the archive file' % name)

        return info

    def read(self, name):
        """Return the bytes of the file name in the archive. name is the name of
        the file in the archive, or a ArchiveInfo object. The archive must be
        open for read or append.

        Args:
            name: ArchiveInfo name.

        Returns:
            File as bytes.
        """

        info = self.getinfo(name)

        with self.open(name, 'r') as fp:
            return fp.read(info.file_size)

    def open(self, name, mode='r'):
        """Access a member of the archive as a binary file-like object. name can
        be either the name of a file within the archive or an ArchiveInfo object.
        The mode parameter, if included, must be 'r' (the default) or 'w'.

        open() is also a context manager and supports the with statement::

            with ArchiveFile('archive.file') as archive_file:
                with archive_file.open('entry') as entry_file:
                    print(entry_file.read())

        Args:
            name: Name or ArchiveInfo object.

            mode: File mode to open object.

        Returns:
            A binary file-like object.

        Raises:
            ValueError: If mode isn't 'r' or 'w'.

            RuntimeError: If file was already closed.
        """

        if mode not in ('r', 'w'):
            raise ValueError("open() requires mode 'r' or 'w'")

        if not self.fp:
            raise RuntimeError('Attempt to read archive that was already closed')

        if isinstance(name, self.factory.ArchiveInfo):
            info = name

        elif mode == 'w':
            info = self.factory.ArchiveInfo(name)
            info.file_offset = self.fp.tell()

        else:
            info = self.getinfo(name)

        if mode == 'w':
            return self._open_to_write(info)

        self._file_reference_count += 1
        shared_file = self.factory.SharedFile(
            self.fp,
            info.file_offset,
            info.file_size,
            self._fpclose,
            self._lock,
            lambda: self._writing
        )

        try:
            return self.factory.ArchiveExtFile(shared_file, mode, info, True)

        except:
            shared_file.close()
            raise

    def _open_to_write(self, archive_info):
        if self._writing:
            raise ValueError("Can't write to the archive file while there is "
                             "another write handle open on it. Close the first"
                             " handle before opening another.")

        self._write_check(archive_info)

        self._did_modify = True
        self._writing = True

        return self.factory.ArchiveWriteFile(self, archive_info)

    def extract(self, member, path=None):
        """Extract a member from the archive to the current working directory;
        member must be its full name or a ArchiveInfo object. Its file
        information is extracted as accurately as possible. path specifies a
        different directory to extract to. member can be a filename or an
        ArchiveInfo object.

        Args:
            member: Either the name of the member to extract or a ArchiveInfo
                instance.

            path: The directory to extract to. The current working directory
                will be used if None.

        Returns:
            Path to extracted file.
        """

        if not isinstance(member, self.factory.ArchiveInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        return self._extract_member(member, path)

    def extractall(self, path=None, members=None):
        """Extract all members from the archive to the current working
        directory. path specifies a different directory to extract to. members
        is optional and must be a subset of the list returned by namelist().

        Args:
            path: The directory to extract to. The current working directory
                will be used if None.

            members: The names of the members to extract. This must be a subset
                of the list returned by namelist(). All members will be
                extracted if None.
        """

        if members is None:
            members = self.namelist()

        for archiveinfo in members:
            self.extract(archiveinfo, path)

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
        """Extract the ArchiveInfo object 'member' to a physical file on the path
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

    def _write_check(self, archive_info):
        if self.mode not in ('w', 'x', 'a'):
            raise ValueError("write() requires mode 'w', 'x', or 'a'")

        if not self.fp:
            raise ValueError('Attempting to write to archive that was already closed')

    def write(self, filename, arcname=None):
        """Write the file named filename to the archive, giving it the archive
        name arcname (by default, this will be the same as filename, but without
        a drive letter and with leading path separators removed). The archive
        must be open with mode 'w', or 'a'.

        Args:
            filename:

            arcname: Optional. Name of the info object. If omitted filename
                will be used.
        """

        if not self.fp:
            raise ValueError('Attempting to write to archive that was'
                             ' already closed')
        if self._writing:
            raise ValueError("Can't write to archive while an open writing"
                             " handle exists")

        info = self.factory.ArchiveInfo.from_file(filename)
        info.file_offset = self.fp.tell()

        if arcname:
            info.filename = arcname

        if filename[-1] == '/':
            raise RuntimeError('ArchiveFile expects a file, got a directory')

        else:
            with open(filename, 'rb') as src, self.open(info, 'w') as dest:
                shutil.copyfileobj(src, dest, 8*1024)

    def writestr(self, info_or_arcname, data):
        """Write a file into the archive. The contents is data, which may be
        either a string or a bytes instance; if it is a string, it is encoded as
        UTF-8 first. info_or_arcname is either the file name it will be given in
        the archive, or a ArchiveInfo instance. If it’s an instance, at least
        the filename must be given. The archive must be opened with mode 'w'
        or 'a'.

        Args:
            info_or_arcname:

            data: Data to be written. Either a string or bytes.
        """
        if not self.fp:
            raise ValueError('Attempting to write to archive that was'
                             ' already closed')
        if self._writing:
            raise ValueError("Can't write to archive while an open writing"
                             " handle exists")

        if not isinstance(info_or_arcname, self.factory.ArchiveInfo):
            info = self.factory.ArchiveInfo(info_or_arcname)

        else:
            info = info_or_arcname

        info.file_offset = self.fp.tell()

        if not info.file_size:
            info.file_size = len(data)

        should_close = False

        if isinstance(data, str):
            data = data.encode('ascii')

        if isinstance(data, bytes):
            data = io.BytesIO(data)
            should_close = True

        if not hasattr(data, 'read'):
            raise TypeError('Invalid data type. ArchiveFile.writestr expects a string or bytes')

        with data as src, self.open(info, 'w') as dest:
            shutil.copyfileobj(src, dest, 8*1024)

        if should_close:
            data.close()

    def close(self):
        """Close the archive file. You must call close() before exiting your
        program or essential records will not be written.

        Raises:
            ValueError: If open writing handles exist.
        """

        if self.fp is None:
            return

        if self._writing:
            raise ValueError("Can't close archive file while there is an open"
                             "writing handle on it. Close the writing handle"
                             "before closing the archive.")

        try:
            if self.mode in ('w', 'x', 'a') and self._did_modify and hasattr(self, 'end_of_data'):
                with self._lock:
                    self.fp.seek(self.end_of_data)
                    self._write_directory()

        finally:
            fp = self.fp
            self.fp = None
            self._fpclose(fp)

    def _fpclose(self, fp):
        assert self._file_reference_count > 0
        self._file_reference_count -= 1

        if not self._file_reference_count and not self._file_passed:
            fp.close()
