import struct

from vgio._core import ReadWriteFile


class SpriteType:
    VP_PARALLEL_UPRIGHT = 0
    FACING_UPRIGHT = 1
    VP_PARALLEL = 2
    ORIENTED = 3
    VP_PARALLEL_ORIENTED = 4


class TextureFormatType:
    NORMAL = 0
    ADDITIVE = 1
    INDEXALPHA = 2
    ALPHTEST = 3


class SyncType:
    SYNCHRONIZED = 0
    RANDOM = 1


class Header:
    """ Class for representing a Mdl file header

    Attributes:
        identity: File identity. Must be b'IDSP'

        version: File version. Should be 2

        type: Sprite type

        texture_format: Texture format

        radius: Bounding radius.

        width_max: Maximum width of sprite in pixels.

        height_max: Maximum height of sprite in pixels.

        frame_count: Number of frames.

        beam_length: Beam length.

        sync_type: Synchronization type.
    """
    format = '<4s3if3Ifi'
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'version',
        'type',
        'texture_format',
        'radius',
        'width_max',
        'height_max',
        'frame_count',
        'beam_length',
        'sync_type'
    )

    def __init__(self,
                 identity,
                 version,
                 type_,
                 texture_format,
                 radius,
                 width_max,
                 height_max,
                 frame_count,
                 beam_length,
                 sync_type):
        self.identity = identity
        self.version = version
        self.type = type_
        self.texture_format = texture_format
        self.radius = radius
        self.width_max = width_max
        self.height_max = height_max
        self.frame_count = frame_count
        self.beam_length = beam_length
        self.sync_type = sync_type

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.identity,
            header.version,
            header.type,
            header.texture_format,
            header.radius,
            header.width_max,
            header.height_max,
            header.frame_count,
            header.beam_length,
            header.sync_type
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Frame:
    """Class for representing a single sprite frame

    Attributes:
        type: The type of frame. Half-life only uses 0

        origin: The offset of the model. Used to correctly position the model.

        width: The pixel width of this individual frame.

        height: The pixel height of this individual frame.

        pixels: A tuple of unstructured indexed pixel data represented as
            integers. A palette must be used to obtain RGB data.
            The size of this tuple is:

            spr_sprite_frame.width * spr_sprite_frame.skin_height.
    """
    format = '<I2i2I'
    size = struct.calcsize(format)

    __slots_ = (
        'type',
        'origin',
        'width',
        'height',
        'pixels'
    )

    def __init__(self,
                 type,
                 origin_x,
                 origin_y,
                 width,
                 height,
                 pixels):
        self.type = type
        self.origin = origin_x, origin_y
        self.width = width
        self.height = height
        self.pixels = pixels

    @classmethod
    def write(cls, file, sprite_frame):
        sprite_frame_data = struct.pack(
            cls.format,
            sprite_frame.type,
            *sprite_frame.origin,
            sprite_frame.width,
            sprite_frame.height
        )

        file.write(sprite_frame_data)

        pixels_format = '<%iB' % len(sprite_frame.pixels)
        pixels_data = struct.pack(pixels_format, *sprite_frame.pixels)
        file.write(pixels_data)

    @classmethod
    def read(cls, file):
        frame_data = file.read(cls.size)
        frame_struct = struct.unpack(cls.format, frame_data)

        frame = cls(*frame_struct, b'')

        pixels_count = frame.width * frame.height
        pixels_format = f'<{pixels_count}B'
        pixels_size = struct.calcsize(pixels_format)
        pixels = file.read(pixels_size)

        frame.pixels = pixels

        return frame


class Spr(ReadWriteFile):
    """Class for working with Spr files

    Example:
        Basic usage::

            from vgio.halflife.spr import Spr
            s = Spr.open(file)

    Attributes:
        identity: File identity. Must be b'IDSP'

        version: File version. Should be 2

        type: Sprite type

        texture_format: Texture format

        radius: Bounding radius.

        width_max: Maximum width of sprite in pixels.

        height_max: Maximum height of sprite in pixels.

        beam_length: Beam length.

        sync_type: Synchronization type.

        frames: A sequence of frame objects.

        palette: A sequence of up to 768 bytes representing a 256 RGB color
            palette.
    """
    class factory:
        Header = Header
        Frame = Frame

    def __init__(self,
                 identity,
                 version,
                 type_,
                 texture_format,
                 radius,
                 width_max,
                 height_max,
                 beam_length,
                 sync_type,
                 frames,
                 palette):
        """Constructs an Spr object"""
        super().__init__()

        self.identity = identity
        self.version = version
        self.type = type_
        self.texture_format = texture_format
        self.radius = radius
        self.width_max = width_max
        self.height_max = height_max
        self.beam_length = beam_length
        self.sync_type = sync_type
        self.frames = frames
        self.palette = palette

    @classmethod
    def _read_file(cls, file, mode):
        header = cls.factory.Header.read(file)

        palette_size = struct.unpack('<H', file.read(2))[0]
        palette = file.read(struct.calcsize(f'<{palette_size * 3}B'))

        frames = [cls.factory.Frame.read(file) for _ in range(header.frame_count)]

        return cls(
            header.identity,
            header.version,
            header.type,
            header.texture_format,
            header.radius,
            header.width_max,
            header.height_max,
            header.beam_length,
            header.sync_type,
            frames,
            palette
        )

    @classmethod
    def _write_file(cls, file, spr):
        header = cls.factory.Header(
            spr.identity,
            spr.version,
            spr.type,
            spr.texture_format,
            spr.radius,
            spr.width_max,
            spr.height_max,
            len(spr.frames),
            spr.beam_length,
            spr.sync_type
        )

        cls.factory.Header.write(file, header)

        palette_size_data = struct.pack('<H', len(spr.palette) // 3)

        file.write(palette_size_data)
        file.write(spr.palette)

        for frame in spr.frames:
            cls.factory.Frame.write(file, frame)
