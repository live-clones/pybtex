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

1. Construct a :py:class:`Text` object.
2. Render it as LaTeX, HTML or other markup.

.. doctest::

    >>> from pybtex.richtext import Text, Tag
    >>> text = Text('How to be ', Tag('em', 'a cat'), '.')
    >>> print text.render_as('html')
    How to be <em>a cat</em>.
    >>> print text.render_as('latex')
    How to be \emph{a cat}.


Rich text classes
-----------------

There are four main rich text classes in Pybtex:

- :py:class:`Text`
- :py:class:`String`
- :py:class:`Tag`
- :py:class:`HRef`


:py:class:`Text` is the top level container that may contain
:py:class:`String`, :py:class:`Tag`, and :py:class:`HRef` objects.
When a :py:class:`Text` object is rendered into markup,
it renders all of its child objects, then concatenates the result.

:py:class:`String` is just a wrapper for a single Python string.

:py:class:`Tag` and :py:class:`HRef` are also containers that may
contain other :py:class:`String`, :py:class:`Tag`, and :py:class:`HRef`
objects, so nested formatting is possible.  For example, this formatted text


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


All rich text classes share the same API more or less similar to plain
:ref:`Python strings <python:textseq>`.

Like Python strings, rich text objects are supposed to be immutable. Methods like
:py:meth:`Text.append` or :py:meth:`Text.upper` return a new :py:class:`Text`
object instead of modifying the data in place.
Attempting to modify the contents of an existing :py:class:`Text` object is
not supported and may lead to weird results.

Here we document the methods of the :py:class:`Text` class.
The other classes have similar methods.

.. autoclass:: pybtex.richtext.Text
    :members:
    :inherited-members:

    .. automethod:: Text.__init__


.. autoclass:: pybtex.richtext.String

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
