"""Command line utility for creating and creating WAD files from BSP files

Supported Games:
    - QUAKE
"""

import argparse
import io
import os
import sys

from quake import bsp, wad


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


parser = Parser(prog='bsp2wad',
                description='Default action is to create a wad archive from '
                            'miptextures extracted from the file.',
                epilog='example: bsp2wad {0} => creates the wad file {1}'.format('e1m1.bsp', 'e1m1.wad'))

parser.add_argument('file', metavar='file.bsp', action=ResolvePathAction, help='wad file to ')
parser.add_argument('-d', metavar='file.wad', default=os.getcwd(), dest='dest', action=ResolvePathAction, help='extract textures from file.bsp into file.wad')
parser.add_argument('-q', dest='quiet', action='store_true', help='quiet mode')

args = parser.parse_args()

print(args.file)

if not bsp.is_bspfile(args.file):
    print('{0}: cannot find or open {1}'.format(parser.prog, args.file),
          file=sys.stderr)
    sys.exit(1)

bsp_file = bsp.Bsp.open(args.file)

if not args.dest:
    wad_path = os.path.dirname(args.file)
    wad_name = os.path.basename(args.file).split('.')[0] + '.wad'
    args.dest = os.path.join(wad_path, wad_name)

if not os.path.exists(os.path.dirname(args.dest)):
    os.makedirs(os.path.dirname(args.dest))

with wad.WadFile(args.dest, mode='w') as wad_file:
    if not args.quiet:
        print('Archive: %s' % os.path.basename(args.file))

    for miptex in bsp_file.miptextures:
        buff = io.BytesIO()
        bsp.Miptexture.write(buff, miptex)
        buff.seek(0)

        info = wad.WadInfo(miptex.name)
        info.file_size = 40 + len(miptex.pixels)
        info.disk_size = info.file_size
        info.compression = wad.CMP_NONE
        info.type = wad.TYPE_MIPTEX

        if not args.quiet:
            print(' adding: %s' % info.filename)

        wad_file.write_info(info, buff)

sys.exit(0)
