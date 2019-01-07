================
Designing styles
================


.. testsetup:: *

    from __future__ import unicode_literals, print_function

    import six

    from pybtex.richtext import Text, String, Tag, HRef, Protected, Symbol, nbsp, textutils


.. currentmodule:: pybtex.richtext


.. contents::
    :local:


.. _rich-text:

Rich text
=========

Pybtex has a set of classes for working with formatted text
and producing formatted output.
A piece of formatted text in Pybtex is represented by a :py:class:`Text`
object.
A :py:class:`Text` is basically a container that holds a list of

* plain text parts, represented by :py:class:`String` objects,
* formatted parts, represented by :py:class:`Tag` and :py:class:`HRef` objects.

The basic workflow is:

1. Construct a :py:class:`Text` object.
2. Render it as LaTeX, HTML or other markup.

.. doctest::

    >>> from pybtex.richtext import Text, Tag
    >>> text = Text('How to be ', Tag('em', 'a cat'), '.')
    >>> print(text.render_as('html'))
    How to be <em>a cat</em>.
    >>> print(text.render_as('latex'))
    How to be \emph{a cat}.


Rich text classes
-----------------

There are several rich text classes in Pybtex:

- :py:class:`Text`
- :py:class:`String`
- :py:class:`Tag`
- :py:class:`HRef`
- :py:class:`Protected`


:py:class:`Text` is the top level container that may contain
:py:class:`String`, :py:class:`Tag`, and :py:class:`HRef` objects.
When a :py:class:`Text` object is rendered into markup,
it renders all of its child objects, then concatenates the result.

:py:class:`String` is just a wrapper for a single Python string.

:py:class:`Tag` and :py:class:`HRef` are also containers that may contain
other :py:class:`String`, :py:class:`Tag`, and :py:class:`HRef` objects. This
makes nested formatting possible.  For example, this stupidly formatted text:

    |CTAN hyperlink|_ is *comprehensive*.

    .. |CTAN hyperlink| replace:: *Comprehensive* TeX Archive Network
    .. _CTAN hyperlink: https://ctan.org/

is represented by this object tree:

.. doctest::

    >>> text = Text(
    ...     HRef('https://ctan.org/', Tag('em', 'Comprehensive'), ' TeX Archive Network'),
    ...     ' is ',
    ...     Tag('em', 'comprehensive'),
    ...     '.',
    ... )
    >>> print(text.render_as('html'))
    <a href="https://ctan.org/"><em>Comprehensive</em> TeX Archive Network</a> is <em>comprehensive</em>.

:py:class:`Protected` represents a "protected" piece of text, something like
{braced text} in BibTeX. It is not affected by case-changing operations, like
:py:meth:`Text.upper()` or :py:meth:`Text.lower()`, and is not splittable by
:py:meth:`Text.split()`.

All rich text classes share the same API which is more or less similar to plain
`Python strings`_.

.. _Python strings: https://docs.python.org/3/library/stdtypes.html#string-methods


Like Python strings, rich text objects are supposed to be immutable. Methods like
:py:meth:`Text.append` or :py:meth:`Text.upper` return a new :py:class:`Text`
object instead of modifying the data in place.
Attempting to modify the contents of an existing :py:class:`Text` object is
not supported and may lead to weird results.

Here we document the methods of the :py:class:`Text` class.
The other classes have the same methods.

.. autoclass:: pybtex.richtext.Text
    :members:
    :inherited-members:

    .. automethod:: Text.__init__
    .. automethod:: Text.__eq__
    .. automethod:: Text.__len__
    .. automethod:: Text.__contains__
    .. automethod:: Text.__getitem__
    .. automethod:: Text.__add__


.. autoclass:: pybtex.richtext.String

.. autoclass:: pybtex.richtext.Tag

.. autoclass:: pybtex.richtext.HRef

.. autoclass:: pybtex.richtext.Protected

.. autoclass:: pybtex.richtext.Symbol


Style API
=========

A formatting style in Pybtex is a class inherited from
:py:class:`pybtex.style.formatting.BaseStyle`.

.. autoclass:: pybtex.style.formatting.BaseStyle
    :members:

.. currentmodule:: pybtex.richtext


Pybtex loads the style class as a :doc:`plugin <plugins>`,
instantiates it with proper parameters and
calls the :py:meth:`~.BaseStyle.format_bibliography` method that does
the actual formatting job.
The default implementation of :py:meth:`~.BaseStyle.format_bibliography`
calls a ``format_<type>()`` method for each bibliography entry, where ``<type>``
is the entry type, in lowercase. For example, to format
an entry of type ``book``, the ``format_book()`` method is called.
The method must return a :py:class:`.Text` object.
Style classes are supposed to implement ``format_<type>()`` methods
for all entry types they support. If a formatting method
is not found for some entry, Pybtex complains about unsupported entry type.

An example minimalistic style:

.. sourcecode:: python

    from pybtex.style.formatting import BaseStyle
    from pybtex.richtext import Text, Tag

    class MyStyle(BaseStyle):
        def format_article(self, entry):
            return Text('Article ', Tag('em', entry.fields['title']))


Template language
=================

Manually creating :py:class:`.Text` objects may be tedious.
Pybtex has a small template language to simplify common formatting tasks,
like joining words with spaces, adding commas and periods, or handling missing fields.

The template language is is not very documented for now, so you should look at
the code in the :source:`pybtex.style.template <pybtex/style/template.py>` module
and the :source:`existing styles <pybtex/style/formatting>`.

An example formatting style using template language:

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
