# -*- coding: utf8 -*-
#
# Copyright (c) 2014  Andrey Golovizin, Jorrit Wronski
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

from pybtex.backends import BaseBackend


class Backend(BaseBackend):
    u""" A backend to support markdown output. It implements the same
    features as the HTML backend.

    In addition to that, you can use the keyword php_extra=True to enable
    the definition list extension of php-markdown. The default is not to use
    it, since we cannot be sure that this feature is implemented on all
    systems.

    More information:
    http://www.michelf.com/projects/php-markdown/extra/#def-list



    """

    def __init__(self, encoding=None, php_extra=False):
        super(Backend, self).__init__(encoding=encoding)
        self.php_extra = php_extra

    default_suffix = '.md'
    symbols = {
        'ndash': u'&ndash',# or 'ndash': u'–',
        'newblock': u'\n',
        'nbsp': u' '
    }
    tags = {
         'emph': u'*',
    }

    def format_str(self, str_):
        """Format the given string *str_*.
        Escapes special markdown control characters.
        """
        table = {
          ord(u'\\'): u'\\\\',  # backslash
          ord(u'`') : u'\\`',   # backtick
          ord(u'*') : u'\\*',   # asterisk
          ord(u'_') : u'\\_',   # underscore
          ord(u'{') : u'\\{',   # curly braces
          ord(u'}') : u'\\}',   # curly braces
          ord(u'[') : u'\\[',   # square brackets
          ord(u']') : u'\\]',   # square brackets
          ord(u'(') : u'\\(',   # parentheses
          ord(u')') : u'\\)',   # parentheses
          ord(u'#') : u'\\#',   # hash mark
          ord(u'+') : u'\\+',   # plus sign
          ord(u'-') : u'\\-',   # minus sign (hyphen)
          ord(u'.') : u'\\.',   # dot
          ord(u'!') : u'\\!',   # exclamation mark
          #ord(u'&') : u'&amp;', # ampersand
          #ord(u'<') : u'&lt;',  # left angle bracket
        }
        return str_.translate(table)

    def format_tag(self, tag_name, text):
        tag = self.tags[tag_name]
        return ur'%s%s%s' % (tag, text, tag)

    def format_href(self, url, text):
        return ur'[%s](%s)' % (text, url)

    def write_entry(self, key, label, text):
        # Support http://www.michelf.com/projects/php-markdown/extra/#def-list
        if self.php_extra:
            self.output(u'%s\n' % label)
            self.output(u':   %s\n\n' % text)
        else:
            self.output(u'[%s] ' % label)
            self.output(u'%s  \n' % text)