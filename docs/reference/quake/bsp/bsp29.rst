.. py:module:: vgio.quake.bsp.bsp29
.. py:currentmodule:: vgio.quake.bsp.bsp29

:py:mod:`bsp29` Module
======================

**Source code:** bsp29.py_

.. _bsp29.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/quake/bsp/bsp29.py

The :py:mod:`bsp29` module provides an :py:class:`Bsp` class which derives
from :py:class:`~vgio._core.ReadWriteFile` and is used to read and write Quake
bsp29 data.

.. autofunction:: is_bspfile

:py:class:`~vgio.quake.bsp.bsp29.Bsp` Class
---------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.Bsp
    :members:
    :exclude-members: image, mesh, validate

.. automethod:: vgio.quake.bsp.bsp29.Bsp.__init__
.. automethod:: vgio.quake.bsp.bsp29.Bsp.open
.. automethod:: vgio.quake.bsp.bsp29.Bsp.close
.. automethod:: vgio.quake.bsp.bsp29.Bsp.save

:py:class:`~vgio.quake.bsp.bsp29.Plane` Class
---------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.Plane
    :members:

.. automethod:: vgio.quake.bsp.bsp29.Plane.__init__
.. automethod:: vgio.quake.bsp.bsp29.Plane.read
.. automethod:: vgio.quake.bsp.bsp29.Plane.write

:py:class:`~vgio.quake.bsp.bsp29.Miptexture` Class
--------------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.Miptexture
    :members:

.. automethod:: vgio.quake.bsp.bsp29.Miptexture.__init__
.. automethod:: vgio.quake.bsp.bsp29.Miptexture.read
.. automethod:: vgio.quake.bsp.bsp29.Miptexture.write

:py:class:`~vgio.quake.bsp.bsp29.Vertex` Class
----------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.Vertex
    :members:

.. automethod:: vgio.quake.bsp.bsp29.Vertex.__init__
.. automethod:: vgio.quake.bsp.bsp29.Vertex.read
.. automethod:: vgio.quake.bsp.bsp29.Vertex.write

:py:class:`~vgio.quake.bsp.bsp29.Node` Class
--------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.Node
    :members:

.. automethod:: vgio.quake.bsp.bsp29.Node.__init__
.. automethod:: vgio.quake.bsp.bsp29.Node.read
.. automethod:: vgio.quake.bsp.bsp29.Node.write

:py:class:`~vgio.quake.bsp.bsp29.TextureInfo` Class
---------------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.TextureInfo
    :members:

.. automethod:: vgio.quake.bsp.bsp29.TextureInfo.__init__
.. automethod:: vgio.quake.bsp.bsp29.TextureInfo.read
.. automethod:: vgio.quake.bsp.bsp29.TextureInfo.write

:py:class:`~vgio.quake.bsp.bsp29.Face` Class
--------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.Face
    :members:

.. automethod:: vgio.quake.bsp.bsp29.Face.__init__
.. automethod:: vgio.quake.bsp.bsp29.Face.read
.. automethod:: vgio.quake.bsp.bsp29.Face.write

:py:class:`~vgio.quake.bsp.bsp29.ClipNode` Class
------------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.ClipNode
    :members:

.. automethod:: vgio.quake.bsp.bsp29.ClipNode.__init__
.. automethod:: vgio.quake.bsp.bsp29.ClipNode.read
.. automethod:: vgio.quake.bsp.bsp29.ClipNode.write

:py:class:`~vgio.quake.bsp.bsp29.Leaf` Class
--------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.Leaf
    :members:

.. automethod:: vgio.quake.bsp.bsp29.Leaf.__init__
.. automethod:: vgio.quake.bsp.bsp29.Leaf.read
.. automethod:: vgio.quake.bsp.bsp29.Leaf.write

:py:class:`~vgio.quake.bsp.bsp29.Edge` Class
--------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.Edge
    :members:

.. automethod:: vgio.quake.bsp.bsp29.Edge.__init__
.. automethod:: vgio.quake.bsp.bsp29.Edge.read
.. automethod:: vgio.quake.bsp.bsp29.Edge.write

:py:class:`~vgio.quake.bsp.bsp29.Model` Class
---------------------------------------------

.. autoclass:: vgio.quake.bsp.bsp29.Model
    :members:

.. automethod:: vgio.quake.bsp.bsp29.Model.__init__
.. automethod:: vgio.quake.bsp.bsp29.Model.read
.. automethod:: vgio.quake.bsp.bsp29.Model.write
