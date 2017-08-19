=====================================
Reading and writing bibliography data
=====================================


.. testsetup:: *

    from __future__ import unicode_literals, print_function

    import six

    from pybtex.database import BibliographyData, Entry, Person, parse_string


.. contents::
    :local:


Reading bibliography data
=========================

One of the most common things to do with Pybtex API is parsing BibTeX files.
There are several high level functions in the :py:mod:`pybtex.database` module
for reading bibliography databases.

.. autofunction:: pybtex.database.parse_string

.. autofunction:: pybtex.database.parse_bytes

.. autofunction:: pybtex.database.parse_file


Each of these functions does basically the same thing.
It reads the bibliography data from a string or a file and returns a
:py:class:`.BibliographyData` object containing all the bibliography data.

Here is a quick example:
.. doctest::

    >>> from pybtex.database import parse_file
    >>> bib_data = parse_file('../examples/tugboat/tugboat.bib')
    >>> print(bib_data.entries['Knuth:TB8-1-14'].fields['title'])
    Mixing right-to-left texts with left-to-right texts
    >>> for author in bib_data.entries['Knuth:TB8-1-14'].persons['author']:
    ...     print(unicode(author))
    Knuth, Donald
    MacKay, Pierre


Writing bibliography data
=========================

The :py:class:`.BibliographyData` class has several methods that are
symmetrical to the functions described above:

- :py:meth:`.BibliographyData.to_string` formats the bibliograhy data into a string,
- :py:meth:`.BibliographyData.to_bytes` formats the bibliograhy data into a byte string,
- :py:meth:`.BibliographyData.to_file` writes the bibliograhy data to a file.


.. doctest::

    >>> from pybtex.database import BibliographyData, Entry
    >>> bib_data = BibliographyData({
    ...     'article-minimal': Entry('article', [
    ...         ('author', 'L[eslie] B. Lamport'),
    ...         ('title', 'The Gnats and Gnus Document Preparation System'),
    ...         ('journal', "G-Animal's Journal"),
    ...         ('year', '1986'),
    ...     ]),
    ... })
    >>> print(bib_data.to_string('bibtex'))
    @article{article-minimal,
        author = "L[eslie] B. Lamport",
        title = "The Gnats and Gnus Document Preparation System",
        journal = "G-Animal's Journal",
        year = "1986"
    }
    <BLANKLINE>


Bibliography data classes
=========================

Pybtex uses several classes to represent bibligraphy databases:

- :py:class:`.BibliographyData` is a collection of individual bibliography
  entries and some additional metadata.

- :py:class:`.Entry` is a single bibliography entry (a book, an article, etc.).

  An entry has a key (like ``"knuth74"``), a type (``"book"``, ``"article"``, etc.),
  and a number of key-value fields (``"author"``, ``"title"``, etc.).

- :py:class:`.Person` is a person related to a bibliography entry
  (usually as an author or an editor).

.. autoclass:: pybtex.database.BibliographyData
    :members:

.. autoclass:: pybtex.database.Entry
    :members:

.. autoclass:: pybtex.database.Person
    :members:
