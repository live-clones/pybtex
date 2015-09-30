from unittest import TestCase

from pybtex import textutils
from pybtex.richtext import Text, String, Tag, HRef, nbsp


class TestText(TestCase):
    def test_add(self):
        t = Text('a')
        assert unicode(t + 'b') == 'ab'
        assert unicode(t + t) == 'aa'
        assert unicode(t) == 'a'

    def test_getitem(self):
        t = Text('123', Text('456', Text('78'), '9'), '0')
        assert unicode(t) == '1234567890'
        assert unicode(t[:0]) == ''
        assert unicode(t[:1]) == '1'
        assert unicode(t[:3]) == '123'
        assert unicode(t[:5]) == '12345'
        assert unicode(t[:7]) == '1234567'
        assert unicode(t[:10]) == '1234567890'
        assert unicode(t[:100]) == '1234567890'
        assert unicode(t[:-100]) == ''
        assert unicode(t[:-10]) == ''
        assert unicode(t[:-9]) == '1'
        assert unicode(t[:-7]) == '123'
        assert unicode(t[:-5]) == '12345'
        assert unicode(t[:-3]) == '1234567'
        assert unicode(t[-100:]) == '1234567890'
        assert unicode(t[-10:]) == '1234567890'
        assert unicode(t[-9:]) == '234567890'
        assert unicode(t[-7:]) == '4567890'
        assert unicode(t[-5:]) == '67890'
        assert unicode(t[-3:]) == '890'
        assert unicode(t[1:]) == '234567890'
        assert unicode(t[3:]) == '4567890'
        assert unicode(t[5:]) == '67890'
        assert unicode(t[7:]) == '890'
        assert unicode(t[10:]) == ''
        assert unicode(t[100:]) == ''
        assert unicode(t[0:10]) == '1234567890'
        assert unicode(t[0:100]) == '1234567890'
        assert unicode(t[2:3]) == '3'
        assert unicode(t[2:4]) == '34'
        assert unicode(t[3:7]) == '4567'
        assert unicode(t[4:7]) == '567'
        assert unicode(t[4:7]) == '567'
        assert unicode(t[7:9]) == '89'
        assert unicode(t[100:200]) == ''

    def test_append(self):
        text = Tag('strong', 'Chuck Norris')
        assert (text +  ' wins!').render_as('html') == '<strong>Chuck Norris</strong> wins!'
        assert text.append(' wins!').render_as('html') == '<strong>Chuck Norris wins!</strong>'
        text = HRef('/', 'Chuck Norris')
        assert (text +  ' wins!').render_as('html') == '<a href="/">Chuck Norris</a> wins!'
        assert text.append(' wins!').render_as('html') == '<a href="/">Chuck Norris wins!</a>'

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
