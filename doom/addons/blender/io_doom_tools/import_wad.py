import bpy
import bmesh
import time
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

from . import wadfile

def load(operator,
         context,
         filepath):
    """Called by the user interface or another script."""
    print("\nImporting WAD file %r\n" % filepath)
    time_main = time.time()

    loaded_wad = wadfile.load(filepath)

    # MAP01
    offset = 6
    lines = loaded_wad["lumps"][offset + 2]["value"]
    sides = loaded_wad["lumps"][offset + 3]["value"]
    vertices = loaded_wad["lumps"][offset + 4]["value"]
    sectors = loaded_wad["lumps"][offset + 8]["value"]

    me = bpy.data.meshes.new("MAP01")
    bm = bmesh.new()

    sector_map = {}

    def addLineToSector(line, sector):
        if not sector in sector_map:
            sector_map[sector] = []

        sector_map[sector].append(line)


    # Render linedefs
    for line in lines:
        vertex_1 = vertices[line["vertex_1"]]
        vertex_2 = vertices[line["vertex_2"]]

        # Render front side
        if line["front_side"] > -1 and line["back_side"] == -1:
            front_side = sides[line["front_side"]]
            front_sector = sectors[front_side["sector"]]
            addLineToSector(line, front_side["sector"])

            bv1 = bm.verts.new([vertex_1["x"], vertex_1["y"], front_sector["floor_height"]])
            bv2 = bm.verts.new([vertex_2["x"], vertex_2["y"], front_sector["floor_height"]])
            bv3 = bm.verts.new([vertex_2["x"], vertex_2["y"], front_sector["ceiling_height"]])
            bv4 = bm.verts.new([vertex_1["x"], vertex_1["y"], front_sector["ceiling_height"]])

            bm.faces.new([bv1, bv2, bv3, bv4])

        # Render back side. Is this even valid?
        elif line["back_side"] > -1 and line["front_side"] == -1:
            print("Rendering back side only sidedef")

            back_side = sides[line["back_side"]]
            back_sector = sectors[back_side["sector"]]
            addLineToSector(line, back_side["sector"])

            bv1 = bm.verts.new([vertex_1["x"], vertex_1["y"], back_sector["floor_height"]])
            bv2 = bm.verts.new([vertex_2["x"], vertex_2["y"], back_sector["floor_height"]])
            bv3 = bm.verts.new([vertex_2["x"], vertex_2["y"], back_sector["ceiling_height"]])
            bv4 = bm.verts.new([vertex_1["x"], vertex_1["y"], back_sector["ceiling_height"]])

            bm.faces.new([bv1, bv2, bv3, bv4])

        # Render lines connecting sectors
        elif line["back_side"] > -1 and line["front_side"] > -1:
            front_side = sides[line["front_side"]]
            front_sector = sectors[front_side["sector"]]
            front_floor_height = front_sector["floor_height"]
            front_ceiling_height = front_sector["ceiling_height"]

            back_side = sides[line["back_side"]]
            back_sector = sectors[back_side["sector"]]
            back_floor_height = back_sector["floor_height"]
            back_ceiling_height = back_sector["ceiling_height"]

            addLineToSector(line, front_side["sector"])
            addLineToSector(line, back_side["sector"])

            lower_floor_height = min(front_floor_height, back_floor_height)
            upper_floor_height = max(front_floor_height, back_floor_height)
            lower_ceiling_height = min(front_ceiling_height, back_ceiling_height)
            upper_ceiling_height = max(front_ceiling_height, back_ceiling_height)

            # Render lower side
            if front_floor_height != back_floor_height:
                bv1 = bm.verts.new([vertex_1["x"], vertex_1["y"], lower_floor_height])
                bv2 = bm.verts.new([vertex_2["x"], vertex_2["y"], lower_floor_height])
                bv3 = bm.verts.new([vertex_2["x"], vertex_2["y"], upper_floor_height])
                bv4 = bm.verts.new([vertex_1["x"], vertex_1["y"], upper_floor_height])

                if front_floor_height < back_floor_height:
                    bm.faces.new([bv1, bv2, bv3, bv4])
                else:
                    bm.faces.new([bv2, bv1, bv4, bv3])

            # Render upper side
            if front_ceiling_height != back_ceiling_height:
                bv5 = bm.verts.new([vertex_1["x"], vertex_1["y"], lower_ceiling_height])
                bv6 = bm.verts.new([vertex_2["x"], vertex_2["y"], lower_ceiling_height])
                bv7 = bm.verts.new([vertex_2["x"], vertex_2["y"], upper_ceiling_height])
                bv8 = bm.verts.new([vertex_1["x"], vertex_1["y"], upper_ceiling_height])

                if front_ceiling_height > back_ceiling_height:
                    bm.faces.new([bv5, bv6, bv7, bv8])
                else:
                    bm.faces.new([bv6, bv5, bv8, bv7])

            # Render middle side
            bv3 = bm.verts.new([vertex_2["x"], vertex_2["y"], upper_floor_height])
            bv4 = bm.verts.new([vertex_1["x"], vertex_1["y"], upper_floor_height])
            bv5 = bm.verts.new([vertex_1["x"], vertex_1["y"], lower_ceiling_height])
            bv6 = bm.verts.new([vertex_2["x"], vertex_2["y"], lower_ceiling_height])

            if front_side["middle_texture"] != "-":
                bm.faces.new([bv4, bv3, bv6, bv5])

            if back_side["middle_texture"] != "-":
                bm.faces.new([bv3, bv4, bv5, bv6])

    # Render sectors
    for sector_index in sector_map:
        lines = sector_map[sector_index]
        floor_height = sectors[sector_index]["floor_height"]

        points = []

        # Render simple sectors
        for line in lines:
            v1 = line["vertex_1"]
            v2 = line["vertex_2"]

            vert = vertices[v1]
            points.append(Vector(([vert["x"], vert["y"], floor_height])))

            vert = vertices[v2]
            points.append(Vector(([vert["x"], vert["y"], floor_height])))

        tesselation = tessellate_polygon((points,))

        faces = []
        for tri in tesselation:
            verts = []
            for point in tri:
                verts.append(bm.verts.new(points[point]))
            faces.append(bm.faces.new(verts))

    bm.to_mesh(me)
    bm.free()

    ob = bpy.data.objects.new("MAP01", me)
    bpy.context.scene.objects.link(ob)

    print("\nFinished importing: %r in %.4f sec." % (filepath, (time.time() - time_main)))
    return {"FINISHED"}
