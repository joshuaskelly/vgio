import math

import pyglet
from pyglet.gl import *
from pyglet.window import key

from doom.formats import wad as wadfile
from doom.core.wad import Wad

from camera import FirstPersonCamera as Camera

#wad = Wad('C:\\Users\\Joshua\\Desktop\\DOOM2.WAD')
#doom_map = wad.map('MAP01')

import struct

from quake.formats.pak import PakFile

#pak = pak.load('/Users/joshua/Games/Quake/id1/PAK0.PAK')

pak_file = PakFile('/Users/joshua/Games/Quake/id1/PAK0.PAK')
#pak_file.extract('progs/player.mdl', '/Users/joshua/Desktop/out')
pak_file.extractall('/Users/joshua/Desktop/out')

quit()

with PakFile('/Users/joshua/Games/Quake/id1/PAK0.PAK') as pak_file:
    with pak_file.open('quake.rc') as file:
        r = file.read()

    with pak_file.open('progs/player.mdl') as file:
        mdl_struct = '<4sl10f8lf'
        mdl_size = struct.calcsize(mdl_struct)
        mdl_header = file.read(mdl_size)
        mdl_header = struct.unpack(mdl_struct, mdl_header)

        magic_number = mdl_header[0].split(b'\00')[0].decode('ascii')
        version = mdl_header[1]
        scale = mdl_header[2:5]
        origin = mdl_header[5:8]
        radius = mdl_header[8]
        offsets = mdl_header[9:12]
        numskins = mdl_header[12]
        skinwidth = mdl_header[13]
        skinheight = mdl_header[14]
        numverts = mdl_header[15]
        numtris = mdl_header[16]
        numframes = mdl_header[17]
        synctype = mdl_header[18]
        flags = mdl_header[19]
        size = mdl_header[20]

        print(magic_number)


quit()

class Mesh:
    def __init__(self, vertices, triangles):
        self.vertices =vertices
        self.triangles = triangles

class Model:
    def __init__(self, mesh):
        self.mesh = mesh
        self.batch = pyglet.graphics.Batch()

        color = ('c3f', (1,1,1,)*3)

        for triangle in self.mesh.triangles:
            v0 = self.mesh.vertices[triangle[0]]
            v1 = self.mesh.vertices[triangle[1]]
            v2 = self.mesh.vertices[triangle[2]]
            
            self.batch.add(3, GL_TRIANGLES, None, ('v3f', v0 + v1 + v2))

    def draw(self):
        self.batch.draw()

class Polygon:
    def __init__(self, vertices, lines):
        self.batch = pyglet.graphics.Batch()

        color = ('c3f', (1,1,1,)*3)

        for line in lines:
            v0 = vertices[line[0]]
            v1 = vertices[line[1]]
            
            self.batch.add(2, GL_LINES, None, ('v3f', v0 + v1))

    def draw(self):
        self.batch.draw()

class Grid:
    def __init__(self):
        start_alpha = 0.25
        end_alpha = 0.0
        axis_length = 200
        self.batch = pyglet.graphics.Batch()
        self.batch.add(3, GL_LINE_STRIP, None, ('v3f', (-axis_length,0,0) + (0,0,0) + (axis_length,0,0)), ('c4f', (1,0,0,end_alpha) + (1,0,0,start_alpha) + (1,0,0,end_alpha)))
        self.batch.add(3, GL_LINE_STRIP, None, ('v3f', (0,-axis_length,0) + (0,0,0) + (0,axis_length,0)), ('c4f', (0,1,0,end_alpha) + (0,1,0,start_alpha) + (0,1,0,end_alpha)))
        self.batch.add(3, GL_LINE_STRIP, None, ('v3f', (0,0,-axis_length) + (0,0,0) + (0,0,axis_length)), ('c4f', (0,0,1,end_alpha) + (0,0,1,start_alpha) + (0,0,1,end_alpha)))

    def draw(self):
        self.batch.draw()

class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(320, 240)
        self.__camera_view_enabled = False

        verts = [(v.x, 0, v.y) for v in doom_map.vertexes]
        lines = [(l.vertex_1.index, l.vertex_2.index) for l in doom_map.linedefs]

        self.model = Polygon(verts, lines)
        self.grid = Grid()

        pyglet.clock.schedule(self.update)

        self.camera = Camera(self, (0,0,-4))

    @property
    def camera_view_enabled(self):
        return self.__camera_view_enabled

    @camera_view_enabled.setter
    def camera_view_enabled(self, value):
        self.__camera_view_enabled = value
        self.set_exclusive_mouse(value)

    def update(self, delta_time):
        if self.camera_view_enabled:
            self.camera.update(delta_time)

    def on_mouse_press(self, x, y , button, modifiers):
        if button == pyglet.window.mouse.RIGHT:
            self.camera_view_enabled = not self.camera_view_enabled

    def on_draw(self):
        self.clear()
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70, self.width/self.height, 0.05, 1000)
        
        self.camera.draw()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.grid.draw()

        glPushMatrix()
        scale_factor = 1/32
        glScalef(-scale_factor, scale_factor, scale_factor)
        
        # Draw model
        glColor3f(1,1,1)
        self.model.draw()

        # Draw model in wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(0,0,0)
        self.model.draw()
        glPopMatrix()

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

if __name__ == '__main__':
    window_options = {
    'width': 640,
    'height': 480,
    'caption': 'Model Viewer',
    'resizable': True
    }

    window = Window(**window_options)

    glClearColor(0.5, 0.5, 0.5, 1)


    pyglet.app.run()