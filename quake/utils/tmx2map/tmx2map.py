"""Command line utility for creating and creating WAD files from BSP files

Supported Games:
    - QUAKE
"""

import argparse
import os
import sys

import tmx

from quake import map


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


parser = Parser(prog='tmx2map',
                description='Default action is to create a map file from a tmx tilemap',
                epilog='example: tmx2map {0} {1} => creates the map file {2}'.format('e1m1.tmx', 'tile_mappings.json', 'e1m1.map'))

parser.add_argument('file',
                    metavar='file.bsp',
                    action=ResolvePathAction,
                    help='bsp file to extract from')

parser.add_argument('mapping',
                    metavar='mapping.json',
                    action=ResolvePathAction,
                    help='json tile mapping file')

parser.add_argument('-d',
                    metavar='file.map',
                    dest='dest',
                    default=os.getcwd(),
                    action=ResolvePathAction,
                    help='wad file to create')

parser.add_argument('-q',
                    dest='quiet',
                    action='store_true',
                    help='quiet mode')

args = parser.parse_args()

print(args.file)

tmx_file = tmx.TileMap.load(args.file)

# Resolve path to map file
if args.dest == os.getcwd():
    map_path = os.path.dirname(args.file)
    map_name = os.path.basename(args.file).split('.')[0] + '.map'
    args.dest = os.path.join(map_path, map_name)

# Create the file path if needed
dir = os.path.dirname(args.dest) or '.'
if not os.path.exists(dir):
    os.makedirs(dir)

sys.exit(0)
