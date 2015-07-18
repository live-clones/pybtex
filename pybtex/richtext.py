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
import itertools
from copy import deepcopy
from pybtex import textutils
from pybtex.utils import deprecated


def ensure_text(value):
    if isinstance(value, basestring):
        return String(value)
    elif isinstance(value, BaseText):
        return value
    else:
        bad_type = type(value).__name__
        raise TypeError('parts must be strings or BaseText instances, not ' + bad_type)


class BaseText(object):
    def __getitem__(self, key):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __reversed__(self):
        raise NotImplementedError

    def _flatten(self):
        yield self

    def _typeinfo(self):
        return None, ()

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


class BaseMultipartText(BaseText):
    info = ()

    def __init__(self, *parts):
        """Create a text object consisting of one or more parts.

        Text() objects are unpacked and their children are included directly.

        >>> Text(Text('Multi', ' '), Tag('em', 'part'), Text(' ', Text('text!')))
        Text(u'Multi', u' ', Tag(u'em', u'part'), u' ', u'text!')
        >>> Tag('strong', Text('Multi', ' '), Tag('em', 'part'), Text(' ', 'text!'))
        Tag(u'strong', u'Multi', u' ', Tag(u'em', u'part'), u' ', u'text!')

        Similar objects are merged into one.

        >>> Text('Multi', Tag('em', 'part'), Text(Tag('em', ' ', 'text!')))
        Text(u'Multi', Tag(u'em', u'part', u' ', u'text!'))
        >>> Text('Please ', HRef('http://example.com/', 'click'), HRef('http://example.com/', ' here'), '.')
        Text(u'Please ', HRef(u'http://example.com/', u'click', u' here'), u'.')
        """

        parts = [ensure_text(part) for part in parts]
        nonenpty_parts = [part for part in parts if part]
        flat_parts = itertools.chain(*(part._flatten() for part in parts))
        merged_parts = self._merge(flat_parts)
        self.parts = list(merged_parts)
        self.length = sum(len(part) for part in self.parts)

    def __len__(self):
        """Return the number of characters in this Text."""
        return self.length

    def __iter__(self):
        return iter(self.parts)

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

    def __getitem__(self, key):
        """
        >>> t = Text('123', Text('456', Text('78'), '9'), '0')
        >>> print unicode(t)
        1234567890
        >>> print unicode(t[:0])
        <BLANKLINE>
        >>> print unicode(t[:1])
        1
        >>> print unicode(t[:3])
        123
        >>> print unicode(t[:5])
        12345
        >>> print unicode(t[:7])
        1234567
        >>> print unicode(t[:10])
        1234567890
        >>> print unicode(t[:100])
        1234567890

        >>> print unicode(t[:-100])
        <BLANKLINE>
        >>> print unicode(t[:-10])
        <BLANKLINE>
        >>> print unicode(t[:-9])
        1
        >>> print unicode(t[:-7])
        123
        >>> print unicode(t[:-5])
        12345
        >>> print unicode(t[:-3])
        1234567

        >>> print unicode(t[-100:])
        1234567890
        >>> print unicode(t[-10:])
        1234567890
        >>> print unicode(t[-9:])
        234567890
        >>> print unicode(t[-7:])
        4567890
        >>> print unicode(t[-5:])
        67890
        >>> print unicode(t[-3:])
        890

        >>> print unicode(t[1:])
        234567890
        >>> print unicode(t[3:])
        4567890
        >>> print unicode(t[5:])
        67890
        >>> print unicode(t[7:])
        890
        >>> print unicode(t[10:])
        <BLANKLINE>
        >>> print unicode(t[100:])
        <BLANKLINE>

        >>> print unicode(t[0:10])
        1234567890
        >>> print unicode(t[0:100])
        1234567890
        >>> print unicode(t[2:3])
        3
        >>> print unicode(t[2:4])
        34
        >>> print unicode(t[3:7])
        4567
        >>> print unicode(t[4:7])
        567
        >>> print unicode(t[4:7])
        567
        >>> print unicode(t[7:9])
        89
        >>> print unicode(t[100:200])
        <BLANKLINE>

        """

        if isinstance(key, (int, long)):
            start = key
            end = key + 1
        elif isinstance(key, slice):
            start, end, step = key.indices(len(self))
            if step != 1:
                raise NotImplementedError
        else:
            raise ValueError(key, type(key))

        if start < 0:
            start = len(self) + start
        if end < 0:
            end = len(self) + end
        return self._slice_end(len(self) - start)._slice_beginning(end - start)

    def _slice_beginning(self, slice_length):
        parts = []
        length = 0
        for part in self.parts:
            if length + len(part) > slice_length:
                parts.append(part[:slice_length - length])
                break
            else:
                parts.append(part)
                length += len(part)
        return self.from_list(parts)

    def _slice_end(self, slice_length):
        parts = []
        length = 0
        for part in reversed(self.parts):
            if length + len(part) > slice_length:
                parts.append(part[len(part) -(slice_length - length):])
                break
            else:
                parts.append(part)
                length += len(part)
        return self.from_list(reversed(parts))

    def _typeinfo(self):
        return type(self), self.info

    def _merge(self, parts):
        groups = itertools.groupby(parts, lambda value: value._typeinfo())
        for typeinfo, group in groups:
            cls, info = typeinfo
            group = list(group)
            if cls and len(group) > 1:
                group_parts = itertools.chain(*(text.parts for text in group))
                args = list(info) + list(group_parts)
                yield cls(*args)
            else:
                for text in group:
                    yield text

    def render(self, backend):
        """Return backend-dependent textual representation of this Text."""

        rendered_list = [part.render(backend) for part in self.parts]
        assert all(isinstance(item, backend.RenderType)
                   for item in rendered_list)
        return backend.render_sequence(rendered_list)

    def enumerate(self):
        for n, child in enumerate(self.parts):
            try:
                for p in child.enumerate():
                    yield p
            except AttributeError:
                yield self, n

    def reversed(self):
        for n, child in reversed(list(enumerate(self.parts))):
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
            for index, child in enumerate(self.parts):
                if hasattr(child, 'map'):
                    yield child.map(f, condition) if condition(index, length) else child
                else:
                    yield f(child) if condition(index, length) else child
        return self.from_list(iter_map_with_condition())

    def upper(self):
        return self.map(string.upper)

    @deprecated('0.19', 'use slicing instead')
    def apply_to_start(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == 0)

    @deprecated('0.19', 'use slicing instead')
    def apply_to_end(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == length - 1)

    def get_beginning(self):
        try:
            l, i = self.enumerate().next()
        except StopIteration:
            pass
        else:
            return l.parts[i]

    def get_end(self):
        try:
            l, i = self.reversed().next()
        except StopIteration:
            pass
        else:
            return l.parts[i]

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
        return ''.join(unicode(part) for part in self.parts)

    def capfirst(self):
        """Capitalize the first letter of the text.

        >>> text = Text(Text(), Text('mary ', 'had ', 'a little lamb'))
        >>> print unicode(text)
        mary had a little lamb
        >>> print unicode(text.capfirst())
        Mary had a little lamb

        """
        return self[:1].upper() + self[1:]

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
            return self.from_list(self.parts + [period])
        else:
            return self


class String(unicode, BaseText):
    def capfirst(self):
        """
        Capitalize the first letter.

        >>> print String('').capfirst()
        <BLANKLINE>
        >>> print String('november').capfirst()
        November
        """

        try:
            first_char = self[0]
        except IndexError:
            return self
        else:
            return first_char.upper() + self[1:]

    def add_period(self):
        return self + '.'

    def render(self, backend):
        return backend.format_str(self)


class Text(BaseMultipartText):
    """
    Rich text is basically a list of:

    - plain strings
    - Text objects, including objects derived from Text (Tag, HRef, ...)
    - Symbol objects

    Text is used as an internal formatting language of Pybtex,
    being rendered to to HTML or LaTeX markup or whatever in the end.

    >>> Text()
    Text()
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

    def __repr__(self):
        return 'Text({})'.format(', '.join(repr(part) for part in self.parts))

    def _flatten(self):
        for part in self.parts:
            yield part

    def from_list(self, lst):
        return Text(*lst)


class Tag(BaseMultipartText):
    """A tag is somethins like <foo>some text</foo> in HTML
    or \\foo{some text} in LaTeX. 'foo' is the tag's name, and
    'some text' is tag's text.

    >>> emph = Tag('em', 'emphasized text')
    >>> from pybtex.backends import latex, html
    >>> print emph.render(latex.Backend())
    \emph{emphasized text}
    >>> print emph.render(html.Backend())
    <em>emphasized text</em>

    >>> t = Tag(u'emph', u'123', Tag(u'emph', u'456', Text(u'78'), u'9'), u'0')
    >>> print t[:2].render(html.Backend())
    <em>12</em>
    >>> print t[2:4].render(html.Backend())
    <em>3<em>4</em></em>
    >>> print t[4:].render(html.Backend())
    <em><em>56789</em>0</em>
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
        self.info = self.name,
        super(Tag, self).__init__(*args)

    def __repr__(self):
        reprparts = ', '.join(repr(part) for part in self.parts)
        return 'Tag({}, {})'.format(repr(self.name), reprparts)

    def render(self, backend):
        text = super(Tag, self).render(backend)
        return backend.format_tag(self.name, text)


class HRef(BaseMultipartText):
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
        self.info = self.url,
        super(HRef, self).__init__(*args)

    def __repr__(self):
        reprparts = ', '.join(repr(part) for part in self.parts)
        return 'HRef({}, {})'.format(repr(self.url), reprparts)

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
        self.info = self.name,

    def __len__(self):
        return 1

    def __repr__(self):
        return "Symbol(%s)" % repr(self.name)

    def __unicode__(self):
        return u'<%s>' % self.name

    def render(self, backend):
        return backend.symbols[self.name]


nbsp = Symbol('nbsp')
