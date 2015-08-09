=========================
Using Pybtex as a library
=========================


.. testsetup:: *

    from pybtex.database import BibliographyData, Entry, Person


Using the BibTeX parser
=======================

.. doctest::

    >>> from pybtex.database import parse_file
    >>> bib_data = parse_file('../examples/tugboat/tugboat.bib')
    >>> print bib_data.entries['Knuth:TB8-1-14'].fields['title']
    Mixing right-to-left texts with left-to-right texts
    >>> for author in bib_data.entries['Knuth:TB8-1-14'].persons['author']:
    ...     print(unicode(author))
    Knuth, Donald
    MacKay, Pierre

.. autofunction:: pybtex.database.parse_string

.. autofunction:: pybtex.database.parse_bytes

.. autofunction:: pybtex.database.parse_file

.. autoclass:: pybtex.database.BibliographyData
    :members:

.. autoclass:: pybtex.database.Entry
    :members:

.. autoclass:: pybtex.database.Person
    :members:
