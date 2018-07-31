from setuptools import setup
from quake2 import __version__

setup(name='quake2-tools',
      version=__version__,
      description='Python API for Quake 2 File Formats',
      url='https://github.com/JoshuaSkelly/game-tools/quake2',
      author='Joshua Skelton',
      author_email='joshua.skelton@gmail.com',
      license='MIT',
      packages=['quake2'])
