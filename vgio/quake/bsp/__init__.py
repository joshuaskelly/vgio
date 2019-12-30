from vgio import quake

from . import bsp29
from . import bsp29a


def is_bspfile(filename):
    """Quickly see if a file is a bsp file by checking the magic number.

    The filename argument may be a file for file-like object.

    Args:
        filename: File to check as string or file-like object.

    Returns:
        True if given file's magic number is correct.
    """
    return bsp29.is_bspfile(filename) or bsp29a.is_bspfile(filename)


class Bsp:
    """Factory class for working with bsp files. Will automatically detect the
    version of the provided file and open it with the correct versioned Bsp
    object.

    Example:
        Basic usage::

            from vgio.quake.bsp import Bsp
            b = Bsp.open('example.bsp')
    """

    @staticmethod
    def open(file, mode='r'):
        """Open a Bsp object where file can be a path to a file (a
        string), or a file-like object.

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file.

        Returns:
            A Bsp object.
        """

        if mode == 'r' or mode == 'a':
            if bsp29.is_bspfile(file):
                return bsp29.Bsp.open(file, mode)

            elif bsp29a.is_bspfile(file):
                return bsp29a.Bsp.open(file, mode)

            raise bsp29.BadBspFile('Not a bsp file')

        # Open for write
        return bsp29.Bsp.open(file, mode)
