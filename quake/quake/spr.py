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

import io
import struct

__all__ = ['BadSprFile', 'Spr', 'is_sprfile']


class BadSprFile(Exception):
    pass


# The spr header structure
header_format = '<4s2if3ifi'
header_magic_number = b'IDSP'
header_version = 1
header_size = struct.calcsize(header_format)

# Indexes of the header structure
_HEADER_IDENTIFIER = 0
_HEADER_VERSION = 1
_HEADER_TYPE = 2
_HEADER_BOUNDING_RADIUS = 3
_HEADER_WIDTH = 4
_HEADER_HEIGHT = 5
_HEADER_NUMBER_OF_FRAMES = 6
_HEADER_BEAM_LENGTH = 7
_HEADER_SYNC_TYPE = 8

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

    return data == header_magic_number


def is_sprfile(filename):
    """Quickly see if a file is an spr file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    result = False

    try:
        if hasattr(filename, 'read'):
            return _check_sprfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_sprfile(fp)

    except:
        pass

    return result


default_palette = (
    (0x00,0x00,0x00),(0x0f,0x0f,0x0f),(0x1f,0x1f,0x1f),(0x2f,0x2f,0x2f),
    (0x3f,0x3f,0x3f),(0x4b,0x4b,0x4b),(0x5b,0x5b,0x5b),(0x6b,0x6b,0x6b),
    (0x7b,0x7b,0x7b),(0x8b,0x8b,0x8b),(0x9b,0x9b,0x9b),(0xab,0xab,0xab),
    (0xbb,0xbb,0xbb),(0xcb,0xcb,0xcb),(0xdb,0xdb,0xdb),(0xeb,0xeb,0xeb),
    (0x0f,0x0b,0x07),(0x17,0x0f,0x0b),(0x1f,0x17,0x0b),(0x27,0x1b,0x0f),
    (0x2f,0x23,0x13),(0x37,0x2b,0x17),(0x3f,0x2f,0x17),(0x4b,0x37,0x1b),
    (0x53,0x3b,0x1b),(0x5b,0x43,0x1f),(0x63,0x4b,0x1f),(0x6b,0x53,0x1f),
    (0x73,0x57,0x1f),(0x7b,0x5f,0x23),(0x83,0x67,0x23),(0x8f,0x6f,0x23),
    (0x0b,0x0b,0x0f),(0x13,0x13,0x1b),(0x1b,0x1b,0x27),(0x27,0x27,0x33),
    (0x2f,0x2f,0x3f),(0x37,0x37,0x4b),(0x3f,0x3f,0x57),(0x47,0x47,0x67),
    (0x4f,0x4f,0x73),(0x5b,0x5b,0x7f),(0x63,0x63,0x8b),(0x6b,0x6b,0x97),
    (0x73,0x73,0xa3),(0x7b,0x7b,0xaf),(0x83,0x83,0xbb),(0x8b,0x8b,0xcb),
    (0x00,0x00,0x00),(0x07,0x07,0x00),(0x0b,0x0b,0x00),(0x13,0x13,0x00),
    (0x1b,0x1b,0x00),(0x23,0x23,0x00),(0x2b,0x2b,0x07),(0x2f,0x2f,0x07),
    (0x37,0x37,0x07),(0x3f,0x3f,0x07),(0x47,0x47,0x07),(0x4b,0x4b,0x0b),
    (0x53,0x53,0x0b),(0x5b,0x5b,0x0b),(0x63,0x63,0x0b),(0x6b,0x6b,0x0f),
    (0x07,0x00,0x00),(0x0f,0x00,0x00),(0x17,0x00,0x00),(0x1f,0x00,0x00),
    (0x27,0x00,0x00),(0x2f,0x00,0x00),(0x37,0x00,0x00),(0x3f,0x00,0x00),
    (0x47,0x00,0x00),(0x4f,0x00,0x00),(0x57,0x00,0x00),(0x5f,0x00,0x00),
    (0x67,0x00,0x00),(0x6f,0x00,0x00),(0x77,0x00,0x00),(0x7f,0x00,0x00),
    (0x13,0x13,0x00),(0x1b,0x1b,0x00),(0x23,0x23,0x00),(0x2f,0x2b,0x00),
    (0x37,0x2f,0x00),(0x43,0x37,0x00),(0x4b,0x3b,0x07),(0x57,0x43,0x07),
    (0x5f,0x47,0x07),(0x6b,0x4b,0x0b),(0x77,0x53,0x0f),(0x83,0x57,0x13),
    (0x8b,0x5b,0x13),(0x97,0x5f,0x1b),(0xa3,0x63,0x1f),(0xaf,0x67,0x23),
    (0x23,0x13,0x07),(0x2f,0x17,0x0b),(0x3b,0x1f,0x0f),(0x4b,0x23,0x13),
    (0x57,0x2b,0x17),(0x63,0x2f,0x1f),(0x73,0x37,0x23),(0x7f,0x3b,0x2b),
    (0x8f,0x43,0x33),(0x9f,0x4f,0x33),(0xaf,0x63,0x2f),(0xbf,0x77,0x2f),
    (0xcf,0x8f,0x2b),(0xdf,0xab,0x27),(0xef,0xcb,0x1f),(0xff,0xf3,0x1b),
    (0x0b,0x07,0x00),(0x1b,0x13,0x00),(0x2b,0x23,0x0f),(0x37,0x2b,0x13),
    (0x47,0x33,0x1b),(0x53,0x37,0x23),(0x63,0x3f,0x2b),(0x6f,0x47,0x33),
    (0x7f,0x53,0x3f),(0x8b,0x5f,0x47),(0x9b,0x6b,0x53),(0xa7,0x7b,0x5f),
    (0xb7,0x87,0x6b),(0xc3,0x93,0x7b),(0xd3,0xa3,0x8b),(0xe3,0xb3,0x97),
    (0xab,0x8b,0xa3),(0x9f,0x7f,0x97),(0x93,0x73,0x87),(0x8b,0x67,0x7b),
    (0x7f,0x5b,0x6f),(0x77,0x53,0x63),(0x6b,0x4b,0x57),(0x5f,0x3f,0x4b),
    (0x57,0x37,0x43),(0x4b,0x2f,0x37),(0x43,0x27,0x2f),(0x37,0x1f,0x23),
    (0x2b,0x17,0x1b),(0x23,0x13,0x13),(0x17,0x0b,0x0b),(0x0f,0x07,0x07),
    (0xbb,0x73,0x9f),(0xaf,0x6b,0x8f),(0xa3,0x5f,0x83),(0x97,0x57,0x77),
    (0x8b,0x4f,0x6b),(0x7f,0x4b,0x5f),(0x73,0x43,0x53),(0x6b,0x3b,0x4b),
    (0x5f,0x33,0x3f),(0x53,0x2b,0x37),(0x47,0x23,0x2b),(0x3b,0x1f,0x23),
    (0x2f,0x17,0x1b),(0x23,0x13,0x13),(0x17,0x0b,0x0b),(0x0f,0x07,0x07),
    (0xdb,0xc3,0xbb),(0xcb,0xb3,0xa7),(0xbf,0xa3,0x9b),(0xaf,0x97,0x8b),
    (0xa3,0x87,0x7b),(0x97,0x7b,0x6f),(0x87,0x6f,0x5f),(0x7b,0x63,0x53),
    (0x6b,0x57,0x47),(0x5f,0x4b,0x3b),(0x53,0x3f,0x33),(0x43,0x33,0x27),
    (0x37,0x2b,0x1f),(0x27,0x1f,0x17),(0x1b,0x13,0x0f),(0x0f,0x0b,0x07),
    (0x6f,0x83,0x7b),(0x67,0x7b,0x6f),(0x5f,0x73,0x67),(0x57,0x6b,0x5f),
    (0x4f,0x63,0x57),(0x47,0x5b,0x4f),(0x3f,0x53,0x47),(0x37,0x4b,0x3f),
    (0x2f,0x43,0x37),(0x2b,0x3b,0x2f),(0x23,0x33,0x27),(0x1f,0x2b,0x1f),
    (0x17,0x23,0x17),(0x0f,0x1b,0x13),(0x0b,0x13,0x0b),(0x07,0x0b,0x07),
    (0xff,0xf3,0x1b),(0xef,0xdf,0x17),(0xdb,0xcb,0x13),(0xcb,0xb7,0x0f),
    (0xbb,0xa7,0x0f),(0xab,0x97,0x0b),(0x9b,0x83,0x07),(0x8b,0x73,0x07),
    (0x7b,0x63,0x07),(0x6b,0x53,0x00),(0x5b,0x47,0x00),(0x4b,0x37,0x00),
    (0x3b,0x2b,0x00),(0x2b,0x1f,0x00),(0x1b,0x0f,0x00),(0x0b,0x07,0x00),
    (0x00,0x00,0xff),(0x0b,0x0b,0xef),(0x13,0x13,0xdf),(0x1b,0x1b,0xcf),
    (0x23,0x23,0xbf),(0x2b,0x2b,0xaf),(0x2f,0x2f,0x9f),(0x2f,0x2f,0x8f),
    (0x2f,0x2f,0x7f),(0x2f,0x2f,0x6f),(0x2f,0x2f,0x5f),(0x2b,0x2b,0x4f),
    (0x23,0x23,0x3f),(0x1b,0x1b,0x2f),(0x13,0x13,0x1f),(0x0b,0x0b,0x0f),
    (0x2b,0x00,0x00),(0x3b,0x00,0x00),(0x4b,0x07,0x00),(0x5f,0x07,0x00),
    (0x6f,0x0f,0x00),(0x7f,0x17,0x07),(0x93,0x1f,0x07),(0xa3,0x27,0x0b),
    (0xb7,0x33,0x0f),(0xc3,0x4b,0x1b),(0xcf,0x63,0x2b),(0xdb,0x7f,0x3b),
    (0xe3,0x97,0x4f),(0xe7,0xab,0x5f),(0xef,0xbf,0x77),(0xf7,0xd3,0x8b),
    (0xa7,0x7b,0x3b),(0xb7,0x9b,0x37),(0xc7,0xc3,0x37),(0xe7,0xe3,0x57),
    (0x7f,0xbf,0xff),(0xab,0xe7,0xff),(0xd7,0xff,0xff),(0x67,0x00,0x00),
    (0x8b,0x00,0x00),(0xb3,0x00,0x00),(0xd7,0x00,0x00),(0xff,0x00,0x00),
    (0xff,0xf3,0x93),(0xff,0xf7,0xc7),(0xff,0xff,0xff),(0x9f,0x5b,0x53),
)


SINGLE = 0
GROUP = 1


class SpriteFrame(object):
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
        sprite_frame_data = struct.pack(sprite_frame_format,
                                        sprite_frame.type,
                                        *sprite_frame.origin,
                                        sprite_frame.width,
                                        sprite_frame.height)

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


class SpriteGroup(object):
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


class Image(object):
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


class Spr(object):
    """Class for working with Spr files

    Example:
        s = Spr.open(file)

    Attributes:
        identifier: The magic number of the model, must be b'IDSP'

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

    def __init__(self):
        self.fp = None
        self.mode = None
        self._did_modify = False

        self.identifier = header_magic_number
        self.version = header_version
        self.type = VP_PARALLEL_UPRIGHT
        self.bounding_radius = 0
        self.width = 0
        self.height = 0
        self.number_of_frames = 0
        self.beam_length = 0
        self.sync_type = SYNC

        self.frames = []

    @staticmethod
    def open(file, mode='r'):
        """Returns an Spr object

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file

        Returns:
            An Spr object constructed from the information read from the
            file-like object.
        """

        if mode not in ('r', 'w', 'a'):
            raise ValueError("invalid mode: '%s'" % mode)

        filemode = {'r': 'rb', 'w': 'w+b', 'a': 'r+b'}[mode]

        if isinstance(file, str):
            file = io.open(file, filemode)

        elif isinstance(file, bytes):
            file = io.BytesIO(file)

        elif not hasattr(file, 'read'):
            raise RuntimeError(
                "Spr.open() requires 'file' to be a path, a file-like object, or bytes")

        # Read
        if mode == 'r':
            return Spr._read_file(file, mode)

        # Write
        elif mode == 'w':
            spr = Spr()
            spr.fp = file
            spr.mode = 'w'
            spr._did_modify = True

            return spr

        # Append
        else:
            spr = Spr._read_file(file, mode)
            spr._did_modify = True

            return spr

    @staticmethod
    def _read_file(file, mode):
        spr = Spr()
        spr.fp = file
        spr.mode = mode

        data = file.read(header_size)
        data = struct.unpack(header_format, data)

        if data[_HEADER_IDENTIFIER] != header_magic_number:
            raise BadSprFile('Bad magic number: %r' % data[_HEADER_IDENTIFIER])

        if data[_HEADER_VERSION] != header_version:
            raise BadSprFile('Bad version number: %r' % data[_HEADER_VERSION])

        spr.identifier = data[_HEADER_IDENTIFIER]
        spr.version = data[_HEADER_VERSION]
        spr.type = data[_HEADER_TYPE]
        spr.bounding_radius = data[_HEADER_BOUNDING_RADIUS]
        spr.width = data[_HEADER_WIDTH]
        spr.height = data[_HEADER_HEIGHT]
        spr.number_of_frames = data[_HEADER_NUMBER_OF_FRAMES]
        spr.beam_length = data[_HEADER_BEAM_LENGTH]
        spr.sync_type = data[_HEADER_SYNC_TYPE]

        for sprite_id in range(spr.number_of_frames):
            pos = file.tell()
            frame_type = struct.unpack('<i', file.read(4))[0]
            file.seek(pos)

            if frame_type == SINGLE:
                sprite_frame = SpriteFrame.read(file)
                spr.frames.append(sprite_frame)

            else:
                sprite_group = SpriteGroup.read(file)
                spr.frames.append(sprite_group)

        return spr

    @staticmethod
    def _write_file(file, spr):
        # Validate Spr Data
        spr.validate()

        # Header
        header_data = struct.pack(header_format,
                                  spr.identifier,
                                  spr.version,
                                  spr.type,
                                  spr.bounding_radius,
                                  spr.width,
                                  spr.height,
                                  spr.number_of_frames,
                                  spr.beam_length,
                                  spr.sync_type)

        file.write(header_data)

        # Frames
        for frame in spr.frames:
            if frame.type == SINGLE:
                SpriteFrame.write(file, frame)

            elif frame.type == GROUP:
                SpriteGroup.write(file, frame)

            else:
                raise BadSprFile('Unknown frame type: %s' % frame.type)

    def validate(self):
        """Verifies the correctness of Spr data.

        Raises:
            BadSprFile: If a discrepancy is found.
        """

        if self.identifier != header_magic_number:
            raise BadSprFile('Bad magic number: %r' % self.identifier)

        if self.version != header_version:
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


    @staticmethod
    def write(file, lmp):
        Spr._write_file(file, lmp)

    def save(self, file):
        """Writes Spr data to file

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
                "Spr.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        Spr._write_file(file, self)

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
                Spr._write_file(self.fp, self)
                self.fp.truncate()

        file_object = self.fp
        self.fp = None
        file_object.close()

    def image(self, index=0, subindex=0, palette=default_palette):
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
