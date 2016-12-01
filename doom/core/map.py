class Map(object):
    valid_lumps = ['THINGS','LINEDEFS','SIDEDEFS','VERTEXES','SEGS','SSECTORS','NODES','SECTORS','REJECT','BLOCKMAP','BEHAVIOR','SCRIPTS']

    def __init__(self, map_struct):
        def load_lumps(lump_type):
            lump = map_struct[lump_type.LUMP_NAME]

            if not lump or not lump.data:
                return []

            return [lump_type(lump.data[i], i, self) for i in range(len(lump.data))] 

        self.name = map_struct[0].name
        self.vertexes = load_lumps(Vertex)
        self.sectors = load_lumps(Sector)
        self.sidedefs = load_lumps(SideDef)
        self.things = load_lumps(Thing)
        self.linedefs = load_lumps(LineDef)
        self.segs = load_lumps(Seg)
        self.ssectors = load_lumps(SSector)
        self.nodes = load_lumps(Node)
        self.reject = load_lumps(Reject)
        self.blockmap = load_lumps(BlockMap)

class Thing(object):
    LUMP_NAME = 'THINGS'

    def __init__(self, thing_struct, index, map):
        self.index = index
        self.x = thing_struct.x
        self.y = thing_struct.y
        self.angle = thing_struct.angle
        self.type = thing_struct.type
        self.options = thing_struct.options

class LineDefFlags(object):
    def __init__(self, flags):
        self.impassable     = flags & 1 << 0 > 0
        self.block_monsters = flags & 1 << 1 > 0
        self.two_sided      = flags & 1 << 2 > 0
        self.upper_unpegged = flags & 1 << 3 > 0
        self.lower_unpegged = flags & 1 << 4 > 0
        self.secret         = flags & 1 << 5 > 0
        self.block_sound    = flags & 1 << 6 > 0
        self.not_on_map     = flags & 1 << 7 > 0
        self.already_on_map = flags & 1 << 8 > 0

class LineDef(object):
    LUMP_NAME = 'LINEDEFS'

    def __init__(self, linedef_struct, index, map):
        self.index = index
        self.vertex_1 = map.vertexes[linedef_struct.vertex_1]
        self.vertex_2 = map.vertexes[linedef_struct.vertex_2]
        self.flags = LineDefFlags(linedef_struct.flags)
        self.specials = linedef_struct.specials
        self.tag = linedef_struct.tag
        self.front_side = map.sidedefs[linedef_struct.front_side] if linedef_struct.front_side < 65535 else None
        self.back_side = map.sidedefs[linedef_struct.back_side] if linedef_struct.back_side < 65535 else None

        self.segs = []
        self.front_side.linedef = self
        if self.back_side:
            self.back_side.linedef = self

class SideDef(object):
    LUMP_NAME = 'SIDEDEFS'

    def __init__(self, sidedef_struct, index, map):
        self.index = index
        self.x_offset = sidedef_struct.x_offset
        self.y_offset = sidedef_struct.y_offset
        self.top_texture = sidedef_struct.top_texture
        self.bottom_texture = sidedef_struct.bottom_texture
        self.middle_texture = sidedef_struct.middle_texture
        self.sector = map.sectors[sidedef_struct.sector]

        self.linedef = None
        self.segs = []
        self.sector.sidedefs.append(self)

class Vertex(object):
    LUMP_NAME = 'VERTEXES'

    def __init__(self, vertex_struct, index, map):
        self.index = index
        self.x = vertex_struct.x
        self.y = vertex_struct.y

class Seg(object):
    LUMP_NAME = 'SEGS'

    def __init__(self, seg_struct, index, map):
        self.index = index
        self.vertex_1 = map.vertexes[seg_struct.vertex_1]
        self.vertex_2 = map.vertexes[seg_struct.vertex_2]
        self.angle = seg_struct.angle
        self.linedef = map.linedefs[seg_struct.linedef]
        self.side = map.sidedefs[seg_struct.side]
        self.offset = seg_struct.offset

        self.linedef.segs.append(self)
        self.side.segs.append(self)

class SSector(object):
    LUMP_NAME = 'SSECTORS'
    
    def __init__(self, ssector_struct, index, map):
        self.index = index
        self.number_of_segs = ssector_struct.number_of_segs
        self.first_seg = map.segs[ssector_struct.first_seg]

class BoundingBox(object):
    def __init__(self, bottom, left, top, right):
        self.bottom = bottom
        self.left = left
        self.top = top
        self.right = right

class Node(object):
    LUMP_NAME = 'NODES'

    def __init__(self, node_struct, index, map):
        self.index = index
        self.x = node_struct.x
        self.y = node_struct.y
        self.dx = node_struct.dx
        self.dy = node_struct.dy
        self.right_bounding_box = BoundingBox(node_struct.right_bounding_box_bottom, node_struct.right_bounding_box_left, node_struct.right_bounding_box_top, node_struct.right_bounding_box_right)
        self.left_bounding_box = BoundingBox(node_struct.left_bounding_box_bottom, node_struct.left_bounding_box_left, node_struct.left_bounding_box_top, node_struct.left_bounding_box_right)
        self.right_child = node_struct.right_child
        self.left_child = node_struct.left_child

class Sector(object):
    LUMP_NAME = 'SECTORS'

    def __init__(self,sector_struct, index, map):
        self.index = index
        self.floor_height = sector_struct.floor_height
        self.ceiling_height = sector_struct.ceiling_height
        self.floor_texture = sector_struct.floor_texture
        self.ceiling_texture = sector_struct.ceiling_texture
        self.light_level = sector_struct.light_level
        self.special = sector_struct.special
        self.tag = sector_struct.tag

        self.sidedefs = []

class Reject(object):
    LUMP_NAME = 'REJECT'

    def __init__(self, reject_struct, index, map):
        self.index = index

class BlockMap(object):
    LUMP_NAME = 'BLOCKMAP'

    def __init__(self, blockmap_struct, index, map):
        self.index = index
