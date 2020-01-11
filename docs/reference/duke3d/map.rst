.. py:module:: vgio.duke3d.map
.. py:currentmodule:: vgio.duke3d.map

:py:mod:`map` Module
====================

**Source code:** map.py_

.. _map.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/duke3d/map.py

The :py:mod:`map` module provides an :py:class:`Map` class which
derives from :py:class:`~vgio._core.ReadWriteFile` and is used to read and write
Duke3D map data.

.. autofunction:: vgio.duke3d.map.is_mapfile

:py:class:`~vgio.duke3d.map.Map` Class
--------------------------------------

.. autoclass:: vgio.duke3d.map.Map
    :members:

.. automethod:: vgio.duke3d.map.Map.__init__
.. automethod:: vgio.duke3d.map.Map.open
.. automethod:: vgio.duke3d.map.Map.close
.. automethod:: vgio.duke3d.map.Map.save

:py:class:`~vgio.duke3d.map.Sector` Class
-----------------------------------------

.. autoclass:: vgio.duke3d.map.Sector
    :members:

.. automethod:: vgio.duke3d.map.Sector.__init__
.. automethod:: vgio.duke3d.map.Sector.read
.. automethod:: vgio.duke3d.map.Sector.write

:py:class:`~vgio.duke3d.map.Sprite` Class
-----------------------------------------

.. autoclass:: vgio.duke3d.map.Sprite
    :members:

.. automethod:: vgio.duke3d.map.Sprite.__init__
.. automethod:: vgio.duke3d.map.Sprite.read
.. automethod:: vgio.duke3d.map.Sprite.write

:py:class:`~vgio.duke3d.map.Wall` Class
---------------------------------------

.. autoclass:: vgio.duke3d.map.Wall
    :members:

.. automethod:: vgio.duke3d.map.Wall.__init__
.. automethod:: vgio.duke3d.map.Wall.read
.. automethod:: vgio.duke3d.map.Wall.write
