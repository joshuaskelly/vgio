"""Command line utility for extracting image files from ART files

Supported Games:
    - Duke Nukem 3D
"""

import argparse
import os
import sys

import numpy
from tabulate import tabulate

from PIL import Image

from duke3d import art


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


if __name__ == '__main__':
    parser = Parser(prog='unart',
                    description='Default action is to extract files to xdir.',
                    epilog='example: unart tiles001.art -d {0} => extract all files to {0}'.format(os.path.expanduser('./extracted')))

    parser.add_argument('file', metavar='file.art', action=ResolvePathAction)
    parser.add_argument('-l', '--list', action='store_true', help='list files')
    parser.add_argument('-d', metavar='xdir', default=os.getcwd(), dest='dest', action=ResolvePathAction, help='extract files into xdir')
    parser.add_argument('-q', dest='quiet', action='store_true', help='quiet mode')
    parser.add_argument('-f', dest='format', default='png', choices=['bmp','gif','png','tga'], help='image format to convert to')

    args = parser.parse_args()

    if not art.is_artfile(args.file):
        print('{0}: cannot find or open {1}'.format(parser.prog, args.file), file=sys.stderr)
        sys.exit(1)

    if args.list:
        with art.ArtFile(args.file) as art_file:
            info_list = sorted(art_file.infolist(), key=lambda i: i.filename)

            headers = ['Length', 'Name']
            table = [[i.file_size, i.filename] for i in info_list]
            length = sum([i.file_size for i in info_list])
            count = len(info_list)
            table.append([length, '', '%d file%s' % (count, 's' if count > 1 else '')])

            separator = []
            for i in range(len(headers)):
                t = max(len(str(length)), len(headers[i]) + 2)
                separator.append('-' * t)

            table.insert(-1, separator)

            print('Archive: %s' % os.path.basename(args.file))
            print(tabulate(table, headers=headers))

            sys.exit(0)

    if not os.path.exists(args.dest):
        os.makedirs(args.dest)

    with art.ArtFile(args.file) as art_file:
        if not args.quiet:
            print('Archive: %s' % os.path.basename(args.file))

        # Flatten out palette
        palette = []
        for p in art.default_palette:
            palette += p

        for item in art_file.infolist():
            filename = str(item.tile_index)
            size = item.tile_dimensions
            width, height = size
            fullpath = os.path.join(args.dest, filename)
            fullpath_ext = '{0}.{1}'.format(fullpath, args.format)

            if size == (0, 0):
                with open(fullpath_ext, 'w'):
                    pass

                continue

            pixels = art_file.read(item.tile_index)

            if not pixels:
                continue

            data = numpy.fromstring(pixels, '<B')
            data = data.reshape((width, height))
            data = data.transpose()

            img = Image.fromarray(data, 'P')
            img.putpalette(palette)
            img.save(fullpath_ext)

            if not args.quiet:
                print(' extracting: %s' % fullpath_ext)

    sys.exit(0)
