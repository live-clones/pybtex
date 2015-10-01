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

>>> t = Text('this ', 'is a ', Tag('em', 'very'), Text(' rich', ' text'))
>>> print t.render_as('latex')
this is a \emph{very} rich text
>>> print unicode(t)
this is a very rich text
>>> t = t.capitalize().add_period()
>>> print t.render_as('latex')
This is a \emph{very} rich text.
>>> print unicode(t)
This is a very rich text.
>>> print Symbol('ndash').render_as('latex')
--
>>> t = Text('Some ', Tag('em', Text('nested ', Tag('tt', 'Text', Text(' objects')))), '.')
>>> print t.render_as('latex')
Some \emph{nested \texttt{Text objects}}.
>>> print unicode(t)
Some nested Text objects.
>>> t = t.upper()
>>> print t.render_as('latex')
SOME \emph{NESTED \texttt{TEXT OBJECTS}}.
>>> print unicode(t)
SOME NESTED TEXT OBJECTS.

>>> t = Text(', ').join(['one', 'two', Tag('em', 'three')])
>>> print t.render_as('latex')
one, two, \emph{three}
>>> print unicode(t)
one, two, three
>>> t = Text(Symbol('nbsp')).join(['one', 'two', Tag('em', 'three')])
>>> print t.render_as('latex')
one~two~\emph{three}
>>> print unicode(t)
one<nbsp>two<nbsp>three
"""


import warnings
import itertools
from abc import ABCMeta, abstractmethod
from pybtex import textutils
from pybtex.utils import deprecated, collect_iterable


# workaround for doctests in Python 2/3
def str_repr(string):
    """
    >>> print str_repr('test')
    'test'
    >>> print str_repr(u'test')
    'test'
    """

    result = repr(string)
    if result.startswith('u'):
        return result[1:]
    else:
        return result



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
    def __contains__(self, item):
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
        """

        return Text(self, other)

    def append(self, text):
        """
        Append text to the end of this text.

        Normally, this is the same as concatenating texts with +,
        but for tags and similar objects the appended text is placed _inside_ the tag.

        >>> text = Tag('em', 'Look here')
        >>> print (text +  '!').render_as('html')
        <em>Look here</em>!
        >>> print text.append('!').render_as('html')
        <em>Look here!</em>
        """

        return self + text

    def join(self, parts):
        """Join a list using this text (like string.join)

        >>> print unicode(String('-').join(['a', 'b', 'c']))
        a-b-c
        """

        if not parts:
            return Text()
        joined = []
        for part in parts[:-1]:
            joined.extend([part, self])
        joined.append(parts[-1])
        return Text(*joined)

    @abstractmethod
    def split(sep=None):
        raise NotImplementedError

    @abstractmethod
    def startswith(self, prefix):
        """
        Return True if string starts with the prefix,
        otherwise return False.

        prefix can also be a tuple of suffixes to look for.
        """

        raise NotImplementedError

    @abstractmethod
    def endswith(self, suffix):
        """
        Return True if the string ends with the specified suffix,
        otherwise return False.

        suffix can also be a tuple of suffixes to look for.
        """

        raise NotImplementedError

    def add_period(self, period='.'):
        """
        Add a period to the end of text, if the last character is not ".", "!" or "?".

        >>> text = Text("That's all, folks")
        >>> print unicode(text.add_period())
        That's all, folks.

        >>> text = Text("That's all, folks!")
        >>> print unicode(text.add_period())
        That's all, folks!

        """

        if self and not textutils.is_terminated(self):
            return self.append(period)
        else:
            return self

    @deprecated('0.19', 'renamed to capitalize()')
    def capfirst(self):
        return self.capitalize()

    def capitalize(self):
        """Capitalize the first letter of the text."""
        return self[:1].upper() + self[1:]

    @abstractmethod
    def lower(self):
        raise NotImplementedError

    @abstractmethod
    def upper(self):
        raise NotImplementedError

    @abstractmethod
    def render(self, backend):
        raise NotImplementedError

    def render_as(self, format_name):
        from pybtex.plugin import find_plugin
        backend_cls = find_plugin('pybtex.backends', format_name)
        return self.render(backend_cls())

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

        Empty parts are ignored:

        >>> Text() == Text('') == Text('', '', '')
        True
        >>> Text('Word', '') == Text('Word')
        True

        Text() objects are unpacked and their children are included directly:

        >>> Text(Text('Multi', ' '), Tag('em', 'part'), Text(' ', Text('text!')))
        Text('Multi ', Tag('em', 'part'), ' text!')
        >>> Tag('strong', Text('Multi', ' '), Tag('em', 'part'), Text(' ', 'text!'))
        Tag('strong', 'Multi ', Tag('em', 'part'), ' text!')

        Similar objects are merged into one:

        >>> Text('Multi', Tag('em', 'part'), Text(Tag('em', ' ', 'text!')))
        Text('Multi', Tag('em', 'part text!'))
        >>> Text('Please ', HRef('http://example.com/', 'click'), HRef('http://example.com/', ' here'), '.')
        Text('Please ', HRef('http://example.com/', 'click here'), '.')
        """

        parts = (ensure_text(part) for part in parts)
        nonempty_parts = (part for part in parts if part)
        unpacked_parts = itertools.chain(*(part._unpack() for part in nonempty_parts))
        merged_parts = self._merge_similar(unpacked_parts)
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

    def __contains__(self, item):
        if not isinstance(item, basestring):
            raise ValueError(item)
        return not item or any(part.__contains__(item) for part in self.parts)

    def __getitem__(self, key):
        """
        Slicing and extracting characters works like with regular strings,
        formatting is preserved.
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

        >>> text = Tag('strong', 'Chuck Norris')
        >>> print (text +  ' wins!').render_as('html')
        <strong>Chuck Norris</strong> wins!
        >>> print text.append(' wins!').render_as('html')
        <strong>Chuck Norris wins!</strong>
        """

        return self._create_similar(self.parts + [text])

    @collect_iterable
    def split(self, sep=None, keep_empty_parts=None):
        """
        >>> Text('a + b').split()
        [Text('a'), Text('+'), Text('b')]

        >>> Text('a, b').split(', ')
        [Text('a'), Text('b')]
        """

        if keep_empty_parts is None:
            keep_empty_parts = sep is not None

        tail = [''] if keep_empty_parts else []
        for part in self.parts:
            split_part = part.split(sep, keep_empty_parts=True)
            if not split_part:
                continue
            for item in split_part[:-1]:
                if tail:
                    yield self._create_similar(tail + [item])
                    tail = []
                else:
                    if item or keep_empty_parts:
                        yield self._create_similar([item])
            tail.append(split_part[-1])
        if tail:
            tail_text = self._create_similar(tail)
            if tail_text or keep_empty_parts:
                yield tail_text


    def startswith(self, text):
        if not self.parts:
            return False
        else:
            return self.parts[0].startswith(text)

    def endswith(self, text):
        if not self.parts:
            return False
        else:
            return self.parts[-1].endswith(text)

    def lower(self):
        return self._create_similar(part.lower() for part in self.parts)

    def upper(self):
        return self._create_similar(part.upper() for part in self.parts)

    def render(self, backend):
        """
        Return backend-dependent textual representation of this Text.
        """

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
        >>> text._create_similar(['Apples!'])
        Tag('strong', 'Apples!')
        """

        cls, cls_args = self._typeinfo()
        args = list(cls_args) + list(parts)
        return cls(*args)

    def _merge_similar(self, parts):
        """Merge adjacent text objects with the same type and parameters together.

        >>> text = Text()
        >>> parts = [Tag('em', 'Breaking'), Tag('em', ' '), Tag('em', 'news!')]
        >>> list(text._merge_similar(parts))
        [Tag('em', 'Breaking news!')]
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
        return self.map(f, lambda index, length: index == 0)

    @deprecated('0.19', 'use slicing instead')
    def apply_to_end(self, f):
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
    <BLANKLINE>
    >>> print unicode(String('').add_period('!'))
    <BLANKLINE>
    >>> print unicode(String('').add_period().add_period())
    <BLANKLINE>
    >>> print unicode(String('').add_period().add_period('!'))
    <BLANKLINE>
    >>> print unicode(String('').add_period('!').add_period())
    <BLANKLINE>

    >>> print unicode(String('november').capitalize())
    November
    >>> print unicode(String('November').capitalize())
    November
    >>> print unicode(String('November').add_period())
    November.
    >>> print unicode(String('November').add_period().add_period())
    November.

    """

    def __init__(self, *parts):
        """
        >>> print unicode(String('November', ', ', 'December', '.'))
        November, December.
        """

        self.value = ''.join(parts)

    def __repr__(self):
        return str_repr(self.value)

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

    def __contains__(self, item):
        """
        >>> '' in String()
        True
        >>> 'abc' in String()
        False
        >>> '' in String(' ')
        True
        >>> ' + ' in String('2 + 2')
        True
        """

        return self.value.__contains__(item)

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

    def split(self, sep=None, keep_empty_parts=None):
        """
        >>> String().split()
        []
        >>> String().split('abc') == [String('')]
        True
        >>> String('a').split() == [String('a')]
        True
        >>> String('a ').split() == [String('a')]
        True
        >>> String('a + b').split() == [String('a'), String('+'), String('b')]
        True
        >>> String('a + b').split(' + ') == [String('a'), String('b')]
        True
        """

        if keep_empty_parts is None:
            keep_empty_parts = sep is not None

        if sep is None:
            from .textutils import whitespace_re
            parts = whitespace_re.split(self.value)
        else:
            parts = self.value.split(sep)
        return [String(part) for part in parts if part or keep_empty_parts]

    def startswith(self, prefix):
        """
        Return True if string starts with the prefix,
        otherwise return False.

        prefix can also be a tuple of suffixes to look for.

        >>> String().startswith('n')
        False
        >>> String('').startswith('n')
        False
        >>> String().endswith('n')
        False
        >>> String('').endswith('n')
        False
        >>> String('November.').startswith('n')
        False
        >>> String('November.').startswith('N')
        True
        """
        return self.value.startswith(prefix)


    def endswith(self, suffix):
        """
        Return True if the string ends with the specified suffix,
        otherwise return False.

        suffix can also be a tuple of suffixes to look for.
        return self.value.endswith(text)

        >>> String().endswith('.')
        False
        >>> String().endswith(('.', '!'))
        False
        >>> String('November.').endswith('r')
        False
        >>> String('November.').endswith('.')
        True
        >>> String('November.').endswith(('.', '!'))
        True
        >>> String('November.').endswith(('?', '!'))
        False
        """
        return self.value.endswith(suffix)

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

    >>> empty = Tag('em')
    >>> print unicode(empty)
    <BLANKLINE>
    >>> print unicode(empty.lower())
    <BLANKLINE>
    >>> print unicode(empty.capitalize())
    <BLANKLINE>
    >>> print unicode(empty.add_period())
    <BLANKLINE>
    >>> empty.split()
    []
    >>> empty.split('abc')
    [Tag('em')]

    >>> em = Tag('em', 'Emphasized text')
    >>> print em.render_as('latex')
    \emph{Emphasized text}
    >>> print em.upper().render_as('latex')
    \emph{EMPHASIZED TEXT}
    >>> print em.lower().render_as('latex')
    \emph{emphasized text}
    >>> print em.render_as('html')
    <em>Emphasized text</em>
    >>> em.split()
    [Tag('em', 'Emphasized'), Tag('em', 'text')]
    >>> em.split(' ')
    [Tag('em', 'Emphasized'), Tag('em', 'text')]
    >>> em.split('no such text') == [em]
    True

    >>> t = Tag(u'em', u'123', Tag(u'em', u'456', Text(u'78'), u'9'), u'0')
    >>> print t[:2].render_as('html')
    <em>12</em>
    >>> print t[2:4].render_as('html')
    <em>3<em>4</em></em>

    >>> tag = Tag('em', Text(), Text('mary ', 'had ', 'a little lamb'))
    >>> print tag.render_as('html')
    <em>mary had a little lamb</em>
    >>> print tag.upper().render_as('html')
    <em>MARY HAD A LITTLE LAMB</em>
    >>> print tag.lower().render_as('html')
    <em>mary had a little lamb</em>
    >>> print tag.capitalize().render_as('html')
    <em>Mary had a little lamb</em>
    >>> print tag.add_period().render_as('html')
    <em>mary had a little lamb.</em>
    >>> print tag.add_period().add_period().render_as('html')
    <em>mary had a little lamb.</em>

    >>> 'mary' in tag
    True
    >>> 'Mary' in tag
    False
    >>> 'had a little' in tag
    True
    >>> tag.startswith('M')
    False
    >>> tag.startswith('m')
    True
    >>> tag.endswith('B')
    False
    >>> tag.endswith('b')
    True
    >>> tag = Tag('em', 'a', 'b', 'c')
    >>> tag.startswith('ab')
    True
    >>> tag.endswith('bc')
    True
    >>> tag = Tag('em', 'This is good')
    >>> tag.startswith(('This', 'That'))
    True
    >>> tag.startswith(('That', 'Those'))
    False
    >>> tag.endswith(('good', 'wonderful'))
    True
    >>> tag.endswith(('bad', 'awful'))
    False
    >>> text = Text('This ', Tag('em', 'is'), ' good')
    >>> 'This is' in unicode(text)
    True
    >>> unicode(text).startswith('This is')
    True
    >>> unicode(text).endswith('is good')
    True
    >>> 'This is' in text
    False
    >>> text.startswith('This is')
    False
    >>> text.endswith('is good')
    False

    >>> text = Text('Bonnie ', Tag('em', 'and'), ' Clyde')
    >>> text.split('and')
    [Text('Bonnie '), Text(' Clyde')]
    >>> text.split(' and ') == [text]
    True
    >>> text = Text('Bonnie', Tag('em', ' and '), 'Clyde')
    >>> text.split('and')
    [Text('Bonnie', Tag('em', ' ')), Text(Tag('em', ' '), 'Clyde')]
    >>> text.split(' and ')
    [Text('Bonnie'), Text('Clyde')]
    >>> text = Text('From ', Tag('em', 'the very beginning'), ' of things')
    >>> text.split()
    [Text('From'), Text(Tag('em', 'the')), Text(Tag('em', 'very')), Text(Tag('em', 'beginning')), Text('of'), Text('things')]
    >>> dashified = String('-').join(text.split())
    >>> dashified
    Text('From-', Tag('em', 'the'), '-', Tag('em', 'very'), '-', Tag('em', 'beginning'), '-of-things')
    >>> dashified = Tag('em', '-').join(text.split())
    >>> dashified
    Text('From', Tag('em', '-the-very-beginning-'), 'of', Tag('em', '-'), 'things')

    """

    def __check_name(self, name):
        depr_map = {}
        depr_map[u'emph'] = u'em'
        if name in depr_map:
            msg  = u"The tag '%s' is deprecated" % name
            msg += u", use '%s' instead." % depr_map[name]
            warnings.warn(msg, DeprecationWarning, stacklevel=3)
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
        if self.parts:
            reprparts = ', '.join(repr(part) for part in self.parts)
            return 'Tag({}, {})'.format(str_repr(self.name), reprparts)
        else:
            return 'Tag({})'.format(str_repr(self.name))

    def render(self, backend):
        r"""
        >>> empty = Tag('em')
        >>> print empty.render_as('html')
        <BLANKLINE>
        >>> print empty.render_as('latex')
        <BLANKLINE>
        >>> tag = Tag('em', 'a', 'b')
        >>> print tag.render_as('html')
        <em>ab</em>
        >>> print tag.render_as('latex')
        \emph{ab}
        """

        text = super(Tag, self).render(backend)
        return backend.format_tag(self.name, text)


class HRef(BaseMultipartText):
    """A href is somethins like <href url="URL">some text</href> in HTML
    or \href{URL}{some text} in LaTeX.

    >>> empty = HRef('/')
    >>> print unicode(empty)
    <BLANKLINE>
    >>> print unicode(empty.lower())
    <BLANKLINE>
    >>> print unicode(empty.capitalize())
    <BLANKLINE>
    >>> print unicode(empty.add_period())
    <BLANKLINE>
    >>> empty.split()
    []
    >>> empty.split('abc') == [empty]
    True

    >>> href = HRef('http://www.example.com', 'Hyperlinked text.')
    >>> print href.upper().render_as('latex')
    \href{http://www.example.com}{HYPERLINKED TEXT.}
    >>> print href.lower().render_as('latex')
    \href{http://www.example.com}{hyperlinked text.}
    >>> print href.render_as('latex')
    \href{http://www.example.com}{Hyperlinked text.}
    >>> print href.render_as('html')
    <a href="http://www.example.com">Hyperlinked text.</a>
    >>> print href.render_as('plaintext')
    Hyperlinked text.

    >>> tag = HRef('info.html', Text(), Text('Mary ', 'had ', 'a little lamb'))
    >>> print tag.render_as('html')
    <a href="info.html">Mary had a little lamb</a>
    >>> print tag.upper().render_as('html')
    <a href="info.html">MARY HAD A LITTLE LAMB</a>
    >>> print tag.lower().render_as('html')
    <a href="info.html">mary had a little lamb</a>
    >>> print tag.lower().capitalize().render_as('html')
    <a href="info.html">Mary had a little lamb</a>
    >>> print tag.add_period().render_as('html')
    <a href="info.html">Mary had a little lamb.</a>
    >>> print tag.add_period().add_period().render_as('html')
    <a href="info.html">Mary had a little lamb.</a>

    >>> 'mary' in tag
    False
    >>> 'Mary' in tag
    True
    >>> 'had a little' in tag
    True
    >>> tag.startswith('M')
    True
    >>> tag.startswith('m')
    False
    >>> tag.endswith('B')
    False
    >>> tag.endswith('b')
    True
    >>> tag = HRef('/', 'a', 'b', 'c')
    >>> tag.startswith('ab')
    True
    >>> tag.endswith('bc')
    True
    >>> tag = HRef('/', 'This is good')
    >>> tag.startswith(('This', 'That'))
    True
    >>> tag.startswith(('That', 'Those'))
    False
    >>> tag.endswith(('good', 'wonderful'))
    True
    >>> tag.endswith(('bad', 'awful'))
    False
    >>> text = Text('This ', HRef('/', 'is'), ' good')
    >>> 'This is' in unicode(text)
    True
    >>> unicode(text).startswith('This is')
    True
    >>> unicode(text).endswith('is good')
    True
    >>> 'This is' in text
    False
    >>> text.startswith('This is')
    False
    >>> text.endswith('is good')
    False

    >>> href = HRef('/', 'World Wide Web')
    >>> href.split()
    [HRef('/', 'World'), HRef('/', 'Wide'), HRef('/', 'Web')]
    >>> Text('-').join(Text('Estimated size of the ', href).split())
    Text('Estimated-size-of-the-', HRef('/', 'World'), '-', HRef('/', 'Wide'), '-', HRef('/', 'Web'))
    >>> text = Text(Tag('em', Text(Tag('strong', HRef('/', '  Very, very'), ' bad'), ' guys')), '! ')
    >>> print text.render_as('html')
    <em><strong><a href="/">  Very, very</a> bad</strong> guys</em>! 
    >>> text.split(', ')
    [Text(Tag('em', Tag('strong', HRef('/', '  Very')))), Text(Tag('em', Tag('strong', HRef('/', 'very'), ' bad'), ' guys'), '! ')]
    >>> text.split(' ')
    [Text(), Text(), Text(Tag('em', Tag('strong', HRef('/', 'Very,')))), Text(Tag('em', Tag('strong', HRef('/', 'very')))), Text(Tag('em', Tag('strong', 'bad'))), Text(Tag('em', 'guys'), '!'), Text()]
    >>> text.split(' ', keep_empty_parts=False)
    [Text(Tag('em', Tag('strong', HRef('/', 'Very,')))), Text(Tag('em', Tag('strong', HRef('/', 'very')))), Text(Tag('em', Tag('strong', 'bad'))), Text(Tag('em', 'guys'), '!')]
    >>> text.split()
    [Text(Tag('em', Tag('strong', HRef('/', 'Very,')))), Text(Tag('em', Tag('strong', HRef('/', 'very')))), Text(Tag('em', Tag('strong', 'bad'))), Text(Tag('em', 'guys'), '!')]
    >>> text.split(keep_empty_parts=True)
    [Text(), Text(Tag('em', Tag('strong', HRef('/', 'Very,')))), Text(Tag('em', Tag('strong', HRef('/', 'very')))), Text(Tag('em', Tag('strong', 'bad'))), Text(Tag('em', 'guys'), '!'), Text()]
    >>> text = Text(' A', Tag('em', ' big', HRef('/', ' ', Tag('strong', 'no-no'), '!  ')))
    >>> print text.render_as('html')
     A<em> big<a href="/"> <strong>no-no</strong>!  </a></em>
    >>> text.split('-')
    [Text(' A', Tag('em', ' big', HRef('/', ' ', Tag('strong', 'no')))), Text(Tag('em', HRef('/', Tag('strong', 'no'), '!  ')))]
    >>> text.split(' ')
    [Text(), Text('A'), Text(Tag('em', 'big')), Text(Tag('em', HRef('/', Tag('strong', 'no-no'), '!'))), Text(), Text()]
    >>> text.split(' ', keep_empty_parts=False)
    [Text('A'), Text(Tag('em', 'big')), Text(Tag('em', HRef('/', Tag('strong', 'no-no'), '!')))]
    >>> text.split()
    [Text('A'), Text(Tag('em', 'big')), Text(Tag('em', HRef('/', Tag('strong', 'no-no'), '!')))]
    >>> text.split(keep_empty_parts=True)
    [Text(), Text('A'), Text(Tag('em', 'big')), Text(Tag('em', HRef('/', Tag('strong', 'no-no'), '!'))), Text()]
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
        return 'HRef({}, {})'.format(str_repr(self.url), reprparts)

    def render(self, backend):
        text = super(HRef, self).render(backend)
        return backend.format_href(self.url, text)


class Symbol(BaseText):
    """A special symbol.

    Examples of special symbols are non-breaking spaces and dashes.

    >>> print nbsp.render_as('latex')
    ~
    >>> print nbsp.render_as('html')
    &nbsp;

    >>> Text(nbsp, nbsp)
    Text(Symbol('nbsp'), Symbol('nbsp'))
    >>> print Text(nbsp, nbsp).render_as('html')
    &nbsp;&nbsp;
    >>> print Text(nbsp, nbsp).capitalize().render_as('html')
    &nbsp;&nbsp;
    >>> print nbsp.upper().render_as('html')
    &nbsp;
    >>> print nbsp.lower().render_as('html')
    &nbsp;
    >>> print nbsp.add_period().render_as('html')
    &nbsp;.
    >>> print nbsp.add_period().add_period().render_as('html')
    &nbsp;.
    >>> print (nbsp + '.').render_as('html')
    &nbsp;.
    >>> print nbsp.append('.').render_as('html')
    &nbsp;.

    >>> nbsp.startswith('.')
    False
    >>> nbsp.startswith(('.', '?!'))
    False
    >>> nbsp.endswith('.')
    False
    >>> nbsp.endswith(('.', '?!'))
    False
    """

    def __init__(self, name):
        self.name = name
        self.info = self.name,

    def __len__(self):
        return 1

    def __repr__(self):
        return "Symbol(%s)" % str_repr(self.name)

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

    def __contains__(self, item):
        """
        >>> '' in nbsp
        False
        >>> 'abc' in nbsp
        False
        """

        return False

    def __getitem__(self, index):
        """
        >>> symbol = Symbol('nbsp')
        >>> symbol[0]
        Symbol('nbsp')
        >>> symbol[0:]
        Symbol('nbsp')
        >>> symbol[0:5]
        Symbol('nbsp')
        >>> print symbol[1:].render_as('html')
        <BLANKLINE>
        >>> print symbol[1:5].render_as('html')
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

    def split(self, sep=None, keep_empty_parts=None):
        """
        >>> nbsp.split() == [nbsp]
        True
        >>> text = Text('F.', nbsp, 'Miller')
        >>> text.split() == [text]
        True
        """
        return [self]

    def startswith(self, text):
        return False

    def endswith(self, text):
        return False

    def render(self, backend):
        """
        >>> empty = HRef('/')
        >>> print empty.render_as('html')
        <BLANKLINE>
        >>> print empty.render_as('latex')
        <BLANKLINE>
        >>> tag = HRef('/', 'a', 'b')
        >>> print tag.render_as('html')
        <a href="/">ab</a>
        >>> print tag.render_as('latex')
        \href{/}{ab}
        """

        return backend.symbols[self.name]

    def upper(self):
        return self

    def lower(self):
        return self


nbsp = Symbol('nbsp')
