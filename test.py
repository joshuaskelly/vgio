from wad import wadfile2 as wadfile
import math
from polygon_utils import *

doom2_wad = wadfile.load("C:\Users\Joshua\Desktop\DOOM2.WAD")

vertices = doom2_wad["lumps"][10]["value"]
vertices = [[v.x, v.y] for v in vertices]

lines = doom2_wad["lumps"][8]["value"]
sectors = doom2_wad["lumps"][14]["value"]
sides = doom2_wad["lumps"][9]["value"]
