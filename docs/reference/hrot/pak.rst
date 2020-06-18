.. py:module:: vgio.hrot.pak
.. py:currentmodule:: vgio.hrot.pak

:py:mod:`pak` Module
====================

**Source code:** pak.py_

.. _pak.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/hrot/pak.py

The :py:mod:`pak` module provides an :py:class:`PakFile` class which
derives from :py:class:`~vgio._core.ArchiveFile` and is used to read and write
Quake archive data.

.. autofunction:: vgio.hrot.pak.is_pakfile

:py:class:`~vgio.hrot.pak.PakFile` Class
------------------------------------------

.. autoclass:: vgio.hrot.pak.PakFile()
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

:py:class:`~vgio.hrot.pak.PakInfo` Class
------------------------------------------

.. autoclass:: vgio.hrot.pak.PakInfo()
    :members:

.. automethod:: PakInfo.__init__
