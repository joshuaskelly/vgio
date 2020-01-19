.. py:module:: vgio.quake.lmp
.. py:currentmodule:: vgio.quake.lmp

:py:mod:`lmp` Module
====================

**Source code:** lmp.py_

.. _lmp.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/quake/lmp.py

The :py:mod:`lmp` module provides an :py:class:`Lmp` class which derives
from :py:class:`~vgio._core.ReadWriteFile` and is used to read and write Quake
lmp data.

:py:class:`~vgio.quake.lmp.Lmp` Class
-------------------------------------

.. autoclass:: vgio.quake.lmp.Lmp
    :members:
    :exclude-members: image

.. automethod:: vgio.quake.lmp.Lmp.__init__
.. automethod:: vgio.quake.lmp.Lmp.open
.. automethod:: vgio.quake.lmp.Lmp.close
.. automethod:: vgio.quake.lmp.Lmp.save
