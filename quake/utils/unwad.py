"""Command line utility for extracting image files from WAD files

Supported Games:
    - QUAKE
"""

import array
import argparse
import os
import struct
import sys

from PIL import Image

from quake.bsp import BspMiptexture, miptexture_format, miptexture_size
from quake.lmp import Lmp, default_palette
from quake.wad import WadFile, is_wadfile


class ResolvePathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        fullpath = os.path.expanduser(values)
        setattr(namespace, self.dest, fullpath)


class Parser(argparse.ArgumentParser):
    """Simple wrapper class to provide help on error"""
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(1)


parser = Parser(prog='unwad',
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
    sys.exit(1)

if args.list:
    with WadFile(args.file) as wad_file:
        for filename in sorted(wad_file.namelist()):
            print(filename)

        sys.exit(0)

if not os.path.exists(args.dest):
    os.makedirs(args.dest)

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
                lmp = Lmp.open(lmp_file)
                size = lmp_file.width, lmp.height
                data = array.array('B', lmp.pixels)

        # Special cases
        elif item.type == 68:
            # Console characters
            if item.file_size == 128 * 128:
                size = 128, 128

                with wad_file.open(filename) as lmp:
                    data = lmp.read(item.file_size)

            else:
                # Miptextures
                try:
                    with wad_file.open(filename) as mip_file:
                        mip_data = mip_file.read(miptexture_size)
                        mip_struct = struct.unpack(miptexture_format, mip_data)

                        mip = BspMiptexture(mip_struct)

                        # Calculate miptexture size using the simplified form
                        # of the geometric series where r = 1/4 and n = 4
                        pixels_size = mip.width * mip.height * 85 // 64
                        pixels_format = '<%dB' % pixels_size
                        pixels_data = struct.unpack(pixels_format, mip_file.read(pixels_size))

                        mip.pixels = pixels_data
                        data = mip.pixels[:mip.width * mip.height]
                        data = array.array('B', data)
                        size = mip.width, mip.height
                except:
                    print(' failed to extract resource: %s' % item.filename, file=sys.stderr)
                    continue

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

sys.exit(0)
