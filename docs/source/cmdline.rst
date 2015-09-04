======================
Command line interface
======================

.. highlight:: sh


Making bibliographies with :command:`pybtex`
============================================

:command:`pybtex` executable is fully compatible with :command:`bibtex` and accepts the same command line options.
So you basically just type :command:`pybtex` instead of :command:`bibtex`.

For example, to compile a LaTex file named :file:`book.tex`, you run:

.. code-block:: shell

    $ latex book
    $ pybtex book
    $ latex book
    $ latex book  # to get cross-references right


.. todo:: link to BibTeX manual


Bibliography formats other then BibTeX
--------------------------------------

.. todo::
    link to BibTeX format description

Besides standard :file:`.bib` files, Pybtex supports bibliography data
in other formats. A (short) list of supported formats can bee seen in :command:`pybtex --help` output.

By default, BibTeX format is used. That is, if your LaTeX file contains:

.. code-block:: latex

    \bibliogrpahy{report}

Pybtex will try to read the bibliography data from a file named :file:`report.bib`.
You can change that with the :option:`-f` option:

.. code-block:: shell

    $ pybtex -f yaml book

(In this case Pybtex will look for a YAML-formatted file :file:`report.yaml` instead of
`report.bib`).

Support for additional bibliography formats can be added by :doc:`plugins <api/plugins>`.

    
Pythonic bibliography styles
----------------------------

BibTeX has a particular built-in programming language for defining
bibliography formatting styles, and Pybtex supports it too. Basically, it
looks like this:

.. code-block:: bst

    FUNCTION {new.block}
    { output.state before.all =
        'skip$
        { after.block 'output.state := }
      if$
    }

Usually it is hidden inside :file:`.bst` files and you don't have to worry
about that unless you are designing your own BibTeX styles.

Additionally, Pybtex allows writing bibliography styles in Python (although
this feature is still experimental and under development).
Some base BibTeX styles, including ``plain``, ``alpha``, ``unsrt`` have been already ported to Python.
They can be found in :file:`pybtex/style/formatting` subdirectory in Pybtex sources. Additional styles can be added as :doc:`plugins <api/plugins>`.

By default, Pybtex used BibTeX :file:`.bst` styles. You can switch the style
language from BibTeX to Python with the :option:`-l` option:

.. code-block:: shell

    $ pybtex -l python foo

Unlike the old BibTeX styles, Pythonic styles are not tied to LaTeX markup. They can also
produce HTML or plain text output (enabled with :option:`-b` command line
option):

.. code-block:: shell

    $ pybtex -l python -b html foo
    $ pybtex -l python -b plaintext foo

Support for other output formats can be allso added by :doc:`plugins <api/plugins>`.

It is also possible to override the default label and name styles with
command line options:

.. code-block:: shell

    $ pybtex -l python --label-style number --name-style last_first foo

(Again, support for label and name styles can be added by :doc:`plugins <api/plugins>`.)


Converting bibliography databases with :command:`bibtex-convert`
================================================================

Pybtex comes with an additional ``pybtex-convert`` utillty, which can convert bibliography
databases between supported formats:

.. code-block:: shell

    $ pybtex-convert book.bib book.yaml

Be aware, that the conversion is not always lossless. For example:

- BibTeXML format does not support LaTeX preambles.

- Conversion from/to YAML format does not preserve order of entries (PyYAML limitation, may be fixed some day).

- In the standard BibTeX format names are stored as single strings while BibTexML
  and Pybtex' YAML format store first name, last name, and other name parts
  seprately.


Pretty-printing bibliography databases with :command:`bibtex-format`
====================================================================

Sometimes you would want to convert a bibliography database to a
human-readable format (for example, for printing). That can be achieved with
:command:`pybtex-format`:

.. code-block:: shell

    $ pybtex-format book.bib book.txt
    $ pybtex-format book.bib book.html

By default ``unsrt`` formatting style is used. This can be changed with the
:option:`-s` option:

.. code-block:: shell

    $ pybtex-format -s plain book.bib book.txt
