.. py:module:: vgio.hexen2.bsp
.. py:currentmodule:: vgio.hexen2.bsp

:py:mod:`bsp` Module
=======================

**Source code:** bsp.py_

.. _bsp.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/hexen2/bsp.py

The :py:mod:`bsp` module provides an :py:class:`Bsp` class which derives
from :py:class:`~vgio.quake.bsp.bsp29.Bsp` and is used to read and write Hexen 2
bsp data.

.. autofunction:: is_bspfile

:py:class:`~vgio.hexen2.bsp.Bsp` Class
----------------------------------------------

.. autoclass:: vgio.hexen2.bsp.Bsp
    :members:
    :exclude-members: image, mesh, validate

.. automethod:: vgio.hexen2.bsp.Bsp.__init__
.. automethod:: vgio.hexen2.bsp.Bsp.open
.. automethod:: vgio.hexen2.bsp.Bsp.close
.. automethod:: vgio.hexen2.bsp.Bsp.save

:py:class:`~vgio.hexen2.bsp.Model` Class
---------------------------------------------

.. autoclass:: vgio.hexen2.bsp.Model
    :members:

.. automethod:: vgio.hexen2.bsp.Model.__init__
.. automethod:: vgio.hexen2.bsp.Model.read
.. automethod:: vgio.hexen2.bsp.Model.write
