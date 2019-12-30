"""This module provides file I/O for Quake 2 DM2 dm2o files.

References:
    Quake Source
    - id Software
    - https://github.com/id-Software/Quake-2

    The Unofficial DM2 Format Description
    - Uwe Girlich, et al.
    - https://www.quakewiki.net/archives/dm2ospecs/dm2/dm2.pdf
"""

from vgio._core import ReadWriteFile
from . import protocol


__all__ = ['Dm2']


class Dm2(ReadWriteFile):
    """Class for working with Dm2 files

    Example:
        Basic usage::

            d = Dm2.open(file)

    Attributes:
        message_blocks: A sequence of Message objects
    """

    def __init__(self):
        super().__init__()

        self.message_blocks = []

    @staticmethod
    def _read_file(file, mode):
        dm2 = Dm2()
        dm2.mode = mode
        dm2.fp = file

        # Message Blocks
        while file.peek(4)[:4] != b'':
            message_block = protocol.MessageBlock.read(file)
            dm2.message_blocks.append(message_block)

        return dm2

    @staticmethod
    def _write_file(file, dm2):
        for message_block in dm2.message_blocks:
            protocol.MessageBlock.write(file, message_block)
