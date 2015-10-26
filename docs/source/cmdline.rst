======================
Command line interface
======================

.. contents::
    :local:


Making bibliographies with :command:`pybtex`
============================================

The :command:`pybtex` executable is used in the same was as the original :command:`bibtex`
command and accepts the same command line options.
The only difference is that you type :command:`pybtex` instead of
:command:`bibtex`.

For example, to compile the bibliography for a LaTeX file named
:file:`book.tex`, you need to type:

.. code-block:: shell

    $ latex book
    $ pybtex book
    $ latex book
    $ latex book  # to get cross-references right


See the `BibTeX tutorial`_ by Andrew Roberts for a basic explanation of how to use
BibTeX.


.. _BibTeX tutorial: http://www.andy-roberts.net/writing/latex/bibliographies


Bibliography formats other then BibTeX
--------------------------------------

.. todo::
    link to BibTeX format description


Pybtex is fully compatible with BibTeX' :file:`.bib` files.
Besides that, Pybtex supports other bibliography formats.
The list of supported formats can bee seen in the output of :command:`pybtex --help`.

By default, the BibTeX format is used. If a LaTeX file :file:`book.tex` contains:

.. code-block:: latex

    \bibliogrpahy{mybook}


Then this command:

.. code-block:: shell

    $ pybtex book

will expect to find the bibliography data in a BibTeX-formatted file :file:`mybook.bib`.

Pybtex can be instructed to use a different format with the :option:`--format` option.
For example this command:

.. code-block:: shell

    $ pybtex --format yaml book

will tell Pybtex to look for a YAML-formatted file :file:`mybook.yaml` instead of :file:`mybook.bib`).

Support for additional bibliography formats can be added by :doc:`plugins <api/plugins>`.

    
Pythonic bibliography styles
----------------------------

BibTeX has a built-in stack oriented programming language for defining
bibliography formatting styles. This language is used in :file:`.bst`
style files. Pybtex is fully compatible with BIbTeX' :file:`.bst` style files.

Additionally, Pybtex allows
:doc:`to write bibliography styles in Python <api/styles>`.
Some base BibTeX styles, including ``plain``, ``alpha``, ``unsrt``, have been
already ported to Python.  They can be found in
:source:`pybtex/style/formatting` subdirectory. Additional
styles can be added as :doc:`plugins <api/plugins>`.

By default, Pybtex uses BibTeX' :file:`.bst` styles. You can switch the style
language from BibTeX to Python with the :option:`--style-language` option:

.. code-block:: shell

    $ pybtex --style-language python book

One of the advantage of using Pythonic styles is that they can produce HTML,
Markdown or plain text output besides the usual LaTeX markup.
To change the output backend from LaTeX to something else,
use the :option:`--output-backend` option:

.. code-block:: shell

    $ pybtex --style-language python --output-backend html book
    $ pybtex --style-language python --output-backend plaintext book

(In this case Pybtex will write the bibliography to :file:`book.html` or
:file:`book.txt` instead of :file:`book.bbl`).

Support for other markup formats can be added by :doc:`plugins <api/plugins>`.

Additionally, Pythonic styles are configurable with command line options to
some extent. For example, the :option:`--name-style` option tells Pybtex to
use a different name formatting style, :option:`--abbreviate-names` forces
Pybtex to use the abbreviated name format, etc. See :command:`pybtex --help`
for more options.


Converting bibliography databases with :command:`bibtex-convert`
================================================================

Pybtex comes with an additional utility called :command:`pybtex-convert`.
It converts bibliography databases between supported formats:

.. code-block:: shell

    $ pybtex-convert book.bib book.yaml

Be aware that the conversion is not always lossless. For example:

- BibTeX' string macros are substituted by their values during conversion.

- BibTeXML does not support LaTeX preambles.

- In the standard BibTeX format, names are stored as single strings. BibTexML
  and Pybtex' YAML format store first name, last name, and other name parts
  seprately.


Pretty-printing bibliography databases with :command:`bibtex-format`
====================================================================

Sometimes you would want to convert a bibliography database to a
human-readable format. Pybtex has another utility called :command:`pybtex-format` for
that:

.. code-block:: shell

    $ pybtex-format book.bib book.txt
    $ pybtex-format book.bib book.html

By default, the ``unsrt`` style is used for formatting. This can be changed with the
:option:`--style` option:

.. code-block:: shell

    $ pybtex-format --style alpha book.bib book.txt
