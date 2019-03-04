from setuptools import setup, find_packages
from vgio import __version__

setup(name='vgio',
      version=__version__,
      description='Video Game IO',
      url='https://github.com/JoshuaSkelly/vgio',
      author='Joshua Skelton',
      author_email='joshua.skelton@gmail.com',
      license='MIT',
      packages=find_packages(exclude=('tests', '*.tests', '*.tests.*'))
)