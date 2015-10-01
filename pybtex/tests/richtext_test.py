#! vim:fileencoding=utf-8

from abc import ABCMeta, abstractmethod
from unittest import TestCase

from nose.tools import assert_raises

from pybtex import textutils
from pybtex.richtext import Text, String, Tag, HRef, Symbol, nbsp


class TextTestMixin(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def test__init__(self):
        raise NotImplementedError

    @abstractmethod
    def test__unicode__(self):
        raise NotImplementedError

    @abstractmethod
    def test__eq__(self):
        raise NotImplementedError

    @abstractmethod
    def test__len__(self):
        raise NotImplementedError

    @abstractmethod
    def test__contains__(self):
        raise NotImplementedError

    @abstractmethod
    def test__getitem__(self):
        raise NotImplementedError

    @abstractmethod
    def test__add__(self):
        raise NotImplementedError

    @abstractmethod
    def test_append(self):
        raise NotImplementedError

    @abstractmethod
    def test_join(self):
        raise NotImplementedError

    @abstractmethod
    def test_split(self):
        raise NotImplementedError

    @abstractmethod
    def test_startswith(self):
        raise NotImplementedError

    @abstractmethod
    def test_endswith(self):
        raise NotImplementedError

    @abstractmethod
    def test_add_period(self):
        raise NotImplementedError

    @abstractmethod
    def test_lower(self):
        raise NotImplementedError

    @abstractmethod
    def test_upper(self):
        raise NotImplementedError

    @abstractmethod
    def test_render_as(self):
        raise NotImplementedError


class TestText(TextTestMixin, TestCase):
    def test__init__(self):
        assert unicode(Text('a', '', 'c')) == 'ac'
        assert unicode(Text('a', Text(), 'c')) == 'ac'

        text = Text(Text(), Text('mary ', 'had ', 'a little lamb'))
        assert unicode(text) == 'mary had a little lamb'

        text = unicode(Text('a', Text('b', 'c'), Tag('em', 'x'), Symbol('nbsp'), 'd'))
        assert text == 'abcx<nbsp>d'

        assert_raises(TypeError, Text, {})

    def test__eq__(self):
        assert Text() == Text()

    def test__len__(self):
        assert len(Text()) == 0
        assert len(Text('Never', ' ', 'Knows', ' ', 'Best')) == len('Never Knows Best')
        assert len(Text('Never', ' ', Tag('em', 'Knows', ' '), 'Best')) == len('Never Knows Best')
        assert len(Text('Never', ' ', Tag('em', HRef('/', 'Knows'), ' '), 'Best')) == len('Never Knows Best')

    def test__unicode__(self):
        assert unicode(Text()) == ''
        assert unicode(Text(u'Чудаки украшают мир')) == u'Чудаки украшают мир'

    def test__contains__(self):
        text = Text('mary ', 'had ', 'a little lamb')
        assert 'mary' in text
        assert not 'Mary' in text
        assert 'had a little' in text

        text = Text('a', 'b', 'c')
        assert 'abc' in text

    def test_startswith(self):
        text = Text('mary ', 'had ', 'a little lamb')
        assert not Text().startswith('.')
        assert not Text().startswith(('.', '!'))

    def test_endswith(self):
        text = Text('mary ', 'had ', 'a little lamb')
        assert not Text().endswith('.')
        assert not Text().endswith(('.', '!'))

    def test_capitalize(self):
        text = Text('mary ', 'had ', 'a little lamb')
        assert unicode(text.capitalize()) == 'Mary had a little lamb'

    def test__add__(self):
        t = Text('a')
        assert unicode(t + 'b') == 'ab'
        assert unicode(t + t) == 'aa'
        assert unicode(t) == 'a'

    def test__getitem__(self):
        t = Text('123', Text('456', Text('78'), '9'), '0')
        assert t == Text('1234567890')
        assert t[:0] == Text('')
        assert t[:1] == Text('1')
        assert t[:3] == Text('123')
        assert t[:5] == Text('12345')
        assert t[:7] == Text('1234567')
        assert t[:10] == Text('1234567890')
        assert t[:100] == Text('1234567890')
        assert t[:-100] == Text('')
        assert t[:-10] == Text('')
        assert t[:-9] == Text('1')
        assert t[:-7] == Text('123')
        assert t[:-5] == Text('12345')
        assert t[:-3] == Text('1234567')
        assert t[-100:] == Text('1234567890')
        assert t[-10:] == Text('1234567890')
        assert t[-9:] == Text('234567890')
        assert t[-7:] == Text('4567890')
        assert t[-5:] == Text('67890')
        assert t[-3:] == Text('890')
        assert t[1:] == Text('234567890')
        assert t[3:] == Text('4567890')
        assert t[5:] == Text('67890')
        assert t[7:] == Text('890')
        assert t[10:] == Text('')
        assert t[100:] == Text('')
        assert t[0:10] == Text('1234567890')
        assert t[0:100] == Text('1234567890')
        assert t[2:3] == Text('3')
        assert t[2:4] == Text('34')
        assert t[3:7] == Text('4567')
        assert t[4:7] == Text('567')
        assert t[4:7] == Text('567')
        assert t[7:9] == Text('89')
        assert t[100:200] == Text('')

    def test_append(self):
        text = Tag('strong', 'Chuck Norris')
        assert (text +  ' wins!').render_as('html') == '<strong>Chuck Norris</strong> wins!'
        assert text.append(' wins!').render_as('html') == '<strong>Chuck Norris wins!</strong>'
        text = HRef('/', 'Chuck Norris')
        assert (text +  ' wins!').render_as('html') == '<a href="/">Chuck Norris</a> wins!'
        assert text.append(' wins!').render_as('html') == '<a href="/">Chuck Norris wins!</a>'

    def test_upper(self):
        text = Text('mary ', 'had ', 'a little lamb')
        assert unicode(text.upper()) == 'MARY HAD A LITTLE LAMB'

    def test_lower(self):
        text = Text('mary ', 'had ', 'a little lamb')
        assert unicode(text.lower()) == 'mary had a little lamb'

    def test_startswith(self):
        text = Text('mary ', 'had ', 'a little lamb')
        assert not text.startswith('M')
        assert text.startswith('m')

        text = Text('a', 'b', 'c')
        assert text.startswith('ab')

        assert Text('This is good').startswith(('This', 'That'))
        assert not Text('This is good').startswith(('That', 'Those'))

    def test_endswith(self):
        text = Text('mary ', 'had ', 'a little lamb')
        assert not text.endswith('B')
        assert text.endswith('b')

        text = Text('a', 'b', 'c')
        assert text.endswith('bc')

        assert Text('This is good').endswith(('good', 'wonderful'))
        assert not Text('This is good').endswith(('bad', 'awful'))

    def test_join(self):
        assert unicode(Text(' ').join(['a', Text('b c')])) == 'a b c'
        assert unicode(Text(nbsp).join(['a', 'b', 'c'])) == 'a<nbsp>b<nbsp>c'
        assert unicode(nbsp.join(['a', 'b', 'c'])) == 'a<nbsp>b<nbsp>c'
        assert unicode(String('-').join(['a', 'b', 'c'])) == 'a-b-c'
        result = Tag('em', ' and ').join(['a', 'b', 'c']).render_as('html')
        assert result == 'a<em> and </em>b<em> and </em>c'
        result = HRef('/', ' and ').join(['a', 'b', 'c']).render_as('html')
        assert result == 'a<a href="/"> and </a>b<a href="/"> and </a>c'

    def test_split(self):
        assert Text().split() == []
        assert Text().split('abc') == [Text()]
        assert Text('a').split() == [Text('a')]
        assert Text('a ').split() == [Text('a')]
        assert Text('   a   ').split() == [Text('a')]
        assert Text('a + b').split() == [Text('a'), Text('+'), Text('b')]
        assert Text('a + b').split(' + ') == [Text('a'), Text('b')]
        assert Text('abc').split('xyz') == [Text('abc')]
        assert Text('---').split('--') == [Text(), Text('-')]
        assert Text('---').split('-') == [Text(), Text(), Text(), Text()]

    def test_add_period(self):
        assert Text().endswith(('.', '!', '?')) == False
        assert textutils.is_terminated(Text()) == False

        assert unicode(Text().add_period()) == ''

        text = Text("That's all, folks")
        assert unicode(text.add_period()) == "That's all, folks."

    def test_render_as(self):
        string = Text('Detektivbyrån & friends')
        assert string.render_as('text') == 'Detektivbyrån & friends'
        assert string.render_as('html') == 'Detektivbyrån &amp; friends'


class TestString(TextTestMixin, TestCase):
    def test__init__(self):
        assert String().value == ''
        assert String('').value == ''
        assert String('Wa', '', 'ke', ' ', 'up!').value == 'Wake up!'

    def test__eq__(self):
        assert String() != ''
        assert String('') != ''
        assert String() == String()
        assert String('') == String()
        assert String('', '', '') == String()
        assert String('Wa', '', 'ke', ' ', 'up!') == String('Wake up!')

    def test__len__(self):
        assert len(String()) == len(String('')) == 0

        val = 'test string'
        assert len(String(val)) == len(val)

    def test__unicode__(self):
        val = u'Detektivbyrån'
        assert unicode(String(val)) == val

    def test__contains__(self):
        assert '' in String()
        assert 'abc' not in String()
        assert '' in String(' ')
        assert ' + ' in String('2 + 2')

    def test__getitem__(self):
        digits = String('0123456789')
        assert digits[0] != '0'
        assert digits[0] == String('0')

    def test__add__(self):
        assert String('Python') + String(' 3') != 'Python 3'
        assert String('Python') + String(' 3') == Text('Python 3')
        assert String('A').lower() == String('a')
        assert unicode(String('Python') + String(' ') + String('3')) == 'Python 3'
        assert unicode(String('Python') + Text(' ') + String('3')) == 'Python 3'
        assert unicode(String('Python') + ' ' + '3') == 'Python 3'
        assert unicode(String('Python').append(' 3')) == 'Python 3'

    def test_startswith(self):
        assert not String().startswith('n')
        assert not String('').startswith('n')
        assert not String().endswith('n')
        assert not String('').endswith('n')
        assert not String('November.').startswith('n')
        assert String('November.').startswith('N')

    def test_endswith(self):
        assert not String().endswith('.')
        assert not String().endswith(('.', '!'))
        assert not String('November.').endswith('r')
        assert String('November.').endswith('.')
        assert String('November.').endswith(('.', '!'))
        assert not String('November.').endswith(('?', '!'))

    def test_append(self):
        assert String().append('') == Text()
        text = String('The').append(' Adventures of ').append('Tom Sawyer')
        assert text == Text('The Adventures of Tom Sawyer')

    def test_lower(self):
        assert String('').lower() == String()
        assert String('A').lower() == String('a')
        assert String('November').lower() == String('november')

    def test_upper(self):
        assert String('').upper() == String()
        assert String('a').upper() == String('A')
        assert String('November').upper() == String('NOVEMBER')

    def test_split(self):
        assert String().split() == []
        assert String().split('abc') == [String('')]
        assert String('a').split() == [String('a')]
        assert String('a ').split() == [String('a')]
        assert String('a + b').split() == [String('a'), String('+'), String('b')]
        assert String('a + b').split(' + ') == [String('a'), String('b')]

    def test_join(self):
        assert String().join([]) == Text()
        assert String('nothing to see here').join([]) == Text()
        assert String().join(['a', 'b', 'c']) == Text('abc')
        assert String(', ').join(['tomatoes']) == Text('tomatoes')
        assert String(', ').join(['tomatoes', 'cucumbers']) == Text('tomatoes, cucumbers')
        assert String(', ').join(['tomatoes', 'cucumbers', 'lemons']) == Text('tomatoes, cucumbers, lemons')

    def test_capitalize(self):
        assert unicode(String('').capitalize()) == ''
        assert unicode(String('').add_period()) == ''
        assert unicode(String('').add_period('!')) == ''
        assert unicode(String('').add_period().add_period()) == ''
        assert unicode(String('').add_period().add_period('!')) == ''
        assert unicode(String('').add_period('!').add_period()) == ''
        assert unicode(String('november').capitalize()) == 'November'
        assert unicode(String('November').capitalize()) == 'November'
        assert unicode(String('November').add_period()) == 'November.'

    def test_add_period(self):
        result = unicode(String('November').add_period().add_period())
        assert result == 'November.'

    def test_render_as(self):
        string = String('Detektivbyrån & friends')
        assert string.render_as('text') == 'Detektivbyrån & friends'
        assert string.render_as('html') == 'Detektivbyrån &amp; friends'


class TestTag(TestCase):
    def test_append(self):
        text = Tag('em', 'Look here')
        assert (text +  '!').render_as('html') == '<em>Look here</em>!'
        assert text.append('!').render_as('html') == '<em>Look here!</em>'

    def test_add_period(self):
        text = Tag('em', Text("That's all, folks"))
        assert text.add_period().render_as('html') == "<em>That's all, folks.</em>"
        assert text.add_period().add_period().render_as('html') == "<em>That's all, folks.</em>"

        text = Text("That's all, ", Tag('em', 'folks'))
        assert text.add_period().render_as('html') == "That's all, <em>folks</em>."
        assert text.add_period().add_period().render_as('html') == "That's all, <em>folks</em>."

        text = Text("That's all, ", Tag('em', 'folks.'))
        assert text.add_period().render_as('html') == "That's all, <em>folks.</em>"

        text = Text("That's all, ", Tag('em', 'folks'))
        assert text.add_period('!').render_as('html') == "That's all, <em>folks</em>!"

        text = text.add_period('!').add_period('.').render_as('html')
        assert text == "That's all, <em>folks</em>!"
