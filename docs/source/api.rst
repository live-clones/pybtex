=========================
Using Pybtex as a library
=========================


Using the BibTeX parser
=======================

.. sourcecode:: pycon

    >>> from pybtex.database.input import bibtex
    >>> parser = bibtex.Parser()
    >>> bib_data = parser.parse_file('examples/foo.bib')
    >>> bib_data.entries.keys()
    [u'ruckenstein-diffusion', u'viktorov-metodoj', u'test-inbook', u'test-booklet']
    >>> print bib_data.entries['ruckenstein-diffusion'].fields['title']
    Predicting the Diffusion Coefficient in Supercritical Fluids

(to be continued)
