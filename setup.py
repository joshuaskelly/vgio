from setuptools import setup, find_packages
from vgio import __version__

with open('README.md') as readme_file:
    long_description = readme_file.read()

setup(
    name='vgio',
    version=__version__,
    description='Video Game IO',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/JoshuaSkelly/vgio',
    author='Joshua Skelton',
    author_email='joshua.skelton@gmail.com',
    license='MIT',
    packages=find_packages(exclude=('tests', '*.tests', '*.tests.*'))
)
