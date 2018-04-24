"""Command line utility for creating and manipulating ART files

Supported Games:
    - Duke Nukem 3D
"""

import argparse
import os
import sys

import drawSvg
from duke3d import map


class BoundingBox(object):
    def __init__(self, point=None):
        self.min = None
        self.max = None

        if point:
            self.min = point[0], point[1]
            self.max = point[0], point[1]

    def extend(self, point):
        px, py = point

        if not self.min:
            self.min = point[0], point[1]
            self.max = point[0], point[1]

            return

        if px < self.min[0]:
            self.min = px, self.min[1]

        if px > self.max[0]:
            self.max = px, self.max[1]

        if py < self.min[1]:
            self.min = self.min[0], py

        if py > self.max[1]:
            self.max = self.max[0], py


class ResolvePathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, list):
            fullpath = [os.path.expanduser(v) for v in values]
        else:
            fullpath = os.path.expanduser(values)

        setattr(namespace, self.dest, fullpath)


class Parser(argparse.ArgumentParser):
    """Simple wrapper class to provide help on error"""
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(1)


parser = Parser(prog='map2svg',
                description='Default action is to convert the given map to svg',
                epilog='example: map2svg {0} => converts {0} to {1}'.format('e1l1.map', 'e1l1.svg'))

parser.add_argument('file',
                    metavar='file.map',
                    action=ResolvePathAction,
                    help='map file to convert to svg')

parser.add_argument('-q',
                    dest='quiet',
                    action='store_true',
                    help='quiet mode')

args = parser.parse_args()

dir = os.path.dirname(args.file) or '.'
if not os.path.exists(dir):
    os.makedirs(dir)

with map.Map.open(args.file, 'r') as map_file:
    if not args.quiet:
        print('Converting: %s' % os.path.basename(args.file))

    bounds = BoundingBox()
    for sector in map_file.sectors:
        current_wall = map_file.walls[sector.wall_pointer]

        for _ in range(sector.wall_number):
            bounds.extend((current_wall.x, current_wall.y))
            current_wall = map_file.walls[current_wall.point2]

    print(bounds)

    d = drawSvg.Drawing(65000, 65000, origin='center')

    for sector in map_file.sectors:
        current_wall = map_file.walls[sector.wall_pointer]
        current_point = current_wall.x, current_wall.y
        first_point = current_point

        p = drawSvg.Path(stroke_width=4, stroke='black')
        p.M(*current_point)

        for _ in range(sector.wall_number):
            next_wall = map_file.walls[current_wall.point2]
            next_point = next_wall.x, next_wall.y
            p.L(*next_point)
            current_wall = next_wall

        p.L(*first_point)
        p.Z()
        d.append(p)

    d.saveSvg('/Users/Joshua/Desktop/e1l1.svg')

sys.exit(0)
