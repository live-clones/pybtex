=========================
Formatting bibliographies
=========================

.. contents::
    :local:

The main purpose of Pybtex is turning machine-readable bibliography data into
human-readable bibliographies formatted in a specific style.
In other words, pybtex reads bibliography data that looks like this:

.. sourcecode:: bibtex

    @book{graham1989concrete,
        title = "Concrete mathematics: a foundation for computer science",
        author = "Graham, Ronald Lewis and Knuth, Donald Ervin"
            # " and Patashnik, Oren",
        series = "A foundation for computer science",
        year = "1989",
        publisher = "Addison-Wesley"
    }

and formats it like this:

    R. L. Graham, D. E. Knuth, and O. Patashnik.
    *Concrete mathematics: a foundation for computer science*.
    A foundation for computer science. Addison-Wesley, 1989.

Pybtex contains two different engines for formatting bibliographies:

- The :ref:`BibTeX engine <bibtex-engine>` that is compatible with the original BibTeX ``.bst`` styles.

- The :ref:`Python engine <python-engine>` that uses styles written in Python.


.. _bibtex-engine:

BibTeX engine
=============

The BibTeX is backward compatible with BibTeX and is used by default.
When you type ``pybtex mydocument`` the following things happen:


1.  Pybtex reads the file ``mydocument.aux`` in the current directory.
    This file is normally created by LaTeX and contains all sorts of auxiliary information
    collected during processing the LaTeX document.

    Pybtex is interested in these pieces of information:

    Bibliography style:
        First, Pybtex searches the ``.aux`` file for a ``\bibstyle`` tells what formatting style to use.

        For example, ``\bibstyle{unsrt}`` instructs Pybtex to use formatting style defined by ``unsrt.bst``.

    Bibliography data:
        Next, Pybtex expects to find at least one ``\bibdata`` command in the aux file that tells
        where to look for the bibliography data.

        For example, ``\bibdata{mydocument}`` means "use the bibliography data from ``mydocument.bib``".

    Citations:
        Finally, Pybtex needs to know what entries to put into the resulting bibliography.
        Pybtex gets the list of citation keys from ``\citation`` commands in the ``.aux`` file.

        For example, ``\citation{graham1989concrete}`` means "include the entry with key
        ``graham1989concrete`` into the resulting bibliograhy".

        A wildcard citation ``\citation{*}`` tells Pybtex to format the bibliography for all
        entries from all data files specified by ``\bibdata`` commands.

2.  Pybtex executes the style program in the ``.bst`` file specified by the ``\bibstyle`` command.
    As a result, a ``.bbl`` file containing the resulting formatted is created.

    A ``.bst`` style is a program in a domain-specific stack-based language.
    It contains complete instructions on how to create the formatted bibliography
    from the given bibliography data and citation keys.
    For example, a ``READ`` command tells Pybtex to read the data from all
    files specified earlier by ``\bibdata`` commands in the ``.aux`` file,
    an ``ITERATE`` command tells Pybtex to execute a piece of code for each
    citation key specified by ``\citation`` commands, and so on.
    The built-in ``write$`` function tells Pybtex to output the given string to
    the resulting ``.bbl`` file.
    Pybtex simply executes the ``.bst`` program and implements all the built-in
    functions and commands.

    A complete reference of the ``.bst`` language can be found in the `BibTeX hacking guide`_ by Oren Patashnik.
    It is available by running ``texdoc btxhak`` in most TeX distributions.

.. _`BibTeX hacking guide`: http://mirrors.ctan.org/biblio/bibtex/base/btxhak.pdf


.. _python-engine:

Python engine
=============
