"""Command line utility for creating and creating SPR files from image files

Supported Games:
    - QUAKE
"""


__version__ = '1.0.0'

import argparse
import os
import struct
import sys

from PIL import Image

from quake import spr


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
    parser = Parser(prog='image2spr',
                    description='Default action is to convert an image file(s)'
                                ' to an spr.\nIf image file is omitted, '
                                'image2spr will use stdin.',
                    epilog='example: image2spr {1} {0} => converts {0} to {1}'.format('anim.gif', 'anim.spr'))

    parser.add_argument('dest_file',
                        metavar='file.spr',
                        action=ResolvePathAction,
                        help='spr file to create')

    parser.add_argument('source_files',
                        nargs='*',
                        metavar='file.gif',
                        action=ResolvePathAction,
                        #default=[t.strip('\n') for t in sys.stdin] if not sys.stdin.isatty() else None,
                        help='image source file')

    parser.add_argument('-q',
                        dest='quiet',
                        action='store_true',
                        help='quiet mode')

    parser.add_argument('-v', '--version',
                        dest='version',
                        action='version',
                        help=argparse.SUPPRESS,
                        version='{} version {}'.format(parser.prog, __version__))

    args = parser.parse_args()

    # Flatten out palette
    quake_palette = [channel for rgb in spr.default_palette for channel in rgb]

    # Create palette image for Image.quantize()
    quake_palette_image = Image.frombytes('P', (16, 16), bytes(quake_palette))
    quake_palette_image.putpalette(quake_palette)

    images = []

    # Build a list of source images
    for source_file in args.source_files:
        if not os.path.exists(source_file):
            print('{0}: cannot find or open {1}'.format(parser.prog, source_file), file=sys.stderr)
            continue

        # Open source image
        source_image = Image.open(source_file)
        size = source_image.size
        source_mode = source_image.mode
        global_transparency = source_image.info.get('transparency')

        # Decompose the source image frames into a sequence of images
        try:
            while True:
                if source_image.mode != 'P':
                    alpha = source_image.split()[-1]

                    # Set all alpha pixels to a known color
                    source_image = source_image.convert('RGB')

                    mask = Image.eval(alpha, lambda a: 255 if a <=128 else 0)
                    transparent_color = tuple(quake_palette[-3:])
                    source_image.paste(transparent_color, mask)
                    source_image.info['transparency'] = 255

                    source_image = source_image.quantize(palette=quake_palette_image)
                    source_image.putpalette(bytes(quake_palette))

                # Set the current palette's transparent color to Quake's
                local_transparency = source_image.info.get('transparency')
                source_palette = source_image.palette.palette
                source_palette = list(struct.unpack('{}B'.format(len(source_palette)), source_palette))

                if local_transparency:
                    source_palette[local_transparency * 3:local_transparency * 3 + 3] = spr.default_palette[-1]

                if global_transparency and global_transparency != local_transparency:
                    source_palette[global_transparency * 3:global_transparency * 3 + 3] = spr.default_palette[-1]

                source_palette = bytes(source_palette)

                # Create new image from current frame
                data = source_image.tobytes()
                sub_image = Image.frombytes('P', size, data, 'raw', 'P', 0, 1)
                sub_image.info['transparency'] = local_transparency
                sub_image.putpalette(source_palette)

                # Convert from indexed color to RGB color then quantize to Quake's palette
                sub_image = sub_image.convert('RGB', dither=None)
                sub_image = sub_image.quantize(palette=quake_palette_image)
                sub_image.info['transparency'] = 255
                sub_image.putpalette(bytes(quake_palette))
                images.append(sub_image)
                source_image.seek(source_image.tell() + 1)

        except EOFError:
            pass

    if not images:
        print('{0}: no usable source images given'.format(parser.prog), file=sys.stderr)
        sys.exit(1)

    # Build Quake sprite
    with spr.Spr.open(args.dest_file, 'w') as spr_file:
        spr_file.width, spr_file.height = size
        spr_file.number_of_frames = len(images)

        origin = -size[0] // 2, size[1] // 2

        for image in images:
            frame = spr.SpriteFrame()
            frame.width, frame.height = size
            frame.origin = origin
            data = image.tobytes()
            data = struct.unpack('{}B'.format(frame.width * frame.height), data)
            frame.pixels = data
            spr_file.frames.append(frame)

    sys.exit(0)
