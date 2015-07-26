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
from .codegen import PythonCode


def print_warning(msg):
    report_error(BibTeXError(msg))
builtins = {}
inline_builtins = {}


def builtin(name):
    def _builtin(f):
        builtins[name] = f
        return f
    return _builtin


def inline_builtin(name):
    def _builtin(f):
        inline_builtins[name] = f
        return f
    return _builtin


@inline_builtin('>')
def operator_more(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('1 if {} > {} else 0', a1, a2)


@inline_builtin('<')
def operator_more(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('1 if {} < {} else 0', a1, a2)


@inline_builtin('=')
def operator_equals(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('1 if {} == {} else 0', a1, a2)


@inline_builtin('*')
def operator_asterisk(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('{} + {}', a1, a2)


@inline_builtin(':=')
def operator_assign(i, code):
    var = code.pop()
    val = code.pop()
    code.stmt('{}.set({})', var, val)


@inline_builtin('+')
def operator_plus(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('{} + {}', a1, a2)


@inline_builtin('-')
def operator_plus(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('{} - {}', a1, a2)


@inline_builtin('add.period$')
def add_period(i, code):
    text = code.pop()
    code.push('utils.bibtex_add_period({})', text)


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


@inline_builtin('change.case$')
def change_case(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('utils.change_case({}, {})', a1, a2)


@inline_builtin('chr.to.int$')
def chr_to_int(i, code):
    a1 = code.pop()
    code.push('utils.chr_to_int({})', a1)


@inline_builtin('cite$')
def cite(i, code):
    code.push('i.current_entry_key')


@inline_builtin('duplicate$')
def duplicate(i, code):
    a1 = code.pop()
    code.push(a1)
    code.push(a1)


@inline_builtin('empty$')
def empty(i, code):
    a1 = code.pop()
    code.push('0 if {0} and not {0}.isspace() else 1', a1)


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


@inline_builtin('if$')
def if_(i, code):
    a2 = code.pop()
    a1 = code.pop()
    cond = code.pop()
    code.stmt('({1} if {0} > 0 else {2}).execute(i)', cond, a1, a2)


@inline_builtin('int.to.chr$')
def int_to_chr(i, code):
    a1 = code.pop()
    code.push('utils.int_to_chr({})', a1)


@inline_builtin('int.to.str$')
def int_to_str(i, code):
    a1 = code.pop()
    code.push('str({})', a1)


@inline_builtin('missing$')
def missing(i, code):
    a1 = code.pop()
    code.push('1 if i.is_missing_field({}) else 0', a1)


@inline_builtin('newline$')
def newline(i, code):
    code.stmt('i.newline()')


@inline_builtin('num.names$')
def num_names(i, code):
    a1 = code.pop()
    code.push('len(utils.split_name_list({}))', a1)


@inline_builtin('pop$')
def pop(i, code):
    code.pop(discard=True)


@inline_builtin('preamble$')
def preamble(i, code):
    code.push('i.bib_data.get_preamble()')


@inline_builtin('purify$')
def purify(i, code):
    a1 = code.pop()
    code.push('utils.bibtex_purify({})', a1)


@inline_builtin('quote$')
def quote(i, code):
    code.push('{!r}'.format('"'))


@inline_builtin('skip$')
def skip(i, code):
    code.stmt('pass')
    pass


@inline_builtin('substring$')
def substring(i, code):
    stop = code.pop()
    start = code.pop()
    string = code.pop()
    code.push('utils.bibtex_substring({}, {}, {})', string, start, stop)


@builtin('stack$')
def stack(i):
    while i.stack:
        print >>pybtex.io.stdout, i.pop()


@inline_builtin('swap$')
def swap(i, code):
    a1 = code.pop()
    a2 = code.pop()
    code.push_var(a1)
    code.push_var(a2)


@inline_builtin('text.length$')
def text_length(i, code):
    a1 = code.pop()
    code.push('utils.bibtex_len({})', a1)


@inline_builtin('text.prefix$')
def text_prefix(i, code):
    length = code.pop()
    string = code.pop()
    code.push('utils.bibtex_prefix({}, {})', string, length)


@builtin('top$')
def top(i):
    print >>pybtex.io.stdout, i.pop()


@inline_builtin('type$')
def type_(i, code):
    code.push('i.current_entry.type')


@builtin('warning$')
def warning(i):
    msg = i.pop()
    print_warning(msg)


@inline_builtin('while$')
def while_(i, code):
    func = code.pop()
    cond = code.pop()
    code.stmt('while True:')
    with code.nested() as body:
        body.stmt('{}.execute(i)', cond)
        body.stmt('if pop() <= 0: break')
        body.stmt('{}.execute(i)', func)


@inline_builtin('width$')
def width(i, code):
    string = code.pop()
    code.push('utils.bibtex_width({})', string)


@inline_builtin('write$')
def write(i, code):
    string = code.pop()
    code.stmt('i.output({})', string)
