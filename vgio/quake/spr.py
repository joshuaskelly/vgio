"""This module provides file I/O for Quake SPR sprite files.

Example:
    spr_file = spr.Spr.open('s_bubble.spr')

References:
    Quake Source
    - id Software
    - https://github.com/id-Software/Quake

    Quake Documentation Version 3.4
    - Olivier Montanuy, et al.
    - http://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_6.htm
"""

import struct

from vgio._core import ReadWriteFile
from vgio import quake

__all__ = ['BadSprFile', 'Spr', 'is_sprfile']


VERSION = 1
IDENTITY = b'IDSP'


class BadSprFile(Exception):
    pass


# Sprite Frame structure
sprite_frame_format = '<5i'
sprite_frame_size = struct.calcsize(sprite_frame_format)

# Indexes of Sprite Frame structure
_SPRITE_FRAME_TYPE = 0
_SPRITE_FRAME_ORIGIN = 1
_SPRITE_FRAME_WIDTH = 3
_SPRITE_FRAME_HEIGHT = 4


def _check_sprfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4s'))

    return data == IDENTITY


def is_sprfile(filename):
    """Quickly see if a file is an spr file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_sprfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_sprfile(fp)

    except Exception:
        return False


class Header:
    format = '<4s2if3ifi'
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'version',
        'type',
        'bounding_radius',
        'width',
        'height',
        'number_of_frames',
        'beam_length',
        'sync_type'
    )

    def __init__(self,
                 identity,
                 version,
                 type,
                 bounding_radius,
                 width,
                 height,
                 number_of_frames,
                 beam_length,
                 sync_type):
        self.identity = identity
        self.version = version
        self.type = type
        self.bounding_radius = bounding_radius
        self.width = width
        self.height = height
        self.number_of_frames = number_of_frames
        self.beam_length = beam_length
        self.sync_type = sync_type

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.identity,
            header.version,
            header.type,
            header.bounding_radius,
            header.width,
            header.height,
            header.number_of_frames,
            header.beam_length,
            header.sync_type
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


SINGLE = 0
GROUP = 1


class SpriteFrame:
    """Class for representing a single sprite frame

    Attributes:
        origin: The offset of the model. Used to correctly position the model.

        width: The pixel width of the sprite.

        height: The pixel height of the sprite.

        pixels: A tuple of unstructured indexed pixel data represented as
            integers. A palette must be used to obtain RGB data.
            The size of this tuple is:

            spr_sprite_frame.width * spr_sprite_frame.skin_height.
    """

    __slots_ = (
        'type',
        'origin',
        'width',
        'height',
        'pixels'
    )

    def __init__(self):
        self.type = SINGLE
        self.origin = 0, 0
        self.width = None
        self.height = None
        self.pixels = None

    @staticmethod
    def write(file, sprite_frame):
        sprite_frame_data = struct.pack(
            sprite_frame_format,
            sprite_frame.type,
            *sprite_frame.origin,
            sprite_frame.width,
            sprite_frame.height
        )

        file.write(sprite_frame_data)

        pixels_format = '<%iB' % len(sprite_frame.pixels)
        pixels_data = struct.pack(pixels_format, *sprite_frame.pixels)
        file.write(pixels_data)

    @staticmethod
    def read(file):
        sprite_frame = SpriteFrame()
        sprite_frame_data = file.read(sprite_frame_size)
        sprite_frame_struct = struct.unpack(sprite_frame_format, sprite_frame_data)

        sprite_frame.type = sprite_frame_struct[_SPRITE_FRAME_TYPE]
        sprite_frame.origin = sprite_frame_struct[_SPRITE_FRAME_ORIGIN:_SPRITE_FRAME_WIDTH]
        sprite_frame.width = sprite_frame_struct[_SPRITE_FRAME_WIDTH]
        sprite_frame.height = sprite_frame_struct[_SPRITE_FRAME_HEIGHT]

        pixels_count = sprite_frame.width * sprite_frame.height
        pixels_format = '<%iB' % pixels_count
        pixels_size = struct.calcsize(pixels_format)
        pixels = struct.unpack(pixels_format, file.read(pixels_size))

        sprite_frame.pixels = pixels

        return sprite_frame


class SpriteGroup:
    """Class for representing a sprite group

    Attributes:
        number_of_frames: The number of sprite frames in this group.

        intervals: A sequence of timings for each frame.

        frames: A list of SprSpriteFrame objects.
    """

    __slots__ = (
        'type',
        'number_of_frames',
        'intervals',
        'frames'
    )

    def __init__(self):
        self.type = GROUP
        self.number_of_frames = 0
        self.intervals = []
        self.frames = []

    @staticmethod
    def write(file, sprite_group):
        frame_type_data = struct.pack('<i', sprite_group.type)
        file.write(frame_type_data)

        frame_count_data = struct.pack('<i', sprite_group.number_of_frames)
        file.write(frame_count_data)

        intervals_format = '<%if' % sprite_group.number_of_frames
        intervals_data = struct.pack(intervals_format, *sprite_group.intervals)
        file.write(intervals_data)

        for frame in sprite_group.frames:
            SpriteFrame.write(file, frame)

    @staticmethod
    def read(file):
        frame_type = struct.unpack('<i', file.read(4))[0]
        number_of_frames = struct.unpack('<i', file.read(4))[0]
        intervals_format = '<%if' % number_of_frames
        intervals_size = struct.calcsize(intervals_format)
        intervals = struct.unpack(intervals_format, file.read(intervals_size))

        sprite_group = SpriteGroup()
        sprite_group.type = frame_type
        sprite_group.number_of_frames = number_of_frames
        sprite_group.intervals = intervals
        sprite_group.frames = [SpriteFrame.read(file) for _ in range(number_of_frames)]

        return sprite_group


class Image:
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


VP_PARALLEL_UPRIGHT = 0
FACING_UPRIGHT = 1
VP_PARALLEL = 2
ORIENTED = 3
VP_PARALLEL_ORIENTED = 4

SYNC = 0
RAND = 1


class Spr(ReadWriteFile):
    """Class for working with Spr files

    Example:
        s = Spr.open(file)

    Attributes:
        identity: The magic number of the model, must be b'IDSP'

        version: The version of the model, should be 1

        type: Type of model. Defines how the sprite orients itself relative to
            the camera.

        bounding_radius: The bounding radius of the model.

        width: The width of the model.

        height: The height of the model.

        number_of_frames: The number of frames (sprites or groups).

        beam_length: ???

        sync_type: The syncronization type for the model. It is either
            SYNC or RAND.

        fp: The file-like object to read data from.

        mode: The file mode for the file-like object.
    """
    class factory:
        Header = Header
        SpriteFrame = SpriteFrame
        SpriteGroup = SpriteGroup

    def __init__(self):
        super().__init__()

        self.identity = IDENTITY
        self.version = VERSION
        self.type = VP_PARALLEL_UPRIGHT
        self.bounding_radius = 0
        self.width = 0
        self.height = 0
        self.number_of_frames = 0
        self.beam_length = 0
        self.sync_type = SYNC

        self.frames = []

    @classmethod
    def _read_file(cls, file, mode):
        spr = cls()
        spr.fp = file
        spr.mode = mode

        header = cls.factory.Header.read(file)

        if header.identity != IDENTITY:
            raise BadSprFile(f'Bad magic number: {header.identity}')

        if header.version != VERSION:
            raise BadSprFile(f'Bad version number: {header.version}')

        spr.identity = header.identity
        spr.version = header.version
        spr.type = header.type
        spr.bounding_radius = header.bounding_radius
        spr.width = header.width
        spr.height = header.height
        spr.number_of_frames = header.number_of_frames
        spr.beam_length = header.beam_length
        spr.sync_type = header.sync_type

        for sprite_id in range(spr.number_of_frames):
            pos = file.tell()
            frame_type = struct.unpack('<i', file.read(4))[0]
            file.seek(pos)

            class_ = (cls.factory.SpriteFrame, cls.factory.SpriteGroup)[frame_type]
            frame = class_.read(file)
            spr.frames.append(frame)

        return spr

    @classmethod
    def _write_file(cls, file, spr):
        # Validate Spr Data
        spr.validate()

        # Header
        header = cls.factory.Header(
            spr.identity,
            spr.version,
            spr.type,
            spr.bounding_radius,
            spr.width,
            spr.height,
            spr.number_of_frames,
            spr.beam_length,
            spr.sync_type
        )

        cls.factory.Header.write(file, header)

        # Frames
        for frame in spr.frames:
            class_ = (cls.factory.SpriteFrame, cls.factory.SpriteGroup)[frame.type]
            class_.write(file, frame)

    def validate(self):
        """Verifies the correctness of Spr data.

        Raises:
            BadSprFile: If a discrepancy is found.
        """

        if self.identity != IDENTITY:
            raise BadSprFile('Bad magic number: %r' % self.identity)

        if self.version != VERSION:
            raise BadSprFile('Bad version number: %r' % self.version)

        if self.number_of_frames != len(self.frames):
            raise BadSprFile('Incorrect number of frames. Expected: %r Actual: %r' % (self.number_of_frames, len(self.frames)))

        for frame in self.frames:
            if frame.type == SINGLE:
                if len(frame.pixels) != frame.width * frame.height:
                    raise BadSprFile('Incorrect number of pixels. Expected: %r Actual: %r' % (frame.width * frame.height, len(frame.pixels)))

            elif frame.type == GROUP:
                if frame.number_of_frames != len(frame.invervals):
                    raise BadSprFile('Incorrect number of frame intervals. Expected: %r Actual: %r' % (frame.number_of_frames, len(frame.invervals)))

                if frame.number_of_frames != len(frame.frames):
                    raise BadSprFile('Incorrect number of subframes. Expected: %r Actual: %r' % (self.number_of_frames, len(self.frames)))

                for subframe in frame.frames:
                    if subframe.type == SINGLE and len(subframe.pixels) != subframe.width * subframe.height:
                        raise BadSprFile('Incorrect number of pixels. Expected: %r Actual: %r' % (subframe.width * subframe.height, len(subframe.pixels)))

                    else:
                        raise BadSprFile('Bad subframe type: %r' % (subframe.type))

            else:
                raise BadSprFile('Bad frame type: %r' % (frame.type))

    def image(self, index=0, subindex=0, palette=quake.palette):
        """Returns an Image object.

        Args:
            index: The index of the sprite frame or group to get image data for.

            subindex: The index of sprite frame in a sprite group to get image
                data for.

            palette: A 256 color palette to use for converted index color data to
                RGB data.

        Returns:
            An Image object.
        """

        if index > len(self.frames):
            raise IndexError('list index out of range')

        sprite = self.frames[0]
        if hasattr(sprite, 'intervals'):
            sprite = sprite.frames[subindex]

        image = Image()
        image.width = sprite.width
        image.height = sprite.height
        image.pixels = sprite.pixels

        p = []
        for row in reversed(range(image.height)):
            p += image.pixels[row * image.width:(row + 1) * image.width]

        d = []

        for i in p:
            d += palette[i]
            d += [255] if i is not 255 else [0]

        image.pixels = d

        return image
