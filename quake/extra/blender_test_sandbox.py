import bpy
import bmesh

from importlib.machinery import SourceFileLoader
mdlfile = SourceFileLoader('mdlfile', '/Users/joshua/Repositories/game-tools/quake/formats/mdlfile.py').load_module()
from mdlfile import Mdl

mdl = Mdl.open('/Users/joshua/Desktop/out/progs/player.mdl')
mdl.close()

image = mdl.image()
img = bpy.data.images.new('IMG', image.width, image.height)
p = list(map(lambda x: x / 255, image.pixels))
    
img.pixels[:] = p
img.update()

tex = bpy.data.textures.new('TEX', 'IMAGE')
tex.image = img

mat = bpy.data.materials.new('MAT')
mat.diffuse_color = 1,1,1

tex_slot = mat.texture_slots.add()
tex_slot.texture = tex
tex_slot.texture_coords = 'UV'

frame_index = 0
mesh = mdl.mesh(frame_index)

me = bpy.data.meshes.new(mdl.frames[frame_index].name)
bm = bmesh.new()

for vert in mesh.vertices:
    bm.verts.new(vert)
    
bm.verts.ensure_lookup_table()
uv_layer = bm.loops.layers.uv.new()

for triangle in mesh.triangles:
    t0 = bm.verts[triangle[0]]
    t1 = bm.verts[triangle[1]]
    t2 = bm.verts[triangle[2]]
    
    face = bm.faces.new((t0, t1, t2))
    
    face.loops[0][uv_layer].uv = mesh.uvs[triangle[0]]
    face.loops[1][uv_layer].uv = mesh.uvs[triangle[1]]
    face.loops[2][uv_layer].uv = mesh.uvs[triangle[2]]

bm.to_mesh(me)
bm.free()

ob = bpy.data.objects.new(mdl.frames[frame_index].name, me)

ob.scale = mdl.scale
ob.location = mdl.origin

for texpoly in me.uv_textures[0].data:
    texpoly.image = img

me.materials.append(mat)

bpy.context.scene.objects.link(ob)