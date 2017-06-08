"""Command line utility for mounting a PAK file as a logical volume

Supported Games:
    - QUAKE

Notes:
    Watchdog will raise an uncatchable exception if it attempts to walk a
    directory that it does not have read permissions to.

    dirsnapshot.py
        In the walk function defined in the constructor I added an os.access()
        check to the recursive call:

        if S_ISDIR(st.st_mode) and os.access(path, os.R_OK):
"""

import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler as Handler

from quake import pak


# Fix for frozen packages
def handleSIGINT(signum, frame):
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handleSIGINT)


blacklisted_files = '.DS_Store', '.Trashes'


def ignore_blacklisted_files(func):
    def inner(*args, **kwargs):
        event = args[1]
        filename = os.path.basename(event.src_path)

        if filename in blacklisted_files:
            return

        return func(*args, **kwargs)

    return inner


def ignore_directories(func):
    def inner(*args, **kwargs):
        event = args[1]
        if os.path.isdir(event.src_path):
            return None

        return func(*args, **kwargs)

    return inner


class TempPakFileHandler(Handler):
    @ignore_directories
    @ignore_blacklisted_files
    def on_modified(self, event):
        context['dirty'] = True

        if args.verbose:
            print('{0} modified'.format(os.path.relpath(event.src_path, temp_directory)))

        rel_path = os.path.relpath(event.src_path, temp_directory)
        with open(event.src_path, 'rb') as file:
            files[rel_path] = file.read()

    @ignore_directories
    @ignore_blacklisted_files
    def on_created(self, event):
        context['dirty'] = True

        if args.verbose:
            print('{0} created'.format(os.path.relpath(event.src_path, temp_directory)))

        rel_path = os.path.relpath(event.src_path, temp_directory)
        with open(event.src_path, 'rb') as file:
            files[rel_path] = file.read()

    @ignore_directories
    @ignore_blacklisted_files
    def on_deleted(self, event):
        context['dirty'] = True

        if args.verbose:
            print('{0} deleted'.format(os.path.relpath(event.src_path, temp_directory)))

        rel_path = os.path.relpath(event.src_path, temp_directory)
        files.pop(rel_path, None)

    @ignore_directories
    @ignore_blacklisted_files
    def on_moved(self, event):
        context['dirty'] = True

        if args.verbose:
            print('{0} moved'.format(os.path.relpath(event.src_path, temp_directory)))

        rel_src_path = os.path.relpath(event.src_path, temp_directory)
        rel_dest_path = os.path.relpath(event.dest_path, temp_directory)

        files[rel_dest_path] = files.pop(rel_src_path)


class PlatformHelper(object):
    @staticmethod
    def temp_directory():
        if sys.platform == 'darwin':
            disk_name = os.path.basename(args.file).upper()
            td = '/Volumes/{0}'.format(disk_name)

            if os.path.exists(td):
                subprocess.run('diskutil unmount {0}'.format(td), shell=True)

            print('Mounting {0} to {1}'.format(os.path.basename(args.file), td))

            subprocess.run("diskutil erasevolume HFS+ '{0}' `hdiutil attach -nomount ram://262144`".format(disk_name), stdout=subprocess.DEVNULL, shell=True)

            return td

        else:
            td = tempfile.mkdtemp()
            print('Mounting {0} to {1}'.format(os.path.basename(args.file), td))

            return td

    @staticmethod
    def clean_up_temp_directory(path):
        if sys.platform == 'darwin':
            if os.path.exists(path):
                subprocess.call('diskutil unmount {0}'.format(path), shell=True)

        else:
            shutil.rmtree(path)

    @staticmethod
    def open_file_browser(path):
        if sys.platform == 'darwin':
            subprocess.run('open %s' % path, shell=True)

        elif sys.platform == 'win32':
            subprocess.run('start %s' % path, shell=True)

        elif sys.platform == 'linux':
            subprocess.run('xdg-open %s' % path, shell=True)

        else:
            raise


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


parser = Parser(prog='qmount',
                description='Default action is to mount the given pak file as a logical volume.',
                epilog='example: qmount TEST.PAK => mounts TEST.PAK as a logical volume.')

parser.add_argument('file',
                    metavar='file.pak',
                    action=ResolvePathAction,
                    help='pak file to mount')

parser.add_argument('-f', '--file-browser',
                    dest='open_file_browser',
                    action='store_true',
                    help='opens a file browser once mounted')

parser.add_argument('-v', '--verbose',
                    dest='verbose',
                    action='store_true',
                    help='verbose mode')

args = parser.parse_args()

STDOUT = subprocess.DEVNULL

if args.verbose:
    STDOUT = subprocess.STDOUT

dir = os.path.dirname(args.file) or '.'
if not os.path.exists(dir):
    os.makedirs(dir)

context = {'dirty': False}
files = {}

# If the pak file exists put the contents into the file dictionary
if os.path.exists(args.file):
    with pak.PakFile(args.file) as pak_file:
        for info in pak_file.infolist():
            name = info.filename
            files[name] = pak_file.read(name)
else:
    context['dirty'] = True

temp_directory = PlatformHelper.temp_directory()

# Copy pak file contents into the temporary directory
for filename in files:
    abs_path = os.path.join(temp_directory, filename)
    dir = os.path.dirname(abs_path)

    if not os.path.exists(dir):
        os.makedirs(dir)

    with open(abs_path, 'wb') as out_file:
        out_file.write(files[filename])

# Open a native file browser
if args.open_file_browser:
    PlatformHelper.open_file_browser(temp_directory)

# Start file watching
observer = Observer()
handler = TempPakFileHandler(ignore_patterns=['*/.DS_Store'])
handler.start = temp_directory
observer.schedule(handler, path=temp_directory, recursive=True)

print('Press Ctrl+C to save and quit')

observer.start()

# Wait for user to terminate
try:
    while True:
        time.sleep(1)

        # Detect the deletion of the watched directory.
        if not os.path.exists(temp_directory):
            raise KeyboardInterrupt

except KeyboardInterrupt:
    print()
    try:
        observer.stop()

    except:
        """This is a temporary workaround. Watchdog will raise an exception
        if the watched media is ejected."""

observer.join()

# Write out updated files
if context['dirty']:
    print('Updating changes to {0}'.format(os.path.basename(args.file)))

    with pak.PakFile(args.file, 'w') as pak_file:
        for filename in files:
            pak_file.writestr(filename, files[filename])

else:
    print('No changes detected to {0}'.format(os.path.basename(args.file)))

# Clean up temp directory
PlatformHelper.clean_up_temp_directory(temp_directory)

sys.exit(0)
