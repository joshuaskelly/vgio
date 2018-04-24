"""Command line utility for extracting files from PAK files

Supported Games:
    - QUAKE
"""

import argparse
import os
import sys
from tabulate import tabulate

from quake import pak


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
    parser = Parser(prog='unpak',
                    description='Default action is to extract files to xdir.',
                    epilog='example: unpak PAK0.PAK -d {0} => extract all files to {0}'.format(os.path.expanduser('./extracted')))

    parser.add_argument('file',
                        metavar='file.pak',
                        action=ResolvePathAction)

    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='list files')

    parser.add_argument('-d',
                        metavar='xdir',
                        dest='dest',
                        default=os.getcwd(),
                        action=ResolvePathAction,
                        help='extract files into xdir')

    parser.add_argument('-q',
                        dest='quiet',
                        action='store_true',
                        help='quiet mode')

    args = parser.parse_args()

    if not pak.is_pakfile(args.file):
        print('{0}: cannot find or open {1}'.format(parser.prog, args.file), file=sys.stderr)
        sys.exit(1)

    if args.list:
        with pak.PakFile(args.file) as pak_file:
            info_list = sorted(pak_file.infolist(), key=lambda i: i.filename)

            headers = ['Length', 'Name']
            table = [[i.file_size, i.filename] for i in info_list]
            length = sum([i.file_size for i in info_list])
            count = len(info_list)
            table.append([length, '%d file%s' % (count, 's' if count == 1 else '')])

            separator = []
            for i in range(len(headers)):
                t = max(len(str(length)), len(headers[i]) + 2)
                separator.append('-' * t)

            table.insert(-1, separator)

            print('Archive: %s' % os.path.basename(args.file))
            print(tabulate(table, headers=headers))

            sys.exit(0)

    with pak.PakFile(args.file) as pak_file:
        info_list = pak_file.infolist()
        for item in sorted(info_list, key=lambda i: i.filename):
            filename = item.filename
            fullpath = os.path.join(args.dest, filename)

            if not args.quiet:
                print(' extracting: %s' % fullpath)

            try:
                pak_file.extract(filename, args.dest)
            except:
                print('{0}: error: {1}'.format(parser.prog, sys.exc_info()[0]), file=sys.stderr)

    sys.exit(0)
