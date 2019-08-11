"""This module provides file I/O for Quake DEM demo files.

Example:
    dem_file = dem.Dem.open('demo1.dem')

References:
    Quake Source
    - id Software
    - https://github.com/id-Software/Quake

    The Unofficial DEM Format Description
    - Uwe Girlich, et al.
    - https://www.quakewiki.net/archives/demospecs/dem/dem.html
"""

from vgio._core import ReadWriteFile
from . import protocol


__all__ = ['Dem']


class Dem(ReadWriteFile):
    """Class for working with Dem files

    Example:
        d = Dem.open(file)

    Attributes:
        cd_track: The number of the cd track to play. The track will be '-1' if
            no music.

        message_blocks: A sequence of Message objects
    """

    def __init__(self):
        super().__init__()

        self.cd_track = '-1'
        self.message_blocks = []

    @staticmethod
    def _read_file(file, mode):
        dem = Dem()
        dem.mode = mode
        dem.fp = file

        # CD Track
        dem.cd_track = protocol._IO.read.string(file, b'\n')

        # Message Blocks
        while file.peek(4)[:4] != b'':
            message_block = protocol.MessageBlock.read(file)
            dem.message_blocks.append(message_block)

        return dem

    @staticmethod
    def _write_file(file, dem):
        protocol._IO.write.string(file, dem.cd_track, b'\n')

        for message_block in dem.message_blocks:
            protocol.MessageBlock.write(file, message_block)
