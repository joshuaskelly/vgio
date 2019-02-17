"""Command line utility for creating and manipulating ART files

Supported Games:
    - Duke Nukem 3D
"""

import argparse
import os
import sys

import numpy
from PIL import Image

from duke3d import art


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


if __name__ == '__main__':
    parser = Parser(prog='art',
                    description='Default action is to add or replace tiles into '
                                'art files entries from list.\nIf list is omitted, art will '
                                'use stdin.',
                    epilog='example: art {0} {1} => appends {1} to {0}'.format('tex.art', 'image.png'))

    parser.add_argument('file',
                        metavar='file.art',
                        action=ResolvePathAction,
                        help='art file to add tiles to')

    parser.add_argument('list',
                        nargs='*',
                        action=ResolvePathAction,
                        default=[t.strip('\n') for t in sys.stdin] if not sys.stdin.isatty() else None)

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

    with art.ArtFile(args.file, filemode) as art_file:
        if not args.quiet:
            print('Archive: %s' % os.path.basename(args.file))

        # Flatten out palette
        palette = []
        for p in art.default_palette:
            palette += p

        # Create palette image for Image.quantize()
        palette_image = Image.frombytes('P', (16, 16), bytes(palette))
        palette_image.putpalette(palette)

        # Process input files
        for index, file in enumerate(args.list):
            try:
                img = Image.open(file).convert(mode='RGB')
                img = img.quantize(palette=palette_image)
                width, height = img.size

                data = numpy.fromstring(img.tobytes(), '<B')
                data = data.reshape(width, height)
                data = data.transpose()
                data = data.tobytes()

                info = art.ArtInfo(str(index))
                info.file_size = len(data)
                info.tile_dimensions = width, height

                if not args.quiet:
                    print('  adding: %s' % index)

                art_file.writebytes(info, data)

            except:
                print('{0}: error: {1}'.format(parser.prog, sys.exc_info()[1]), file=sys.stderr)

    sys.exit(0)
