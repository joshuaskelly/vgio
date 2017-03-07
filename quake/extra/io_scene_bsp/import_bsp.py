import bpy
import bmesh

from .quake.bsp import Bsp, is_bspfile


def load(operator, context, filepath):

    if not is_bspfile(filepath):
        # TODO: Error out
        return {'FINISHED'}

    bsp = Bsp.open(filepath)
    bsp.close()

    # Create materials
    for i in range(len(bsp.miptextures)):
        pass

    materials = []
    images = bsp.images()
    for i, image in enumerate(images):
        if image is None:
            img = bpy.data.images.new('IMG', 0, 0)
            name = 'missing %d' % i
        else:
            name = bsp.miptextures[i].name

            image_index = bpy.data.images.find(name)

            if image_index < 0:
                img = bpy.data.images.new(name, image.width, image.height)
                pixels = list(map(lambda x: x / 255, image.pixels))
                img.pixels[:] = pixels
                img.update()
            else:
                img = bpy.data.images[image_index]

        texture_index = bpy.data.textures.find(name)

        if texture_index < 0:
            tex = bpy.data.textures.new(name, 'IMAGE')
            tex.image = img
        else:
            tex = bpy.data.textures[texture_index]

        material_index = bpy.data.materials.find(name)

        if material_index < 0:
            mat = bpy.data.materials.new(name)
            mat.diffuse_color = 1, 1, 1
            mat.specular_intensity = 0
            mat.use_shadeless = True

            tex_slot = mat.texture_slots.add()
            tex_slot.texture = tex
            tex_slot.texture_coords = 'UV'

    # Create meshes
    for i in range(len(bsp.models)):
        mesh = bsp.mesh(i)
        me = bpy.data.meshes.new("model %d" % i)
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

        bm.faces.ensure_lookup_table()

        for i, sub_mesh in enumerate(mesh.sub_meshes):
            if not sub_mesh:
                continue

            name = bsp.miptextures[i].name
            mat = bpy.data.materials.find(name)

            for triangle in sub_mesh:
                bm.faces[triangle].material_index = mat

        bm.to_mesh(me)
        bm.free()

        ob = bpy.data.objects.new("bsp object", me)

        for i in range(len(bsp.miptextures)):
            ob.data.materials.append(bpy.data.materials[i])

        bpy.context.scene.objects.link(ob)

    return {'FINISHED'}
