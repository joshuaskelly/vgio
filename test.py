from doom.formats import wad as wadfile

doom2_wad = wadfile.load('C:\\Users\\Joshua\\Desktop\\DOOM2.WAD')

name = doom2_wad.lumps[7].name
data = doom2_wad.lumps[7].data

print('!')
