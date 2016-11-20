from doom.formats import wad as wadfile

doom2_wad = wadfile.load('C:\\Users\\Joshua\\Desktop\\DOOM2.WAD')

map = doom2_wad.lumps["MAP01":"MAP02"]

print('!')
