"""Command line utility for creating and creating WAD files from BSP files

Supported Games:
    - QUAKE
"""

__version__ = '0.0.1'

import argparse
import os
import sys

import numpy as np
import svgwrite

from quake import bsp
from bsphelper import Bsp
from common import Parser, ResolvePathAction

if __name__ == '__main__':
    parser = Parser(prog='bsp2svg',
                    description='Default action is to create an svg document '
                                'from the given bsp file.',
                    epilog='example: bsp2svg {0} => creates the svg file {1}'.format('e1m1.bsp', 'e1m1.svg'))

    parser.add_argument('file',
                        metavar='file.bsp',
                        action=ResolvePathAction)

    parser.add_argument('-d',
                        metavar='file.svg',
                        dest='dest',
                        default=os.getcwd(),
                        action=ResolvePathAction,
                        help='svg file to create')

    parser.add_argument('-q',
                        dest='quiet',
                        action='store_true',
                        help='quiet mode')

    parser.add_argument('-v', '--version',
                        dest='version',
                        action='version',
                        help=argparse.SUPPRESS,
                        version='{} version {}'.format(parser.prog, __version__))

    args = parser.parse_args()

    if not bsp.is_bspfile(args.file):
        print('{0}: cannot find or open {1}'.format(parser.prog, args.file), file=sys.stderr)

    # Validate or create out file
    if args.dest == os.getcwd():
        svg_path = os.path.dirname(args.file)
        svg_name = os.path.basename(args.file).split('.')[0] + '.svg'
        args.dest = os.path.join(svg_path, svg_name)

    dest_dir = os.path.dirname(args.dest) or '.'
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    bsp_file = Bsp.open(args.file)

    vs = [vertex[:] for model in bsp_file.models for face in model.faces for vertex in face.vertexes]
    xs = [v[0] for v in vs]
    ys = [v[1] for v in vs]

    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)

    width = max_x - min_x
    height = max_y - min_y
    padding_x = width // 10
    padding_y = height // 10

    dwg = svgwrite.Drawing(args.dest, size=(width + padding_x * 2, height + padding_y * 2), profile='tiny')
    group = dwg.g()
    dwg.add(group)

    processed_edges = []

    for model in bsp_file.models:
        for face in model.faces:
            vertexes = face.vertexes

            # Disregard vertical faces
            #a = np.subtract(vertexes[0][:], vertexes[1][:])
            #b = np.subtract(vertexes[0][:], vertexes[2][:])
            #normal = np.cross(a, b)
            #if normal[2] == 0:
            #    continue

            # Transform 3D into 2D!
            points = [tuple(v[:2]) for v in vertexes]
            points = list(map(lambda x: (x[0] - (min_x - padding_x), x[1] - (min_y - padding_y)), points))

            group.add(dwg.polygon(points,
                                stroke=svgwrite.rgb(0, 0, 0, '%'),
                                stroke_width=1,
                                fill='none'
                                ))

    dwg.save()

    sys.exit(0)
