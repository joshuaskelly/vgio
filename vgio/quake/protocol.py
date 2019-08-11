"""This module provides file I/O for the Quake network protocol.

References:
    Quake Source
    - id Software
    - https://github.com/id-Software/Quake

    The Unofficial DEM Format Description
    - Uwe Girlich, et al.
    - https://www.quakewiki.net/archives/demospecs/dem/dem.html
"""

import io
import struct


__all__ = ['Bad', 'Nop', 'Disconnect', 'UpdateStat', 'Version', 'SetView',
           'Sound', 'Time', 'Print', 'StuffText', 'SetAngle', 'ServerInfo',
           'LightStyle', 'UpdateName', 'UpdateFrags', 'ClientData',
           'StopSound', 'UpdateColors', 'Particle', 'Damage', 'SpawnStatic',
           'SpawnBinary', 'SpawnBaseline', 'TempEntity', 'SetPause',
           'SignOnNum', 'CenterPrint', 'KilledMonster', 'FoundSecret',
           'SpawnStaticSound', 'Intermission', 'Finale', 'CdTrack',
           'SellScreen', 'CutScene', 'UpdateEntity', 'MessageBlock']


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


class BadMessage(Exception):
    pass


SVC_BAD = 0
SVC_NOP = 1
SVC_DISCONNECT = 2
SVC_UPDATESTAT = 3
SVC_VERSION = 4
SVC_SETVIEW = 5
SVC_SOUND = 6
SVC_TIME = 7
SVC_PRINT = 8
SVC_STUFFTEXT = 9
SVC_SETANGLE = 10
SVC_SERVERINFO = 11
SVC_LIGHTSTYLE = 12
SVC_UPDATENAME = 13
SVC_UPDATEFRAGS = 14
SVC_CLIENTDATA = 15
SVC_STOPSOUND = 16
SVC_UPDATECOLORS = 17
SVC_PARTICLE = 18
SVC_DAMAGE = 19
SVC_SPAWNSTATIC = 20
SVC_SPAWNBINARY = 21
SVC_SPAWNBASELINE = 22
SVC_TEMP_ENTITY = 23
SVC_SETPAUSE = 24
SVC_SIGNONNUM = 25
SVC_CENTERPRINT = 26
SVC_KILLEDMONSTER = 27
SVC_FOUNDSECRET = 28
SVC_SPAWNSTATICSOUND = 29
SVC_INTERMISSION = 30
SVC_FINALE = 31
SVC_CDTRACK = 32
SVC_SELLSCREEN = 33
SVC_CUTSCENE = 34


class Bad:
    """Class for representing a Bad message

    This is an error message and should not appear.
    """

    __slots__ = ()

    @staticmethod
    def write(file, bad=None):
        _IO.write.byte(file, SVC_BAD)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_BAD
        return Bad()


class Nop:
    """Class for representing a Nop message"""

    __slots__ = ()

    @staticmethod
    def write(file, nop=None):
        _IO.write.byte(file, SVC_NOP)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_NOP
        return Nop()


class Disconnect:
    """Class for representing a Disconnect message

    Disconnect from the server and end the game. Typically this the last
    message of a demo.
    """

    __slots__ = ()

    @staticmethod
    def write(file, disconnect=None):
        _IO.write.byte(file, SVC_DISCONNECT)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_DISCONNECT
        return Disconnect()


class UpdateStat:
    """Class for representing UpdateStat messages

    Updates a player state value.

    Attributes:
        index: The index to update in the player state array.

        value: The new value to set.
    """

    __slots__ = (
        'index',
        'value'
    )

    def __init__(self):
        self.index = None
        self.value = None

    @staticmethod
    def write(file, update_stat):
        _IO.write.byte(file, SVC_UPDATESTAT)
        _IO.write.byte(file, update_stat.index)
        _IO.write.long(file, update_stat.value)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_UPDATESTAT
        update_stat = UpdateStat()
        update_stat.index = _IO.read.byte(file)
        update_stat.value = _IO.read.long(file)

        return update_stat


class Version:
    """Class for representing Version messages

    Attributes:
        protocol_version: Protocol version of the server. Quake uses 15.
    """

    __slots__ = (
        'protocol_version'
    )

    def __init__(self):
        self.protocol_version = None

    @staticmethod
    def write(file, version):
        _IO.write.byte(file, SVC_VERSION)
        _IO.write.long(file, version.protocol_version)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_VERSION
        version = Version()
        version.protocol_version = _IO.read.long(file)

        return version


class SetView:
    """Class for representing SetView messages

    Sets the camera position to the given entity.

    Attributes:
        entity: The entity number
    """

    __slots__ = (
        'entity'
    )

    def __init__(self):
        self.entity = None

    @staticmethod
    def write(file, set_view):
        _IO.write.byte(file, SVC_SETVIEW)
        _IO.write.short(file, set_view.entity)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SETVIEW
        set_view = SetView()
        set_view.entity = _IO.read.short(file)

        return set_view


SND_VOLUME = 0b0001
SND_ATTENUATION = 0b0010
SND_LOOPING = 0b0100


class Sound:
    """Class for representing Sound messages

    Plays a sound on a channel at a position.

    Attributes:
        entity: The entity that caused the sound.

        bit_mask: A bit field indicating what data is sent.

        volume: Optional. The sound volume or None.

        attenuation: Optional. The sound attenuation or None.

        channel: The sound channel, maximum of eight.

        sound_number: The number of the sound in the sound table.

        origin: The position of the sound.
    """

    __slots__ = (
        'entity',
        'bit_mask',
        'volume',
        'attenuation',
        'channel',
        'sound_number',
        'origin'
    )

    def __init__(self):
        self.entity = None
        self.bit_mask = 0b0000
        self.volume = 255
        self.attenuation = 1.0
        self.channel = None
        self.sound_number = None
        self.origin = None, None, None

    @staticmethod
    def write(file, sound):
        _IO.write.byte(file, SVC_SOUND)
        _IO.write.byte(file, sound.bit_mask)

        if sound.bit_mask & SND_VOLUME:
            _IO.write.byte(file, sound.volume)

        if sound.bit_mask & SND_ATTENUATION:
            _IO.write.byte(file, sound.attenuation * 64)

        channel = sound.entity << 3
        channel |= sound.channel

        _IO.write.short(file, channel)
        _IO.write.byte(file, sound.sound_number)
        _IO.write.position(file, sound.origin)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SOUND
        sound = Sound()
        sound.bit_mask = _IO.read.byte(file)

        if sound.bit_mask & SND_VOLUME:
            sound.volume = _IO.read.byte(file)

        if sound.bit_mask & SND_ATTENUATION:
            sound.attenuation = _IO.read.byte(file) / 64

        sound.channel = _IO.read.short(file)
        sound.entity = sound.channel >> 3
        sound.channel &= 7
        sound.sound_number = _IO.read.byte(file)
        sound.origin = _IO.read.position(file)

        return sound


class Time:
    """Class for representing Time messages

    A time stamp that should appear in each block of messages.

    Attributes:
        time: The amount of elapsed time(in seconds) since the start of the
            game.
    """

    __slots__ = (
        'time'
    )

    def __init__(self):
        self.time = None

    @staticmethod
    def write(file, time):
        _IO.write.byte(file, SVC_TIME)
        _IO.write.float(file, time.time)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_TIME
        time = Time()
        time.time = _IO.read.float(file)

        return time


class Print:
    """Class for representing Print messages

    Prints text in the top left corner of the screen and console.

    Attributes:
        text: The text to be shown.
    """

    __slots__ = (
        'text'
    )

    def __init__(self):
        self.text = None

    @staticmethod
    def write(file, _print):
        _IO.write.byte(file, SVC_PRINT)
        _IO.write.string(file, _print.text)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_PRINT
        _print = Print()
        _print.text = _IO.read.string(file)

        return _print


class StuffText:
    """Class for representing StuffText messages

    Text sent to the client console and ran.

    Attributes:
        text: The text to send to the client console.

            Note: This string is '\n' terminated.
    """

    __slots__ = (
        'text'
    )

    def __init__(self):
        self.text = None

    @staticmethod
    def write(file, stuff_text):
        _IO.write.byte(file, SVC_STUFFTEXT)
        _IO.write.string(file, stuff_text.text, b'\n')

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_STUFFTEXT
        stuff_text = StuffText()
        stuff_text.text = _IO.read.string(file, b'\n')

        return stuff_text


class SetAngle:
    """Class for representing SetAngle messages

    Sets the camera's orientation.

    Attributes:
        angles: The new angles for the camera.
    """

    __slots__ = (
        'angles'
    )

    def __init__(self):
        self.angles = None

    @staticmethod
    def write(file, set_angle):
        _IO.write.byte(file, SVC_SETANGLE)
        _IO.write.angles(file, set_angle.angles)


    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SETANGLE
        set_angle = SetAngle()
        set_angle.angles = _IO.read.angles(file)

        return set_angle


class ServerInfo:
    """Class for representing ServerInfo messages

    Handles the loading of assets. Usually first message sent after a level
    change.

    Attributes:
        protocol_version: Protocol version of the server. Quake uses 15.

        max_clients: Number of clients.

        multi: Multiplayer flag. Set to 0 for single-player and 1 for
            multiplayer.

        map_name: The name of the level.

        models: The model table as as sequence of strings.

        sounds: The sound table as a sequence of strings.
    """
    __slots__ = (
        'protocol_version',
        'max_clients',
        'multi',
        'map_name',
        'models',
        'sounds'
    )

    def __init__(self):
        self.protocol_version = 15
        self.max_clients = 0
        self.multi = 0
        self.map_name = ''
        self.models = []
        self.sounds = []

    @staticmethod
    def write(file, server_data):
        _IO.write.byte(file, SVC_SERVERINFO)
        _IO.write.long(file, server_data.protocol_version)
        _IO.write.byte(file, server_data.max_clients)
        _IO.write.byte(file, server_data.multi)
        _IO.write.string(file, server_data.map_name)

        for model in server_data.models:
            _IO.write.string(file, model)

        _IO.write.byte(file, 0)

        for sound in server_data.sounds:
            _IO.write.string(file, sound)

        _IO.write.byte(file, 0)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SERVERINFO
        server_data = ServerInfo()
        server_data.protocol_version = _IO.read.long(file)
        server_data.max_clients = _IO.read.byte(file)
        server_data.multi = _IO.read.byte(file)
        server_data.map_name = _IO.read.string(file)

        model = _IO.read.string(file)
        while model:
            server_data.models.append(model)
            model = _IO.read.string(file)

        server_data.models = tuple(server_data.models)

        sound = _IO.read.string(file)
        while sound:
            server_data.sounds.append(sound)
            sound = _IO.read.string(file)

        server_data.sounds = tuple(server_data.sounds)

        return server_data


class LightStyle:
    """Class for representing a LightStyle message

    Defines the style of a light. Usually happens shortly after level change.

    Attributes:
        style: The light style number.

        string: A string of arbitrary length representing the brightness of
            the light. The brightness is mapped to the characters 'a' to 'z',
            with 'a' being black and 'z' being pure white.

            Example:
                # Flickering light
                light_style_message = LightStyle()
                light_style.style = 0
                light_style.string = 'aaazaazaaaaaz'
    """

    __slots__ = (
        'style',
        'string'
    )

    def __init__(self):
        self.style = None
        self.string = None

    @staticmethod
    def write(file, light_style):
        _IO.write.byte(file, SVC_LIGHTSTYLE)
        _IO.write.byte(file, light_style.style)
        _IO.write.string(file, light_style.string)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_LIGHTSTYLE
        light_style = LightStyle()
        light_style.style = _IO.read.byte(file)
        light_style.string = _IO.read.string(file)

        return light_style


class UpdateName:
    """Class for representing UpdateName messages

    Sets the player's name.

    Attributes:
        player: The player number to update.

        name: The new name as a string.
    """

    __slots__ = (
        'player',
        'name'
    )

    def __init__(self):
        self.player = None
        self.name = None

    @staticmethod
    def write(file, update_name):
        _IO.write.byte(file, SVC_UPDATENAME)
        _IO.write.byte(file, update_name.player)
        _IO.write.string(file, update_name.name)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_UPDATENAME
        update_name = UpdateName()
        update_name.player = _IO.read.byte(file)
        update_name.name = _IO.read.string(file)

        return update_name


class UpdateFrags:
    """Class for representing UpdateFrags messages

    Sets the player's frag count.

    Attributes:
        player: The player to update.

        frags: The new frag count.
    """
    __slots__ = (
        'player',
        'frags'
    )

    def __init__(self):
        self.player = None
        self.frags = None

    @staticmethod
    def write(file, update_frags):
        _IO.write.byte(file, SVC_UPDATEFRAGS)
        _IO.write.byte(file, update_frags.player)
        _IO.write.short(file, update_frags.frags)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_UPDATEFRAGS
        update_frags = UpdateFrags()
        update_frags.player = _IO.read.byte(file)
        update_frags.frags = _IO.read.short(file)

        return update_frags


# Client Data bit mask
SU_VIEWHEIGHT = 0b0000000000000001
SU_IDEALPITCH = 0b0000000000000010
SU_PUNCH1 = 0b0000000000000100
SU_PUNCH2 = 0b0000000000001000
SU_PUNCH3 = 0b0000000000010000
SU_VELOCITY1 = 0b0000000000100000
SU_VELOCITY2 = 0b0000000001000000
SU_VELOCITY3 = 0b0000000010000000
SU_ITEMS = 0b0000001000000000
SU_ONGROUND = 0b0000010000000000
SU_INWATER = 0b0000100000000000
SU_WEAPONFRAME = 0b0001000000000000
SU_ARMOR = 0b0010000000000000
SU_WEAPON = 0b0100000000000000


class ClientData:
    """Class for representing ClientData messages

    Server information about this client.

    Attributes:
        bit_mask: A bit field indicating what data is sent.

        view_height: Optional. The view offset from the origin along the z-axis.

        ideal_pitch: Optional. The calculated angle for looking up/down slopes.

        punch_angle: Optional. A triple representing camera shake.

        velocity: Optional. Player velocity.

        item_bit_mask: A bit field for player inventory.

        on_ground: Flag indicating if player is on the ground.

        in_water: Flag indicating if player is in a water volume.

        weapon_frame: Optional. The animation frame of the weapon.

        armor: Optional. The current armor value.

        weapon: Optional. The model number in the model table.

        health: The current health value.

        active_ammo: The amount count for the active weapon.

        ammo: The current ammo counts as a quadruple.

        active_weapon: The actively held weapon.
    """

    __slots__ = (
        'bit_mask',
        'view_height',
        'ideal_pitch',
        'punch_angle',
        'velocity',
        'item_bit_mask',
        'on_ground',
        'in_water',
        'weapon_frame',
        'armor',
        'weapon',
        'health',
        'active_ammo',
        'ammo',
        'active_weapon'

    )

    def __init__(self):
        self.bit_mask = 0b0000000000000000
        self.view_height = 22
        self.ideal_pitch = 0
        self.punch_angle = 0, 0, 0
        self.velocity = 0, 0, 0
        self.item_bit_mask = 0b0000
        self.on_ground = False
        self.in_water = False
        self.weapon_frame = 0
        self.armor = 0
        self.weapon = None
        self.health = None
        self.active_ammo = None
        self.ammo = None
        self.active_weapon = None

    @staticmethod
    def write(file, client_data):
        _IO.write.byte(file, SVC_CLIENTDATA)

        if client_data.on_ground:
            client_data.bit_mask |= SU_ONGROUND

        if client_data.in_water:
            client_data.bit_mask |= SU_INWATER

        _IO.write.short(file, client_data.bit_mask)

        if client_data.bit_mask & SU_VIEWHEIGHT:
            _IO.write.char(file, client_data.view_height)

        if client_data.bit_mask & SU_IDEALPITCH:
            _IO.write.char(file, client_data.ideal_pitch)

        if client_data.bit_mask & SU_PUNCH1:
            pa = client_data.punch_angle
            _IO.write.angle(file, pa[0])

        if client_data.bit_mask & SU_VELOCITY1:
            ve = client_data.velocity
            _IO.write.char(file, ve[0] // 16)

        if client_data.bit_mask & SU_PUNCH2:
            pa = client_data.punch_angle
            _IO.write.angle(file, pa[1])

        if client_data.bit_mask & SU_VELOCITY2:
            ve = client_data.velocity
            _IO.write.char(file, ve[1] // 16)

        if client_data.bit_mask & SU_PUNCH3:
            pa = client_data.punch_angle
            _IO.write.angle(file, pa[2])

        if client_data.bit_mask & SU_VELOCITY3:
            ve = client_data.velocity
            _IO.write.char(file, ve[2] // 16)

        _IO.write.long(file, client_data.item_bit_mask)

        if client_data.bit_mask & SU_WEAPONFRAME:
            _IO.write.byte(file, client_data.weapon_frame)

        if client_data.bit_mask & SU_ARMOR:
            _IO.write.byte(file, client_data.armor)

        if client_data.bit_mask & SU_WEAPON:
            _IO.write.byte(file, client_data.weapon)

        _IO.write.short(file, client_data.health)
        _IO.write.byte(file, client_data.active_ammo)
        _IO.write.byte(file, client_data.ammo[0])
        _IO.write.byte(file, client_data.ammo[1])
        _IO.write.byte(file, client_data.ammo[2])
        _IO.write.byte(file, client_data.ammo[3])
        _IO.write.byte(file, client_data.active_weapon)


    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_CLIENTDATA
        client_data = ClientData()
        client_data.bit_mask = _IO.read.short(file)
        client_data.on_ground = client_data.bit_mask & SU_ONGROUND != 0
        client_data.in_water = client_data.bit_mask & SU_INWATER != 0

        if client_data.bit_mask & SU_VIEWHEIGHT:
            client_data.view_height = _IO.read.char(file)

        if client_data.bit_mask & SU_IDEALPITCH:
            client_data.ideal_pitch = _IO.read.char(file)

        if client_data.bit_mask & SU_PUNCH1:
            pa = client_data.punch_angle
            client_data.punch_angle = _IO.read.angle(file), pa[1], pa[2]

        if client_data.bit_mask & SU_VELOCITY1:
            ve = client_data.velocity
            client_data.velocity = _IO.read.char(file) * 16, ve[1], ve[2]

        if client_data.bit_mask & SU_PUNCH2:
            pa = client_data.punch_angle
            client_data.punch_angle = pa[0], _IO.read.angle(file), pa[2]

        if client_data.bit_mask & SU_VELOCITY2:
            ve = client_data.velocity
            client_data.velocity = ve[0], _IO.read.char(file) * 16, ve[2]

        if client_data.bit_mask & SU_PUNCH3:
            pa = client_data.punch_angle
            client_data.punch_angle = pa[0], pa[1], _IO.read.angle(file)

        if client_data.bit_mask & SU_VELOCITY3:
            ve = client_data.velocity
            client_data.velocity = ve[0], ve[1], _IO.read.char(file) * 16

        client_data.item_bit_mask = _IO.read.long(file)

        if client_data.bit_mask & SU_WEAPONFRAME:
            client_data.weapon_frame = _IO.read.byte(file)

        if client_data.bit_mask & SU_ARMOR:
            client_data.armor = _IO.read.byte(file)

        if client_data.bit_mask & SU_WEAPON:
            client_data.weapon = _IO.read.byte(file)

        client_data.health = _IO.read.short(file)
        client_data.active_ammo = _IO.read.byte(file)
        client_data.ammo = _IO.read.byte(file), _IO.read.byte(file), _IO.read.byte(file), _IO.read.byte(file)
        client_data.active_weapon = _IO.read.byte(file)

        return client_data


class StopSound:
    """Class for representing StopSound messages

    Stops a playing sound.

    Attributes:
        channel: The channel on which the sound is playing.

        entity: The entity that caused the sound.
    """

    __slots__ = (
        'channel',
        'entity'
    )

    def __init__(self):
        self.channel = None

    @staticmethod
    def write(file, stop_sound):
        _IO.write.byte(file, SVC_STOPSOUND)
        data = stop_sound.entity << 3 | (stop_sound.channel & 0x07)
        _IO.write.short(file, data)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_STOPSOUND
        stop_sound = StopSound()
        data = _IO.read.short(file)

        stop_sound.channel = data & 0x07
        stop_sound.entity = data >> 3

        return stop_sound


class UpdateColors:
    """Class for representing UpdateColors messages

    Sets the player's colors.

    Attributes:
        player: The player to update.

        colors: The combined shirt/pant color.
    """
    __slots__ = (
        'player',
        'colors'
    )

    def __init__(self):
        self.player = None
        self.colors = None

    @staticmethod
    def write(file, update_colors):
        _IO.write.byte(file, SVC_UPDATECOLORS)
        _IO.write.byte(file, update_colors.player)
        _IO.write.byte(file, update_colors.colors)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_UPDATECOLORS
        update_colors = UpdateColors()
        update_colors.player = _IO.read.byte(file)
        update_colors.colors = _IO.read.byte(file)

        return update_colors


class Particle:
    """Class for representing Particle messages

    Creates particle effects

    Attributes:
        origin: The origin position of the particles.

        direction: The velocity of the particles represented as a triple.

        count: The number of particles.

        color: The color index of the particle.
    """

    __slots__ = (
        'origin',
        'direction',
        'count',
        'color'
    )

    def __init__(self):
        self.origin = None
        self.direction = None
        self.count = None
        self.color = None

    @staticmethod
    def write(file, particle):
        _IO.write.byte(file, SVC_PARTICLE)
        _IO.write.position(file, particle.origin)
        _IO.write.char(file, particle.direction[0] * 16)
        _IO.write.char(file, particle.direction[1] * 16)
        _IO.write.char(file, particle.direction[2] * 16)
        _IO.write.byte(file, particle.count)
        _IO.write.byte(file, particle.color)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_PARTICLE
        particle = Particle()
        particle.origin = _IO.read.position(file)
        particle.direction = _IO.read.char(file) / 16, _IO.read.char(file) / 16, _IO.read.char(file) / 16,
        particle.count = _IO.read.byte(file)
        particle.color = _IO.read.byte(file)

        return particle


class Damage:
    """Class for representing Damage messages

    Damage information

    Attributes:
        armor: The damage amount to be deducted from player armor.

        blood: The damage amount to be deducted from player health.

        origin: The position of the entity that inflicted the damage.
    """

    __slots__ = (
        'armor',
        'blood',
        'origin'
    )

    def __init__(self):
        self.armor = None
        self.blood = None
        self.origin = None

    @staticmethod
    def write(file, damage):
        _IO.write.byte(file, SVC_DAMAGE)
        _IO.write.byte(file, damage.armor)
        _IO.write.byte(file, damage.blood)
        _IO.write.position(file, damage.origin)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_DAMAGE
        damage = Damage()
        damage.armor = _IO.read.byte(file)
        damage.blood = _IO.read.byte(file)
        damage.origin = _IO.read.position(file)

        return damage


class SpawnStatic:
    """Class for representing SpawnStatic messages

    Creates a static entity

    Attributes:
        model_index: The model number in the model table.

        frame: The frame number of the model.

        color_map: The color map used to display the model.

        skin: The skin number of the model.

        origin: The position of the entity.

        angles: The orientation of the entity.
    """

    __slots__ = (
        'model_index',
        'frame',
        'color_map',
        'skin',
        'origin',
        'angles'
    )

    def __init__(self):
        self.model_index = None
        self.frame = None
        self.color_map = None
        self.skin = None
        self.origin = None
        self.angles = None

    @staticmethod
    def write(file, spawn_static):
        _IO.write.byte(file, SVC_SPAWNSTATIC)
        _IO.write.byte(file, spawn_static.model_index)
        _IO.write.byte(file, spawn_static.frame)
        _IO.write.byte(file, spawn_static.color_map)
        _IO.write.byte(file, spawn_static.skin)
        _IO.write.position(file, spawn_static.origin)
        _IO.write.angles(file, spawn_static.angles)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SPAWNSTATIC
        spawn_static = SpawnStatic()
        spawn_static.model_index = _IO.read.byte(file)
        spawn_static.frame = _IO.read.byte(file)
        spawn_static.color_map = _IO.read.byte(file)
        spawn_static.skin = _IO.read.byte(file)
        spawn_static.origin = _IO.read.position(file)
        spawn_static.angles = _IO.read.angles(file)

        return spawn_static


class SpawnBinary:
    """Class for representing SpawnBinary messages

    This is a deprecated message.
    """

    __slots__ = ()

    @staticmethod
    def write(file):
        raise BadMessage('SpawnBinary message obsolete')

    @staticmethod
    def read(file):
        raise BadMessage('SpawnBinary message obsolete')


class SpawnBaseline:
    """Class for representing SpawnBaseline messages

    Creates a dynamic entity

    Attributes:
        entity: The number of the entity.

        model_index: The number of the model in the model table.

        frame: The frame number of the model.

        color_map: The color map used to display the model.

        skin: The skin number of the model.

        origin: The position of the entity.

        angles: The orientation of the entity.
    """

    __slots__ = (
        'entity',
        'model_index',
        'frame',
        'color_map',
        'skin',
        'origin',
        'angles'
    )

    def __init__(self):
        self.entity = None
        self.model_index = None
        self.frame = None
        self.color_map = None
        self.skin = None
        self.origin = None
        self.angles = None

    @staticmethod
    def write(file, spawn_baseline):
        _IO.write.byte(file, SVC_SPAWNBASELINE)
        _IO.write.short(file, spawn_baseline.entity)
        _IO.write.byte(file, spawn_baseline.model_index)
        _IO.write.byte(file, spawn_baseline.frame)
        _IO.write.byte(file, spawn_baseline.color_map)
        _IO.write.byte(file, spawn_baseline.skin)
        _IO.write.position(file, spawn_baseline.origin)
        _IO.write.angles(file, spawn_baseline.angles)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SPAWNBASELINE
        spawn_baseline = SpawnBaseline()
        spawn_baseline.entity = _IO.read.short(file)
        spawn_baseline.model_index = _IO.read.byte(file)
        spawn_baseline.frame = _IO.read.byte(file)
        spawn_baseline.color_map = _IO.read.byte(file)
        spawn_baseline.skin = _IO.read.byte(file)
        spawn_baseline.origin = _IO.read.position(file)
        spawn_baseline.angles = _IO.read.angles(file)

        return spawn_baseline


TE_SPIKE = 0
TE_SUPERSPIKE = 1
TE_GUNSHOT = 2
TE_EXPLOSION = 3
TE_TAREXPLOSION = 4
TE_LIGHTNING1 = 5
TE_LIGHTNING2 = 6
TE_WIZSPIKE = 7
TE_KNIGHTSPIKE = 8
TE_LIGHTNING3 = 9
TE_LAVASPLASH = 10
TE_TELEPORT = 11
TE_EXPLOSION2 = 12
TE_BEAM = 13


class TempEntity:
    """Class for representing TempEntity messages

    Creates a temporary entity. The attributes of the message depend on the
    type of entity being created.

    Attributes:
        type: The type of the temporary entity.
    """

    def __init__(self):
        self.type = None

    @staticmethod
    def write(file, temp_entity):
        _IO.write.byte(file, SVC_TEMP_ENTITY)
        _IO.write.byte(file, temp_entity.type)

        if temp_entity.type == TE_WIZSPIKE or \
                        temp_entity.type == TE_KNIGHTSPIKE or \
                        temp_entity.type == TE_SPIKE or \
                        temp_entity.type == TE_SUPERSPIKE or \
                        temp_entity.type == TE_GUNSHOT or \
                        temp_entity.type == TE_EXPLOSION or \
                        temp_entity.type == TE_TAREXPLOSION or \
                        temp_entity.type == TE_LAVASPLASH or \
                        temp_entity.type == TE_TELEPORT:

            _IO.write.position(file, temp_entity.origin)

        elif temp_entity.type == TE_LIGHTNING1 or \
                        temp_entity.type == TE_LIGHTNING2 or \
                        temp_entity.type == TE_LIGHTNING3 or \
                        temp_entity.type == TE_BEAM:

            _IO.write.short(file, temp_entity.entity)
            _IO.write.position(file, temp_entity.start)
            _IO.write.position(file, temp_entity.end)

        elif temp_entity.type == TE_EXPLOSION2:
            _IO.write.position(file, temp_entity.origin)
            _IO.write.byte(file, temp_entity.color_start)
            _IO.write.byte(file, temp_entity.color_length)

        else:
            raise BadMessage('Invalid Temporary Entity type: %r' % temp_entity.type)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_TEMP_ENTITY
        temp_entity = TempEntity()
        temp_entity.type = _IO.read.byte(file)

        if temp_entity.type == TE_WIZSPIKE or \
                temp_entity.type == TE_KNIGHTSPIKE or \
                temp_entity.type == TE_SPIKE or \
                temp_entity.type == TE_SUPERSPIKE or \
                temp_entity.type == TE_GUNSHOT or \
                temp_entity.type == TE_EXPLOSION or \
                temp_entity.type == TE_TAREXPLOSION or \
                temp_entity.type == TE_LAVASPLASH or \
                temp_entity.type == TE_TELEPORT:

            temp_entity.origin = _IO.read.position(file)

        elif temp_entity.type == TE_LIGHTNING1 or \
                temp_entity.type == TE_LIGHTNING2 or \
                temp_entity.type == TE_LIGHTNING3 or \
                temp_entity.type == TE_BEAM:

            temp_entity.entity = _IO.read.short(file)
            temp_entity.start = _IO.read.position(file)
            temp_entity.end = _IO.read.position(file)

        elif temp_entity.type == TE_EXPLOSION2:
            temp_entity.origin = _IO.read.position(file)
            temp_entity.color_start = _IO.read.byte(file)
            temp_entity.color_length = _IO.read.byte(file)

        else:
            raise BadMessage(f'Invalid Temporary Entity type: {temp_entity.type}')

        return temp_entity


class SetPause:
    """Class for representing SetPause messages

    Sets the pause state

    Attributes:
        paused: The pause state. 1 for paused, 0 otherwise.
    """

    __slots__ = (
        'paused'
    )

    def __init__(self):
        self.paused = None

    @staticmethod
    def write(file, set_pause):
        _IO.write.byte(file, SVC_SETPAUSE)
        _IO.write.byte(file, set_pause.paused)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SETPAUSE
        set_pause = SetPause()
        set_pause.paused = _IO.read.byte(file)

        return set_pause


class SignOnNum:
    """Class for representing SignOnNum messages

    This message represents the client state.

    Attributes:
        sign_on: The client state.
    """

    __slots__ = (
        'sign_on'
    )

    def __init__(self):
        self.sign_on = None

    @staticmethod
    def write(file, sign_on_num):
        _IO.write.byte(file, SVC_SIGNONNUM)
        _IO.write.byte(file, sign_on_num.sign_on)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SIGNONNUM
        sign_on_num = SignOnNum()
        sign_on_num.sign_on = _IO.read.byte(file)

        return sign_on_num


class CenterPrint:
    """Class for representing CenterPrint messages

    Prints text in the center of the screen.

    Attributes:
        text: The text to be shown.
    """

    __slots__ = (
        'text'
    )

    def __init__(self):
        self.text = None

    @staticmethod
    def write(file, center_print):
        _IO.write.byte(file, SVC_CENTERPRINT)
        _IO.write.string(file, center_print.text)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_CENTERPRINT
        center_print = CenterPrint()
        center_print.text = _IO.read.string(file)

        return center_print


class KilledMonster:
    """Class for representing KilledMonster messages

    Indicates the death of a monster.
    """

    __slots__ = ()

    @staticmethod
    def write(file, killed_monster=None):
        _IO.write.byte(file, SVC_KILLEDMONSTER)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_KILLEDMONSTER
        return KilledMonster()


class FoundSecret:
    """Class for representing FoundSecret messages

    Indicates a secret has been found.
    """

    __slots__ = ()

    @staticmethod
    def write(file, found_secret=None):
        _IO.write.byte(file, SVC_FOUNDSECRET)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_FOUNDSECRET
        return FoundSecret()


class SpawnStaticSound:
    """Class for representing SpawnStaticSound messages

    Creates a static sound

    Attributes:
        origin: The position of the sound.

        sound_number: The sound number in the sound table.

        volume: The sound volume.

        attenuation: The sound attenuation.
    """

    __slots__ = (
        'origin',
        'sound_number',
        'volume',
        'attenuation'
    )

    def __init__(self):
        self.origin = None
        self.sound_number = None
        self.volume = None
        self.attenuation = None

    @staticmethod
    def write(file, spawn_static_sound):
        _IO.write.byte(file, SVC_SPAWNSTATICSOUND)
        _IO.write.position(file, spawn_static_sound.origin)
        _IO.write.byte(file, spawn_static_sound.sound_number)
        _IO.write.byte(file, spawn_static_sound.volume * 256)
        _IO.write.byte(file, spawn_static_sound.attenuation * 64)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SPAWNSTATICSOUND
        spawn_static_sound = SpawnStaticSound()
        spawn_static_sound.origin = _IO.read.position(file)
        spawn_static_sound.sound_number = _IO.read.byte(file)
        spawn_static_sound.volume = _IO.read.byte(file) / 256
        spawn_static_sound.attenuation = _IO.read.byte(file) / 64

        return spawn_static_sound


class Intermission:
    """Class for representing Intermission messages

    Displays the level end screen.
    """

    __slots__ = ()

    @staticmethod
    def write(file, intermission=None):
        _IO.write.byte(file, SVC_INTERMISSION)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_INTERMISSION
        return Intermission()


class Finale:
    """Class for representing Finale messages

    Displays the episode end screen.

    Attributes:
        text: The text to show.
    """

    __slots__ = (
        'text'
    )

    def __init__(self):
        self.text = None

    @staticmethod
    def write(file, finale):
        _IO.write.byte(file, SVC_FINALE)
        _IO.write.string(file, finale.text)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_FINALE
        finale = Finale()
        finale.text = _IO.read.string(file)

        return finale


class CdTrack:
    """Class for representing CdTrack messages

    Selects the cd track

    Attributes:
        from_track: The start track.

        to_track: The end track.
    """

    __slots__ = (
        'from_track',
        'to_track'
    )

    def __init__(self):
        self.from_track = None
        self.to_track = None

    @staticmethod
    def write(file, cd_track):
        _IO.write.byte(file, SVC_CDTRACK)
        _IO.write.byte(file, cd_track.from_track)
        _IO.write.byte(file, cd_track.to_track)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_CDTRACK
        cd_track = CdTrack()
        cd_track.from_track = _IO.read.byte(file)
        cd_track.to_track = _IO.read.byte(file)

        return cd_track


class SellScreen:
    """Class for representing SellScreen messages

    Displays the help and sell screen.
    """

    __slots__ = ()

    @staticmethod
    def write(file, sell_screen=None):
        _IO.write.byte(file, SVC_SELLSCREEN)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_SELLSCREEN
        return SellScreen()


class CutScene:
    """Class for representing CutScene messages

    Displays end screen and text.

    Attributes:
        text: The text to be shown.
    """

    __slots__ = (
        'text'
    )

    def __init__(self):
        self.text = None

    @staticmethod
    def write(file, cut_scene):
        _IO.write.byte(file, SVC_CUTSCENE)
        _IO.write.string(file, cut_scene.text)

    @staticmethod
    def read(file):
        assert _IO.read.byte(file) == SVC_CUTSCENE
        cut_scene = CutScene()
        cut_scene.text = _IO.read.string(file)

        return cut_scene


_messages = [Bad, Nop, Disconnect, UpdateStat, Version, SetView, Sound,
             Time, Print, StuffText, SetAngle, ServerInfo, LightStyle,
             UpdateName, UpdateFrags, ClientData, StopSound, UpdateColors,
             Particle, Damage, SpawnStatic, SpawnBinary, SpawnBaseline,
             TempEntity, SetPause, SignOnNum, CenterPrint, KilledMonster,
             FoundSecret, SpawnStaticSound, Intermission, Finale, CdTrack,
             SellScreen, CutScene]


U_MOREBITS = 0b0000000000000001
U_ORIGIN1 = 0b0000000000000010
U_ORIGIN2 = 0b0000000000000100
U_ORIGIN3 = 0b0000000000001000
U_ANGLE2 = 0b0000000000010000
U_NOLERP = 0b0000000000100000
U_FRAME = 0b0000000001000000
U_SIGNAL = 0b0000000010000000
U_ANGLE1 = 0b0000000100000000
U_ANGLE3 = 0b0000001000000000
U_MODEL = 0b0000010000000000
U_COLORMAP = 0b0000100000000000
U_SKIN = 0b0001000000000000
U_EFFECTS = 0b0010000000000000
U_LONGENTITY = 0b0100000000000000


class UpdateEntity:
    """Class for representing UpdateEntity messages

    Updates an entity.

    Attributes:
        bit_mask: A bit field indicating what data is sent.

        entity: The number of the entity.

        model_index: The number of the model in the model table.

        frame: The frame number of the model.

        color_map: The color map used to display the model.

        skin: The skin number of the model.

        effects: A bit field indicating special effects.

        origin: The position of the entity.

        angles: The orientation of the entity.
    """

    __slots__ = (
        'bit_mask',
        'entity',
        'model_index',
        'frame',
        'colormap',
        'skin',
        'effects',
        'origin',
        'angles'
    )

    def __init__(self):
        self.bit_mask = 0b0000000000000000
        self.entity = None
        self.model_index = None
        self.frame = None
        self.colormap = None
        self.skin = None
        self.effects = None
        self.origin = None, None, None
        self.angles = None, None, None

    @staticmethod
    def write(file, update_entity):
        _IO.write.byte(file, update_entity.bit_mask & 0xFF | 0x80)

        if update_entity.bit_mask & U_MOREBITS:
            _IO.write.byte(file, update_entity.bit_mask >> 8 & 0xFF)

        if update_entity.bit_mask & U_LONGENTITY:
            _IO.write.short(file, update_entity.entity)

        else:
            _IO.write.byte(file, update_entity.entity)

        if update_entity.bit_mask & U_MODEL:
            _IO.write.byte(file, update_entity.model_index)

        if update_entity.bit_mask & U_FRAME:
            _IO.write.byte(file, update_entity.frame)

        if update_entity.bit_mask & U_COLORMAP:
            _IO.write.byte(file, update_entity.colormap)

        if update_entity.bit_mask & U_SKIN:
            _IO.write.byte(file, update_entity.skin)

        if update_entity.bit_mask & U_EFFECTS:
            _IO.write.byte(file, update_entity.effects)

        if update_entity.bit_mask & U_ORIGIN1:
            _IO.write.coord(file, update_entity.origin[0])

        if update_entity.bit_mask & U_ANGLE1:
            _IO.write.angle(file, update_entity.angles[0])

        if update_entity.bit_mask & U_ORIGIN2:
            _IO.write.coord(file, update_entity.origin[1])

        if update_entity.bit_mask & U_ANGLE2:
            _IO.write.angle(file, update_entity.angles[1])

        if update_entity.bit_mask & U_ORIGIN3:
            _IO.write.coord(file, update_entity.origin[2])

        if update_entity.bit_mask & U_ANGLE3:
            _IO.write.angle(file, update_entity.angles[2])

    @staticmethod
    def read(file):
        update_entity = UpdateEntity()
        b = _IO.read.byte(file)
        update_entity.bit_mask = b & 0x7F

        if update_entity.bit_mask & U_MOREBITS:
            update_entity.bit_mask |= _IO.read.byte(file) << 8

        if update_entity.bit_mask & U_LONGENTITY:
            update_entity.entity = _IO.read.short(file)

        else:
            update_entity.entity = _IO.read.byte(file)

        if update_entity.bit_mask & U_MODEL:
            update_entity.model_index = _IO.read.byte(file)

        if update_entity.bit_mask & U_FRAME:
            update_entity.frame = _IO.read.byte(file)

        if update_entity.bit_mask & U_COLORMAP:
            update_entity.colormap = _IO.read.byte(file)

        if update_entity.bit_mask & U_SKIN:
            update_entity.skin = _IO.read.byte(file)

        if update_entity.bit_mask & U_EFFECTS:
            update_entity.effects = _IO.read.byte(file)

        if update_entity.bit_mask & U_ORIGIN1:
            update_entity.origin = _IO.read.coord(file), update_entity.origin[1], update_entity.origin[2]

        if update_entity.bit_mask & U_ANGLE1:
            update_entity.angles = _IO.read.angle(file), update_entity.angles[1], update_entity.angles[2]

        if update_entity.bit_mask & U_ORIGIN2:
            update_entity.origin = update_entity.origin[0], _IO.read.coord(file), update_entity.origin[2]

        if update_entity.bit_mask & U_ANGLE2:
            update_entity.angles = update_entity.angles[0], _IO.read.angle(file), update_entity.angles[2]

        if update_entity.bit_mask & U_ORIGIN3:
            update_entity.origin = update_entity.origin[0], update_entity.origin[1], _IO.read.coord(file)

        if update_entity.bit_mask & U_ANGLE3:
            update_entity.angles = update_entity.angles[0], update_entity.angles[1], _IO.read.angle(file)

        return update_entity


class MessageBlock:
    """Class for representing a message block

    Attributes:
        view_angles: The client view angles.

        messages: A sequence of messages.
    """

    __slots__ = (
        'view_angles',
        'messages'
    )

    def __init__(self):
        self.view_angles = None
        self.messages = []

    @staticmethod
    def write(file, message_block):
        start_of_block = file.tell()
        _IO.write.long(file, 0)
        _IO.write.float(file, message_block.view_angles[0])
        _IO.write.float(file, message_block.view_angles[1])
        _IO.write.float(file, message_block.view_angles[2])
        start_of_messages = file.tell()

        for message in message_block.messages:
            message.__class__.write(file, message)

        end_of_messages = file.tell()
        block_size = end_of_messages - start_of_messages

        file.seek(start_of_block)
        _IO.write.long(file, block_size)
        file.seek(end_of_messages )

    @staticmethod
    def read(file):
        message_block = MessageBlock()
        blocksize = _IO.read.long(file)
        message_block.view_angles = _IO.read.float(file), _IO.read.float(file), _IO.read.float(file)
        message_block_data = file.read(blocksize)

        buff = io.BufferedReader(io.BytesIO(message_block_data))
        message_id = buff.peek(1)[:1]

        while message_id != b'':
            message_id = struct.unpack('<B', message_id)[0]

            if message_id < 128:
                message = _messages[message_id].read(buff)

            else:
                message = UpdateEntity.read(buff)

            if message:
                message_block.messages.append(message)

            message_id = buff.peek(1)[:1]

        buff.close()

        return message_block
