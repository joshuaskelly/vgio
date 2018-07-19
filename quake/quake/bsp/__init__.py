from . import bsp29
from . import bsp29a


def is_bspfile(filename):
    """Quickly see if a file is a bsp file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    return bsp29.is_bspfile(filename) or bsp29a.is_bspfile(filename)


class Bsp(object):
    @staticmethod
    def open(file, mode='r'):
        # Open for read or append
        if mode == 'r' or mode == 'a':
            if bsp29.is_bspfile(file):
                return bsp29.Bsp.open(file, mode)

            elif bsp29a.is_bspfile(file):
                return bsp29a.Bsp.open(file, mode)

            raise bsp29.BadBspFile('Not a bsp file')

        # Open for write
        return bsp29.Bsp.open(file, mode)