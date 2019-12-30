.. py:module:: vgio.quake.pak
.. py:currentmodule:: vgio.quake.pak

:py:mod:`pak` Module
====================

**Source code:** pak.py_

.. _pak.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/quake/pak.py

The :py:mod:`pak` module provides an :py:class:`PakFile` class which
derives from :py:class:`~vgio._core.ArchiveFile` and is used to read and write
Quake archive data.

.. autofunction:: vgio.quake.pak.is_pakfile

:py:class:`~vgio.quake.pak.PakFile` Class
------------------------------------------

.. autoclass:: vgio.quake.pak.PakFile()
    :members:

.. automethod:: PakFile.__init__
.. automethod:: PakFile.open
.. automethod:: PakFile.close
.. automethod:: PakFile.read
.. automethod:: PakFile.write
.. automethod:: PakFile.writestr
.. automethod:: PakFile.extract
.. automethod:: PakFile.extractall
.. automethod:: PakFile.getinfo
.. automethod:: PakFile.infolist
.. automethod:: PakFile.namelist

:py:class:`~vgio.quake.pak.PakInfo` Class
------------------------------------------

.. autoclass:: vgio.quake.pak.PakInfo()
    :members:

.. automethod:: PakInfo.__init__
