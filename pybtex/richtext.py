# Copyright (c) 2006-2014  Andrey Golovizin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

r"""(simple but) rich text formatting tools

Usage:

>>> from pybtex.backends import latex
>>> backend = latex.Backend()
>>> t = Text('this ', 'is a ', Tag('em', 'very'), Text(' rich', ' text'))
>>> print t.render(backend)
this is a \emph{very} rich text
>>> print unicode(t)
this is a very rich text
>>> t = t.capfirst().add_period()
>>> print t.render(backend)
This is a \emph{very} rich text.
>>> print unicode(t)
This is a very rich text.
>>> print Symbol('ndash').render(backend)
--
>>> t = Text('Some ', Tag('em', Text('nested ', Tag('tt', 'Text', Text(' objects')))), '.')
>>> print t.render(backend)
Some \emph{nested \texttt{Text objects}}.
>>> print unicode(t)
Some nested Text objects.
>>> t = t.map(lambda string: string.upper())
>>> print t.render(backend)
SOME \emph{NESTED \texttt{TEXT OBJECTS}}.
>>> print unicode(t)
SOME NESTED TEXT OBJECTS.

>>> t = Text(', ').join(['one', 'two', Tag('em', 'three')])
>>> print t.render(backend)
one, two, \emph{three}
>>> print unicode(t)
one, two, three
>>> t = Text(Symbol('nbsp')).join(['one', 'two', Tag('em', 'three')])
>>> print t.render(backend)
one~two~\emph{three}
>>> print unicode(t)
one<nbsp>two<nbsp>three
"""


import string
import warnings
from copy import deepcopy
from pybtex import textutils
from pybtex.utils import deprecated


class BaseText(object):
    def __getitem__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __reversed__(self):
        raise NotImplementedError

    def render(self, backend):
        raise NotImplementedError

    def upper(self):
        raise NotImplementedError

    def lower(self):
        raise NotImplementedError

    def capfirst(self):
        raise NotImplementedError

    def add_period(self):
        raise NotImplementedError


class Text(BaseText):
    """
    Rich text is basically a list of:

    - plain strings
    - Text objects, including objects derived from Text (Tag, HRef, ...)
    - Symbol objects

    Text is used as an internal formatting language of Pybtex,
    being rendered to to HTML or LaTeX markup or whatever in the end.

    >>> Text()
    []
    >>> print unicode(Text('a', '', 'c'))
    ac
    >>> print unicode(Text('a', Text(), 'c'))
    ac
    >>> print unicode(Text('a', Text('b', 'c'), Tag('em', 'x'), Symbol('nbsp'), 'd'))
    abcx<nbsp>d
    >>> Text({}) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: ...

    """

    def __init__(self, *parts):
        """Create a Text consisting of one or more parts."""

        if not all(isinstance(part, (basestring, Text, Symbol))
                   for part in parts):
            raise TypeError(
                "parts must be str, Text or Symbol")
        self._parts = [part for part in parts if part]

    def __iter__(self):
        return iter(self._parts)

    def __repr__(self):
        return repr(self._parts)

    def __len__(self):
        """Return the number of characters in this Text."""
        return sum(len(part) for part in self)

    def __add__(self, other):
        """
        Concatenate this Text with another Text or string.

        >>> t = Text('a')
        >>> print unicode(t + 'b')
        ab
        >>> print unicode(t + t)
        aa
        >>> print unicode(t)
        a
        """

        return Text(self, other)

    def from_list(self, lst):
        return Text(*lst)

    def append(self, item):
        """Appends some text or something.
        Empty strings and similar things are ignored.
        """
        if item:
            list.append(self, item)

    def extend(self, list_):
        for item in list_:
            self.append(item)

    def render(self, backend):
        """Return backend-dependent textual representation of this Text."""

        rendered_list = []
        for item in self:
            if isinstance(item, basestring):
                rendered_list.append(backend.format_str(item))
            else:
                assert isinstance(item, (Text, Symbol))
                rendered_list.append(item.render(backend))
        assert all(isinstance(item, backend.RenderType)
                   for item in rendered_list)
        return backend.render_sequence(rendered_list)


    def enumerate(self):
        for n, child in enumerate(self):
            try:
                for p in child.enumerate():
                    yield p
            except AttributeError:
                yield self, n

    def reversed(self):
        for n, child in reversed(list(enumerate(self))):
            try:
                for p in child.reversed():
                    yield p
            except AttributeError:
                yield self, n

    def map(self, f, condition=None):
        if condition is None:
            condition = lambda index, length: True
        def iter_map_with_condition():
            length = len(self)
            for index, child in enumerate(self):
                if hasattr(child, 'map'):
                    yield child.map(f, condition) if condition(index, length) else child
                else:
                    yield f(child) if condition(index, length) else child
        return self.from_list(iter_map_with_condition())

    def upper(self):
        return self.map(string.upper)

    def apply_to_start(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == 0)

    def apply_to_end(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == length - 1)

    def get_beginning(self):
        try:
            l, i = self.enumerate().next()
        except StopIteration:
            pass
        else:
            return l._parts[i]

    def get_end(self):
        try:
            l, i = self.reversed().next()
        except StopIteration:
            pass
        else:
            return l._parts[i]

    def join(self, parts):
        """Join a list using this text (like string.join)

        >>> print unicode(Text(' ').join([]))
        <BLANKLINE>
        >>> print unicode(Text(' ').join(['a', 'b', 'c']))
        a b c
        >>> print unicode(Text(nbsp).join(['a', 'b', 'c']))
        a<nbsp>b<nbsp>c
        """

        if not parts:
            return Text()
        joined = []
        for part in parts[:-1]:
            joined.extend([part, deepcopy(self)])
        joined.append(parts[-1])
        return Text(*joined)

    @deprecated('0.19', 'use __unicode__() instead')
    def plaintext(self):
        return unicode(self)

    def __unicode__(self):
        return ''.join(unicode(part) for part in self)

    def capfirst(self):
        """Capitalize the first letter of the text.

        >>> text = Text(Text(), Text('mary ', 'had ', 'a little lamb'))
        >>> print unicode(text)
        mary had a little lamb
        >>> print unicode(text.capfirst())
        Mary had a little lamb

        """
        return self.apply_to_start(textutils.capfirst)

    def add_period(self, period='.'):
        """Add a period to the end of text, if necessary.

        >>> import pybtex.backends.html
        >>> html = pybtex.backends.html.Backend()

        >>> text = Text("That's all, folks")
        >>> print unicode(text.add_period())
        That's all, folks.

        >>> text = Tag('em', Text("That's all, folks"))
        >>> print text.add_period().render(html)
        <em>That's all, folks.</em>
        >>> print text.add_period().add_period().render(html)
        <em>That's all, folks.</em>

        >>> text = Text("That's all, ", Tag('em', 'folks'))
        >>> print text.add_period().render(html)
        That's all, <em>folks</em>.
        >>> print text.add_period().add_period().render(html)
        That's all, <em>folks</em>.

        >>> text = Text("That's all, ", Tag('em', 'folks.'))
        >>> print text.add_period().render(html)
        That's all, <em>folks.</em>

        >>> text = Text("That's all, ", Tag('em', 'folks'))
        >>> print text.add_period('!').render(html)
        That's all, <em>folks</em>!
        >>> print text.add_period('!').add_period('.').render(html)
        That's all, <em>folks</em>!
        """

        end = self.get_end()
        if end and not textutils.is_terminated(end):
            return self.from_list(self._parts + [period])
        else:
            return self


class Tag(Text):
    """A tag is somethins like <foo>some text</foo> in HTML
    or \\foo{some text} in LaTeX. 'foo' is the tag's name, and
    'some text' is tag's text.

    >>> emph = Tag('em', 'emphasized text')
    >>> from pybtex.backends import latex, html
    >>> print emph.render(latex.Backend())
    \emph{emphasized text}
    >>> print emph.render(html.Backend())
    <em>emphasized text</em>
    """

    def from_list(self, lst):
        return Tag(self.name, *lst)

    def __check_name(self, name):
        depr_map = {}
        depr_map[u'emph'] = u'em'
        if name in depr_map:
            msg  = u"The tag '%s' is deprecated" % name
            msg += u", use '%s' instead." % depr_map[name]
            warnings.warn(msg, DeprecationWarning)
            return depr_map[name]
        return name

    def __init__(self, name, *args):
        if not isinstance(name, (basestring, Text)):
            raise TypeError(
                "name must be str or Text (got %s)" % name.__class__.__name__)
        self.name = self.__check_name(unicode(name))
        super(Tag, self).__init__(*args)

    def render(self, backend):
        text = super(Tag, self).render(backend)
        return backend.format_tag(self.name, text)


class HRef(Text):
    """A href is somethins like <href url="URL">some text</href> in HTML
    or \href{URL}{some text} in LaTeX.

    >>> href = HRef('http://www.example.com', 'hyperlinked text')
    >>> from pybtex.backends import latex, html, plaintext
    >>> print href.render(latex.Backend())
    \href{http://www.example.com}{hyperlinked text}
    >>> print href.render(html.Backend())
    <a href="http://www.example.com">hyperlinked text</a>
    >>> print href.render(plaintext.Backend())
    hyperlinked text
    """

    def __init__(self, url, *args):
        if not isinstance(url, (basestring, Text)):
            raise TypeError(
                "url must be str or Text (got %s)" % url.__class__.__name__)
        self.url = unicode(url)
        Text.__init__(self, *args)

    def render(self, backend):
        text = super(HRef, self).render(backend)
        return backend.format_href(self.url, text)


class Symbol(BaseText):
    """A special symbol.

    Examples of special symbols are non-breaking spaces and dashes.

    >>> nbsp = Symbol('nbsp')
    >>> from pybtex.backends import latex, html
    >>> print nbsp.render(latex.Backend())
    ~
    >>> print nbsp.render(html.Backend())
    &nbsp;
    """

    def __init__(self, name):
        self.name = name

    def __len__(self):
        return 1

    def __repr__(self):
        return "Symbol('%s')" % self.name

    def __unicode__(self):
        return u'<%s>' % self.name

    def render(self, backend):
        return backend.symbols[self.name]


nbsp = Symbol('nbsp')
