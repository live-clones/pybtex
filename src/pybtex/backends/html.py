# Copyright (c) 2006-2021  Andrey Golovizin
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


"""
HTML output backend.

>>> from pybtex.richtext import Tag, HRef
>>> html = Backend()
>>> print(Tag("em", "").render(html))
<BLANKLINE>
>>> print(Tag("em", "Hard &", " heavy").render(html))
<em>Hard &amp; heavy</em>
>>> print(HRef("/", "").render(html))
<BLANKLINE>
>>> print(HRef("/", "Hard & heavy").render(html))
<a href="/">Hard &amp; heavy</a>
"""

from types import MappingProxyType
from xml.sax.saxutils import escape

import pybtex.io
from pybtex.backends import BaseBackend

PROLOGUE = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head><meta name="generator" content="Pybtex">
<meta http-equiv="Content-Type" content="text/html; charset=%s">
<title>Bibliography</title>
</head>
<body>
<dl>
"""


class Backend(BaseBackend):
    """
    >>> from pybtex.richtext import Text, Tag, Symbol
    >>> print(Tag("em", Text("Л.:", Symbol("nbsp"), "<<Химия>>")).render(Backend()))
    <em>Л.:&nbsp;&lt;&lt;Химия&gt;&gt;</em>

    """

    default_suffix = ".html"
    symbols = MappingProxyType({"ndash": "&ndash;", "newblock": "\n", "nbsp": "&nbsp;"})

    def format_str(self, text):
        return escape(text)

    def format_protected(self, text):
        return rf'<span class="bibtex-protected">{text}</span>'

    def format_tag(self, tag, text):
        return rf"<{tag}>{text}</{tag}>" if text else ""

    @staticmethod
    def format_href(url, text, external=False):
        target = ' target="_blank"' if external else ""
        return rf'<a href="{url}"{target}>{text}</a>' if text else ""

    def write_prologue(self):
        encoding = self.encoding or pybtex.io.get_default_encoding()
        self.output(PROLOGUE % encoding)

    def write_epilogue(self):
        self.output("</dl></body></html>\n")

    def write_entry(self, key, label, text):
        self.output(f"<dt>{label}</dt>\n")
        self.output(f"<dd>{text}</dd>\n")
