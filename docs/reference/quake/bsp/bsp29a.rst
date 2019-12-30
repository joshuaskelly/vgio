.. py:module:: vgio.quake.bsp.bsp29a
.. py:currentmodule:: vgio.quake.bsp.bsp29a

:py:mod:`bsp29a` Module
=======================

**Source code:** bsp29a.py_

.. _bsp29a.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/quake/bsp/bsp29a.py

The :py:mod:`bsp29a` module provides an :py:class:`Bsp` class which derives
from :py:class:`ReadWriteFile` and is used to read and write Quake bsp29a data.

.. autofunction:: is_bspfile

:py:class:`~vgio.quake.bsp.bsp29a.Bsp` Class
----------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29a.Bsp
    :members:
    :exclude-members: image, mesh, validate

.. automethod:: vgio.quake.bsp.bsp29a.Bsp.__init__
.. automethod:: vgio.quake.bsp.bsp29a.Bsp.open
.. automethod:: vgio.quake.bsp.bsp29a.Bsp.close
.. automethod:: vgio.quake.bsp.bsp29a.Bsp.save

:py:class:`~vgio.quake.bsp.bsp29a.Node` Class
---------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29a.Node
    :members:

.. automethod:: vgio.quake.bsp.bsp29a.Node.__init__
.. automethod:: vgio.quake.bsp.bsp29a.Node.read
.. automethod:: vgio.quake.bsp.bsp29a.Node.write

:py:class:`~vgio.quake.bsp.bsp29a.Face` Class
---------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29a.Face
    :members:

.. automethod:: vgio.quake.bsp.bsp29a.Face.__init__
.. automethod:: vgio.quake.bsp.bsp29a.Face.read
.. automethod:: vgio.quake.bsp.bsp29a.Face.write

:py:class:`~vgio.quake.bsp.bsp29a.ClipNode` Class
-------------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29a.ClipNode
    :members:

.. automethod:: vgio.quake.bsp.bsp29a.ClipNode.__init__
.. automethod:: vgio.quake.bsp.bsp29a.ClipNode.read
.. automethod:: vgio.quake.bsp.bsp29a.ClipNode.write

:py:class:`~vgio.quake.bsp.bsp29a.Leaf` Class
---------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29a.Leaf
    :members:

.. automethod:: vgio.quake.bsp.bsp29a.Leaf.__init__
.. automethod:: vgio.quake.bsp.bsp29a.Leaf.read
.. automethod:: vgio.quake.bsp.bsp29a.Leaf.write

:py:class:`~vgio.quake.bsp.bsp29a.Edge` Class
---------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29a.Edge
    :members:

.. automethod:: vgio.quake.bsp.bsp29a.Edge.__init__
.. automethod:: vgio.quake.bsp.bsp29a.Edge.read
.. automethod:: vgio.quake.bsp.bsp29a.Edge.write

