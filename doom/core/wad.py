from doom.core.map import Map
from doom.core.palette import Palette
from doom.formats import wad

class Wad(object):
    valid_types = ['IWAD', 'PWAD']

    def __init__(self, filepath):
        wad_struct = wad.load(filepath)

        if wad_struct.type not in Wad.valid_types:
            raise TypeError('WAD type must be one of the following: %s' % ', '.join(Wad.valid_types))

        self.__data = wad_struct

    def keys(self):
        return [lump.name for lump in self.__data.lumps]

    def __getitem__(self, key):
        lump_struct = self.__data.lumps.__getitem__(key)

        if lump_struct:
            return Lump(lump_struct) 
        else:
            raise KeyError(key)

    @property
    def version(self):
        return '1'

    @property
    def format(self):
        return 'HEXEN' if 'BEHAVIOR' in self.markers() else 'DOOM'

    @property
    def type(self):
        return self.__data.type

    def markers(self):
        return [lump.name for lump in self.__data.lumps if lump.size == 0]

    def map(self, key):
        if key not in self.markers():
            raise KeyError(key)

        start = self.__data.lumps.index(key) + 1
        stop = start

        l = len(self.__data.lumps)

        for i in range(min(len(self.__data.lumps) - 1, len(Map.valid_lumps))):
            lump = self.__data.lumps[start + i]
            if lump.name in Map.valid_lumps:
                stop += 1
            else:
                break;

        map_lumps = self.__data.lumps[start - 1:stop]
        
        return Map(map_lumps)

    def palette(self, index):
        if index < 0 or index > 13:
            raise IndexError(index)

        return Palette(self.__data.lumps['PLAYPAL'].data, index)
