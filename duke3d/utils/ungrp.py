"""Command line utility for extracting image files from GRP files

Supported Games:
    - Duke Nukem 3D
"""

import argparse
import os
import sys
from tabulate import tabulate

from duke3d import grp


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


parser = Parser(prog='ungrp',
                description='Default action is to extract files to xdir.',
                epilog='example: ungrp duke3d.grp -d {0} => extract all files to {0}'.format(os.path.expanduser('./extracted')))

parser.add_argument('file', metavar='file.grp', action=ResolvePathAction)
parser.add_argument('-l', '--list', action='store_true', help='list files')
parser.add_argument('-d', metavar='xdir', default=os.getcwd(), dest='dest', action=ResolvePathAction, help='extract files into xdir')
parser.add_argument('-q', dest='quiet', action='store_true', help='quiet mode')

args = parser.parse_args()

if not grp.is_grpfile(args.file):
    print('{0}: cannot find or open {1}'.format(parser.prog, args.file), file=sys.stderr)
    sys.exit(1)

if args.list:
    with grp.GrpFile(args.file) as grp_file:
        info_list = sorted(grp_file.infolist(), key=lambda i: i.filename)

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

with grp.GrpFile(args.file) as grp_file:
    if not args.quiet:
        print('Archive: %s' % os.path.basename(args.file))

    for item in grp_file.infolist():
        filename = item.filename
        fullpath = os.path.join(args.dest, filename)

        # Extract as raw file
        grp_file.extract(filename, args.dest)

        if not args.quiet:
            print(' extracting: %s' % fullpath)

sys.exit(0)
