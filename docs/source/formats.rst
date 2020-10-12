=================
Supported formats
=================


.. contents::
    :local:


Bibliography formats
====================


BibTeX
------

BibTeX is the default bibliography format used by Pybtex:

.. sourcecode:: bibtex-pybtex

    @BOOK{strunk-and-white,
        author = "Strunk, Jr., William and E. B. White",
        title = "The Elements of Style",
        publisher = "Macmillan",
        edition = "Third",
        year = 1979
    }


Some links:

- `A basic description of the BibTeX format. <https://www.bibtex.com/g/bibtex-format/>`_

- `An in-depth description of the quirky BibTeX syntax. <http://artis.imag.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html>`_

BibTeXML
--------

`BibTeXML`_ is an attempt to translate
the BibTeX format into XML.
The above BibTeX snippet translates into this XML:

.. sourcecode:: xml

    <bibtex:entry id="strunk-and-white">
        <bibtex:book>
            <bibtex:author>
                <bibtex:person>
                    <bibtex:first>William</bibtex:first>
                    <bibtex:last>Strunk</bibtex:last>
                    <bibtex:lineage>Jr.</bibtex:lineage>
                </bibtex:person>
                <bibtex:person>
                    <bibtex:first>E.</bibtex:first>
                    <bibtex:middle>B.</bibtex:first>
                    <bibtex:last>White</bibtex:last>
                </bibtex:person>
            </bibtex:author>
            <bibtex:title>The Elements of Style</bibtex:title>
            <bibtex:publisher>Macmillan<bibtex:publisher>
            <bibtex:edition>Third</bibtex:edition>
            <bibtex:year>1979</bibtex:year>
        </bibtex:book>
    </bibtex:entry>


YAML
----

We added our own experimental YAML-based bibliography format to Pybtex.
It is mostly a straightforward translation of `BibTeXML`_
into YAML:

.. sourcecode:: yaml

    strunk-and-white:
        type: book
        author:
            - first: William
              last: Strunk
              lineage: Jr.
            - first: E.
              middle: B.
              last: White
        title: The Elements of Style
        publisher: Macmillan
        edition: Third
        year: 1979


.. _BibTeXML: http://bibtexml.sourceforge.net

Bibliography style formats
==========================

Pybtex currently supports bibliography styles in two formats:

- BibTeX' ``.bst`` files
- Pybtex' :doc:`Pythonic styles <api/styles>`


Output formats
==============

BibTeX's :file:`.bst` styles usually contain hardcoded LaTeX markup
and are LaTeX-only. Pythonic styles in Pybtex are markup-independent
and can output multiple formats, including:

- LaTeX
- Markdown
- HTML
- plain text

There is also `pybtex-docutils`_ by Matthias Troffaes that integrates Pybtex with Docutils_,
and `sphinxcontrib-bibtex`_ by the same author, integrating Pybtex with Sphinx_.

.. _pybtex-docutils: https://github.com/mcmtroffaes/pybtex-docutils
.. _sphinxcontrib-bibtex: https://github.com/mcmtroffaes/sphinxcontrib-bibtex
.. _Docutils: http://docutils.sourceforge.net/
.. _Sphinx: http://sphinx-doc.org/
