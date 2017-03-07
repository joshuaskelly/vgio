import bpy
import bmesh

from .quake.mdl import Mdl, is_mdlfile


def load(operator, context, filepath):

    if not is_mdlfile(filepath):
        # TODO: Error out
        return {'FINISHED'}

    mdl = Mdl.open(filepath)
    mdl.close()

    # Load skin and create a material
    image = mdl.image()
    img = bpy.data.images.new('IMG', image.width, image.height)
    pixels = list(map(lambda x: x / 255, image.pixels))

    img.pixels[:] = pixels
    img.update()

    tex = bpy.data.textures.new('TEX', 'IMAGE')
    tex.image = img

    mat = bpy.data.materials.new('MAT')
    mat.diffuse_color = 1,1,1

    tex_slot = mat.texture_slots.add()
    tex_slot.texture = tex
    tex_slot.texture_coords = 'UV'

    # Create mesh data
    mesh = mdl.mesh(0)
    me = bpy.data.meshes.new(mdl.frames[0].name)
    bm = bmesh.new()

    for vertex in mesh.vertices:
        bm.verts.new(vertex)

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

    ob = bpy.data.objects.new(mdl.frames[0].name, me)

    ob.scale = mdl.scale
    ob.location = mdl.origin

    for texpoly in me.uv_textures[0].data:
        texpoly.image = img

    me.materials.append(mat)

    bpy.context.scene.objects.link(ob)

    return {'FINISHED'}
