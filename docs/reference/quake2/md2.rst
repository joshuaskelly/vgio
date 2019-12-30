.. py:module:: vgio.quake2.md2
.. py:currentmodule:: vgio.quake2.md2

:py:mod:`md2` Module
====================

**Source code:** md2.py_

.. _md2.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/quake2/md2.py

The :py:mod:`md2` module provides an :py:class:`Md2` class which derives
from :py:class:`~vgio._core.ReadWriteFile` and is used to read and write Quake
md2 data.

.. autofunction:: is_md2file

:py:class:`~vgio.quake2.md2.Md2` Class
--------------------------------------

.. autoclass:: vgio.quake2.md2.Md2
    :members:

.. automethod:: vgio.quake2.md2.Md2.__init__
.. automethod:: vgio.quake2.md2.Md2.open
.. automethod:: vgio.quake2.md2.Md2.close
.. automethod:: vgio.quake2.md2.Md2.save

:py:class:`~vgio.quake2.md2.Skin` Class
---------------------------------------

.. autoclass:: vgio.quake2.md2.Skin
    :members:

.. automethod:: vgio.quake2.md2.Skin.__init__
.. automethod:: vgio.quake2.md2.Skin.read
.. automethod:: vgio.quake2.md2.Skin.write

:py:class:`~vgio.quake2.md2.TriVertex` Class
--------------------------------------------

.. autoclass:: vgio.quake2.md2.TriVertex
    :members:

.. automethod:: vgio.quake2.md2.TriVertex.__init__
.. automethod:: vgio.quake2.md2.TriVertex.read
.. automethod:: vgio.quake2.md2.TriVertex.write

:py:class:`~vgio.quake2.md2.StVertex` Class
-------------------------------------------

.. autoclass:: vgio.quake2.md2.StVertex
    :members:

.. automethod:: vgio.quake2.md2.StVertex.__init__
.. automethod:: vgio.quake2.md2.StVertex.read
.. automethod:: vgio.quake2.md2.StVertex.write

:py:class:`~vgio.quake2.md2.Triangle` Class
-------------------------------------------

.. autoclass:: vgio.quake2.md2.Triangle
    :members:

.. automethod:: vgio.quake2.md2.Triangle.__init__
.. automethod:: vgio.quake2.md2.Triangle.read
.. automethod:: vgio.quake2.md2.Triangle.write

:py:class:`~vgio.quake2.md2.Frame` Class
----------------------------------------

.. autoclass:: vgio.quake2.md2.Frame
    :members:

.. automethod:: vgio.quake2.md2.Frame.__init__
.. automethod:: vgio.quake2.md2.Frame.read
.. automethod:: vgio.quake2.md2.Frame.write

:py:class:`~vgio.quake2.md2.GlVertex` Class
-------------------------------------------

.. autoclass:: vgio.quake2.md2.GlVertex
    :members:

.. automethod:: vgio.quake2.md2.GlVertex.__init__
.. automethod:: vgio.quake2.md2.GlVertex.read
.. automethod:: vgio.quake2.md2.GlVertex.write

:py:class:`~vgio.quake2.md2.GlCommand` Class
--------------------------------------------

.. autoclass:: vgio.quake2.md2.GlCommand
    :members:

.. automethod:: vgio.quake2.md2.GlCommand.__init__
.. automethod:: vgio.quake2.md2.GlCommand.read
.. automethod:: vgio.quake2.md2.GlCommand.write
