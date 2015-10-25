=============================
Extending Pybtex with plugins
=============================


.. contents::
    :local:


Pybtex uses plugins for bibliography formats, markup formans and formatting
styles. This allows to add new formats or styles to Pybtex withoud modifying
Pybtex itself.

The plugins are based on `Setuptools' entry points <Setuptools' documentation_>`_.


Entry Points
============

Here is the list of entry points supported by Pybtex:


pybtex.database.input
---------------------

This entry point is used for bibliography parsers.
Must point to a subclass of :py:class:`pybtex.database.input.BaseParser`.

There is also an additional entry point called ``pybtex.database.output.suffixes``.
It is used for registering bibliography formats for specific file suffixes
(like BibTeX for ``.bib``).

For example, a JSON input plugin for Pybtex could use these entry points:

.. sourcecode:: ini

    [pybtex.database.input]
    json = pybtexjson:JSONParser

    [pybtex.database.input.suffixes]
    .json = pybtexjson:JSONParser


pybtex.database.output
----------------------

This entry poing is used for bibliography writers.
Must point to a subclass of :py:class:`pybtex.database.output.BaseWriter`.

There is also an additional entry point called ``pybtex.database.output.suffixes``.
It is used for registering default plugins for specific file suffixes in the
same way as ``pybtex.database.input.suffixes`` described above.


pybtex.backends
---------------

This entry point is for adding new markup types for Pythonic bibliography
styles. Existing plugins are ``latex``, ``html``, ``markdown``, and ``plaintext``.
Must point to a :py:class:`pybtex.backends.BaseBackend`
subclass.


pybtex.style.formatting
-----------------------

Pythonic bibliography styles themselves. Must point to a
:py:class:`pybtex.style.formatting.BaseStyle` subclass.


pybtex.style.labels
-------------------

Label styles for Pythonic bibliography styles.


pybtex.style.names
------------------

Name styles for Pythonic bibliography styles.



Registering Plugins
===================

see `Setuptools' documentation`_.


.. _Setuptools' documentation: https://pythonhosted.org/setuptools/setuptools.html#extensible-applications-and-frameworks


Example Plugins
===============

An example project directory with two simple plugins and a ``setup.py`` file can
be found in the :source:`examples/sample_plugins` subdirectory.
