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
>>> print(Tag("em", "").render(markdown))
<BLANKLINE>
>>> print(Tag("em", "Non-", "empty").render(markdown))
*Non\-empty*
>>> print(Tag("sup", "super", "man").render(markdown))
<sup>superman</sup>
>>> print(HRef("/", "").render(markdown))
<BLANKLINE>
>>> print(HRef("/", "Non-", "empty").render(markdown))
[Non\-empty](/)
"""

from types import MappingProxyType
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
        super().__init__(encoding=encoding)
        self.php_extra = php_extra

    default_suffix = ".md"
    symbols = MappingProxyType(
        {
            "ndash": "&ndash;",  # or 'ndash': u'–',  # noqa: RUF003
            "newblock": "\n",
            "nbsp": " ",
        }
    )
    tags = MappingProxyType(
        {
            "em": "*",  # emphasize text
            "strong": "**",  # emphasize text even more
            "i": "*",  # italicize text: be careful, i is not semantic
            "b": "**",  # embolden text: be careful, b is not semantic
            "tt": "`",  # make text appear as code (typically typewriter text), a little hacky
        }
    )

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
            return rf"<{tag_name}>{text}</{tag_name}>" if text else ""
        return rf"{tag}{text}{tag}" if text else ""

    def format_href(self, url, text, external=False):
        if not text:
            return ""
        if external:
            return html.Backend.format_href(url, text, external)
        return rf"[{text}]({url})"

    def write_entry(self, key, label, text):
        # Support http://www.michelf.com/projects/php-markdown/extra/#def-list
        if self.php_extra:
            self.output(f"{label}\n")
            self.output(f":   {text}\n\n")
        else:
            self.output(f"[{label}] ")
            self.output(f"{text}  \n")
