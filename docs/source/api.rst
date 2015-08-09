=========================
Using Pybtex as a library
=========================


Using the BibTeX parser
=======================

.. doctest::

    >>> from pybtex.database.input import bibtex
    >>> parser = bibtex.Parser()
    >>> bib_data = parser.parse_file('../examples/tugboat/tugboat.bib')
    >>> print bib_data.entries['Knuth:TB8-1-14'].fields['title']
    Mixing right-to-left texts with left-to-right texts
    >>> for author in bib_data.entries['Knuth:TB8-1-14'].persons['author']:
    ...     print(unicode(author))
    Knuth, Donald
    MacKay, Pierre

(to be continued)
