# Copyright (c) 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
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

"""Built-in functions for BibTeX interpreter.

CAUTION: functions should PUSH results, not RETURN
"""


import pybtex.io
from pybtex.errors import report_error
from pybtex.bibtex.exceptions import BibTeXError
from pybtex.utils import memoize
from pybtex.bibtex import utils
from pybtex.database import Person
from pybtex.bibtex.names import format_name as format_bibtex_name


def print_warning(msg):
    report_error(BibTeXError(msg))
builtins = {}
builtin_vars = []


def builtin(name):
    def _builtin(f):
        builtins[name] = f
        builtin_vars.append(Builtin(name, f))
        return f
    return _builtin


def inline_builtin(name):
    def _builtin(f):
        builtin_vars.append(InlineBuiltin(name, f))
        # xxx direct execution
        return f
    return _builtin


class Builtin(object):
    def __init__(self, name, f):
        self.name = name
        self.f = f

    def execute(self, interpreter):
        self.f(interpreter)

    def __repr__(self):
        return '<builtin %s>' % self.name

    def write_code(self, interpreter, code):
        code.line('builtins[{!r}](i)'.format(self.name))


class InlineBuiltin:
    def __init__(self, name, write_code):
        self.name = name
        self.write_code = write_code


@inline_builtin('>')
def operator_more(i, code):
    code.pop('a2')
    code.pop('a1')
    code.push('1 if a1 > a2 else 0')


@inline_builtin('<')
def operator_more(i, code):
    code.pop('a2')
    code.pop('a1')
    code.push('1 if a1 < a2 else 0')


@inline_builtin('=')
def operator_equals(i, code):
    code.pop('a2')
    code.pop('a1')
    code.push('1 if a1 == a2 else 0')


@inline_builtin('*')
def operator_asterisk(i, code):
    code.pop('a2')
    code.pop('a1')
    code.push('a1 + a2')


@inline_builtin(':=')
def operator_assign(i, code):
    code.pop('var')
    code.pop('val')
    code.line('var.set(val)')


@inline_builtin('+')
def operator_plus(i, code):
    code.pop('a2')
    code.pop('a1')
    code.push('a1 + a2')


@inline_builtin('-')
def operator_plus(i, code):
    code.pop('a2')
    code.pop('a1')
    code.push('a1 - a2')


@builtin('add.period$')
def add_period(i):
    s = i.pop()
    if s and not s.rstrip('}')[-1] in '.?!':
        s += '.'
    i.push(s)

@builtin('call.type$')
def call_type(i):
    entry_type = i.current_entry.type
    try:
        func = i.vars[entry_type]
    except KeyError:
        print_warning(u'entry type for "{0}" isn\'t style-file defined'.format(
            i.current_entry_key,
        ))
        try:
            func = i.vars['default.type']
        except KeyError:
            return
    func.execute(i)

@builtin('change.case$')
def change_case(i):

    mode = i.pop()
    string = i.pop()

    if not mode:
        raise BibTeXError('empty mode string passed to change.case$')
    mode_letter = mode[0].lower()
    if not mode_letter in ('l', 'u', 't'):
        raise BibTeXError('incorrect change.case$ mode: %s' % mode)

    i.push(utils.change_case(string, mode_letter))

@builtin('chr.to.int$')
def chr_to_int(i):
    s = i.pop()
    try:
        value = ord(s)
    except TypeError:
        raise BibTeXError('%s passed to chr.to.int$', s)
    i.push(value)

@builtin('cite$')
def cite(i):
    i.push(i.current_entry_key)

@builtin('duplicate$')
def duplicate(i):
    tmp = i.pop()
    i.push(tmp)
    i.push(tmp)

@builtin('empty$')
def empty(i):
    #FIXME error checking
    s = i.pop()
    if s and not s.isspace():
        i.push(0)
    else:
        i.push(1)


@memoize
def _split_names(names):
    return utils.split_name_list(names)


@memoize
def _format_name(names, n, format):
    name = _split_names(names)[n - 1]
    return format_bibtex_name(name, format)


@builtin('format.name$')
def format_name(i):
    format = i.pop()
    n = i.pop()
    names = i.pop()
    i.push(_format_name(names, n, format))


@builtin('if$')
def if_(i):
    f1 = i.pop()
    f2 = i.pop()
    p = i.pop()
    if p > 0:
        f2.execute(i)
    else:
        f1.execute(i)

@builtin('int.to.chr$')
def int_to_chr(i):
    n = i.pop()
    try:
        char = unichr(n)
    except ValueError:
        raise BibTeXError('%i passed to int.to.chr$', n)
    i.push(char)

@builtin('int.to.str$')
def int_to_str(i):
    i.push(str(i.pop()))

@builtin('missing$')
def missing(i):
    f = i.pop()
    if i.is_missing_field(f):
        i.push(1)
    else:
        i.push(0)

@builtin('newline$')
def newline(i):
    i.newline()

@builtin('num.names$')
def num_names(i):
    names = i.pop()
    i.push(len(utils.split_name_list(names)))

@builtin('pop$')
def pop(i):
    i.pop()

@builtin('preamble$')
def preamble(i):
    i.push(i.bib_data.get_preamble())

@builtin('purify$')
def purify(i):
    s = i.pop()
    i.push(utils.bibtex_purify(s))

@builtin('quote$')
def quote(i):
    i.push('"')

@builtin('skip$')
def skip(i):
    pass

@builtin('substring$')
def substring(i):
    length = i.pop()
    start = i.pop()
    string = i.pop()
    i.push(utils.bibtex_substring(string, start, length))

@builtin('stack$')
def stack(i):
    while i.stack:
        print >>pybtex.io.stdout, i.pop()

@builtin('swap$')
def swap(i):
    tmp1 = i.pop()
    tmp2 = i.pop()
    i.push(tmp1)
    i.push(tmp2)

@builtin('text.length$')
def text_length(i):
    s = i.pop()
    i.push(utils.bibtex_len(s))

@builtin('text.prefix$')
def text_prefix(i):
    l = i.pop()
    s = i.pop()
    i.push(utils.bibtex_prefix(s, l))

@builtin('top$')
def top(i):
    print >>pybtex.io.stdout, i.pop()

@builtin('type$')
def type_(i):
    i.push(i.current_entry.type)

@builtin('warning$')
def warning(i):
    msg = i.pop()
    print_warning(msg)

@builtin('while$')
def while_(i):
    f = i.pop()
    p = i.pop()
    while True:
        p.execute(i)
        if i.pop() <= 0:
            break
        f.execute(i)

@builtin('width$')
def width(i):
    s = i.pop()
    i.push(utils.bibtex_width(s))

@builtin('write$')
def write(i):
    s = i.pop()
    i.output(s)
