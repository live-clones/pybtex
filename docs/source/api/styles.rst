====================
Designing new styles
====================


.. testsetup:: *

    from pybtex.richtext import Text, String, Tag, HRef, Symbol, nbsp, textutils


.. currentmodule:: pybtex.richtext


.. contents::
    :local:


Rich text
=========

Pybtex has a set of classes for working with formatted text
and producing formatted output.
A piece of formatted text in Pybtex is represented by a :py:class:`Text`
object.
A :py:class:`Text` is basically a container that holds a list of

* plain text strings represented by :py:class:`String` objects,
* or formatted parts, represented by :py:class:`Tag` and :py:class:`HRef` objects.

The basic workflow is:

1. Construct some formatted :py:class:`Text`.
2. Render it as some markup format.

.. doctest::

    >>> from pybtex.richtext import Text, Tag
    >>> text = Text('How to be ', Tag('em', 'a cat'), '.')
    >>> print text.render_as('html')
    How to be <em>a cat</em>.
    >>> print text.render_as('latex')
    How to be \emph{a cat}.


Rich text classes
-----------------

A :py:class:`Text` is the top level container that contains
:py:class:`String`, :py:class:`Tag` or :py:class:`HRef` objects.

A :py:class:`String` is just a wrapper for a Python unicode string:

.. doctest::

    >>> from pybtex.richtext import String
    >>> print String('Crime & Punishment').render_as('text')
    Crime & Punishment
    >>> print String('Crime & Punishment').render_as('html')
    Crime &amp; Punishment

A :py:class:`Tag` represents something like an HTML tag
or a LaTeX formatting command:

.. doctest::

    >>> from pybtex.richtext import Tag
    >>> tag = Tag('em', 'The TeXbook')
    >>> print tag.render_as('html')
    <em>The TeXbook</em>
    >>> print tag.render_as('latex')
    \emph{The TeXbook}


A :py:class:`HRef` represends a hyperlink:

.. doctest::

    >>> from pybtex.richtext import Tag
    >>> href = HRef('http://ctan.org/', 'CTAN')
    >>> print href.render_as('html')
    <a href="http://ctan.org/">CTAN</a>
    >>> print href.render_as('latex')
    \href{http://ctan.org/}{CTAN}

Like :py:class:`Text`, both :py:class:`Tag` and :py:class:`HRef` are also
containers that hold a list of plain text strings or other :py:class:`Tag` or
:py:class:`HRef` objects, so formatting can be nested.
For example, this formatted text

    |CTAN hyperlink|_ is *comprehensive*.

    .. |CTAN hyperlink| replace:: *Comprehensive* TeX Archive Network
    .. _CTAN hyperlink: http://ctan.org/

is represented by this object tree:

.. doctest::

    >>> text = Text(
    ...     HRef('http://ctan.org/', Tag('em', 'Comprehensive'), ' TeX Archive Network'),
    ...     ' is ',
    ...     Tag('em', 'comprehensive'),
    ...     '.',
    ... )
    >>> print text.render_as('html')
    <a href="http://ctan.org/"><em>Comprehensive</em> TeX Archive Network</a> is <em>comprehensive</em>.


.. autoclass:: pybtex.richtext.Text
    :members:
    :inherited-members:

    .. automethod:: Text.__init__


.. autoclass:: pybtex.richtext.Tag

.. autoclass:: pybtex.richtext.HRef

.. autoclass:: pybtex.richtext.String

.. autoclass:: pybtex.richtext.Symbol


Template language
=================

BibTeX uses has a simple stack oriented language for defining bibliography
styles. This is what is inside of ``.bst`` files.  For a Pythonic bibliography
processor it is natural to use Python for writing styles. A Pybtex style file
is basically a Python module containing a class named ``Formatter``. This
class has methods like ``format_article``, ``format_book``, etc. They accept a
bibliography entry (an instance of :py:class:`pybtex.database.Entry` class) and return a
formatted entry (an instance of :py:class:`pybtex.richtex.Text`).

.. sourcecode:: python

    from pybtex.style.formatting import BaseStyle
    from pybtex.richtext import Text, Tag

    class MyStyle(BaseStyle):
        def format_article(self, entry):
            return Text('Article ', Tag('em', entry.fields['title']))

To make things easier we designed a simple template language:

.. sourcecode:: python

    from pybtex.style.formatting import BaseStyle, toplevel
    from pybtex.style.template import field, join, optional

    class MyStyle(BaseStyle):
        def format_article(self, entry):
            if entry.fields['volume']:
                volume_and_pages = join [field('volume'), optional [':', pages]]
            else:
                volume_and_pages = words ['pages', optional [pages]]
            template = toplevel [
                self.format_names('author'),
                sentence [field('title')],
                sentence [
                    tag('emph') [field('journal')], volume_and_pages, date],
            ]
            return template.format_data(entry)

Is that all?
============

More documentation will be written when our style API
gets some form. Use the source for now.
