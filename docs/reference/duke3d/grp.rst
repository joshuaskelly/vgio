.. py:module:: vgio.duke3d.grp
.. py:currentmodule:: vgio.duke3d.grp

:py:mod:`grp` Module
====================

**Source code:** grp.py_

.. _grp.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/duke3d/grp.py

The :py:mod:`grp` module provides an :py:class:`GrpFile` class which
derives from :py:class:`ArchiveFile` and is used to read and write
Duke3D archive data.

.. autofunction:: vgio.duke3d.grp.is_grpfile

:py:class:`~vgio.duke3d.grp.GrpFile` Class
------------------------------------------

.. autoclass:: vgio.duke3d.grp.GrpFile()
    :members:

.. automethod:: GrpFile.__init__
.. automethod:: GrpFile.open
.. automethod:: GrpFile.close
.. automethod:: GrpFile.read
.. automethod:: GrpFile.write
.. automethod:: GrpFile.writestr
.. automethod:: GrpFile.extract
.. automethod:: GrpFile.extractall
.. automethod:: GrpFile.getinfo
.. automethod:: GrpFile.infolist
.. automethod:: GrpFile.namelist

:py:class:`~vgio.duke3d.grp.GrpInfo` Class
------------------------------------------

.. autoclass:: vgio.duke3d.grp.GrpInfo()
    :members:

.. automethod:: GrpInfo.__init__
