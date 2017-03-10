"""Command line utility for extracting image files from WAD files

Supported Games:
    - QUAKE
"""

import array
import argparse
import os
import sys

from PIL import Image

from quake.lmp import Lmp, default_palette
from quake.wad import WadFile, is_wadfile


class ResolvePathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        fullpath = os.path.expanduser(values)
        setattr(namespace, self.dest, fullpath)

parser = argparse.ArgumentParser(prog='unwad',
                                 description='Default action is to convert files to png format and extract to xdir.',
                                 epilog='example: unwad gfx.wad -d {0} => extract all files to {0}'.format(os.path.expanduser('./extracted')))

parser.add_argument('file', metavar='file.wad', action=ResolvePathAction)
parser.add_argument('-l', '--list', action='store_true', help='list files')
parser.add_argument('-d', metavar='xdir', default=os.getcwd(), dest='dest', action=ResolvePathAction, help='extract files into xdir')
parser.add_argument('-q', dest='quiet', action='store_true', help='quiet mode')
parser.add_argument('-f', dest='format', default='png', choices=['bmp','gif','png','tga'], help='image format to convert to')

args = parser.parse_args()

if not is_wadfile(args.file):
    print('{0}: cannot find or open {1}'.format(parser.prog, args.file), file=sys.stderr)
    quit(1)

if args.list:
    with WadFile(args.file) as wad_file:
        for filename in sorted(wad_file.namelist()):
            print(filename)

        quit(0)

with WadFile(args.file) as wad_file:
    # Flatten out palette
    palette = []
    for p in default_palette:
        palette += p

    for item in wad_file.infolist():
        filename = item.filename
        fullpath = os.path.join(args.dest, filename)
        fullpath_ext = '{0}.{1}'.format(fullpath, args.format)

        data = None
        size = None

        # Pictures
        if item.type == 66:
            with wad_file.open(filename) as lmp_file:
                lmp_file = Lmp.open(lmp_file)
                size = lmp_file.width, lmp_file.height
                data = array.array('B', lmp_file.pixels)

        # Special cases
        elif item.type == 68:
            # Console characters
            if item.file_size == 128 * 128:
                size = 128, 128
            else:
                print(' failed to determine size of resource: %s' % item.filename, file=sys.stderr)
                continue

            with wad_file.open(filename) as lmp:
                data = lmp.read(item.file_size)

        try:
            # Convert to image file
            if data is not None and size is not None:
                img = Image.frombuffer('P', size, data, 'raw', 'P', 0, 1)
                img.putpalette(palette)
                img.save(fullpath_ext)

                if not args.quiet:
                    print(' extracting: %s' % fullpath_ext)

            # Extract as raw file
            else:
                wad_file.extract(filename, args.dest)

                if not args.quiet:
                    print(' extracting: %s' % fullpath)
        except:
            print('{0}: error: {1}'.format(parser.prog, sys.exc_info()[0]), file=sys.stderr)
