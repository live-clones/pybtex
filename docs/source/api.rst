=========================
Parsing bibliography data
=========================


.. testsetup:: *

    from pybtex.database import BibliographyData, Entry, Person, parse_string


One of the most common things to do with Pybtex API is parsing BibTeX files.
There are several high level functions in the :py:mod:`pybtex.database` module
for that.

.. autofunction:: pybtex.database.parse_string

.. autofunction:: pybtex.database.parse_bytes

.. autofunction:: pybtex.database.parse_file


All these functions do basically the same thing: parse the data from a string
or a file and return a :py:class:`.BibliographyData` object containing all the
bibliography data.

Here is a quick example:

.. doctest::

    >>> from pybtex.database import parse_file
    >>> bib_data = parse_file('../examples/tugboat/tugboat.bib')
    >>> print bib_data.entries['Knuth:TB8-1-14'].fields['title']
    Mixing right-to-left texts with left-to-right texts
    >>> for author in bib_data.entries['Knuth:TB8-1-14'].persons['author']:
    ...     print(unicode(author))
    Knuth, Donald
    MacKay, Pierre


Bibliography data classes
=========================

:py:class:`.BibliographyData` contains contains a dictionary of bibliography
entries represented by :py:class:`.Entry` objects.
Additionally, it may contain a LaTeX preamble defined by ``@PREAMBLE``
commands in the BibTeX file.

.. autoclass:: pybtex.database.BibliographyData
    :members:

.. autoclass:: pybtex.database.Entry
    :members:

.. autoclass:: pybtex.database.Person
    :members:
