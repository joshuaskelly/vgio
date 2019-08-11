"""This module provides file I/O for Duke3D Map files.

Example:
    map_file = map.Map.open('e1l1.map')

References:
    "Build Engine & Tools"
    - Ken Silverman
    - http://fabiensanglard.net/duke3d/BUILDINF.TXT
"""

import struct

from vgio._core import ReadWriteFile

__all__ = ['BadMapFile', 'is_mapfile', 'Sector', 'Wall', 'Sprite', 'Map']


VERSION = 7


class BadMapFile(Exception):
    pass


def _check_mapfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<1l'))
    version = struct.unpack('<1l', data)[0]

    return version == VERSION


def is_mapfile(filename):
    """Quickly see if a file is a map file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_mapfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_mapfile(fp)

    except Exception:
        return False


class Header:
    format = '<4l2h'
    size = struct.calcsize(format)

    __slots__ = (
        'version',
        'start_position',
        'start_angle',
        'start_sector'
    )

    def __init__(self,
                 version,
                 start_position_0,
                 start_position_1,
                 start_position_2,
                 start_angle,
                 start_sector):
        self.version = version
        self.start_position = start_position_0, start_position_1, start_position_2
        self.start_angle = start_angle
        self.start_sector = start_sector

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.version,
            *header.start_position,
            header.start_angle,
            header.start_sector
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Sector:
    """Class for representing a sector

    Attributes:
        wall_pointer: The index of the first wall.

        wall_number: The total number of walls in sector.

        ceiling_z: The z-coordinate of the ceiling at the first point of sector.

        floor_z: The z-coordinate of the floor at the first point of sector.

        ceiling_stat: A bitmasked field of properties.

        floor_stat: A bitmasked field of properties.

        ceiling_picnum: Texture index into Art file

        ceiling_heinum: Slope value. 0 is parallel to the floor, 4096 is 45 degrees.

        ceiling_shade: Shade offset for ceiling.

        ceiling_palette: Palette lookup number. 0 is the standard palette.

        ceiling_x_panning: Texture x align/pan value.

        ceiling_y_panning: Texture y align/pan value.

        floor_picnum: Texture index into Art file

        floor_heinum: Slope value. 0 is parallel to the floor, 4096 is 45 degrees.

        floor_shade: Shade offset for floor.

        floor_palette: Palette lookup number. 0 is the standard palette.

        floor_x_panning: Texture x align/pan value.

        floor_y_panning: Texture y align/pan value.

        visibility: Determines how fast shade changes relative to distance

        lotag: Tag for driving behavior.

        hitag: Tag for driving behavior.

        extra: Tag for driving behavior.
    """
    format = '<2h2l4h4b2h5bx3h'
    size = struct.calcsize(format)

    __slots__ = (
        'wall_pointer',
        'wall_number',
        'ceiling_z',
        'floor_z',
        'ceiling_stat',
        'floor_stat',
        'ceiling_picnum',
        'ceiling_heinum',
        'ceiling_shade',
        'ceiling_palette',
        'ceiling_x_panning',
        'ceiling_y_panning',
        'floor_picnum',
        'floor_heinum',
        'floor_shade',
        'floor_palette',
        'floor_x_panning',
        'floor_y_panning',
        'visibility',
        'lotag',
        'hitag',
        'extra'
    )

    def __init__(self,
                 wall_pointer,
                 wall_number,
                 ceiling_z,
                 floor_z,
                 ceiling_stat,
                 floor_stat,
                 ceiling_picnum,
                 ceiling_heinum,
                 ceiling_shade,
                 ceiling_palette,
                 ceiling_x_panning,
                 ceiling_y_panning,
                 floor_picnum,
                 floor_heinum,
                 floor_shade,
                 floor_palette,
                 floor_x_panning,
                 floor_y_panning,
                 visibility,
                 lotag,
                 hitag,
                 extra):
        self.wall_pointer = wall_pointer
        self.wall_number = wall_number
        self.ceiling_z = ceiling_z
        self.floor_z = floor_z
        self.ceiling_stat = ceiling_stat
        self.floor_stat = floor_stat
        self.ceiling_picnum = ceiling_picnum
        self.ceiling_heinum = ceiling_heinum
        self.ceiling_shade = ceiling_shade
        self.ceiling_palette = ceiling_palette
        self.ceiling_x_panning = ceiling_x_panning
        self.ceiling_y_panning = ceiling_y_panning
        self.floor_picnum = floor_picnum
        self.floor_heinum = floor_heinum
        self.floor_shade = floor_shade
        self.floor_palette = floor_palette
        self.floor_x_panning = floor_x_panning
        self.floor_y_panning = floor_y_panning
        self.visibility = visibility
        self.lotag = lotag
        self.hitag = hitag
        self.extra = extra

    @classmethod
    def write(cls, file, sector):
        sector_data = struct.pack(
            cls.format,
            sector.wall_pointer,
            sector.wall_number,
            sector.ceiling_z,
            sector.floor_z,
            sector.ceiling_stat,
            sector.floor_stat,
            sector.ceiling_picnum,
            sector.ceiling_heinum,
            sector.ceiling_shade,
            sector.ceiling_palette,
            sector.ceiling_x_panning,
            sector.ceiling_y_panning,
            sector.floor_picnum,
            sector.floor_heinum,
            sector.floor_shade,
            sector.floor_palette,
            sector.floor_x_panning,
            sector.floor_y_panning,
            sector.visibility,
            sector.lotag,
            sector.hitag,
            sector.extra
        )

        file.write(sector_data)

    @classmethod
    def read(cls, file):
        sector_data = file.read(cls.size)
        sector_struct = struct.unpack(cls.format, sector_data)

        return cls(*sector_struct)


class Wall:
    """Class for representing a wall

    Attributes:
        x: X-coordinate of left side of wall.

        y: Y-coordinate of left side of wall.

        point2: Index to the next wall on the right.

        next_wall: Index to wall on the other side of wall. Will be -1 if
            there is no sector.

        next_sector: Index to sector on other side of wall. Will be -1 if
            there is no sector.

        cstat: A bitmasked field of properties.

        picnum: Texture index into Art file.

        over_picnum: Texture index into Art file for masked walls.

        shade: Shade offset of wall.

        palette: Palette lookup number. 0 is the standard palette.

        x_repeat: Used to stretch texture.

        y_repeat: Used to stretch texture.

        x_panning: Used to align/pan texture.

        y_panning: Used to align/pan texture.

        lotag: Tag for driving behavior.

        hitag: Tag for driving behavior.

        extra: Tag for driving behavior.
    """
    format = '<2l6hb5b3h'
    size = struct.calcsize(format)

    __slots__ = (
        'x',
        'y',
        'point2',
        'next_wall',
        'next_sector',
        'cstat',
        'picnum',
        'over_picnum',
        'shade',
        'palette',
        'x_repeat',
        'y_repeat',
        'x_panning',
        'y_panning',
        'lotag',
        'hitag',
        'extra'
    )

    def __init__(self,
                 x,
                 y,
                 point2,
                 next_wall,
                 next_sector,
                 cstat,
                 picnum,
                 over_picnum,
                 shade,
                 palette,
                 x_repeat,
                 y_repeat,
                 x_panning,
                 y_panning,
                 lotag,
                 hitag,
                 extra):
        self.x = x
        self.y = y
        self.point2 = point2
        self.next_wall = next_wall
        self.next_sector = next_sector
        self.cstat = cstat
        self.picnum = picnum
        self.over_picnum = over_picnum
        self.shade = shade
        self.palette = palette
        self.x_repeat = x_repeat
        self.y_repeat = y_repeat
        self.x_panning = x_panning
        self.y_panning = y_panning
        self.lotag = lotag
        self.hitag = hitag
        self.extra = extra

    @classmethod
    def write(cls, file, wall):
        wall_data = struct.pack(
            cls.format,
            wall.x,
            wall.y,
            wall.point2,
            wall.next_wall,
            wall.next_sector,
            wall.cstat,
            wall.picnum,
            wall.over_picnum,
            wall.shade,
            wall.palette,
            wall.x_repeat,
            wall.y_repeat,
            wall.x_panning,
            wall.y_panning,
            wall.lotag,
            wall.hitag,
            wall.extra
        )

        file.write(wall_data)

    @classmethod
    def read(cls, file):
        wall_data = file.read(cls.size)
        wall_struct = struct.unpack(cls.format, wall_data)

        return cls(*wall_struct)


class Sprite:
    """Class for representing a sprite

    Attributes:
        x: X-coordinate of sprite position.

        y: Y-coordinate of sprite position.

        z: Z-coordinate of sprite position.

        cstat: A bitmasked field of properties.

        shade: Shade offset of sprite.

        palette: Palette lookup number. 0 is the standard palette.

        clip_distance: Size of movement clipping square.

        x_repeat: Used to stretch texture.

        y_repeat: Used to stretch texture.

        x_offset: Used to center texture.

        y_offset: Used to center texture.

        sector_number: Current sector of sprite.

        status_number: Current status of sprite.

        angle: Angle the sprite is facing.

        owner:

        x_velocity: X-coordinate of sprite velocity.

        y_velocity: Y-coordinate of sprite velocity.

        z_velocity: Z-coordinate of sprite velocity.

        lotag: Tag for driving behavior.

        hitag: Tag for driving behavior.

        extra: Tag for driving behavior.

    """
    format = '<3l2h3bx2B2b10h'
    size = struct.calcsize(format)

    __slots__ = (
        'x',
        'y',
        'z',
        'cstat',
        'picnum',
        'shade',
        'palette',
        'clip_distance',
        'x_repeat',
        'y_repeat',
        'x_offset',
        'y_offset',
        'sector_number',
        'status_number',
        'angle',
        'owner',
        'x_velocity',
        'y_velocity',
        'z_velocity',
        'lotag',
        'hitag',
        'extra'
    )

    def __init__(self,
                 x,
                 y,
                 z,
                 cstat,
                 picnum,
                 shade,
                 palette,
                 clip_distance,
                 x_repeat,
                 y_repeat,
                 x_offset,
                 y_offset,
                 sector_number,
                 status_number,
                 angle,
                 owner,
                 x_velocity,
                 y_velocity,
                 z_velocity,
                 lotag,
                 hitag,
                 extra):
        self.x = x
        self.y = y
        self.z = z
        self.cstat = cstat
        self.picnum = picnum
        self.shade = shade
        self.palette = palette
        self.clip_distance = clip_distance
        self.x_repeat = x_repeat
        self.y_repeat = y_repeat
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.sector_number = sector_number
        self.status_number = status_number
        self.angle = angle
        self.owner = owner
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        self.z_velocity = z_velocity
        self.lotag = lotag
        self.hitag = hitag
        self.extra = extra

    @classmethod
    def write(cls, file, sprite):
        sprite_data = struct.pack(
            cls.format,
            sprite.x,
            sprite.y,
            sprite.z,
            sprite.cstat,
            sprite.picnum,
            sprite.shade,
            sprite.palette,
            sprite.clip_distance,
            sprite.x_repeat,
            sprite.y_repeat,
            sprite.x_offset,
            sprite.y_offset,
            sprite.sector_number,
            sprite.status_number,
            sprite.angle,
            sprite.owner,
            sprite.x_velocity,
            sprite.y_velocity,
            sprite.z_velocity,
            sprite.lotag,
            sprite.hitag,
            sprite.extra
        )

        file.write(sprite_data)

    @classmethod
    def read(cls, file):
        sprite_data = file.read(cls.size)
        sprite_struct = struct.unpack(cls.format, sprite_data)

        return cls(*sprite_struct)


class Map(ReadWriteFile):
    """Class for working with map files

    Example:
        m = Map.open(file)

    Attributes:
        version: Version of the map file. Build is 7

        position_x: Player start position x-coordinate.

        position_y: Player start position y-coordinate.

        position_z: Player start position z-coordinate.

        angle: Player start angle.

        start_sector: Sector of player start.

        sectors: A list of Sector objects.

        walls: A list of Wall objects.

        sprites: A list of Sprite objects.
    """
    class factory:
        Header = Header
        Sector = Sector
        Wall = Wall
        Sprite = Sprite

    def __init__(self):
        super().__init__()

        self.version = VERSION
        self.start_position = []
        self.start_angle = 0
        self.start_sector = 0
        self.sectors = []
        self.walls = []
        self.sprites = []

    @classmethod
    def _read_file(cls, file, mode):
        map = cls()
        map.mode = mode
        map.fp = file

        # Header
        header = cls.factory.Header.read(file)

        map.version = header.version
        map.start_position = header.start_position
        map.start_angle = header.start_angle
        map.start_sector = header.start_sector

        # Sectors
        number_of_sectors = struct.unpack('<h', file.read(2))[0]
        map.sectors = [cls.factory.Sector.read(file) for _ in range(number_of_sectors)]

        # Walls
        number_of_walls = struct.unpack('<h', file.read(2))[0]
        map.walls = [cls.factory.Wall.read(file) for _ in range(number_of_walls)]

        # Sprites
        number_of_sprites = struct.unpack('<h', file.read(2))[0]
        map.sprites = [cls.factory.Sprite.read(file) for _ in range(number_of_sprites)]

        return map

    @classmethod
    def _write_file(cls, file, map):
        header = cls.factory.Header(
            map.version,
            map.position_x,
            map.position_y,
            map.position_z,
            map.angle,
            map.current_sector_number
        )

        cls.factory.Header.write(file, header)

        # Sectors
        number_of_sectors = len(map.sectors)
        file.write(struct.pack('<h', number_of_sectors))

        for sector in map.sectors:
            Sector.write(file, sector)

        # Walls
        number_of_walls = len(map.walls)
        file.write(struct.pack('<h', number_of_walls))

        for wall in map.walls:
            Wall.write(file, wall)

        # Sprites
        number_of_sprites = len(map.sprites)
        file.write(struct.pack('<h', number_of_sprites))

        for sprite in map.sprites:
            Sprite.write(file, sprite)
