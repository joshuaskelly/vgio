.. py:module:: vgio.quake2.pak
.. py:currentmodule:: vgio.quake2.pak

:py:mod:`pak` Module
====================

**Source code:** pak.py_

.. _pak.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/quake2/pak.py

The :py:mod:`pak` module provides an :py:class:`PakFile` class which
derives from :py:class:`ArchiveFile` and is used to read and write
Quake archive data.

.. autofunction:: vgio.quake2.pak.is_pakfile

:py:class:`~vgio.quake2.pak.PakFile` Class
------------------------------------------

.. autoclass:: vgio.quake2.pak.PakFile()
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

:py:class:`~vgio.quake2.pak.PakInfo` Class
------------------------------------------

.. autoclass:: vgio.quake2.pak.PakInfo()
    :members:

.. automethod:: PakInfo.__init__
