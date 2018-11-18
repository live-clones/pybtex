# Copyright (c) 2006-2018  Andrey Golovigin
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


from __future__ import absolute_import

import re
from string import ascii_letters, digits

from pybtex.database.input.bibtex import NAME_CHARS

from pygments.lexer import (
    ExtendedRegexLexer, RegexLexer, default, include, words
)
from pygments.style import Style
from pygments.token import (
    Comment, Error, Generic, Keyword, Literal, Name, Number, Operator,
    Punctuation, String, Text
)

from . import add_entry_point


class PybtexStyle(Style):
    """
    Port of the default trac highlighter design.
    """

    default_style = ''

    styles = {
        Comment:                'italic #999999',
#        Comment.Preproc:        'bold noitalic #999999',
#        Comment.Special:        'bold #999999',

        Operator:               'bold',

        String:                 '#609000',
        Number:                 '#609000',
        String.Escape:          '#a10',
        Keyword:                'bold',
#        Keyword.Type:           '#445588',

        Name.Builtin:           'bold',
        Name.Function:          'bold #840',
        Name.Class:             'bold #b30',
        Name.Exception:         'bold #b30',
        Name.Decorator:         '#A20',
        Name.Namespace:         '#A20',
        Name.Label:             '#840',
#        Name.Variable:          '#088',
#        Name.Constant:          '#088',
        Name.Tag:               '#666',
#        Name.Entity:            '#800080',

        # used by YAML lexer
        Literal.Scalar.Plain:   '',
        Punctuation.Indicator:  '#888',

#        Generic.Heading:        '#999999',
#        Generic.Subheading:     '#aaaaaa',
#        Generic.Deleted:        'bg:#ffdddd #000000',
#        Generic.Inserted:       'bg:#ddffdd #000000',
        Generic.Error:          '#aa0000',
        Generic.Emph:           'italic',
        Generic.Strong:         'bold',
        Generic.Prompt:         '#666',
        Generic.Output:         '#666',
        Generic.Traceback:      '#aa0000',


        Error:                  'bg:#e3d2d2 #a61717'
    }


class BibTeXLexer(ExtendedRegexLexer):
    name = 'BibTeX'
    aliases = ['bibtex', 'bibtex-pybtex']
    filenames = ['*.bib']
    flags = re.IGNORECASE

    IDENTIFIER = r'[{0}][{1}]*'.format(re.escape(NAME_CHARS), re.escape(NAME_CHARS + digits))

    def open_brace_callback(self, match, ctx):
        opening_brace = match.group()
        ctx.opening_brace = opening_brace
        yield match.start(), Text.Punctuation, opening_brace
        ctx.pos = match.end()

    def close_brace_callback(self, match, ctx):
        closing_brace = match.group()
        if (
            ctx.opening_brace == '{' and closing_brace != '}' or
            ctx.opening_brace == '(' and closing_brace != ')'
        ):
            yield match.start(), Error, closing_brace
        else:
            yield match.start(), Text.Punctuation, closing_brace
        del ctx.opening_brace
        ctx.pos = match.end()

    tokens = {
        'root': [
            include('whitespace'),
            ('@comment', Comment),
            ('@preamble', Name.Class, ('closing-brace', 'value', 'opening-brace')),
            ('@string', Name.Class, ('closing-brace', 'field', 'opening-brace')),
            ('@' + IDENTIFIER, Name.Class, ('closing-brace', 'command-body', 'opening-brace')),
            ('.+', Comment),
        ],
        'opening-brace': [
            include('whitespace'),
            (r'[\{\(]', open_brace_callback, '#pop'),
        ],
        'closing-brace': [
            include('whitespace'),
            (r'[\}\)]', close_brace_callback, '#pop'),
        ],
        'command-body': [
            include('whitespace'),
            (r'[^\s\,\}]+', Name.Label, ('#pop', 'fields')),
        ],
        'fields': [
            include('whitespace'),
            (',', Text.Punctuation, 'field'),
            default('#pop'),
        ],
        'field': [
            include('whitespace'),
            (IDENTIFIER, Text.Punctuation, ('value', '=')),
            default('#pop'),
        ],
        '=': [
            include('whitespace'),
            ('=', Text.Punctuation, '#pop'),
        ],
        'value': [
            include('whitespace'),
            (IDENTIFIER, Name.Variable),
            ('"', String, 'quoted-string'),
            (r'\{', String, 'braced-string'),
            (r'[\d]+', Number),
            ('#', Text.Punctuation),
            default('#pop'),
        ],
        'quoted-string': [
            (r'\{', String, 'braced-string'),
            ('"', String, '#pop'),
            ('[^\{\"]+', String),
        ],
        'braced-string': [
            (r'\{', String, '#push'),
            (r'\}', String, '#pop'),
            ('[^\{\}]+', String),
        ],
        'whitespace': [
            (r'\s+', Text),
        ],
    }


class BSTLexer(RegexLexer):
    name = 'BST'
    aliases = ['bst', 'bst-pybtex']
    filenames = ['*.bst']
    flags = re.IGNORECASE | re.MULTILINE

    tokens = {
        'root': [
            include('whitespace'),
            (words(['read', 'sort']), Name.Class),
            (words(['execute', 'integers', 'iterate', 'reverse', 'strings']), Name.Class, ('group')),
            (words(['function', 'macro']), Name.Class, ('group', 'group')),
            (words(['entry']), Name.Class, ('group', 'group', 'group')),
        ],
        'group': [
            include('whitespace'),
            ('{', Text.Punctuation, ('#pop', 'group-end', 'body')),
        ],
        'group-end': [
            include('whitespace'),
            ('}', Text.Punctuation, '#pop'),
        ],
        'body': [
            include('whitespace'),
            (r'[^#\"\{\}\s]+\$', Name.Builtin),
            (r'[^#\"\{\}\s]+', Name.Variable),
            (r'"[^\"]*"', String),
            (r'#-?\d+', Number),
            ('{', Text.Punctuation, ('group-end', 'body')),
            default('#pop'),
        ],
        'whitespace': [
            ('\s+', Text),
            ('%.*?$', Comment.SingleLine),
        ],
    }


def setup(app):
    add_entry_point('pygments.styles', 'pybtex', 'pybtex_doctools.pygments', 'PybtexStyle')
    add_entry_point('pygments.lexers', 'bibtex-pybtex', 'pybtex_doctools.pygments', 'BibTeXLexer')
    add_entry_point('pygments.lexers', 'bst-pybtex', 'pybtex_doctools.pygments', 'BSTLexer')
