"""Command line utility for extracting files from WAD files

Supported Games:
    - QUAKE
"""

import argparse
import os
import sys

from quake import wad
from quake.wad import WadFile

class ResolvePathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        fullpath = os.path.expanduser(values)
        setattr(namespace, self.dest, fullpath)

parser = argparse.ArgumentParser(prog='unwad',
                                 description='Default action is to extract files to xdir.',
                                 epilog='example: unwad gfx.wad -d {0} => extract all files to {0}'.format(os.path.expanduser('./extracted')))

parser.add_argument('file', metavar='file.wad', action=ResolvePathAction)
parser.add_argument('-l', '--list', action='store_true', help='list files')
parser.add_argument('-d', metavar='xdir', default=os.getcwd(), dest='dest', action=ResolvePathAction, help='extract files into xdir')
parser.add_argument('-q', dest='quiet', action='store_true', help='quiet mode')

args = parser.parse_args()

if not wad.is_wadfile(args.file):
    print('{0}: cannot find or open {1}'.format(parser.prog, args.file), file=sys.stderr)
    quit(1)

if (args.list):
    with WadFile(args.file) as wad_file:
        for filename in sorted(wad_file.namelist()):
            print(filename)

        quit(0)

with WadFile(args.file) as wad_file:
    info_list = wad_file.infolist()
    for item in sorted(info_list, key=lambda i: i.filename):
        filename = item.filename
        fullpath = os.path.join(args.dest, filename)

        if not args.quiet:
            print(' extracting: %s' % fullpath)

        try:
            wad_file.extract(filename, args.dest)
        except:
            print('{0}: error: {1}'.format(parser.prog, sys.exc_info()[0]), file=sys.stderr)
