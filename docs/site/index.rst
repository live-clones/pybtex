=======
Pybtex!
=======

.. container:: download-links

    Current version is |download_url|_ (`see what's new <docs/history.html>`_)


Pybtex is a drop-in replacement for BibTeX written in Python.
You can start using it right now by simply typing ``pybtex`` where you would have typed ``bibtex``.

Please note that the correct spelling is just *Pybtex*, without any camel-casing,
which we considered too annoying to type.

We also suggest reading `the Friendly Manual <docs>`_, although it is
still incomplete.


Oh! Is it really BibTeX-compatible?
===================================

Yes, it really is, most of the time.

BibTeX styles work fine with Pybtex,
although there are still some minor issues.
Nevertheless, we are going to achieve 100% compatibility before releasing
version 1.0.

If something does not work for you, just `let us know
<https://bitbucket.org/pybtex-devs/pybtex/issues/new>`_.


But why should I use it instead of BibTeX?
==========================================

You probably should not if you ask. But still, Pybtex has Unicode inside.
It supports BibTeXML and YAML. It can write HTML and plain text.
It is extensible and fun to hack. It comes with a free database conversion utility.
And designing new bibliography styles is no more a pain with Pybtex'
brand new :doc:`pythonic style API <docs:api/styles>`.

Hmm nice. Wrap it up, I'll take it! Where is the download link?
===============================================================
.. _download:

Release tarballs are available from our `PyPI page
<https://pypi.python.org/pypi/pybtex>`_.

Development sources are available from our `Git repository at Bitbucket
<https://bitbucket.org/pybtex-devs/pybtex>`_:

.. sourcecode:: bash

    git clone https://bitbucket.org/pybtex-devs/pybtex

To run the tests (need `nose <https://nose.readthedocs.org/>`_):

.. sourcecode:: bash

    cd pybtex
    python setup.py egg_info  # or python setup.py develop
    python setup.py nosetests

Pybtex can be also installed with pip:

.. sourcecode:: bash

    pip install pybtex

If something goes wrong, just `file a bug report
<https://bitbucket.org/pybtex-devs/pybtex/issues/new>`_.

Have fun!


.. _file a bug report: https://bitbucket.org/pybtex-devs/pybtex/issues/new
