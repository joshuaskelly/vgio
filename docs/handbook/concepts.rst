Concepts
========

The :py:mod:`vgio` library provides an API to work with data stored in various
video game files formats. The library is structured such that games are
represented by subpackages and file formats are represented by modules.

Broadly speaking :py:mod:`vgio` places file formats into three categories.

Binary Data
-----------

Binary data is structured data that is written to a file as a sequence of bytes.
It is common for the data structure to be composed of other data structures.

:py:mod:`vgio` represents the primary binary data object of the format as a
:py:class:`~vgio._core.ReadWriteFile` object. Helper data structures have
simple :py:data:`read(file)` and :py:data:`write(file, object_)` classmethods.

Archive Data
------------

Archive data is a container for other types of data typically represented as
files. The :py:class:`~vgio._core.ArchiveFile` and :py:class:`~vgio._core.ArchiveInfo` serve as base classes for
working with such data. By design the :py:class:`~vgio._core.ArchiveFile` and
:py:class:`~vgio._core.ArchiveInfo` interfaces are identical to Python's
`ZipFile <https://docs.python.org/3/library/zipfile.html#zipfile-objects>`_ and
`ZipInfo <https://docs.python.org/3/library/zipfile.html#zipinfo-objects>`_
interfaces respectively.

Markup Data
-----------

Markup data is data that is expressed as structured plain text. :py:mod:`vgio` modules
that are markup based expose a similar interace as Python's
`json <https://docs.python.org/3/library/json.html>`_ module interface. Namely
:py:meth:`loads()` and :py:meth:`dumps()`.
