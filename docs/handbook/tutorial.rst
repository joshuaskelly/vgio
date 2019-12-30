Tutorial
========

Using a ReadWriteFile Class
---------------------------

The most common way of working with video game file formats in the
:py:mod:`vgio` library is a class derived from the
:py:class:`~vgio._core.ReadWriteFile` class. You can create instances of this
class by loading from a file or from scratch.

To load a video game file format object from a file use the
:py:data:`open(file, mode='r')` classmethod on the derived
:py:class:`~vgio._core.ReadWriteFile` class. Because
:py:class:`~vgio._core.ReadWriteFile` is a base class this example will use the
Quake :py:class:`~vgio.quake.mdl.Mdl` model format::

    >>> from vgio.quake.mdl import Mdl
    >>> mdl_file = Mdl.open('armor.mdl')

If successful, it will return an :py:class:`~vgio.quake.mdl.Mdl` object. You
can now use instance attributes to examine the file contents::

    >>> print(mdl_file.version)
    6
    >>> print(mdl_file.identifier)
    b'IDPO'

Using an ArchiveFile Class
--------------------------

It is a common for video games to bundle their files in an archive and
the :py:mod:`vgio` library provides classes derived from
:py:class:`~vgio._core.ArchiveFile` to work with that data.

An :py:class:`~vgio._core.ArchiveFile` object must be created using a file or
file-like object. The :py:class:`~vgio._core.ArchiveFile` is a base class so
this example will use the Duke3D :py:class:`~vgio.duke3d.grp.GrpFile` archive
format::

    >>> from vgio.duke3d.grp import GrpFile
    >>> grp_file = GrpFile('DUKE3D.GRP')

If successful, it will return an :py:class:`~vgio.duke3d.grp.GrpFile` object.
You can now use instance attributes and methods to examine the file contents::

    >>> info = grp_file.infolist()[0]
    >>> print(info.filename)
    LOGO.ANM
    >>> print(info.file_size)
    1507336
