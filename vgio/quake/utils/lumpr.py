"""Command line utility for creating and creating image files from SPR files

Supported Games:
    - QUAKE
"""

__version__ = '1.0.0'

import array
import argparse
import os
import struct
import sys

from PIL import Image

from vgio.quake import lmp
from .common import Parser, ResolvePathAction

if __name__ == '__main__':
    parser = Parser(prog='lumpr',
                    description='Default action is to convert a lmp file to an image and vice versa.',
                    epilog='examples: lumpr lump.lmp  => convert lump.lmp to lump.png')

    parser.add_argument('file',
                        action=ResolvePathAction)

    parser.add_argument('-v', '--version',
                        dest='version',
                        action='version',
                        help=argparse.SUPPRESS,
                        version='{} version {}'.format(parser.prog, __version__))

    args = parser.parse_args()

    # Flatten out palette
    palette = [channel for rgb in lmp.default_palette for channel in rgb]

    # Create palette image for Image.quantize()
    palette_image = Image.frombytes('P', (16, 16), bytes(palette))
    palette_image.putpalette(palette)

    # Convert image to lmp
    try:
        image_filename = os.path.basename(args.file)
        lmp_name = image_filename.split('.')[0] + '.lmp'
        lmp_path = os.path.join(os.path.dirname(args.file), lmp_name)

        source_image = Image.open(args.file)
        source_image = source_image.convert('RGB', dither=None)
        source_image = source_image.quantize(palette=palette_image)
        source_image.putpalette(bytes(palette))
        data = source_image.tobytes()
        img = Image.frombytes('P', source_image.size, data, 'raw', 'P', 0, 1)
        img.putpalette(bytes(palette))

        print('Converting {} to {}'.format(image_filename, lmp_name))

        with lmp.Lmp.open(lmp_path, 'w') as lmp_file:
            w, h = img.size
            lmp_file.width = w
            lmp_file.height = h
            data = img.tobytes()
            data = struct.unpack('{}B'.format(w * h), data)
            lmp_file.pixels = data

    # Convert lmp to image
    except OSError as e:
        lmp_filename = os.path.basename(args.file)
        image_name = lmp_filename.split('.')[0] + '.png'
        image_path = os.path.join(os.path.dirname(args.file), image_name)

        print('Converting {} to {}'.format(lmp_filename, image_name))

        with lmp.Lmp.open(args.file) as lmp_file:
            size = lmp_file.width, lmp_file.height
            data = array.array('B', lmp_file.pixels)
            img = Image.frombuffer('P', size, data, 'raw', 'P', 0, 1)
            img.putpalette(palette)
            img.save(image_path)

    sys.exit(0)
