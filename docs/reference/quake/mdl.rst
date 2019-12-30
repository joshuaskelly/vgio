.. py:module:: vgio.quake.mdl
.. py:currentmodule:: vgio.quake.mdl

:py:mod:`mdl` Module
====================

**Source code:** mdl.py_

.. _mdl.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/quake/mdl.py

The :py:mod:`mdl` module provides an :py:class:`Mdl` class which derives
from :py:class:`ReadWriteFile` and is used to read and write Quake mdl data.

.. autofunction:: vgio.quake.mdl.is_mdlfile

:py:class:`~vgio.quake.mdl.Mdl` Class
-------------------------------------

.. autoclass:: vgio.quake.mdl.Mdl
    :members:
    :exclude-members: image, mesh, validate

.. automethod:: vgio.quake.mdl.Mdl.__init__
.. automethod:: vgio.quake.mdl.Mdl.open
.. automethod:: vgio.quake.mdl.Mdl.close
.. automethod:: vgio.quake.mdl.Mdl.save

:py:class:`~vgio.quake.mdl.Skin` Class
--------------------------------------

.. autoclass:: vgio.quake.mdl.Skin
    :members:

.. automethod:: vgio.quake.mdl.Skin.__init__
.. automethod:: vgio.quake.mdl.Skin.read
.. automethod:: vgio.quake.mdl.Skin.write

:py:class:`~vgio.quake.mdl.SkinGroup` Class
-------------------------------------------

.. autoclass:: vgio.quake.mdl.SkinGroup
    :members:

.. automethod:: vgio.quake.mdl.SkinGroup.__init__
.. automethod:: vgio.quake.mdl.SkinGroup.read
.. automethod:: vgio.quake.mdl.SkinGroup.write

:py:class:`~vgio.quake.mdl.StVertex` Class
------------------------------------------

.. autoclass:: vgio.quake.mdl.StVertex
    :members:

.. automethod:: vgio.quake.mdl.StVertex.__init__
.. automethod:: vgio.quake.mdl.StVertex.read
.. automethod:: vgio.quake.mdl.StVertex.write

:py:class:`~vgio.quake.mdl.Triangle` Class
------------------------------------------

.. autoclass:: vgio.quake.mdl.Triangle
    :members:

.. automethod:: vgio.quake.mdl.Triangle.__init__
.. automethod:: vgio.quake.mdl.Triangle.read
.. automethod:: vgio.quake.mdl.Triangle.write

:py:class:`~vgio.quake.mdl.TriVertex` Class
-------------------------------------------

.. autoclass:: vgio.quake.mdl.TriVertex
    :members:

.. automethod:: vgio.quake.mdl.TriVertex.__init__
.. automethod:: vgio.quake.mdl.TriVertex.read
.. automethod:: vgio.quake.mdl.TriVertex.write

:py:class:`~vgio.quake.mdl.Frame` Class
---------------------------------------

.. autoclass:: vgio.quake.mdl.Frame
    :members:

.. automethod:: vgio.quake.mdl.Frame.__init__
.. automethod:: vgio.quake.mdl.Frame.read
.. automethod:: vgio.quake.mdl.Frame.write

:py:class:`~vgio.quake.mdl.FrameGroup` Class
--------------------------------------------

.. autoclass:: vgio.quake.mdl.FrameGroup
    :members:

.. automethod:: vgio.quake.mdl.FrameGroup.__init__
.. automethod:: vgio.quake.mdl.FrameGroup.read
.. automethod:: vgio.quake.mdl.FrameGroup.write
