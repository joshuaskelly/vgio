.. py:module:: vgio.quake.wad
.. py:currentmodule:: vgio.quake.wad

:py:mod:`wad` Module
====================

**Source code:** wad.py_

.. _wad.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/quake/wad.py

The :py:mod:`wad` module provides an :py:class:`WadFile` class which
derives from :py:class:`~vgio._core.ArchiveFile` and is used to read and write
Quake archive data.

.. autofunction:: vgio.quake.wad.is_wadfile

:py:class:`~vgio.quake.wad.WadFile` Class
-----------------------------------------

.. autoclass:: vgio.quake.wad.WadFile()
    :members:

.. automethod:: WadFile.__init__
.. automethod:: WadFile.open
.. automethod:: WadFile.close
.. automethod:: WadFile.read
.. automethod:: WadFile.write
.. automethod:: WadFile.writestr
.. automethod:: WadFile.extract
.. automethod:: WadFile.extractall
.. automethod:: WadFile.getinfo
.. automethod:: WadFile.infolist
.. automethod:: WadFile.namelist

:py:class:`~vgio.quake.wad.WadInfo` Class
-----------------------------------------

.. autoclass:: vgio.quake.wad.WadInfo()
    :members:

.. automethod:: WadInfo.__init__
