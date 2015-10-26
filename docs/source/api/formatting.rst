=========================
Formatting bibliographies
=========================

.. contents::
    :local:

The main purpose of Pybtex is turning machine-readable bibliography data into
human-readable bibliographies formatted in a specific style.
Pybtex reads bibliography data that looks like this:

.. sourcecode:: bibtex

    @book{graham1989concrete,
        title = "Concrete mathematics: a foundation for computer science",
        author = "Graham, Ronald Lewis and Knuth, Donald Ervin and Patashnik, Oren",
        year = "1989",
        publisher = "Addison-Wesley"
    }

and formats it like this:

    R. L. Graham, D. E. Knuth, and O. Patashnik.
    *Concrete mathematics: a foundation for computer science*.
    Addison-Wesley, 1989.

Pybtex contains two different formatting engines:

- The :ref:`BibTeX engine <bibtex-engine>` uses BibTeX ``.bst`` styles.

- The :ref:`Python engine <python-engine>` uses styles written in Python.


.. _bibtex-engine:

BibTeX engine
=============

The BibTeX engine is fully compatible with BibTeX style files and is used by default.


How it works
------------

When you type :command:`pybtex mydocument`, the following things happen:


1.  Pybtex reads the file :file:`mydocument.aux` in the current directory.
    This file is normally created by LaTeX and contains all sorts of auxiliary information
    collected during processing of the LaTeX document.

    Pybtex is interested in these three pieces of information:

    Bibliography style:
        First, Pybtex searches the :file:`.aux` file for a ``\bibstyle``
        command that specifies which formatting style will be used.

        For example, ``\bibstyle{unsrt}`` instructs Pybtex to use formatting
        style defined in the file :file:`unsrt.bst`.

    Bibliography data:
        Next, Pybtex expects to find at least one ``\bibdata`` command in the
        :file:`.aux` file that tells where to look for the bibliography data.

        For example, ``\bibdata{mydocument}`` means "use the bibliography data
        from :file:`mydocument.bib`".

    Citations:
        Finally, Pybtex needs to know which entries to put into the resulting
        bibliography.  Pybtex gets the list of citation keys from
        ``\citation`` commands in the :file:`.aux` file.

        For example, ``\citation{graham1989concrete}`` means "include the
        entry with the key ``graham1989concrete`` into the resulting bibliograhy".

        A wildcard citation ``\citation{*}`` tells Pybtex to format the
        bibliography for all entries from all data files specified by
        all ``\bibdata`` commands.

2.  Pybtex executes the style program in the :file:`.bst` file specified by
    the ``\bibstyle`` command in the :file:`.aux` file. As a result, a
    :file:`.bbl` file containing the resulting formatted bibliography is
    created.

    A :file:`.bst` style file is a program in a domain-specific stack-based
    language. A typical piece of the :file:`.bst` code looks like this:

    .. code-block:: bst-pybtex

        FUNCTION {format.bvolume}
        { volume empty$
            { "" }
            { "volume" volume tie.or.space.connect
            series empty$
                'skip$
                { " of " * series emphasize * }
            if$
            "volume and number" number either.or.check
            }
        if$
        }

    The code in a :file:`.bst` file contains the complete step-by-step
    instructions on how to create the formatted bibliography from the given
    bibliography data and citation keys.  For example, a ``READ`` command
    tells Pybtex to read the bibliography data from all files specified by
    ``\bibdata`` commands in the ``.aux`` file, an ``ITERATE`` command tells
    Pybtex to execute a piece of code for each citation key specified by
    ``\citation`` commands, and so on.  The built-in ``write$`` function tells
    Pybtex to write the given string into the resulting :file:`.bbl` file.
    Pybtex implements all these commands and built-in functions and simply
    executes the :file:`.bst` program step by step.

    A complete reference of the :file:`.bst` language can be found in the
    `BibTeX hacking guide`_ by Oren Patashnik.  It is available by running
    :command:`texdoc btxhak` in most TeX distributions.

.. _`BibTeX hacking guide`: http://mirrors.ctan.org/biblio/bibtex/base/btxhak.pdf


.. _python-engine:

Python engine
=============

The Python engine is enabled by running :command:`pybtex` with  the :option:`-l python` option.


Differences from the BibTeX engine
----------------------------------

* Formatting styles are written in Python instead of the :file:`.bst` language.

* Formatting styles are not tied to LaTeX and do not use hardcoded LaTeX
  markup. Instead of that they produce format-agnostic :py:class:`pybtex.richtext.Text`
  objects that can be converted to any markup format (LaTeX, Markdown, HTML, etc.).

* Name formatting, label formatting, and sorting styles are defined separately
  from the main style.


How it works
------------

When you type :command:`pybtex -l python mydocument`, this things happen:

1.  Pybtex reads the file :file:`mydocument.aux` in the current directory and
    extracts the name of the the bibliography style, the list of bibliography
    data files and the list of citation keys.
    This step is exactly the same as with the BibTeX engine.

2.  Pybtex reads the biliography data from all data files specified in the
    :file:`.aux` file into a single :py:class:`.BibliographyData` object.

3.  Then the formatting style is loaded. The formatting style is a
    Python class with a :py:meth:`~.format_bibliography()` method.  Pybtex passes the
    bibliography data (a :py:class:`.BibliographyData` object) and the list of
    citation keys to :py:meth:`~.format_bibliography()`.

4.  The formatting style formats each of the requested bibliography entries
    in a style-specific way.

    When it comes to formatting names, a name formatting style is loaded and
    used. A name formatting style is also a Python class with a specific
    interface.  Similarly, a label formatting style is used to format entry
    labels, and a sorting style is used to sort the resulting style.  Each
    formatting style has a default name style, a default label style and a
    default sorting style. The defaults can be overridden with options passed
    to the main style class.

    Each formatted entry is put into a :py:class:`.FormattedEntry` object
    which is just a container for the formatted label, the formatted entry
    text (a :py:class:`pybtex.richtext.Text` object) and the entry key.  The reason
    that the label, the key and the main text are stored separately is to give the
    output backend more flexibility when converting the
    :py:class:`.FormattedEntry` object to the actual markup. For example, the
    HTML backend may want to format the bibliography as a definition list, the
    LaTeX backend would use ``\bibitem[label]{key} text`` constructs, etc.

    Formatted entries are put into a :py:class:`.FormattedBibliography`
    object---it simply contains a list of :py:class:`.FormattedEntry` objects
    and some additional metadata.

5.  The resulting :py:class:`.FormattedBibliography` is passed to the output
    backend. The default backend is LaTeX. It can be changed with the ``pybtex
    --output-backend`` option. The output backend converts the formatted
    bibliography to the specific markup format and writes it to the output
    file.


Python API
==========

The base interface
------------------

Both the Python engine and the BibTeX engine use the same interface
defined in :py:class:`pybtex.Engine`.

:py:class:`pybtex.Engine` has a handful of methods but most of them are just
convenience wrappers for :py:meth:`.Engine.format_from_files` that does the
actual job.


.. autoclass:: pybtex.Engine
    :members:


.. _bibtex-engine-api:

The BibTeXEngine class
----------------------

The BibTeX engine lives in the ``pybtex.bibtex`` module.
The public interface consists of the :py:class:`.BibTeXEngine` class and a
couple of convenience functions.


.. autoclass:: pybtex.bibtex.BibTeXEngine
    :members:

.. autofunction:: pybtex.bibtex.make_bibliography
.. autofunction:: pybtex.bibtex.format_from_string
.. autofunction:: pybtex.bibtex.format_from_strings
.. autofunction:: pybtex.bibtex.format_from_file
.. autofunction:: pybtex.bibtex.format_from_files


The PybtexEngine class
----------------------

The Python engine resides in the ``pybtex`` module
and uses an interface similar to the :ref:`BibTeX engine <bibtex-engine-api>`.
There is the :py:class:`.PybtexEngine` class and some convenience functions.

.. autoclass:: pybtex.PybtexEngine
    :members:

.. autofunction:: pybtex.make_bibliography
.. autofunction:: pybtex.format_from_string
.. autofunction:: pybtex.format_from_strings
.. autofunction:: pybtex.format_from_file
.. autofunction:: pybtex.format_from_files
