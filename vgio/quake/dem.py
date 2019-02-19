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

import io

from . import protocol


__all__ = ['Dem']


class Dem(object):
    """Class for working with Dem files

    Example:
        d = Dem.open(file)

    Attributes:
        cd_track: The number of the cd track to play. The track will be '-1' if
            no music.

        message_blocks: A sequence of Message objects
    """

    def __init__(self):
        self.fp = None
        self.mode = None
        self._did_modify = False

        self.cd_track = '-1'
        self.message_blocks = []

    @staticmethod
    def open(file, mode='r'):
        """Returns a Dem object

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file

        Returns:
            An Lmp object constructed from the information read from the
            file-like object.

        Raises:
            ValueError: If an invalid file mode is given.
        """

        if mode not in ('r', 'w', 'a'):
            raise ValueError("invalid mode: '%s'" % mode)

        filemode = {'r': 'rb', 'w': 'w+b', 'a': 'r+b'}[mode]

        if isinstance(file, str):
            file = io.open(file, filemode)

        elif isinstance(file, bytes):
            file = io.BytesIO(file)

        elif not hasattr(file, 'read'):
            raise RuntimeError("Dem.open() requires 'file' to be a path, a file-like object, or bytes")

        # Read
        if mode == 'r':
            return Dem._read_file(file, mode)

        # Write
        elif mode == 'w':
            dem = Dem()
            dem.fp = file
            dem.mode = 'w'
            dem._did_modify = True

            return dem

        # Append
        else:
            dem = Dem._read_file(file, mode)
            dem._did_modify = True

            return dem

    @staticmethod
    def _read_file(file, mode):
        dem = Dem()
        dem.mode = mode
        dem.fp = file

        # CD Track
        dem.cd_track = protocol.IO.read.string(file, b'\n')

        # Message Blocks
        while file.peek(4)[:4] != b'':
            message_block = protocol.MessageBlock.read(file)
            dem.message_blocks.append(message_block)

        return dem

    @staticmethod
    def _write_file(file, dem):
        protocol.IO.write.string(file, dem.cd_track, b'\n')

        for message_block in dem.message_blocks:
            protocol.MessageBlock.write(file, message_block)

    @staticmethod
    def write(file, dem):
        return Dem._write_file(file, dem)

    def save(self, file):
        """Writes Dem data to file

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
                "Dem.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        Dem._write_file(file, self)

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
                Dem._write_file(self.fp, self)
                self.fp.truncate()

        file_object = self.fp
        self.fp = None
        file_object.close()
