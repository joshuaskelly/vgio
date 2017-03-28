import os

import bpy
import bmesh

from .quake import mdl


def load(operator, context, filepath):
    if not mdl.is_mdlfile(filepath):
        # TODO: Error out
        return {'FINISHED'}

    mdl_file = mdl.Mdl.open(filepath)
    mdl_file.close()

    # Load skin and create a material
    image = mdl_file.image()
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
    mesh = mdl_file.mesh()

    name = os.path.basename(filepath).split('.')[0]

    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    for i, vertex in enumerate(mesh.vertices):
        v0 = bm.verts.new(vertex)
        v0.normal = mesh.normals[i]

    bm.verts.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.new()

    for triangle in mesh.triangles:
        t0 = bm.verts[triangle[0]]
        t1 = bm.verts[triangle[1]]
        t2 = bm.verts[triangle[2]]

        try:
            face = bm.faces.new((t0, t1, t2))

            face.loops[0][uv_layer].uv = mesh.uvs[triangle[0]]
            face.loops[1][uv_layer].uv = mesh.uvs[triangle[1]]
            face.loops[2][uv_layer].uv = mesh.uvs[triangle[2]]

        except:
            # Ignore triangles that are defined multiple times
            pass

    bm.to_mesh(me)
    bm.free()

    ob = bpy.data.objects.new(name, me)

    ob.scale = mdl_file.scale
    ob.location = mdl_file.origin

    for texpoly in me.uv_textures[0].data:
        texpoly.image = img

    me.materials.append(mat)

    # Create frames
    for i, frame in enumerate(mdl_file.frames):
        if frame.type == mdl.SINGLE:
            ob.shape_key_add(frame.name)
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            bm.verts.ensure_lookup_table()
            shape_layer = bm.verts.layers.shape[frame.name]

            mesh = mdl_file.mesh(i)

            for j, vertex in enumerate(mesh.vertices):
                bm.verts[j][shape_layer] = vertex

            bm.to_mesh(ob.data)
            bm.free()

    bpy.context.scene.objects.link(ob)

    return {'FINISHED'}
