.. py:module:: vgio.quake.spr
.. py:currentmodule:: vgio.quake.spr

:py:mod:`spr` Module
====================

**Source code:** spr.py_

.. _spr.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/quake/spr.py

The :py:mod:`spr` module provides an :py:class:`Spr` class which derives
from :py:class:`ReadWriteFile` and is used to read and write Quake spr data.

.. autofunction:: vgio.quake.spr.is_sprfile

:py:class:`~vgio.quake.spr.Spr` Class
-------------------------------------

.. autoclass:: vgio.quake.spr.Spr
    :members:
    :exclude-members: image, validate

.. automethod:: vgio.quake.spr.Spr.__init__
.. automethod:: vgio.quake.spr.Spr.open
.. automethod:: vgio.quake.spr.Spr.close
.. automethod:: vgio.quake.spr.Spr.save

:py:class:`~vgio.quake.spr.SpriteFrame` Class
---------------------------------------------

.. autoclass:: vgio.quake.spr.SpriteFrame
    :members:

.. automethod:: vgio.quake.spr.SpriteFrame.__init__
.. automethod:: vgio.quake.spr.SpriteFrame.read
.. automethod:: vgio.quake.spr.SpriteFrame.write

:py:class:`~vgio.quake.spr.SpriteGroup` Class
---------------------------------------------

.. autoclass:: vgio.quake.spr.SpriteGroup
    :members:

.. automethod:: vgio.quake.spr.SpriteGroup.__init__
.. automethod:: vgio.quake.spr.SpriteGroup.read
.. automethod:: vgio.quake.spr.SpriteGroup.write
