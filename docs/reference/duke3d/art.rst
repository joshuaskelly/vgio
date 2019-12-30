.. py:module:: vgio.duke3d.art
.. py:currentmodule:: vgio.duke3d.art

:py:mod:`art` Module
====================

**Source code:** art.py_

.. _art.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/duke3d/art.py

The :py:mod:`art` module provides an :py:class:`ArtFile` class which
derives from :py:class:`~vgio._core.ArchiveFile` and is used to read and write
Duke3D texture data.

.. autofunction:: vgio.duke3d.art.is_artfile

:py:class:`~vgio.duke3d.art.ArtFile` Class
------------------------------------------

.. autoclass:: vgio.duke3d.art.ArtFile()
    :members:

.. automethod:: ArtFile.__init__
.. automethod:: ArtFile.open
.. automethod:: ArtFile.close
.. automethod:: ArtFile.read
.. automethod:: ArtFile.write
.. automethod:: ArtFile.writestr
.. automethod:: ArtFile.extract
.. automethod:: ArtFile.extractall
.. automethod:: ArtFile.getinfo
.. automethod:: ArtFile.infolist
.. automethod:: ArtFile.namelist

:py:class:`~vgio.duke3d.art.ArtInfo` Class
------------------------------------------

.. autoclass:: vgio.duke3d.art.ArtInfo()

.. automethod:: ArtInfo.__init__
