"""This module provides file I/O for Quake 2 SP2 sprite files.

Example:
    with open('s_bubble.sp2') as file:
        sp2_file = sp2.Sp2.read(file)

References:
    Quake 2 Source
    - id Software
    - https://github.com/id-Software/Quake-2
"""

import struct

from vgio._core import ReadWriteFile

__all__ = ['BadSp2File', 'is_sp2file', 'Sp2']


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


class Sp2(ReadWriteFile):
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
    class factory:
        Header = Header
        SpriteFrame = SpriteFrame

    def __init__(self):
        super().__init__()

        self.identity = b'IDS2'
        self.version = 2
        self.number_of_frames = 0

        self.header = None
        self.frames = []

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
