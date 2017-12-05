from setuptools import setup
from quake import __version__

setup(name='quake-tools',
      version=__version__,
      description='Python API for Quake File Formats',
      url='https://github.com/JoshuaSkelly/game-tools/quake',
      author='Joshua Skelton',
      author_email='joshua.skelton@gmail.com',
      license='MIT',
      packages=['quake'])
