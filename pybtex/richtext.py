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
>>> t = t.capitalize().add_period()
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


import warnings
import itertools
from abc import ABCMeta, abstractmethod
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
    __metaclass__ = ABCMeta

    @abstractmethod
    def __unicode__(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError

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

    def append(self, text):
        """
        Append text to the end of this text.

        Normally, this is the same as concatenating texts with +,
        but for tags and similar objects the appended text is placed _inside_ the tag.

        >>> import pybtex.backends.html
        >>> html = pybtex.backends.html.Backend()

        >>> text = Tag('em', 'Look here')
        >>> print (text +  '!').render(html)
        <em>Look here</em>!
        >>> print text.append('!').render(html)
        <em>Look here!</em>
        """

        return self + text

    def add_period(self, period='.'):
        """Add a period to the end of text, if necessary."""

        return self if textutils.is_terminated(unicode(self)) else self + period

    @deprecated('0.19', 'renamed to capitalize()')
    def capfirst(self):
        return self.capitalize()

    def capitalize(self):
        """Capitalize the first letter of the text."""
        return self[:1].upper() + self[1:]

    @abstractmethod
    def render(self, backend):
        raise NotImplementedError

    @abstractmethod
    def lower(self):
        raise NotImplementedError

    @abstractmethod
    def upper(self):
        raise NotImplementedError

    def _unpack(self):
        """
        For Text object, iterate over all text parts.
        Else, yield the object itself.

        Used for unpacking Text objects passed as children to another Text object.
        """

        yield self

    def _typeinfo(self):
        """

        Return the type of this object and its parameters
        (not including the actual text content).

        Used for:

        - merging similar tags together (<em>A</em><em>B</em> -> <em>AB</em>),
        - creating similar text objects with different text content.

        """

        return None, ()


class BaseMultipartText(BaseText):
    info = ()

    def __init__(self, *parts):
        """Create a text object consisting of one or more parts.

        Text() objects are unpacked and their children are included directly.

        >>> text = Text(Text('Multi', ' '), Tag('em', 'part'), Text(' ', Text('text!')))
        >>> text == Text('Multi', ' ', Tag('em', 'part'), ' ', 'text!')
        True
        >>> text = Tag('strong', Text('Multi', ' '), Tag('em', 'part'), Text(' ', 'text!'))
        >>> text == Tag('strong', 'Multi', ' ', Tag('em', 'part'), ' ', 'text!')
        True

        Similar objects are merged into one.

        >>> text = Text('Multi', Tag('em', 'part'), Text(Tag('em', ' ', 'text!')))
        >>> text == Text('Multi', Tag('em', 'part', ' ', 'text!'))
        True
        >>> text = Text('Please ', HRef('http://example.com/', 'click'), HRef('http://example.com/', ' here'), '.')
        >>> text == Text('Please ', HRef('http://example.com/', 'click', ' here'), '.')
        True
        """

        parts = [ensure_text(part) for part in parts]
        nonenpty_parts = [part for part in parts if part]
        flat_parts = itertools.chain(*(part._unpack() for part in parts))
        merged_parts = self._merge_similar(flat_parts)
        self.parts = list(merged_parts)
        self.length = sum(len(part) for part in self.parts)

    def __unicode__(self):
        return ''.join(unicode(part) for part in self.parts)

    def __eq__(self, other):
        return (
            isinstance(other, BaseText) and
            self._typeinfo() == other._typeinfo() and
            self.parts == other.parts
        )

    def __len__(self):
        """Return the number of characters in this Text."""
        return self.length

    def __getitem__(self, key):
        """
        Slicing and extracting characters works like with regular strings,
        formatting is preserved.

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
        """
        Return a text consistng of the first slice_length characters
        of this text (with formatting preserved).
        """

        parts = []
        length = 0
        for part in self.parts:
            if length + len(part) > slice_length:
                parts.append(part[:slice_length - length])
                break
            else:
                parts.append(part)
                length += len(part)
        return self._create_similar(parts)

    def _slice_end(self, slice_length):
        """
        Return a text consistng of the last slice_length characters
        of this text (with formatting preserved).
        """

        parts = []
        length = 0
        for part in reversed(self.parts):
            if length + len(part) > slice_length:
                parts.append(part[len(part) -(slice_length - length):])
                break
            else:
                parts.append(part)
                length += len(part)
        return self._create_similar(reversed(parts))

    def append(self, text):
        """
        Append text to the end of this text.

        For Tags, HRefs, etc. the appended text is placed _inside_ the tag.

        >>> import pybtex.backends.html
        >>> html = pybtex.backends.html.Backend()

        >>> text = Tag('strong', 'Chuck Norris')
        >>> print (text +  ' wins!').render(html)
        <strong>Chuck Norris</strong> wins!
        >>> print text.append(' wins!').render(html)
        <strong>Chuck Norris wins!</strong>

        >>> text = HRef('/', 'Chuck Norris')
        >>> print (text +  ' wins!').render(html)
        <a href="/">Chuck Norris</a> wins!
        >>> print text.append(' wins!').render(html)
        <a href="/">Chuck Norris wins!</a>
        """

        return self._create_similar(self.parts + [text])

    def add_period(self, period='.'):
        """Add a period to the end of text, if necessary.

        >>> import pybtex.backends.html
        >>> html = pybtex.backends.html.Backend()

        >>> text = Text("That's all, folks")
        >>> print unicode(text.upper())
        THAT'S ALL, FOLKS
        >>> print unicode(text.lower())
        that's all, folks
        >>> print unicode(text.add_period())
        That's all, folks.

        >>> text = Tag('em', Text("That's all, folks"))
        >>> print text.upper().render(html)
        <em>THAT'S ALL, FOLKS</em>
        >>> print text.lower().render(html)
        <em>that's all, folks</em>
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
        >>> print text.upper().render(html)
        THAT'S ALL, <em>FOLKS</em>
        >>> print text.lower().render(html)
        that's all, <em>folks</em>
        >>> print text.add_period('!').render(html)
        That's all, <em>folks</em>!
        >>> print text.add_period('!').add_period('.').render(html)
        That's all, <em>folks</em>!
        """

        end = self.get_end()
        if end and not textutils.is_terminated(unicode(end)):
            return self.append(period)
        else:
            return self

    def lower(self):
        return self._create_similar(part.lower() for part in self.parts)

    def upper(self):
        return self._create_similar(part.upper() for part in self.parts)

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

    def render(self, backend):
        """Return backend-dependent textual representation of this Text."""

        rendered_list = [part.render(backend) for part in self.parts]
        assert all(isinstance(item, backend.RenderType)
                   for item in rendered_list)
        return backend.render_sequence(rendered_list)

    def _typeinfo(self):
        """Return the type and the parameters used to create this text object.

        >>> text = Tag('strong', 'Heavy rain!')
        >>> text._typeinfo() == (Tag, ('strong',))
        True

        """

        return type(self), self.info

    def _create_similar(self, parts):
        """
        Create a new text object of the same type with the same parameters,
        with different text content.

        >>> text = Tag('strong', 'Bananas!')
        >>> text._create_similar(['Apples!']) == Tag('strong', 'Apples!')
        True
        """

        cls, cls_args = self._typeinfo()
        args = list(cls_args) + list(parts)
        return cls(*args)

    def _merge_similar(self, parts):
        """Merge adjacent text objects with the same type and parameters together.

        >>> text = Text()
        >>> parts = [Tag('em', 'Breaking'), Tag('em', ' '), Tag('em', 'news!')]
        >>> merged_parts = list(text._merge_similar(parts))
        >>> merged_parts == [Tag('em', 'Breaking news!')]
        True
        """

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

    @deprecated('0.19', 'use __unicode__() instead')
    def plaintext(self):
        return unicode(self)

    @deprecated('0.19')
    def enumerate(self):
        for n, child in enumerate(self.parts):
            try:
                for p in child.enumerate():
                    yield p
            except AttributeError:
                yield self, n

    @deprecated('0.19')
    def reversed(self):
        for n, child in reversed(list(enumerate(self.parts))):
            try:
                for p in child.reversed():
                    yield p
            except AttributeError:
                yield self, n

    @deprecated('0.19', 'use slicing instead')
    def get_beginning(self):
        try:
            l, i = self.enumerate().next()
        except StopIteration:
            pass
        else:
            return l.parts[i]

    @deprecated('0.19', 'use slicing instead')
    def get_end(self):
        try:
            l, i = self.reversed().next()
        except StopIteration:
            pass
        else:
            return l.parts[i]

    @deprecated('0.19', 'use slicing instead')
    def apply_to_start(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == 0)

    @deprecated('0.19', 'use slicing instead')
    def apply_to_end(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == length - 1)

    @deprecated('0.19')
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
        return self._create_similar(iter_map_with_condition())


class String(BaseText):
    """
    A single Python string wrapped into BaseText interface.

    >>> print unicode(String('').capitalize())
    <BLANKLINE>
    >>> print unicode(String('').add_period())
    .
    >>> print unicode(String('').add_period('!'))
    !
    >>> print unicode(String('').add_period().add_period())
    .
    >>> print unicode(String('').add_period().add_period('!'))
    .
    >>> print unicode(String('').add_period('!').add_period())
    !

    >>> print unicode(String('november').capitalize())
    November
    >>> print unicode(String('November').capitalize())
    November
    >>> print unicode(String('November').add_period())
    November.

    """

    def __init__(self, *parts):
        """
        >>> print unicode(String('November', ', ', 'December', '.'))
        November, December.
        """

        self.value = ''.join(parts)

    def __repr__(self):
        return self.value.__repr__()

    def __unicode__(self):
        return unicode(self.value)

    def __eq__(self, other):
        """
        >>> String() == ''
        False
        >>> String('') == ''
        False
        >>> String() == String()
        True
        >>> String('') == String()
        True
        >>> String('', '', '') == String()
        True
        >>> String('Wa', '', 'ke', ' ', 'up') == String('Wake up')
        True
        """
        return type(other) == type(self) and self.value == other.value

    def __len__(self):
        return self.value.__len__()

    def __getitem__(self, index):
        """
        >>> digits = String('0123456789')
        >>> digits[0] == '0'
        False
        >>> digits[0] == String('0')
        True
        """

        return String(self.value.__getitem__(index))

    def __add__(self, other):
        """
        >>> String('Python') + String(' 3') == 'Python 3'
        False
        >>> String('Python') + String(' 3') == Text('Python 3')
        True
        >>> String('A').lower() == String('a')
        True
        >>> print unicode(String('Python') + String(' ') + String('3'))
        Python 3
        >>> print unicode(String('Python') + Text(' ') + String('3'))
        Python 3
        >>> print unicode(String('Python') + ' ' + '3')
        Python 3
        >>> print unicode(String('Python').append(' 3'))
        Python 3

        """

        return BaseText.__add__(self, other)

    def lower(self):
        """
        >>> String('A').lower() == 'a'
        False
        >>> String('A').lower() == String('a')
        True
        >>> print unicode(String('').lower())
        <BLANKLINE>
        >>> print unicode(String('November').lower())
        november
        """

        return String(self.value.lower())

    def upper(self):
        """
        >>> String('a').upper() == 'A'
        False
        >>> String('a').upper() == String('A')
        True
        >>> print unicode(String('').upper())
        <BLANKLINE>
        >>> print unicode(String('', '').upper())
        <BLANKLINE>
        >>> print unicode(String('November').upper())
        NOVEMBER
        """

        return String(self.value.upper())

    @property
    def parts(self):
        return [unicode(self)]

    def _typeinfo(self):
        return String, ()

    def render(self, backend):
        return backend.format_str(self.value)


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

    >>> text = Text(Text(), Text('mary ', 'had ', 'a little lamb'))
    >>> print unicode(text)
    mary had a little lamb
    >>> print unicode(text.capitalize())
    Mary had a little lamb
    >>> print unicode(text.upper())
    MARY HAD A LITTLE LAMB
    >>> print unicode(text.lower())
    mary had a little lamb
    """

    def __repr__(self):
        return 'Text({})'.format(', '.join(repr(part) for part in self.parts))

    def _unpack(self):
        for part in self.parts:
            yield part


class Tag(BaseMultipartText):
    """A tag is somethins like <foo>some text</foo> in HTML
    or \\foo{some text} in LaTeX. 'foo' is the tag's name, and
    'some text' is tag's text.

    >>> em = Tag('em', 'Emphasized text')
    >>> from pybtex.backends import latex, html
    >>> print em.render(latex.Backend())
    \emph{Emphasized text}
    >>> print em.upper().render(latex.Backend())
    \emph{EMPHASIZED TEXT}
    >>> print em.lower().render(latex.Backend())
    \emph{emphasized text}
    >>> print em.render(html.Backend())
    <em>Emphasized text</em>

    >>> t = Tag(u'em', u'123', Tag(u'em', u'456', Text(u'78'), u'9'), u'0')
    >>> print t[:2].render(html.Backend())
    <em>12</em>
    >>> print t[2:4].render(html.Backend())
    <em>3<em>4</em></em>

    >>> tag = Tag('em', Text(), Text('mary ', 'had ', 'a little lamb'))
    >>> print tag.render(html.Backend())
    <em>mary had a little lamb</em>
    >>> print tag.upper().render(html.Backend())
    <em>MARY HAD A LITTLE LAMB</em>
    >>> print tag.lower().render(html.Backend())
    <em>mary had a little lamb</em>
    >>> print tag.capitalize().render(html.Backend())
    <em>Mary had a little lamb</em>
    >>> print tag.add_period().render(html.Backend())
    <em>mary had a little lamb.</em>
    >>> print tag.add_period().add_period().render(html.Backend())
    <em>mary had a little lamb.</em>
    """

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

    >>> href = HRef('http://www.example.com', 'Hyperlinked text.')
    >>> from pybtex.backends import latex, html, plaintext
    >>> print href.upper().render(latex.Backend())
    \href{http://www.example.com}{HYPERLINKED TEXT.}
    >>> print href.lower().render(latex.Backend())
    \href{http://www.example.com}{hyperlinked text.}
    >>> print href.render(latex.Backend())
    \href{http://www.example.com}{Hyperlinked text.}
    >>> print href.render(html.Backend())
    <a href="http://www.example.com">Hyperlinked text.</a>
    >>> print href.render(plaintext.Backend())
    Hyperlinked text.

    >>> tag = HRef('info.html', Text(), Text('Mary ', 'had ', 'a little lamb'))
    >>> print tag.render(html.Backend())
    <a href="info.html">Mary had a little lamb</a>
    >>> print tag.upper().render(html.Backend())
    <a href="info.html">MARY HAD A LITTLE LAMB</a>
    >>> print tag.lower().render(html.Backend())
    <a href="info.html">mary had a little lamb</a>
    >>> print tag.lower().capitalize().render(html.Backend())
    <a href="info.html">Mary had a little lamb</a>
    >>> print tag.add_period().render(html.Backend())
    <a href="info.html">Mary had a little lamb.</a>
    >>> print tag.add_period().add_period().render(html.Backend())
    <a href="info.html">Mary had a little lamb.</a>

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

    >>> print Text(nbsp).capitalize().render(html.Backend())
    &nbsp;
    >>> print nbsp.upper().render(html.Backend())
    &nbsp;
    >>> print nbsp.lower().render(html.Backend())
    &nbsp;
    >>> print nbsp.add_period().render(html.Backend())
    &nbsp;.
    >>> print nbsp.add_period().add_period().render(html.Backend())
    &nbsp;.
    >>> print (nbsp + '.').render(html.Backend())
    &nbsp;.
    >>> print nbsp.append('.').render(html.Backend())
    &nbsp;.
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

    def __eq__(self, other):
        """
        >>> Symbol('nbsp') == Symbol('nbsp')
        True
        >>> Symbol('nbsp') == Symbol('ndash')
        False
        """
        return self.name == other.name

    def __getitem__(self, index):
        """
        >>> import pybtex.backends.html
        >>> html = pybtex.backends.html.Backend()

        >>> symbol = Symbol('nbsp')
        >>> symbol[0]
        Symbol('nbsp')
        >>> symbol[0:]
        Symbol('nbsp')
        >>> symbol[0:5]
        Symbol('nbsp')
        >>> print symbol[1:].render(html)
        <BLANKLINE>
        >>> print symbol[1:5].render(html)
        <BLANKLINE>
        >>> symbol[1]
        Traceback (most recent call last):
            ...
        IndexError: richtext.Symbol index out of range
        """

        # mimic the behavior of a 1-element string
        try:
            result = 'a'[index]
        except IndexError:
            raise IndexError('richtext.Symbol index out of range')
        else:
            return self if result else String()

    def render(self, backend):
        return backend.symbols[self.name]

    def upper(self):
        return self

    def lower(self):
        return self


nbsp = Symbol('nbsp')
