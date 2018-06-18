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

__version__ = '1.0.0'

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


class TempPakFileHandler(Handler):
    """A Watchdog handler that maintains a list of files to be written out to 
    the target pak file.
    """

    def __init__(self, context, working_directory, **kwargs):
        super().__init__(**kwargs)
        self.context = context
        self.working_directory = working_directory

    def on_modified(self, event):
        self.context['dirty'] = True

        if args.verbose:
            print('{0} modified'.format(os.path.relpath(event.src_path, self.working_directory)))

        rel_path = os.path.relpath(event.src_path, self.working_directory)
        with open(event.src_path, 'rb') as file:
            files[rel_path] = file.read()

    def on_created(self, event):
        self.context['dirty'] = True

        if args.verbose:
            print('{0} created'.format(os.path.relpath(event.src_path, self.working_directory)))

        rel_path = os.path.relpath(event.src_path, self.working_directory)

        with open(event.src_path, 'rb') as file:
            files[rel_path] = file.read()

    def on_deleted(self, event):
        self.context['dirty'] = True

        if args.verbose:
            print('{0} deleted'.format(os.path.relpath(event.src_path, self.working_directory)))

        rel_path = os.path.relpath(event.src_path, self.working_directory)
        files.pop(rel_path, None)

    def on_moved(self, event):
        self.context['dirty'] = True

        if args.verbose:
            print('{0} moved'.format(os.path.relpath(event.src_path, self.working_directory)))

        rel_src_path = os.path.relpath(event.src_path, self.working_directory)
        rel_dest_path = os.path.relpath(event.dest_path, self.working_directory)

        files[rel_dest_path] = files.pop(rel_src_path, None)


class PlatformHelper(object):
    """A static helper class for performing OS specific tasks."""

    @staticmethod
    def temp_volume():
        """Creates a temporary volume and returns the path to it.
        
        Notes:
            Darwin:
                The MacOS implementation creates a ram drive.
                
            Win32:
                The Windows implementation creates a temporary directory and 
                uses the SUBST command to make it appear as a drive.
                
            Linux:
                The Linux implementation defaults to using a temporary 
                directory.
        
        Returns:
            A path to the created volume.
        """

        if sys.platform == 'darwin':
            disk_name = os.path.basename(args.file).upper()
            td = '/Volumes/{0}'.format(disk_name)

            if os.path.exists(td):
                subprocess.run('diskutil unmount {0}'.format(td), shell=True)

            print('Mounting {0} to {1}'.format(os.path.basename(args.file), td))
            subprocess.run("diskutil erasevolume HFS+ '{0}' `hdiutil attach -nomount ram://262144`".format(disk_name), stdout=subprocess.DEVNULL, shell=True)

            return td

        elif sys.platform == 'win32':
            td = tempfile.mkdtemp()
            drive = 'Q:\\'

            if os.path.exists(drive):
                subprocess.run('subst /D {0}'.format(drive[:2]), stdout=subprocess.DEVNULL, shell=True)

            print('Mounting {0} to {1}'.format(os.path.basename(args.file), drive))
            subprocess.run('subst Q: {0}'.format(td), stdout=subprocess.DEVNULL, shell=True)

            return drive

        else:
            td = tempfile.mkdtemp()
            print('Mounting {0} to {1}'.format(os.path.basename(args.file), td))

            return td

    @staticmethod
    def unmount_temp_volume(path):
        """Unmounts the given volume
        
        Notes:
            Darwin:
                The MacOS implementation unmounts the ram drive.
                
            Win32:
                The Windows implementation deletes the temporary files and uses
                the SUBST command to remove the drive.
                
            Linux:
                Deletes the temporary directory.
        
        Args:
            path: The path to the volume to unmount.
        """

        if sys.platform == 'darwin':
            if os.path.exists(path):
                subprocess.run('diskutil unmount {0}'.format(path), stdout=subprocess.DEVNULL, shell=True)

        elif sys.platform == 'win32':
            if os.path.exists(path):
                shutil.rmtree(path)
                subprocess.run('subst /D Q:', stdout=subprocess.DEVNULL, shell=True)

        else:
            shutil.rmtree(path)

    @staticmethod
    def open_file_browser(path):
        """Opens a file browser at the given path.
        
        Args:
            path: The location to be opened.
        """
        if sys.platform == 'darwin':
            subprocess.run('open %s' % path, stdout=subprocess.DEVNULL, shell=True)

        elif sys.platform == 'win32':
            subprocess.run('start %s' % path, stdout=subprocess.DEVNULL, shell=True)

        elif sys.platform == 'linux':
            subprocess.run('xdg-open %s' % path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

        else:
            raise


class ResolvePathAction(argparse.Action):
    """Helper class to resolve user paths"""
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

    parser.add_argument('--verbose',
                        dest='verbose',
                        action='store_true',
                        help='verbose mode')

    parser.add_argument('-v', '--version',
                        dest='version',
                        action='version',
                        help=argparse.SUPPRESS,
                        version='{} version {}'.format(parser.prog, __version__))

    args = parser.parse_args()

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

    temp_directory = PlatformHelper.temp_volume()

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
    handler = TempPakFileHandler(context, temp_directory, ignore_patterns=['*/.DS_Store', '*/Thumbs.db'], ignore_directories=True)
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
    PlatformHelper.unmount_temp_volume(temp_directory)

    sys.exit(0)
