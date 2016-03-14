=======
Pybtex!
=======

.. container:: download-links

    `Bitbucket page`_ | |download_url|_ (:doc:`what's new <docs:history>`) | :doc:`docs <docs:index>`


.. meta::
    :description: Pybtex is a BibTeX-compatible bibliography processor written in Python.
    :keywords: Python, BibTeX


Pybtex is a BibTeX-compatible bibliography processor written in Python.\ |br|
You can simply type ``pybtex`` instead of ``bibtex``.

.. rst-class:: doc-links

    For more details, see the :doc:`docs:index`.


How Pybtex is different from BibTeX
===================================

Pybtex aims to be 100% compatible with BibTeX.
It accepts the same command line options, fully supports BibTeX's ``.bst``
styles and produces byte-identical output (if not, please `file a bug
report`_).

Additionally,

* Pybtex is Unicode-aware.

* Pybtex supports :doc:`bibliography formats <docs:formats>` other than BibTeX.

* It is possible to write formatting styles in Python.\ |br|
  As a bonus, Pythonic styles can produce HTML, Markdown and other markup
  besides the usual LaTeX.

Pybtex also includes a :doc:`Python API <docs:api/index>` for managing
bibliographies from Python.


Download and install
====================

Release tarballs are available from our `PyPI page
<https://pypi.python.org/pypi/pybtex>`_.

Pybtex can be also installed with pip:

.. sourcecode:: bash

    pip install pybtex

Development sources are available from our `Git repository at Bitbucket
<Bitbucket page_>`_:

.. sourcecode:: bash

    git clone https://bitbucket.org/pybtex-devs/pybtex

If something goes wrong, just `file a bug report`_.

Have fun!


.. _file a bug report: https://bitbucket.org/pybtex-devs/pybtex/issues?status=new&status=open
.. _Bitbucket page: https://bitbucket.org/pybtex-devs/pybtex
