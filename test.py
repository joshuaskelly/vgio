import pyglet
from pyglet.gl import *
from pyglet.image import ImageData

from camera import FirstPersonCamera as Camera

from quake.pak import PakFile
from quake.mdl import Mdl
from quake.lmp import Lmp

with PakFile('/Users/joshua/Games/Quake/id1/PAK0.PAK') as pak_file:
    for filename in [f for f in pak_file.namelist() if '.lmp' in f]:
        with pak_file.open(filename) as lmp_file:
            lmp = Lmp.open(lmp_file)
            lmp.close()

        image = lmp.image()

        data = image.pixels
        rawData = (GLubyte * len(data))(*data)
        image = ImageData(image.width, image.height, image.format, rawData)

        image.save('/Users/joshua/Desktop/gfx/%s.png' % filename.split('/')[-1].split('.')[0])

quit()

def lerp(a, b, step):
    return a + step * (b - a)


class Model:
    def __init__(self, mesh, image=None):
        self.mesh = mesh
        self.batch = pyglet.graphics.Batch()

        if image:
            texture = image.get_texture()
            coords = texture.tex_coords

            min_x = coords[0]
            min_y = coords[1]
            max_x = coords[6]
            max_y = coords[7]

            def fix_uv(uv):
                return lerp(min_x, max_x, uv[0]), lerp(min_y, max_y, uv[1])

            skin = pyglet.graphics.TextureGroup(texture)
        else:
            skin = None

        for triangle in self.mesh.triangles:
            v0 = self.mesh.vertices[triangle[0]]
            v1 = self.mesh.vertices[triangle[1]]
            v2 = self.mesh.vertices[triangle[2]]

            tt0 = self.mesh.uvs[triangle[0]]
            tt1 = self.mesh.uvs[triangle[1]]
            tt2 = self.mesh.uvs[triangle[2]]

            t0 = fix_uv(tt0)
            t1 = fix_uv(tt1)
            t2 = fix_uv(tt2)

            self.batch.add(3, GL_TRIANGLES, skin, ('v3f', v0 + v1 + v2), ('t2f', t0 + t1 + t2))

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

        self.model = Model(mesh, image)
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

        # Draw grid
        #glEnable(GL_BLEND)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.grid.draw()

        # Draw model
        glPushMatrix()

        glRotatef(90, -1, 0, 0)
        glTranslatef(mdl_file.origin[0],mdl_file.origin[1],mdl_file.origin[2])
        glScalef(mdl_file.scale[0], mdl_file.scale[1], mdl_file.scale[2])

        # Draw model
        glColor3f(1,1,1)
        #glPolygonMode(GL_FRONT_, GL_FILL)
        self.model.draw()

        # Draw model in wireframe
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        #glColor3f(0,0,0)
        #self.model.draw()
        glPopMatrix()



if __name__ == '__main__':
    window_options = {
    'width': 640,
    'height': 480,
    'caption': 'Model Viewer',
    'resizable': True
    }

    window = Window(**window_options)

    glClearColor(0.5, 0.5, 0.5, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


    pyglet.app.run()