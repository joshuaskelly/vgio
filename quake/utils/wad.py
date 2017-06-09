"""Command line utility for creating and manipulating WAD files

Supported Games:
    - QUAKE
"""

import argparse
import io
import os
import struct
import sys

from PIL import Image

from quake import bsp, lmp, wad


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


parser = Parser(prog='wad',
                description='Default action is to add or replace wad files '
                            'entries from list.\nIf list is omitted, wad will '
                            'use stdin.',
                epilog='example: wad {0} {1} => adds {1} to {0}'.format('tex.wad', 'image.png'))

parser.add_argument('file',
                    metavar='file.wad',
                    action=ResolvePathAction,
                    help='wad file to ')

parser.add_argument('list',
                    nargs='*',
                    action=ResolvePathAction,
                    default=[t.strip('\n') for t in sys.stdin] if not sys.stdin.isatty() else None)

parser.add_argument('-t',
                    dest='type',
                    default='MIPTEX',
                    choices=['LUMP', 'QPIC', 'MIPTEX'])

parser.add_argument('-q',
                    dest='quiet',
                    action='store_true',
                    help='quiet mode')

args = parser.parse_args()

if not args.list:
    parser.error('the following arguments are required: list')

dir = os.path.dirname(args.file) or '.'
if not os.path.exists(dir):
    os.makedirs(dir)

filemode = 'a'
if not os.path.isfile(args.file):
    filemode = 'w'

with wad.WadFile(args.file, filemode) as wad_file:
    if not args.quiet:
        print('Archive: %s' % os.path.basename(args.file))

    # Flatten out palette
    palette = []
    for p in bsp.default_palette:
        palette += p

    # Create palette image for Image.quantize()
    palette_image = Image.frombytes('P', (16, 16), bytes(palette))
    palette_image.putpalette(palette)

    # Process input files
    for file in args.list:
        if args.type == 'LUMP':
            if not args.quiet:
                print('  adding: %s' % file)

            wad_file.write(file)

        elif args.type == 'QPIC':
            img = Image.open(file).convert(mode='RGB')
            img = img.quantize(palette=palette_image)
            pixels = img.tobytes()
            name = os.path.basename(file).split('.')[0]

            qpic = lmp.Lmp()
            qpic.width = img.width
            qpic.height = img.height
            qpic.pixels = pixels

            buff = io.BytesIO()
            lmp.Lmp.write(buff, qpic)
            file_size = buff.tell()
            buff.seek(0)

            info = wad.WadInfo(name)
            info.file_size = file_size
            info.disk_size = info.file_size
            info.compression = wad.CMP_NONE
            info.type = wad.TYPE_QPIC

            if not args.quiet:
                print('  adding: %s' % name)

            wad_file.writestr(info, buff)

        else:
            try:
                img = Image.open(file).convert(mode='RGB')
                img = img.quantize(palette=palette_image)

                name = os.path.basename(file).split('.')[0]

                mip = bsp.Miptexture()
                mip.name = name
                mip.width = img.width
                mip.height = img.height
                mip.offsets = [40]
                mip.pixels = []

                # Build mip maps
                for i in range(4):
                    resized_image = img.resize((img.width // pow(2, i), img.height // pow(2, i)))
                    data = resized_image.tobytes()
                    mip.pixels += struct.unpack('<%iB' % len(data), data)
                    if i < 3:
                        mip.offsets += [mip.offsets[-1] + len(data)]

                buff = io.BytesIO()
                bsp.Miptexture.write(buff, mip)
                buff.seek(0)

                info = wad.WadInfo(name)
                info.file_size = 40 + len(mip.pixels)
                info.disk_size = info.file_size
                info.compression = wad.CMP_NONE
                info.type = wad.TYPE_MIPTEX

                if not args.quiet:
                    print('  adding: %s' % name)

                wad_file.writestr(info, buff)

            except:
                print('{0}: error: {1}'.format(parser.prog, sys.exc_info()[1]), file=sys.stderr)

sys.exit(0)
