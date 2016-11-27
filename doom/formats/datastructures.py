from collections import namedtuple

Header = namedtuple('Header', 
    ('type',
     'directory_size',
     'directory_pointer')
    )

header_format = '<4s2i'

LineDef = namedtuple('LineDef',
    ('vertex_1',
     'vertex_2',
     'flags',
     'specials',
     'tag',
     'front_side',
     'back_side')
    )

linedef_format = '<7H'

LINEDEFS = {'typename': LineDef, 'format': linedef_format}

Node = namedtuple('Node',
    ('x',
     'y',
     'dx',
     'dy',
     "right_bounding_box_top",
     "right_bounding_box_bottom",
     "right_bounding_box_left",
     "right_bounding_box_right",
     "left_bounding_box_top",
     "left_bounding_box_bottom",
     "left_bounding_box_left",
     "left_bounding_box_right",
     "right_child",
     "left_child")
    )

node_format = '<12h2H'

NODES = {'typename': Node, 'format': node_format}

PlayPal = namedtuple('PlayPal', 
    ('r',
     'g',
     'b')
    )

playpal_format = '<3B'

PLAYPAL = {'typename': PlayPal, 'format': playpal_format}

SideDef = namedtuple('SideDef',
    ('x_offset',
     'y_offset',
     'top_texture',
     'bottom_texture',
     'middle_texture',
     'sector')
    )

sidedef_format = '<2h8s8s8sh'

SIDEDEFS = {'typename': SideDef, 'format': sidedef_format}

Sector = namedtuple('Sector',
    ('floor_height',
     'ceiling_height',
     'floor_texture',
     'ceiling_texture',
     'light_level',
     'special',
     'tag')
    )

sector_format = '<2h8s8s3h'

SECTORS = {'typename': Sector, 'format': sector_format}

Seg = namedtuple('Seg', 
    ('vertex_1',
     'vertex_2',
     'angle',
     'linedef',
     'side',
     'offset')
    )

seg_format = '<6h'

SEGS = {'typename': Seg, 'format': seg_format}

SSector = namedtuple('SSector', 
    ('number_of_segs',
     'first_seg')
    )

ssector_format = '<2h'

SSECTORS = {'typename': SSector, 'format': ssector_format}

Thing = namedtuple('Thing', 
    ('x',
     'y',
     'angle',
     'type',
     'options')
    )

thing_format = '<5h'

THINGS = {'typename': Thing, 'format': thing_format}

Vertex = namedtuple('Vertex', 
    ('x',
     'y')
    )

vertex_format = '<2h'

VERTEXES = {'typename': Vertex, 'format': vertex_format}