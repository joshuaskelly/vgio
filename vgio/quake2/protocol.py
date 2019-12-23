"""This module provides file I/O for Quake 2 network communication.

References:
    Quake Source
    - id Software
    - https://github.com/id-Software/Quake-2

    The Unofficial DM2 Format Description
    - Uwe Girlich, et al.
    - https://www.quakewiki.net/archives/demospecs/dm2/dm2.pdf
"""

import struct
import io


class _IO:
    """Simple namespace for protocol IO"""

    @staticmethod
    def _read(fmt, file):
        return struct.unpack(fmt, file.read(struct.calcsize(fmt)))[0]

    class read:
        """Read IO namespace"""

        @staticmethod
        def char(file):
            return int(_IO._read('<b', file))

        @staticmethod
        def byte(file):
            return int(_IO._read('<B', file))

        @staticmethod
        def short(file):
            return int(_IO._read('<h', file))

        @staticmethod
        def long(file):
            return int(_IO._read('<l', file))

        @staticmethod
        def float(file):
            return float(_IO._read('<f', file))

        @staticmethod
        def coord(file):
            return _IO.read.short(file) * 0.125

        @staticmethod
        def position(file):
            return _IO.read.coord(file), _IO.read.coord(file), _IO.read.coord(file)

        @staticmethod
        def direction(file):
            return _IO.read.byte(file)

        @staticmethod
        def angle(file):
            return _IO.read.char(file) * 360 / 256

        @staticmethod
        def angles(file):
            return _IO.read.angle(file), _IO.read.angle(file), _IO.read.angle(file)

        @staticmethod
        def string(file, terminal_byte=b'\x00'):
            string = b''
            char = _IO._read('<s', file)

            while char != terminal_byte:
                string += char
                char = _IO._read('<s', file)

            return string.decode('ascii')

    @staticmethod
    def _write(fmt, file, value):
        data = struct.pack(fmt, value)
        file.write(data)

    class write:
        """Write IO namespace"""

        @staticmethod
        def char(file, value):
            _IO._write('<b', file, int(value))

        @staticmethod
        def byte(file, value):
            _IO._write('<B', file, int(value))

        @staticmethod
        def short(file, value):
            _IO._write('<h', file, int(value))

        @staticmethod
        def long(file, value):
            _IO._write('<l', file, int(value))

        @staticmethod
        def float(file, value):
            _IO._write('<f', file, float(value))

        @staticmethod
        def coord(file, value):
            _IO.write.short(file, value / 0.125)

        @staticmethod
        def position(file, values):
            _IO.write.coord(file, values[0]), _IO.write.coord(file, values[1]), _IO.write.coord(file, values[2])

        @staticmethod
        def direction(file, value):
            _IO.write.byte(file, value)

        @staticmethod
        def angle(file, value):
           _IO.write.char(file, int(value * 256 / 360))

        @staticmethod
        def angles(file, values):
            _IO.write.angle(file, values[0]), _IO.write.angle(file, values[1]), _IO.write.angle(file, values[2])

        @staticmethod
        def string(file, value, terminal_byte=b'\x00'):
            value = value[:2048]
            size = len(value)
            format = '<%is' % (size + 1)
            v = value.encode('ascii') + terminal_byte
            data = struct.pack(format, v)
            file.write(data)


SVC_BAD = 0
SVC_MUZZLEFLASH = 1
SVC_MUZZLEFLASH2 = 2
SVC_TEMP_ENTITY = 3
SVC_LAYOUT = 4
SVC_INVENTORY = 5
SVC_NOP = 6
SVC_DISCONNECT = 7
SVC_RECONNECT = 8
SVC_SOUND = 9
SVC_PRINT = 10
SVC_STUFFTEXT = 11
SVC_SERVERDATA = 12
SVC_CONFIGSTRING = 13
SVC_SPAWNBASELINE = 14
SVC_CENTERPRINT = 15
SVC_DOWNLOAD = 16
SVC_PLAYERINFO = 17
SVC_PACKETENTITIES = 18
SVC_DELTAPACKETENTITIES = 19
SVC_FRAME = 20


class Bad:
    """Class for representing a Bad message

    This is an error message and should not appear.
    """

    __slots__ = ()

    @classmethod
    def write(cls, file, bad=None):
        _IO.write.byte(file, SVC_BAD)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_BAD

        return Bad()


class MuzzleFlash:
    """Class for representing a MuzzleFlash message

    Muzzle flashes for player weapons.

    Attributes:
        entity: The entity number

        weapon: The weapon id
    """

    __slots__ = (
        'entity',
        'weapon'
    )

    def __init__(self,
                 entity,
                 weapon):

        self.entity = entity
        self.weapon = weapon

    @classmethod
    def write(cls, file, muzzle_flash):
        _IO.write.byte(file, SVC_MUZZLEFLASH)
        _IO.write.short(file, muzzle_flash.entity)
        _IO.write.byte(file, muzzle_flash.weapon)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_MUZZLEFLASH
        entity = _IO.read.short(file)
        weapon = _IO.read.byte(file)

        return MuzzleFlash(entity, weapon)


class MuzzleFlash2:
    """Class for representing a MuzzleFlash2 message

    Muzzle flashes for enemy weapons.

    Attributes:
        entity: The entity number

        flash_number: The flash number
    """

    __slots__ = (
        'entity',
        'flash_number'
    )

    def __init__(self,
                 entity,
                 flash_number):

        self.entity = entity
        self.flash_number = flash_number

    @classmethod
    def write(cls, file, muzzle_flash2):
        _IO.write.byte(file, SVC_MUZZLEFLASH2)
        _IO.write.short(file, muzzle_flash2.entity)
        _IO.write.byte(file, muzzle_flash2.flash_number)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_MUZZLEFLASH2
        entity = _IO.read.short(file)
        flash_number = _IO.read.byte(file)

        return MuzzleFlash2(entity, flash_number)


TE_GUNSHOT = 0
TE_BLOOD = 1
TE_BLASTER = 2
TE_RAILTRAIL = 3
TE_SHOTGUN = 4
TE_EXPLOSION1 = 5
TE_EXPLOSION2 = 6
TE_ROCKET_EXPLOSION = 7
TE_GRENADE_EXPLOSION = 8
TE_SPARKS = 9
TE_SPLASH = 10
TE_BUBBLETRAIL = 11
TE_SCREEN_SPARKS = 12
TE_SHIELD_SPARKS = 13
TE_BULLET_SPARKS = 14
TE_LASER_SPARKS = 15
TE_PARASITE_ATTACK = 16
TE_ROCKET_EXPLOSION_WATER = 17
TE_GRENADE_EXPLOSION_WATER = 18
TE_MEDIC_CABLE_ATTACK = 19
TE_BFG_EXPLOSION = 20
TE_BFG_BIGEXPLOSION = 21
TE_BOSSTPORT = 22
TE_BFG_LASER = 23
TE_GRAPPLE_CABLE = 24
TE_WELDING_SPARKS = 25
TE_GREENBLOOD = 26
TE_BLUEHYPERBLASTER = 27
TE_PLASMA_EXPLOSION = 28
TE_TUNNEL_SPARKS = 29

particles = [
    TE_BLOOD,
    TE_GUNSHOT,
    TE_SPARKS,
    TE_BULLET_SPARKS,
    TE_SCREEN_SPARKS,
    TE_SHIELD_SPARKS,
    TE_SHOTGUN,
    TE_BLASTER,
    TE_GREENBLOOD
]

splashes = [
    TE_SPLASH,
    TE_LASER_SPARKS,
    TE_WELDING_SPARKS,
    TE_TUNNEL_SPARKS
]

trails = [
    TE_RAILTRAIL,
    TE_BUBBLETRAIL
]

explosions = [
    TE_EXPLOSION1,
    TE_EXPLOSION2,
    TE_GRENADE_EXPLOSION,
    TE_GRENADE_EXPLOSION_WATER,
    TE_PLASMA_EXPLOSION,
    TE_ROCKET_EXPLOSION,
    TE_ROCKET_EXPLOSION_WATER,
    TE_BFG_EXPLOSION,
    TE_BFG_BIGEXPLOSION,
    TE_BOSSTPORT
]


class TempEntity:
    """Class for representing a Temp_entity message

    Creates a temporary entity. The attributes of the message depend on the
    type of entity being created.

    Attributes:
        type: The type of the temporary entity.
    """

    def __init__(self, type, *args):
        self.type = type

        def verify_args(expected):
            if expected != len(args):
                raise TypeError('__init__ called with type={} takes {} positional arguments but {} were given'.format(type, expected, len(args)))

        if type in particles:
            verify_args(2)
            self.position = args[0]
            self.direction = args[1]

        elif type in splashes:
            verify_args(3)
            self.count = args[0]
            self.position = args[1]
            self.direction = args[2]

        elif type == TE_BLUEHYPERBLASTER:
            verify_args(2)
            self.position = args[0]
            self.direction = args[1]

        elif type in trails:
            verify_args(2)
            self.position = args[0]
            self.position2 = args[1]

        elif type in explosions:
            verify_args(1)
            self.position = args[0]

    @classmethod
    def write(cls, file, temp_entity):
        _IO.write.byte(file, SVC_TEMP_ENTITY)

        type = temp_entity.type
        _IO.write.byte(file, type)

        if type in particles:
            _IO.write.position(file, temp_entity.position)
            _IO.write.direction(file, temp_entity.direction)

        elif type in splashes:
            _IO.write.byte(file, temp_entity.count)
            _IO.write.position(file, temp_entity.position)
            _IO.write.direction(file, temp_entity.direction)

        elif type == TE_BLUEHYPERBLASTER:
            _IO.write.position(file, temp_entity.position)
            _IO.write.position(file, temp_entity.direction)

        elif type in trails:
            _IO.write.position(file, temp_entity.position)
            _IO.write.position(file, temp_entity.position2)

        elif type in explosions:
            _IO.write.position(file, temp_entity.position)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_TEMP_ENTITY

        type = _IO.read.byte(file)

        if type in particles:
            position = _IO.read.position(file)
            direction = _IO.read.direction(file)

            return TempEntity(type, position, direction)

        elif type in splashes:
            count = _IO.read.byte(file)
            position = _IO.read.position(file)
            direction = _IO.read.direction(file)

            return TempEntity(type, count, position, direction)

        elif type == TE_BLUEHYPERBLASTER:
            position = _IO.read.position(file)
            direction = _IO.read.position(file)

            return TempEntity(type, position, direction)

        elif type in trails:
            position = _IO.read.position(file)
            position2 = _IO.read.position(file)

            return TempEntity(type, position, position2)

        elif type in explosions:
            position = _IO.read.position(file)

            return TempEntity(type, position)

        return TempEntity(type)


class Layout:
    """Class for representing a Layout message

    Updates the player's field computer via a simple scripting language.

    Attributes:
        text: Script source as plain text
    """

    __slots__ = (
        'text'
    )

    def __init__(self,
                 text):

        self.text = text

    @classmethod
    def write(cls, file, layout):
        _IO.write.byte(file, SVC_LAYOUT)
        _IO.write.string(file, layout.text)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_LAYOUT
        text = _IO.read.string(file)

        return Layout(text)


class Inventory:
    """Class for representing a Inventory message

    Attributes:
        inventory: A sequence of exactly 256 integers representing the player's
            current inventory item counts.
    """

    __slots__ = (
        'inventory'
    )

    def __init__(self,
                 inventory):

        assert len(inventory) == 256
        self.inventory = inventory

    @classmethod
    def write(cls, file, inventory):
        _IO.write.byte(file, SVC_INVENTORY)

        for index in range(256):
            _IO.write.short(file, inventory.inventory[index])

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_INVENTORY
        inventory = [_IO.read.short(file) for _ in range(256)]

        return Inventory(inventory)


class Nop:
    """Class for representing a Nop message"""

    __slots__ = ()

    @classmethod
    def write(cls, file, nop=None):
        _IO.write.byte(file, SVC_NOP)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_NOP
        return Nop()


class Disconnect:
    """Class for representing a Disconnect message"""

    __slots__ = ()

    @classmethod
    def write(cls, file, disconnect=None):
        _IO.write.byte(file, SVC_DISCONNECT)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_DISCONNECT
        return Disconnect()


class Reconnect:
    """Class for representing a Reconnect message"""

    __slots__ = ()

    @classmethod
    def write(cls, file, reconnect=None):
        _IO.write.byte(file, SVC_RECONNECT)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_RECONNECT
        return Reconnect()


SND_VOLUME = 1 << 0
SND_ATTENUATION = 1 << 1
SND_POS = 1 << 2
SND_ENT = 1 << 3
SND_OFFSET = 1 << 4


class Sound:
    """Class for representing a Sound message

    Attributes:
        flags: A bit field indicating what data is sent.

        sound_number: The sound number

        volume: The sound volume

        attenuation: The sound attenuation

        offset: The offset between the frame start and sound start

        channel: The sound channel, maximum of eight.

        entity: The entity that owns the sound

        position: The position of the sound

    """

    __slots__ = (
        'flags',
        'sound_number',
        'volume',
        'attenuation',
        'offset',
        'channel',
        'entity',
        'position'
    )

    def __init__(self,
                 flags,
                 sound_number,
                 volume=1.0,
                 attenuation=1,
                 offset=0,
                 channel=0,
                 entity=0,
                 position=None):

        self.flags = flags
        self.sound_number = sound_number
        self.volume = volume
        self.attenuation = attenuation
        self.offset = offset
        self.channel = channel
        self.entity = entity
        self.position = position

    @classmethod
    def write(cls, file, sound):
        _IO.write.byte(file, SVC_SOUND)
        _IO.write.byte(file, sound.flags)
        _IO.write.byte(file, sound.sound_number)

        flags = sound.flags

        if flags & SND_VOLUME:
            _IO.write.byte(file, sound.volume * 255)

        if flags & SND_ATTENUATION:
            _IO.write.byte(file, sound.attenuation * 64)

        if flags & SND_OFFSET:
            _IO.write.byte(file, sound.offset * 1000)

        if flags & SND_ENT:
            value = sound.entity << 3 | sound.channel
            _IO.write.short(file, value)

        if flags & SND_POS:
            _IO.write.position(file, sound.position)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_SOUND
        flags = _IO.read.byte(file)
        sound_number = _IO.read.byte(file)
        volume = 1.0
        attenuation = 1.0
        offset = 0
        entity = 0
        channel = 0
        position = None

        if flags & SND_VOLUME:
            volume = _IO.read.byte(file) / 255

        if flags & SND_ATTENUATION:
            attenuation = _IO.read.byte(file) / 64

        if flags & SND_OFFSET:
            offset = _IO.read.byte(file) / 1000

        if flags & SND_ENT:
            channel = _IO.read.short(file)
            entity = channel >> 3
            channel &= 7

        if flags & SND_POS:
            position = _IO.read.position(file)

        return Sound(flags,
                     sound_number,
                     volume,
                     attenuation,
                     offset,
                     channel,
                     entity,
                     position)


class Print:
    """Class for representing a Print message

    Attributes:
        level: Priority level of print

        text: The print text
    """

    __slots__ = (
        'level',
        'text'
    )

    def __init__(self,
                 level,
                 text):

        self.level = level
        self.text = text

    @classmethod
    def write(cls, file, print):
        _IO.write.byte(file, SVC_PRINT)
        _IO.write.byte(file, print.level)
        _IO.write.string(file, print.text)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_PRINT
        level = _IO.read.byte(file)
        text = _IO.read.string(file)

        return Print(level, text)


class StuffText:
    """Class for representing a StuffText message

    Attributes:
        text: The text sent to the client console.
    """

    __slots__ = (
        'text'
    )

    def __init__(self,
                 text):

        self.text = text

    @classmethod
    def write(cls, file, stuff_text):
        _IO.write.byte(file, SVC_STUFFTEXT)
        _IO.write.string(file, stuff_text.text)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_STUFFTEXT
        text = _IO.read.string(file)

        return StuffText(text)


class ServerData:
    """Class for representing a ServerData message

    Attributes:
        protocol_version: Protocol version of the server.

        server_count: Server identification.

        attract_loop: The demo type. A value of 0 indicates over wire network
            data.

        game_directory: The game directory. The default is the empty string
            which indicates 'baseq2'

        player_number: The player id.

        map_name: The name of the level.

    """

    __slots__ = (
        'protocol_version',
        'server_count',
        'attract_loop',
        'game_directory',
        'player_number',
        'map_name'
    )

    def __init__(self,
                 protocol_version,
                 server_count,
                 attract_loop,
                 game_directory,
                 player_number,
                 map_name):

        self.protocol_version = protocol_version
        self.server_count = server_count
        self.attract_loop = attract_loop
        self.game_directory = game_directory
        self.player_number = player_number
        self.map_name = map_name

    @classmethod
    def write(cls, file, server_data):
        _IO.write.byte(file, SVC_SERVERDATA)
        _IO.write.long(file, server_data.protocol_version)
        _IO.write.long(file, server_data.server_count)
        _IO.write.byte(file, server_data.attract_loop)
        _IO.write.string(file, server_data.game_directory)
        _IO.write.short(file, server_data.player_number)
        _IO.write.string(file, server_data.map_name)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_SERVERDATA
        protocol_version = _IO.read.long(file)
        server_count = _IO.read.long(file)
        attract_loop = _IO.read.byte(file)
        game_directory = _IO.read.string(file)
        player_number = _IO.read.short(file)
        map_name = _IO.read.string(file)

        return ServerData(protocol_version,
                          server_count,
                          attract_loop,
                          game_directory,
                          player_number,
                          map_name)


class ConfigString:
    """Class for representing a ConfigString message"""

    __slots__ = (
        'index',
        'text'
    )

    def __init__(self,
                 index,
                 text):
        self.index = index
        self.text = text

    @classmethod
    def write(cls, file, config_string):
        _IO.write.byte(file, SVC_CONFIGSTRING)
        _IO.write.short(file, config_string.index)
        _IO.write.string(file, config_string.text)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_CONFIGSTRING
        index = _IO.read.short(file)
        text = _IO.read.string(file)

        return ConfigString(index, text)


# Spawn Baseline bit mask
U_ORIGIN1 = 1 << 0
U_ORIGIN2 = 1 << 1
U_ANGLE2 = 1 << 2
U_ANGLE3 = 1 << 3
U_FRAME8 = 1 << 4
U_EVENT = 1 << 5
U_REMOVE = 1 << 6
U_MOREBITS1 = 1 << 7

U_NUMBER16 = 1 << 8
U_ORIGIN3 = 1 << 9
U_ANGLE1 = 1 << 10
U_MODEL = 1 << 11
U_RENDERFX8 = 1 << 12
U_EFFECTS8 = 1 << 14
U_MOREBITS2 = 1 << 15

U_SKIN8 = 1 << 16
U_FRAME16 = 1 << 17
U_RENDERFX16 = 1 << 18
U_EFFECTS16 = 1 << 19
U_MODEL2 = 1 << 20
U_MODEL3 = 1 << 21
U_MODEL4 = 1 << 22
U_MOREBITS3 = 1 << 23

U_OLDORIGIN = 1 << 24
U_SKIN16 = 1 << 25
U_SOUND = 1 << 26
U_SOLID = 1 << 27

MOREBITS1_MASK = 0b00000000000000001111111100000000
MOREBITS2_MASK = 0b00000000111111110000000000000000
MOREBITS3_MASK = 0b11111111000000000000000000000000


class SpawnBaseline:
    """Class for representing a SpawnBaseline message

    https://github.com/id-Software/Quake-2/blob/372afde46e7defc9dd2d719a1732b8ace1fa096e/client/cl_parse.c#L356
    """

    __slots__ = (
        'bit_mask',
        'number',
        'model_index',
        'model_index_2',
        'model_index_3',
        'model_index_4',
        'frame',
        'skin_number',
        'effects',
        'render_fx',
        'origin',
        'angles',
        'old_origin',
        'sound',
        'event',
        'solid'
    )

    def __init__(self,
                 number=0,
                 model_index=0,
                 model_index_2=0,
                 model_index_3=0,
                 model_index_4=0,
                 frame=0,
                 skin_number=0,
                 effects=0,
                 render_fx=0,
                 origin_x=0,
                 origin_y=0,
                 origin_z=0,
                 angles_x=0,
                 angles_y=0,
                 angles_z=0,
                 old_origin_x=0,
                 old_origin_y=0,
                 old_origin_z=0,
                 sound=0,
                 event=0,
                 solid=0):

        self.bit_mask = 0
        self.number = number

        if number > 255:
            self.bit_mask |= U_NUMBER16

        self.model_index = model_index
        if model_index:
            self.bit_mask |= U_MOREBITS1
            self.bit_mask |= U_MODEL

        self.model_index_2 = model_index_2
        if model_index_2:
            self.bit_mask |= U_MOREBITS2
            self.bit_mask |= U_MODEL2

        self.model_index_3 = model_index_3
        if model_index_3:
            self.bit_mask |= U_MOREBITS2
            self.bit_mask |= U_MODEL3

        self.model_index_4 = model_index_4
        if model_index_4:
            self.bit_mask |= U_MOREBITS2
            self.bit_mask |= U_MODEL4

        self.frame = max(frame, 0)

        if frame:
            if frame < 255:
                self.bit_mask |= U_FRAME8

            else:
                self.bit_mask |= U_FRAME16
                self.bit_mask |= U_MOREBITS2

        self.skin_number = max(skin_number, 0)

        if skin_number:
            if skin_number < 255:
                self.bit_mask |= U_SKIN8
                self.bit_mask |= U_MOREBITS2

            else:
                self.bit_mask |= U_SKIN16
                self.bit_mask |= U_MOREBITS3

        self.effects = max(effects, 0)

        if effects:
            if effects < 255:
                self.bit_mask |= U_EFFECTS8
                self.bit_mask |= U_MOREBITS1

            else:
                self.bit_mask |= U_EFFECTS16
                self.bit_mask |= U_MOREBITS2

        self.render_fx = max(render_fx, 0)

        if render_fx:
            if render_fx < 255:
                self.bit_mask |= U_RENDERFX8
                self.bit_mask |= U_MOREBITS1

            else:
                self.bit_mask |= U_RENDERFX16
                self.bit_mask |= U_MOREBITS2

        self.origin = origin_x, origin_y, origin_z

        if origin_x:
            self.bit_mask |= U_ORIGIN1

        if origin_y:
            self.bit_mask |= U_ORIGIN2

        if origin_z:
            self.bit_mask |= U_ORIGIN3
            self.bit_mask |= U_MOREBITS1

        self.angles = angles_x, angles_y, angles_z

        if angles_x:
            self.bit_mask |= U_ANGLE1
            self.bit_mask |= U_MOREBITS1

        if angles_y:
            self.bit_mask |= U_ANGLE2

        if angles_z:
            self.bit_mask |= U_ANGLE3

        self.old_origin = old_origin_x, old_origin_y, old_origin_z

        if old_origin_x or old_origin_y or old_origin_z:
            self.bit_mask |= U_OLDORIGIN
            self.bit_mask |= U_MOREBITS3

        self.sound = sound

        if sound:
            self.bit_mask |= U_SOUND
            self.bit_mask |= U_MOREBITS3

        self.event = event

        if event:
            self.bit_mask |= U_EVENT

        self.solid = solid

        if solid:
            self.bit_mask |= U_SOLID
            self.bit_mask |= U_MOREBITS3

        if self.bit_mask & U_MOREBITS3:
            self.bit_mask |= U_MOREBITS2

        if self.bit_mask & U_MOREBITS2:
            self.bit_mask |= U_MOREBITS1

    @classmethod
    def write(cls, file, spawn_baseline):
        _IO.write.byte(file, SVC_SPAWNBASELINE)
        mask = spawn_baseline.bit_mask & 255
        _IO.write.byte(file, mask)

        if spawn_baseline.bit_mask & U_MOREBITS1:
            mask = spawn_baseline.bit_mask & MOREBITS1_MASK
            _IO.write.byte(file, mask >> 8)

        if spawn_baseline.bit_mask & U_MOREBITS2:
            mask = spawn_baseline.bit_mask & MOREBITS2_MASK
            _IO.write.byte(file, mask >> 16)

        if spawn_baseline.bit_mask & U_MOREBITS3:
            mask = spawn_baseline.bit_mask & MOREBITS3_MASK
            _IO.write.byte(file, mask >> 24)

        def is_set(mask):
            return spawn_baseline.bit_mask & mask

        if is_set(U_NUMBER16):
            _IO.write.short(file, spawn_baseline.number)

        else:
            _IO.write.byte(file, spawn_baseline.number)

        if is_set(U_MODEL):
            _IO.write.byte(file, spawn_baseline.model_index)

        if is_set(U_MODEL2):
            _IO.write.byte(file, spawn_baseline.model_index_2)

        if is_set(U_MODEL3):
            _IO.write.byte(file, spawn_baseline.model_index_3)

        if is_set(U_MODEL4):
            _IO.write.byte(file, spawn_baseline.model_index_4)

        if is_set(U_FRAME8):
            _IO.write.byte(file, spawn_baseline.frame)

        if is_set(U_FRAME16):
            _IO.write.short(file, spawn_baseline.frame)

        if is_set(U_SKIN8) and is_set(U_SKIN16):
            _IO.write.long(file, spawn_baseline.skin_number)

        elif is_set(U_SKIN8):
            _IO.write.byte(file, spawn_baseline.skin_number)

        elif is_set(U_SKIN16):
            _IO.write.short(file, spawn_baseline.skin_number)

        if spawn_baseline.bit_mask & (U_EFFECTS8 | U_EFFECTS16) == (U_EFFECTS8 | U_EFFECTS16):
            _IO.write.long(file, spawn_baseline.effects)

        elif is_set(U_EFFECTS8):
            _IO.write.byte(file, spawn_baseline.effects)

        elif is_set(U_EFFECTS16):
            _IO.write.short(file, spawn_baseline.effects)

        if spawn_baseline.bit_mask & (U_RENDERFX8 | U_RENDERFX16) == (U_RENDERFX8 | U_RENDERFX16):
            _IO.write.long(file, spawn_baseline.render_fx)

        elif is_set(U_RENDERFX8):
            _IO.write.byte(file, spawn_baseline.render_fx)

        elif is_set(U_RENDERFX16):
            _IO.write.short(file, spawn_baseline.render_fx)

        if is_set(U_ORIGIN1):
            _IO.write.coord(file, spawn_baseline.origin[0])

        if is_set(U_ORIGIN2):
            _IO.write.coord(file, spawn_baseline.origin[1])

        if is_set(U_ORIGIN3):
            _IO.write.coord(file, spawn_baseline.origin[2])

        if is_set(U_ANGLE1):
            _IO.write.angle(file, spawn_baseline.angles[0])

        if is_set(U_ANGLE2):
            _IO.write.angle(file, spawn_baseline.angles[1])

        if is_set(U_ANGLE3):
            _IO.write.angle(file, spawn_baseline.angles[2])

        if is_set(U_OLDORIGIN):
            _IO.write.position(file, spawn_baseline.old_origin)

        if is_set(U_SOUND):
            _IO.write.byte(file, spawn_baseline.sound)

        if is_set(U_EVENT):
            _IO.write.byte(file, spawn_baseline.event)

        if is_set(U_SOLID):
            _IO.write.short(file, spawn_baseline.solid)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_SPAWNBASELINE
        spawn_baseline = SpawnBaseline()
        spawn_baseline.bit_mask = _IO.read.byte(file)

        def is_set(mask):
            return spawn_baseline.bit_mask & mask

        if is_set(U_MOREBITS1):
            b = _IO.read.byte(file)
            spawn_baseline.bit_mask |= b << 8

        if is_set(U_MOREBITS2):
            b = _IO.read.byte(file)
            spawn_baseline.bit_mask |= b << 16

        if is_set(U_MOREBITS3):
            b = _IO.read.byte(file)
            spawn_baseline.bit_mask |= b << 24

        if is_set(U_NUMBER16):
            spawn_baseline.number = _IO.read.short(file)

        else:
            spawn_baseline.number = _IO.read.byte(file)

        if is_set(U_MODEL):
            spawn_baseline.model_index = _IO.read.byte(file)

        if is_set(U_MODEL2):
            spawn_baseline.model_index_2 = _IO.read.byte(file)

        if is_set(U_MODEL3):
            spawn_baseline.model_index_3 = _IO.read.byte(file)

        if is_set(U_MODEL4):
            spawn_baseline.model_index_4 = _IO.read.byte(file)

        if is_set(U_FRAME8):
            spawn_baseline.frame = _IO.read.byte(file)

        if is_set(U_FRAME16):
            spawn_baseline.frame = _IO.read.short(file)

        if is_set(U_SKIN8) and is_set(U_SKIN16):
            spawn_baseline.skin_number = _IO.read.long(file)

        elif is_set(U_SKIN8):
            spawn_baseline.skin_number = _IO.read.byte(file)

        elif is_set(U_SKIN16):
            spawn_baseline.skin_number = _IO.read.short(file)

        if spawn_baseline.bit_mask & (U_EFFECTS8 | U_EFFECTS16) == (U_EFFECTS8 | U_EFFECTS16):
            spawn_baseline.effects = _IO.read.long(file)

        elif is_set(U_EFFECTS8):
            spawn_baseline.effects = _IO.read.byte(file)

        elif is_set(U_EFFECTS16):
            spawn_baseline.effects = _IO.read.short(file)

        if spawn_baseline.bit_mask & (U_RENDERFX8 | U_RENDERFX16) == (U_RENDERFX8 | U_RENDERFX16):
            spawn_baseline.render_fx = _IO.read.long(file)

        elif is_set(U_RENDERFX8):
            spawn_baseline.render_fx = _IO.read.byte(file)

        elif is_set(U_RENDERFX16):
            spawn_baseline.render_fx = _IO.read.short(file)

        if is_set(U_ORIGIN1):
            _, y, z = spawn_baseline.origin
            spawn_baseline.origin = _IO.read.coord(file), y, z

        if is_set(U_ORIGIN2):
            x, _, z = spawn_baseline.origin
            spawn_baseline.origin = x, _IO.read.coord(file), z

        if is_set(U_ORIGIN3):
            x, y, _ = spawn_baseline.origin
            spawn_baseline.origin = x, y, _IO.read.coord(file)

        if is_set(U_ANGLE1):
            _, y, z = spawn_baseline.angles
            spawn_baseline.angles = _IO.read.angle(file), y, z

        if is_set(U_ANGLE2):
            x, _, z = spawn_baseline.angles
            spawn_baseline.angles = x, _IO.read.angle(file), z

        if is_set(U_ANGLE3):
            x, y, _ = spawn_baseline.angles
            spawn_baseline.angles = x, y, _IO.read.angle(file)

        if is_set(U_OLDORIGIN):
            spawn_baseline.old_origin = _IO.read.position(file)

        if is_set(U_SOUND):
            spawn_baseline.sound = _IO.read.byte(file)

        if is_set(U_EVENT):
            spawn_baseline.event = _IO.read.byte(file)

        if is_set(U_SOLID):
            spawn_baseline.solid = _IO.read.short(file)

        return spawn_baseline


class CenterPrint:
    """Class for representing a Centerprint message"""

    __slots__ = (
        'text'
    )

    def __init__(self,
                 text=''):
        self.text = text

    @classmethod
    def write(cls, file, center_print):
        _IO.write.byte(file, SVC_CENTERPRINT)
        _IO.write.string(file, center_print.text)

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_CENTERPRINT
        center_print = CenterPrint()
        center_print.text = _IO.read.string(file)

        return center_print


class Download:
    """Class for representing a Download message

    https://github.com/id-Software/Quake-2/blob/372afde46e7defc9dd2d719a1732b8ace1fa096e/client/cl_parse.c#L195
    """

    __slots__ = ()

    @classmethod
    def write(cls, file, download):
        pass

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_DOWNLOAD
        return Download()


class PlayerInfo:
    """Class for representing a PlayerInfo message"""

    __slots__ = ()

    @classmethod
    def write(cls, file, player_info):
        pass

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_PLAYERINFO
        return PlayerInfo()


class PacketEntities:
    """Class for representing a PacketEntities message"""

    __slots__ = ()

    @classmethod
    def write(cls, file, packet_entities):
        pass

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_PACKETENTITIES
        return PacketEntities()


class DeltaPacketEntities:
    """Class for representing a DeltaPacketEntities message"""

    __slots__ = ()

    @classmethod
    def write(cls, file, delta_packet_entities):
        pass

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_DELTAPACKETENTITIES
        return DeltaPacketEntities()


class Frame:
    """Class for representing a Frame message

    Attributes:
        server_frame:

        delta_frame:

        areas:
    """

    __slots__ = (
        'server_frame',
        'delta_frame',
        'areas'
    )

    def __init__(self,
                 server_frame=0,
                 delta_frame=0,
                 areas=()):

        self.server_frame = server_frame
        self.delta_frame = delta_frame
        self.areas = areas

    @classmethod
    def write(cls, file, frame):
        _IO.write.byte(file, SVC_FRAME)
        _IO.write.long(file, frame.server_frame)
        _IO.write.long(file, frame.delta_frame)
        _IO.write.byte(file, len(frame.areas))
        [_IO.write.byte(file, area) for area in frame.areas]

    @classmethod
    def read(cls, file):
        assert _IO.read.byte(file) == SVC_FRAME
        frame = Frame()

        frame.server_frame = _IO.read.long(file)
        frame.delta_frame = _IO.read.long(file)

        # If protocol version != 26
        if False:
            _IO.read.byte(file)

        count = _IO.read.byte(file)
        frame.areas = [_IO.read.byte(file) for _ in range(count)]

        return frame


_messages = [
    Bad,
    MuzzleFlash,
    MuzzleFlash2,
    TempEntity,
    Layout,
    Inventory,
    Nop,
    Disconnect,
    Reconnect,
    Sound,
    Print,
    StuffText,
    ServerData,
    ConfigString,
    SpawnBaseline,
    CenterPrint,
    Download,
    PlayerInfo,
    PacketEntities,
    DeltaPacketEntities,
    Frame
]


class MessageBlock:
    """Class for representing a message block

    Attributes:
        messages: A sequence of messages.
    """

    __slots__ = (
        'messages'
    )

    def __init__(self):
        self.messages = []

    @staticmethod
    def write(file, message_block):
        start_of_block = file.tell()
        _IO.write.long(file, 0)
        start_of_messages = file.tell()

        for message in message_block.messages:
            message.__class__.write(file, message)

        end_of_messages = file.tell()
        block_size = end_of_messages - start_of_messages

        file.seek(start_of_block)
        _IO.write.long(file, block_size)
        file.seek(end_of_messages)

    @staticmethod
    def read(file):
        message_block = MessageBlock()
        block_size = _IO.read.long(file)
        message_block_data = file.read(block_size)

        buff = io.BufferedReader(io.BytesIO(message_block_data))
        message_id = buff.peek(1)[:1]

        while message_id != b'':
            message_id = struct.unpack('<B', message_id)[0]
            message = _messages[message_id].read(buff)

            if message:
                message_block.messages.append(message)

            message_id = buff.peek(1)[:1]

        buff.close()

        return message_block
