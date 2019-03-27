"""This module provides file I/O for Quake 2 SP2 sprite files.

Example:
    with open('s_bubble.sp2') as file:
        sp2_file = sp2.Sp2.read(file)

References:
    Quake 2 Source
    - id Software
    - https://github.com/id-Software/Quake-2
"""

import io
import struct

from types import SimpleNamespace


class BadSp2File(Exception):
    pass


def _check_sp2file(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4si'))
    identity, version = struct.unpack('<4si', data)

    return identity == b'IDS2' and version == 2


def is_sp2file(filename):
    """Quickly see if a file is a sp2 file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_sp2file(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_sp2file(fp)

    except:
        return False


class Header:
    """ Class for representing a Sp2 file header

    Attributes:
        identity:  File identity. Should be IDS2

        version:  File version. Should be 2

        number_of_frames:  The number of sprite frames.
    """

    format = '<4s2i'
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'version',
        'number_of_frames'
    )

    def __init__(self,
                 identity,
                 version,
                 number_of_frames):
        self.identity = identity.split(b'\x00')[0].decode('ascii') if type(identity) is bytes else identity
        self.version = version
        self.number_of_frames = number_of_frames

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(cls.format,
                                  header.identity.encode('ascii'),
                                  header.version,
                                  header.number_of_frames)

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class SpriteFrame:
    """Class for working with sprite frames

    Attributes:
        width: Width of the frame.

        height: Height of the frame.

        origin: The offset of the frame.

        name: The name of the pcx file to use for the frame.
    """

    format = '<4i64s'
    size = struct.calcsize(format)

    __slots__ = (
        'width',
        'height',
        'origin',
        'name'
    )

    def __init__(self,
                 width,
                 height,
                 origin_x,
                 origin_y,
                 name):

        self.width = width
        self.height = height
        self.origin = origin_x, origin_y
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name

    @classmethod
    def write(cls, file, frame):
        frame_data = struct.pack(cls.format,
                                 frame.width,
                                 frame.height,
                                 *frame.origin,
                                 frame.name.encode('ascii'))

        file.write(frame_data)

    @classmethod
    def read(cls, file):
        frame_data = file.read(cls.size)
        frame_struct = struct.unpack(cls.format, frame_data)

        return SpriteFrame(*frame_struct)


class Sp2:
    """Class for working with Sp2 files

    Example:
        with open('s_bubble.sp2') as file:
            sp2_file = sp2.Sp2.read(file)

    Attributes:
        identity: The identity of the file. Should be b'IDS2'

        version: The version of the file. Should be 2.

        number_of_frames: The number of sprite frames.

        frames: A list of SpriteFrame objects.
    """

    def __init__(self):
        self.fp = None
        self.mode = None
        self._did_modify = False

        self.identity = b'IDS2'
        self.version = 2
        self.number_of_frames = 0

        self.header = None
        self.frames = []

        self.factory = SimpleNamespace(
            Header=Header,
            SpriteFrame=SpriteFrame
        )

    @classmethod
    def open(cls, file, mode='r'):
        """Returns an Sp2 object

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file

        Returns:
            An Sp2 object constructed from the information read from the
            file-like object.

        Raises:
            ValueError: If an invalid file mode is given.

            RuntimeError: If the file argument is not a file-like object.

            BadSp2File: If the file opened is not recognized as an Sp2 file.
        """

        if mode not in ('r', 'w', 'a'):
            raise ValueError("invalid mode: '%s'" % mode)

        filemode = {'r': 'rb', 'w': 'w+b', 'a': 'r+b'}[mode]

        if isinstance(file, str):
            file = io.open(file, filemode)

        elif isinstance(file, bytes):
            file = io.BytesIO(file)

        elif not hasattr(file, 'read'):
            raise RuntimeError("Sp2.open() requires 'file' to be a path, a file-like object, or bytes")

        # Read
        if mode == 'r':
            return Sp2._read_file(file, mode)

        # Write
        elif mode == 'w':
            sp2 = Sp2()
            sp2.fp = file
            sp2.mode = 'w'
            sp2._did_modify = True

            return sp2

        # Append
        else:
            sp2 = Sp2._read_file(file, mode)
            sp2._did_modify = True

            return sp2

    @classmethod
    def _read_file(cls, file, mode):
        sp2 = cls()
        sp2.fp = file
        sp2.mode = mode

        header = sp2.factory.Header.read(file)

        if header.identity != b'IDS2':
            raise BadSp2File('Bad identity: {}'.format(header.identity))

        if header.version != 2:
            raise BadSp2File('Bad version number: {}'.format(header.version))

        sp2.header = header
        sp2.number_of_frames = header.number_of_frames
        sp2.frames = [sp2.factory.SpriteFrame.read(file) for _ in range(header.number_of_frames)]

        return sp2

    @classmethod
    def _write_file(cls, file, sp2):
        header = sp2.factory.Header(
            sp2.identity,
            sp2.version,
            len(sp2.frames)
        )

        sp2.factory.Header.write(file, header)

        for frame in sp2.frames:
            sp2.factory.SpriteFrame.write(file, frame)

    def save(self, file):
        """Writes Sp2 data to file

        Args:
            file: Either the path to the file, or a file-like object, or bytes.

        Raises:
            RuntimeError: If file argument is not a file-like object.
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
                "Sp2.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        Sp2._write_file(file, self)

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
                Sp2._write_file(self.fp, self)
                self.fp.truncate()

            file_object = self.fp
            self.fp = None
            file_object.close()
