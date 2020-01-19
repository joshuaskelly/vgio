.. py:module:: vgio.devildaggers.hxresourcegroup
.. py:currentmodule:: vgio.devildaggers.hxresourcegroup

:py:mod:`hxresourcegroup` Module
================================

**Source code:** hxresourcegroup.py_

.. _hxresourcegroup.py: https://github.com/joshuaskelly/vgio/tree/master/vgio/devildaggers/hxresourcegroup.py

The :py:mod:`hxresourcegroup` module provides an :py:class:`HxResourceGroupFile`
class which derives from :py:class:`~vgio._core.ArchiveFile` and is used to read
and write Devil Daggers archive data.

:py:class:`~vgio.devildaggers.hxresourcegroup.HxResourceGroupFile` Class
------------------------------------------------------------------------

.. autoclass:: vgio.devildaggers.hxresourcegroup.HxResourceGroupFile()
    :members:

.. automethod:: HxResourceGroupFile.__init__
.. automethod:: HxResourceGroupFile.open
.. automethod:: HxResourceGroupFile.close
.. automethod:: HxResourceGroupFile.read
.. automethod:: HxResourceGroupFile.write
.. automethod:: HxResourceGroupFile.writestr
.. automethod:: HxResourceGroupFile.extract
.. automethod:: HxResourceGroupFile.extractall
.. automethod:: HxResourceGroupFile.getinfo
.. automethod:: HxResourceGroupFile.infolist
.. automethod:: HxResourceGroupFile.namelist

:py:class:`~vgio.devildaggers.hxresourcegroup.ResourceGroupInfo` Class
----------------------------------------------------------------------

.. autoclass:: vgio.devildaggers.hxresourcegroup.ResourceGroupInfo()

.. automethod:: ResourceGroupInfo.__init__
.. automethod:: ResourceGroupInfo.from_file
