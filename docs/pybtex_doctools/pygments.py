# Copyright (c) 2007, 2008, 2009, 2010, 2011, 2012, 2015  Andrey Golovizin
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

from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic, Literal, Punctuation

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
        Name.Label:             '#A20',
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


def setup(app):
    add_entry_point('pygments.styles', 'pybtex', 'pybtex_doctools.pygments', 'PybtexStyle')
