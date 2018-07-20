import bpy
import bmesh
from mathutils import Matrix, Vector

from .quake.bsp import Bsp, is_bspfile
from .quake import map as Map


def load(operator, context, filepath='',
         global_scale=1.0,
         use_worldspawn_entity=True,
         use_brush_entities=True,
         use_point_entities=True):

    if not is_bspfile(filepath):
        operator.report(
            {'ERROR'},
            '{} not a recognized BSP file'.format(filepath)
        )
        return {'CANCELLED'}

    bsp = Bsp.open(filepath)
    bsp.close()

    point_entities = Map.loads(bsp.entities)

    # Create materials
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
            tex.use_mipmap = False
        else:
            tex = bpy.data.textures[texture_index]

        material_index = bpy.data.materials.find(name)

        if material_index < 0:
            mat = bpy.data.materials.new(name)
            mat.diffuse_color = 1, 1, 1
            mat.specular_intensity = 0
            mat.use_shadeless = True

            if name.startswith('{'):
                mat.use_transparency = True

            tex_slot = mat.texture_slots.add()
            tex_slot.texture = tex
            tex_slot.texture_coords = 'UV'

    global_matrix  = Matrix.Scale(global_scale, 4)

    # Create point entities
    if use_point_entities:
        for entity in [_ for _ in point_entities if hasattr(_, 'origin')]:
            vec = tuple(map(int, entity.origin.split(' ')))
            ob = bpy.data.objects.new(entity.classname + '.000', None)
            ob.location = Vector(vec) * global_scale
            ob.empty_draw_size = 16 * global_scale
            ob.empty_draw_type = 'CUBE'
            bpy.context.scene.objects.link(ob)

    # Create meshes
    for mesh_index, mesh in enumerate(bsp.meshes()):
        # Worldspawn is always mesh 0
        if mesh_index == 0 and not use_worldspawn_entity:
            continue

        # Brush entities are the remaining meshes
        if mesh_index > 0 and not use_brush_entities:
            break

        me = bpy.data.meshes.new('model %d' % mesh_index)
        bm = bmesh.new()

        for vertex_index, vertex in enumerate(mesh.vertices):
            v0 = bm.verts.new(vertex)
            v0.normal = mesh.normals[vertex_index]
            v0.co = global_matrix * v0.co

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

        for sub_mesh_index, sub_mesh in enumerate(mesh.sub_meshes):
            if not sub_mesh:
                continue

            name = bsp.miptextures[sub_mesh_index].name
            mat = bpy.data.materials.find(name)

            for triangle in sub_mesh:
                bm.faces[triangle].material_index = mat

        bm.to_mesh(me)
        bm.free()

        mesh_name = 'brush_entity.000'

        if mesh_index == 0:
            mesh_name = 'worldspawn'

        ob = bpy.data.objects.new(mesh_name, me)

        for miptexture_index in range(len(bsp.miptextures)):
            ob.data.materials.append(bpy.data.materials[miptexture_index])

        bpy.context.scene.objects.link(ob)

    # Apply textures to faces
    for ob in [o for o in bpy.data.objects if o.type == 'MESH']:
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.faces.ensure_lookup_table()

        for mi, m in enumerate(ob.data.uv_textures[0].data):
            face = bm.faces[mi]
            mat_index = face.material_index
            mat = bpy.data.materials[mat_index]
            tex = mat.texture_slots[0].texture
            m.image = tex.image

    return {'FINISHED'}
