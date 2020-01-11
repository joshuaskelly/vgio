.. py:module:: vgio._core
.. py:currentmodule:: vgio._core

_core Subpackage
=================

**Source code:** `_core <https://github.com/joshuaskelly/vgio/tree/master/vgio/_core/__init__.py>`_

.. automodule:: vgio._core.__init__

:py:class:`~vgio._core.ReadWriteFile` Class
-------------------------------------------

.. autoclass:: vgio._core.ReadWriteFile
    :members:
    :exclude-members: open, close, save

.. automethod:: vgio._core.ReadWriteFile.open
.. automethod:: vgio._core.ReadWriteFile.close
.. automethod:: vgio._core.ReadWriteFile.save

:py:class:`~vgio._core.ArchiveFile` Class
-----------------------------------------

.. autoclass:: vgio._core.ArchiveFile
    :members:
    :exclude-members: open, close, read, write, writestr, extract, extractall, getinfo, infolist, namelist

.. automethod:: ArchiveFile.open
.. automethod:: ArchiveFile.close
.. automethod:: ArchiveFile.read
.. automethod:: ArchiveFile.write
.. automethod:: ArchiveFile.writestr
.. automethod:: ArchiveFile.extract
.. automethod:: ArchiveFile.extractall
.. automethod:: ArchiveFile.getinfo
.. automethod:: ArchiveFile.infolist
.. automethod:: ArchiveFile.namelist

:py:class:`~vgio._core.ArchiveInfo` Class
-----------------------------------------

.. autoclass:: vgio._core.ArchiveInfo
    :members:
    :exclude-members: from_file

.. automethod:: vgio._core.ArchiveInfo.from_file
