# -*- coding: utf8 -*-
#
# Copyright (c) 2006-2021  Andrey Golovizin
# Copyright (c) 2014  Jorrit Wronski
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


r"""
Markdown output backend.

>>> from pybtex.richtext import Tag, HRef
>>> markdown = Backend()
>>> print(Tag('em', '').render(markdown))
<BLANKLINE>
>>> print(Tag('em', 'Non-', 'empty').render(markdown))
*Non\-empty*
>>> print(Tag('sup', 'super', 'man').render(markdown))
<sup>superman</sup>
>>> print(HRef('/', '').render(markdown))
<BLANKLINE>
>>> print(HRef('/', 'Non-', 'empty').render(markdown))
[Non\-empty](/)
"""

from __future__ import unicode_literals

from xml.sax.saxutils import escape

from pybtex.backends import BaseBackend, html

SPECIAL_CHARS = [
    "\\",  # backslash
    "`",  # backtick
    "*",  # asterisk
    "_",  # underscore
    "{",  # curly braces
    "}",  # curly braces
    "[",  # square brackets
    "]",  # square brackets
    "(",  # parentheses
    ")",  # parentheses
    "#",  # hash mark
    "+",  # plus sign
    "-",  # minus sign (hyphen)
    ".",  # dot
    "!",  # exclamation mark
]


class Backend(BaseBackend):
    """A backend to support markdown output. It implements the same
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

    default_suffix = ".md"
    symbols = {
        "ndash": "&ndash;",  # or 'ndash': u'–',
        "newblock": "\n",
        "nbsp": " ",
    }
    tags = {
        "em": "*",  # emphasize text
        "strong": "**",  # emphasize text even more
        "i": "*",  # italicize text: be careful, i is not semantic
        "b": "**",  # embolden text: be careful, b is not semantic
        "tt": "`",  # make text appear as code (typically typewriter text), a little hacky
    }

    def format_str(self, text):
        """Format the given string *str_*.
        Escapes special markdown control characters.
        """
        text = escape(text)
        for special_char in SPECIAL_CHARS:
            text = text.replace(special_char, "\\" + special_char)
        return text

    def format_tag(self, tag_name, text):
        tag = self.tags.get(tag_name)
        if tag is None:  # fall back on html tags
            return r"<{0}>{1}</{0}>".format(tag_name, text) if text else ""
        else:
            return r"{0}{1}{0}".format(tag, text) if text else ""

    def format_href(self, url, text, external=False):
        if not text:
            return ""
        if external:
            return html.Backend.format_href(url, text, external)
        else:
            return r"[%s](%s)" % (text, url)

    def write_entry(self, key, label, text):
        # Support http://www.michelf.com/projects/php-markdown/extra/#def-list
        if self.php_extra:
            self.output("%s\n" % label)
            self.output(":   %s\n\n" % text)
        else:
            self.output("[%s] " % label)
            self.output("%s  \n" % text)
