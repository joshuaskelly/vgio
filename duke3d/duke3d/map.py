"""This module provides file I/O for Duke3D Map files.

Example:
    map_file = map.Map.open('e1l1.map')

References:
    "Build Engine & Tools"
    - Ken Silverman
    - http://fabiensanglard.net/duke3d/BUILDINF.TXT
"""

import io
import struct

__all__ = ['BadMapFile', 'is_mapfile', 'Sector', 'Wall', 'Sprite', 'Map']


class BadMapFile(Exception):
    pass


# The map header structure
header_format = '<4l2h'
header_version = 7
header_size = struct.calcsize(header_format)

# Indices of header structure
_HEADER_VERSION = 0
_HEADER_START_POSITION_X = 1
_HEADER_START_POSITION_Y = 2
_HEADER_START_POSITION_Z = 3
_HEADER_START_ANGLE = 4
_HEADER_START_SECTOR = 5

# Sector structure
sector_format = '<2h2l4h4b2h6b3h'
sector_size = struct.calcsize(sector_format)

# Indices of Sector structure
_SECTOR_WALL_POINTER = 0
_SECTOR_NUMBER_OF_WALLS = 1
_SECTOR_CEILING_Z = 2
_SECTOR_FLOOR_Z = 3
_SECTOR_CEILING_STAT = 4
_SECTOR_FLOOR_STAT = 5
_SECTOR_CEILING_PICNUM = 6
_SECTOR_CEILING_HEINUM = 7
_SECTOR_CEILING_SHADE = 8
_SECTOR_CEILING_PALETTE = 9
_SECTOR_CEILING_X_PANNING = 10
_SECTOR_CEILING_Y_PANNING = 11
_SECTOR_FLOOR_PICNUM = 12
_SECTOR_FLOOR_HEINUM = 13
_SECTOR_FLOOR_SHADE = 14
_SECTOR_FLOOR_PALETTE = 15
_SECTOR_FLOOR_X_PANNING = 16
_SECTOR_FLOOR_Y_PANNING = 17
_SECTOR_VISIBILITY = 18
_SECTOR_FILLER = 19
_SECTOR_LOTAG = 20
_SECTOR_HITAG = 21
_SECTOR_EXTRA = 22

# Wall structure
wall_format = '<2l6hb5b3h'
wall_size = struct.calcsize(wall_format)

_WALL_X = 0
_WALL_Y = 1
_WALL_POINT2 = 2
_WALL_NEXT_WALL = 3
_WALL_NEXT_SECTOR = 4
_WALL_CSTAT = 5
_WALL_PICNUM = 6
_WALL_OVER_PICNUM = 7
_WALL_SHADE = 8
_WALL_PALETTE = 9
_WALL_X_REPEAT = 10
_WALL_Y_REPEAT = 11
_WALL_X_PANNING = 12
_WALL_Y_PANNING = 13
_WALL_LOTAG = 14
_WALL_HITAG = 15
_WALL_EXTRA = 16

# Sprite structure
sprite_format = '<3l2hb3b2B2b10h'
sprite_size = struct.calcsize(sprite_format)

_SPRITE_X = 0
_SPRITE_Y = 1
_SPRITE_Z = 2
_SPRITE_CSTAT = 3
_SPRITE_PICNUM = 4
_SPRITE_SHADE = 5
_SPRITE_PALETTE = 6
_SPRITE_CLIP_DISTANCE = 7
_SPRITE_FILLER = 8
_SPRITE_X_REPEAT = 9
_SPRITE_Y_REPEAT = 10
_SPRITE_X_OFFSET = 11
_SPRITE_Y_OFFSET = 12
_SPRITE_SECTOR_NUMBER = 13
_SPRITE_STAT_NUMBER = 14
_SPRITE_ANGLE = 15
_SPRITE_OWNER = 16
_SPRITE_X_VELOCITY = 17
_SPRITE_Y_VELOCITY = 18
_SPRITE_Z_VELOCITY = 19
_SPRITE_LOTAG = 20
_SPRITE_HITAG = 21
_SPRITE_EXTRA = 22


def _check_mapfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<1l'))
    version = struct.unpack('<1l', data)[0]

    return version == header_version


def is_mapfile(filename):
    """Quickly see if a file is a map file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    result = False

    try:
        if hasattr(filename, 'read'):
            return _check_mapfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_mapfile(fp)

    except:
        pass

    return result


class Sector(object):
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

    def __init__(self):
        self.wall_pointer = None
        self.wall_number = None
        self.ceiling_z = None
        self.floor_z = None
        self.ceiling_stat = None
        self.floor_stat = None
        self.ceiling_picnum = None
        self.ceiling_heinum = None
        self.ceiling_shade = None
        self.ceiling_palette = None
        self.ceiling_x_panning = None
        self.ceiling_y_panning = None
        self.floor_picnum = None
        self.floor_heinum = None
        self.floor_shade = None
        self.floor_palette = None
        self.floor_x_panning = None
        self.floor_y_panning = None
        self.visibility = None
        self.lotag = None
        self.hitag = None
        self.extra = None

    @staticmethod
    def write(file, sector):
        sector_data = struct.pack(sector_format,
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
                                  0,
                                  sector.lotag,
                                  sector.hitag,
                                  sector.extra)

        file.write(sector_data)

    @staticmethod
    def read(file):
        sector = Sector()
        sector_data = file.read(sector_size)
        sector_struct = struct.unpack(sector_format, sector_data)
        sector.wall_pointer = sector_struct[_SECTOR_WALL_POINTER]
        sector.wall_number = sector_struct[_SECTOR_NUMBER_OF_WALLS]
        sector.ceiling_z = sector_struct[_SECTOR_CEILING_Z]
        sector.floor_z = sector_struct[_SECTOR_FLOOR_Z]
        sector.ceiling_stat = sector_struct[_SECTOR_CEILING_STAT]
        sector.floor_stat = sector_struct[_SECTOR_FLOOR_STAT]
        sector.ceiling_picnum = sector_struct[_SECTOR_CEILING_PICNUM]
        sector.ceiling_heinum = sector_struct[_SECTOR_CEILING_HEINUM]
        sector.ceiling_shade = sector_struct[_SECTOR_CEILING_SHADE]
        sector.ceiling_palette = sector_struct[_SECTOR_CEILING_PALETTE]
        sector.ceiling_x_panning = sector_struct[_SECTOR_CEILING_X_PANNING]
        sector.ceiling_y_panning = sector_struct[_SECTOR_CEILING_Y_PANNING]
        sector.floor_picnum = sector_struct[_SECTOR_FLOOR_PICNUM]
        sector.floor_heinum = sector_struct[_SECTOR_FLOOR_HEINUM]
        sector.floor_shade = sector_struct[_SECTOR_FLOOR_SHADE]
        sector.floor_palette = sector_struct[_SECTOR_FLOOR_PALETTE]
        sector.floor_x_panning = sector_struct[_SECTOR_FLOOR_X_PANNING]
        sector.floor_y_panning = sector_struct[_SECTOR_FLOOR_Y_PANNING]
        sector.visibility = sector_struct[_SECTOR_VISIBILITY]
        sector.lotag = sector_struct[_SECTOR_LOTAG]
        sector.hitag = sector_struct[_SECTOR_HITAG]
        sector.extra = sector_struct[_SECTOR_EXTRA]

        return sector


class Wall(object):
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

    def __init__(self):
        self.x = None
        self.y = None
        self.point2 = None
        self.next_wall = None
        self.next_sector = None
        self.cstat = None
        self.picnum = None
        self.over_picnum = None
        self.shade = None
        self.palette = None
        self.x_repeat = None
        self.y_repeat = None
        self.x_panning = None
        self.y_panning = None
        self.lotag = None
        self.hitag = None
        self.extra = None

    @staticmethod
    def write(file, wall):
        wall_data = struct.pack(wall_format,
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
                                wall.extra)

        file.write(wall_data)

    @staticmethod
    def read(file):
        wall = Wall()
        wall_data = file.read(wall_size)
        wall_struct = struct.unpack(wall_format, wall_data)
        wall.x = wall_struct[_WALL_X]
        wall.y = wall_struct[_WALL_Y]
        wall.point2 = wall_struct[_WALL_POINT2]
        wall.next_wall = wall_struct[_WALL_NEXT_WALL]
        wall.next_sector = wall_struct[_WALL_NEXT_SECTOR]
        wall.cstat = wall_struct[_WALL_CSTAT]
        wall.picnum = wall_struct[_WALL_PICNUM]
        wall.over_picnum = wall_struct[_WALL_OVER_PICNUM]
        wall.shade = wall_struct[_WALL_SHADE]
        wall.palette = wall_struct[_WALL_PALETTE]
        wall.x_repeat = wall_struct[_WALL_X_REPEAT]
        wall.y_repeat = wall_struct[_WALL_Y_REPEAT]
        wall.x_panning = wall_struct[_WALL_X_PANNING]
        wall.y_panning = wall_struct[_WALL_Y_PANNING]
        wall.lotag = wall_struct[_WALL_LOTAG]
        wall.hitag = wall_struct[_WALL_HITAG]
        wall.extra = wall_struct[_WALL_EXTRA]

        return wall


class Sprite(object):
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

    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.cstat = None
        self.picnum = None
        self.shade = None
        self.palette = None
        self.clip_distance = None
        self.x_repeat = None
        self.y_repeat = None
        self.x_offset = None
        self.y_offset = None
        self.sector_number = None
        self.status_number = None
        self.angle = None
        self.owner = None
        self.x_velocity = None
        self.y_velocity = None
        self.z_velocity = None
        self.lotag = None
        self.hitag = None
        self.extra = None

    @staticmethod
    def write(file, sprite):
        sprite_data = struct.pack(sprite_format,
                                  sprite.x,
                                  sprite.y,
                                  sprite.z,
                                  sprite.cstat,
                                  sprite.picnum,
                                  sprite.shade,
                                  sprite.palette,
                                  sprite.clip_distance,
                                  0,
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
                                  sprite.extra)

        file.write(sprite_data)

    @staticmethod
    def read(file):
        sprite = Sprite()
        sprite_data = file.read(sprite_size)
        sprite_struct = struct.unpack(sprite_format, sprite_data)
        sprite.x = sprite_struct[_SPRITE_X]
        sprite.y = sprite_struct[_SPRITE_Y]
        sprite.z = sprite_struct[_SPRITE_Z]
        sprite.cstat = sprite_struct[_SPRITE_CSTAT]
        sprite.picnum = sprite_struct[_SPRITE_PICNUM]
        sprite.shade = sprite_struct[_SPRITE_SHADE]
        sprite.palette = sprite_struct[_SPRITE_PALETTE]
        sprite.clip_distance = sprite_struct[_SPRITE_CLIP_DISTANCE]
        sprite.x_repeat = sprite_struct[_SPRITE_X_REPEAT]
        sprite.y_repeat = sprite_struct[_SPRITE_Y_REPEAT]
        sprite.x_offset = sprite_struct[_SPRITE_X_OFFSET]
        sprite.y_offset = sprite_struct[_SPRITE_Y_OFFSET]
        sprite.sector_number = sprite_struct[_SPRITE_SECTOR_NUMBER]
        sprite.status_number = sprite_struct[_SPRITE_STAT_NUMBER]
        sprite.angle = sprite_struct[_SPRITE_ANGLE]
        sprite.owner = sprite_struct[_SPRITE_OWNER]
        sprite.x_velocity = sprite_struct[_SPRITE_X_VELOCITY]
        sprite.y_velocity = sprite_struct[_SPRITE_Y_VELOCITY]
        sprite.z_velocity = sprite_struct[_SPRITE_Z_VELOCITY]
        sprite.lotag = sprite_struct[_SPRITE_LOTAG]
        sprite.hitag = sprite_struct[_SPRITE_HITAG]
        sprite.extra = sprite_struct[_SPRITE_EXTRA]

        return sprite


class Map(object):
    """Class for working with map files

    Example:
        m = Map.open(file)

    Attributes:
        version: Version of the map file. Build is 7

        position_x: Player start position x-coordinate.

        position_y: Player start position y-coordinate.

        position_z: Player start position z-coordinate.

        angle: Player start angle.

        current_sector_number: Sector of player start.

        sectors: A list of Sector objects.

        walls: A list of Wall objects.

        sprites: A list of Sprite objects.
    """

    def __init__(self):
        self.fp = None
        self.mode = None
        self._did_modify = False

        self.version = header_version
        self.position_x = 0
        self.position_y = 0
        self.position_z = 0
        self.angle = 0
        self.current_sector_number = 0
        self.sectors = []
        self.walls = []
        self.sprites = []

    @staticmethod
    def open(file, mode='r'):
        """Returns a Map object

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file

        Returns:
            An Map object constructed from the information read from the
            file-like object.

        Raises:
            ValueError: If an invalid file mode is given.

            RuntimeError: If the file argument is not a file-like object.
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
                "Map.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        # Read
        if mode == 'r':
            return Map._read_file(file, mode)

        # Write
        elif mode == 'w':
            map = Map()
            map.fp = file
            map.mode = 'w'
            map._did_modify = True

            return map

        # Append
        else:
            map = Map._read_file(file, mode)
            map._did_modify = True

            return map

    @staticmethod
    def _read_file(file, mode):
        map = Map()
        map.mode = mode
        map.fp = file

        # Header
        map_data = file.read(header_size)
        map_struct = struct.unpack(header_format, map_data)

        map.version = map_struct[_HEADER_VERSION]
        map.position_x = map_struct[_HEADER_START_POSITION_X]
        map.position_y = map_struct[_HEADER_START_POSITION_Y]
        map.position_z = map_struct[_HEADER_START_POSITION_Z]
        map.angle = map_struct[_HEADER_START_ANGLE]
        map.current_sector_number = map_struct[_HEADER_START_SECTOR]

        # Sectors
        number_of_sectors = struct.unpack('<h', file.read(2))[0]
        for _ in range(number_of_sectors):
            sector = Sector.read(file)
            map.sectors.append(sector)

        # Walls
        number_of_walls = struct.unpack('<h', file.read(2))[0]
        for _ in range(number_of_walls):
            wall = Wall.read(file)
            map.walls.append(wall)

        # Sprites
        number_of_sprites = struct.unpack('<h', file.read(2))[0]
        for _ in range(number_of_sprites):
            sprite = Sprite.read(file)
            map.sprites.append(sprite)

        return map

    @staticmethod
    def _write_file(file, map):
        header_data = struct.pack(header_format,
                                  map.version,
                                  map.position_x,
                                  map.position_y,
                                  map.position_z,
                                  map.angle,
                                  map.current_sector_number)

        file.write(header_data)

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

    def save(self, file):
        """Writes Map data to file

        Args:
            file: Either the path to the file, or a file-like object, or bytes.

        Raises:
            RuntimeError: If the file argument is not a file-like object.
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
                "Map.save() requires 'file' to be a path, a file-like object, "
                "or bytes")

        Map._write_file(file, self)

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
                Map._write_file(self.fp, self)
                self.fp.truncate()

            file_object = self.fp
            self.fp = None
            file_object.close()
