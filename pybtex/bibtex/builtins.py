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


from pybtex.bibtex.exceptions import BibTeXError
from pybtex.utils import memoize
from pybtex.bibtex import utils
from pybtex.bibtex.names import format_name as format_bibtex_name


inline_builtins = {}


def inline_builtin(name):
    def _builtin(f):
        inline_builtins[name] = f
        return f
    return _builtin


@inline_builtin('>')
def operator_more(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('1 if {} > {} else 0', (a1, a2))


@inline_builtin('<')
def operator_less(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('1 if {} < {} else 0', (a1, a2))


@inline_builtin('=')
def operator_equals(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('1 if {} == {} else 0', (a1, a2))


@inline_builtin('*')
def operator_asterisk(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('{} + {}', (a1, a2))


@inline_builtin(':=')
def operator_assign(i, code):
    var = code.pop()
    val = code.pop()
    code.stmt('{}.set({})', (var, val))


@inline_builtin('+')
def operator_plus(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('{} + {}', (a1, a2))


@inline_builtin('-')
def operator_minus(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('{} - {}', (a1, a2))


@inline_builtin('add.period$')
def add_period(i, code):
    text = code.pop()
    code.push('utils.bibtex_add_period({})', (text,))


@inline_builtin('call.type$')
def call_type(i, code):
    code.stmt('i.call_type()')


@inline_builtin('change.case$')
def change_case(i, code):
    a2 = code.pop()
    a1 = code.pop()
    code.push('utils.change_case({}, {})', (a1, a2))


@inline_builtin('chr.to.int$')
def chr_to_int(i, code):
    a1 = code.pop()
    code.push('utils.chr_to_int({})', (a1,))


@inline_builtin('cite$')
def cite(i, code):
    code.push('i.current_entry_key')


@inline_builtin('duplicate$')
def duplicate(i, code):
    a1 = code.pop()
    code.push_var(a1)
    code.push_var(a1)


@inline_builtin('empty$')
def empty(i, code):
    a1 = code.pop()
    code.push('0 if {0} and not {0}.isspace() else 1', (a1,))


@memoize
def _split_names(names):
    return utils.split_name_list(names)


@memoize
def _format_name(names, n, format):
    name = _split_names(names)[n - 1]
    return format_bibtex_name(name, format)


@inline_builtin('format.name$')
def format_name(i, code):
    format = code.pop()
    n = code.pop()
    names = code.pop()
    code.push('_format_name({}, {}, {})', (names, n, format))


@inline_builtin('if$')
def if_(i, code):
    a2 = code.pop()
    a1 = code.pop()
    cond = code.pop()
    code.stmt('({1} if {0} > 0 else {2}).execute(i)', (cond, a1, a2), stack_safe=False)


@inline_builtin('int.to.chr$')
def int_to_chr(i, code):
    a1 = code.pop()
    code.push('utils.int_to_chr({})', (a1,))


@inline_builtin('int.to.str$')
def int_to_str(i, code):
    a1 = code.pop()
    code.push('str({})', (a1,))


@inline_builtin('missing$')
def missing(i, code):
    a1 = code.pop()
    code.push('1 if i.is_missing_field({}) else 0', (a1,))


@inline_builtin('newline$')
def newline(i, code):
    code.stmt('i.newline()')


@inline_builtin('num.names$')
def num_names(i, code):
    a1 = code.pop()
    code.push('len(utils.split_name_list({}))', (a1,))


@inline_builtin('pop$')
def pop(i, code):
    code.pop(discard=True)


@inline_builtin('preamble$')
def preamble(i, code):
    code.push('i.bib_data.get_preamble()')


@inline_builtin('purify$')
def purify(i, code):
    a1 = code.pop()
    code.push('utils.bibtex_purify({})', (a1,))


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
    code.push('utils.bibtex_substring({}, {}, {})', (string, start, stop))


@inline_builtin('stack$')
def stack(i, code):
    code.stmt('i.print_stack()')


@inline_builtin('swap$')
def swap(i, code):
    a1 = code.pop()
    a2 = code.pop()
    code.push_var(a1)
    code.push_var(a2)


@inline_builtin('text.length$')
def text_length(i, code):
    a1 = code.pop()
    code.push('utils.bibtex_len({})', (a1,))


@inline_builtin('text.prefix$')
def text_prefix(i, code):
    length = code.pop()
    string = code.pop()
    code.push('utils.bibtex_prefix({}, {})', (string, length))


@inline_builtin('top$')
def top(i, code):
    top = code.pop()
    code.stmt('utils.print_message({})', (top,))


@inline_builtin('type$')
def type_(i, code):
    code.push('i.current_entry.type')


@inline_builtin('warning$')
def warning(i, code):
    top = code.pop()
    code.stmt('utils.print_warning({})', (top,))


@inline_builtin('while$')
def while_(i, code):
    func = code.pop()
    cond = code.pop()
    code.stmt('while True:', stack_safe=False)
    with code.nested() as body:
        body.stmt('{}.execute(i)', (cond,), stack_safe=False)
        body.stmt('if pop() <= 0: break', stack_safe=False)
        body.stmt('{}.execute(i)', (func,), stack_safe=False)


@inline_builtin('width$')
def width(i, code):
    string = code.pop()
    code.push('utils.bibtex_width({})', (string,))


@inline_builtin('write$')
def write(i, code):
    string = code.pop()
    code.stmt('i.output({})', (string,))
