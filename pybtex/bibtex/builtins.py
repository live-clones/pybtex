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


from pybtex.utils import memoize
from pybtex.bibtex import utils
from pybtex.bibtex.names import format_name as format_bibtex_name

from .codegen import PythonFunction

builtins = {}


def builtin(cls):
    builtins[cls.name] = cls
    return cls


class Builtin(object):
    def execute(self, interpreter):
        self.f(interpreter)

    def f(self, interpreter):
        function = PythonFunction('_builtin_', hint=self.name, args=['i'])
        self.write_code(interpreter, function)
        context = interpreter.exec_code(function)
        self.f = context[function.name]
        self.f(interpreter)


@builtin
class OperatorMore(Builtin):
    name = '>'

    def write_code(self, i, code):
        a2 = code.pop()
        a1 = code.pop()
        code.push('1 if {} > {} else 0', (a1, a2))


@builtin
class OperatorLess(Builtin):
    name = '<'

    def write_code(self, i, code):
        a2 = code.pop()
        a1 = code.pop()
        code.push('1 if {} < {} else 0', (a1, a2))


@builtin
class OperatorEquals(Builtin):
    name = '='

    def write_code(self, i, code):
        a2 = code.pop()
        a1 = code.pop()
        code.push('1 if {} == {} else 0', (a1, a2))


@builtin
class OperatorAsterisk(Builtin):
    name = '*'

    def write_code(self, i, code):
        a2 = code.pop()
        a1 = code.pop()
        code.push('{} + {}', (a1, a2))


@builtin
class OperatorAssign(Builtin):
    name = ':='

    def write_code(self, i, code):
        var = code.pop()
        val = code.pop()
        code.stmt('{}.set({})', (var, val))


@builtin
class OperatorPlus(Builtin):
    name = '+'

    def write_code(self, i, code):
        a2 = code.pop()
        a1 = code.pop()
        code.push('{} + {}', (a1, a2))


@builtin
class OperatorMinus(Builtin):
    name = '-'

    def write_code(self, i, code):
        a2 = code.pop()
        a1 = code.pop()
        code.push('{} - {}', (a1, a2))


@builtin
class AddPeriod(Builtin):
    name = 'add.period$'

    def write_code(self, i, code):
        text = code.pop()
        code.push('utils.bibtex_add_period({})', (text,))


@builtin
class CallType(Builtin):
    name = 'call.type$'

    def write_code(self, i, code):
        code.stmt('i.call_type()')


@builtin
class ChangeCase(Builtin):
    name = 'change.case$'

    def write_code(self, i, code):
        a2 = code.pop()
        a1 = code.pop()
        code.push('utils.change_case({}, {})', (a1, a2))


@builtin
class ChrToInt(Builtin):
    name = 'chr.to.int$'

    def write_code(self, i, code):
        a1 = code.pop()
        code.push('utils.chr_to_int({})', (a1,))


@builtin
class Cite(Builtin):
    name = 'cite$'

    def write_code(self, i, code):
        code.push('i.current_entry_key')


@builtin
class Duplicate(Builtin):
    name = 'duplicate$'

    def write_code(self, i, code):
        a1 = code.pop()
        code.push_var(a1)
        code.push_var(a1)


@builtin
class Empty(Builtin):
    name = 'empty$'

    def write_code(self, i, code):
        a1 = code.pop()
        code.push('0 if {0} and not {0}.isspace() else 1', (a1,))


@memoize
def _split_names(names):
    return utils.split_name_list(names)


@memoize
def _format_name(names, n, format):
    name = _split_names(names)[n - 1]
    return format_bibtex_name(name, format)


@builtin
class ChangeCase(Builtin):
    name = 'format.name$'

    def write_code(self, i, code):
        format = code.pop()
        n = code.pop()
        names = code.pop()
        code.push('_format_name({}, {}, {})', (names, n, format))


def _execute(var, i, code, target_code):
    try:
        obj = code.var_src[var]
    except KeyError:
        target_code.stmt('{}.execute(i)', (var,))
    else:
        obj.write_code(i, target_code)


@builtin
class If(Builtin):
    name = 'if$'

    def write_code(self, i, code):
        a2 = code.pop()
        a1 = code.pop()
        cond = code.pop()
        code.stmt('if {0}:', (cond,), stack_safe=False)
        with code.nested() as block:
            _execute(a1, i, code, block)
        code.stmt('else:')
        with code.nested() as block:
            _execute(a2, i, code, block)


@builtin
class IntToChr(Builtin):
    name = 'int.to.chr$'

    def write_code(self, i, code):
        a1 = code.pop()
        code.push('utils.int_to_chr({})', (a1,))


@builtin
class IntToStr(Builtin):
    name = 'int.to.str$'

    def write_code(self, i, code):
        a1 = code.pop()
        code.push('str({})', (a1,))


@builtin
class Missing(Builtin):
    name = 'missing$'

    def write_code(self, i, code):
        a1 = code.pop()
        code.push('1 if i.is_missing_field({}) else 0', (a1,))


@builtin
class Newline(Builtin):
    name = 'newline$'

    def write_code(self, i, code):
        code.stmt('i.newline()')


@builtin
class NumNames(Builtin):
    name = 'num.names$'

    def write_code(self, i, code):
        a1 = code.pop()
        code.push('len(utils.split_name_list({}))', (a1,))


@builtin
class Pop(Builtin):
    name = 'pop$'

    def write_code(self, i, code):
        code.pop(discard=True)


@builtin
class Preamble(Builtin):
    name = 'preamble$'

    def write_code(self, i, code):
        code.push('i.bib_data.get_preamble()')


@builtin
class Purify(Builtin):
    name = 'purify$'

    def write_code(self, i, code):
        a1 = code.pop()
        code.push('utils.bibtex_purify({})', (a1,))


@builtin
class Quote(Builtin):
    name = 'quote$'

    def write_code(self, i, code):
        code.push('{!r}'.format('"'))


@builtin
class Skip(Builtin):
    name = 'skip$'

    def write_code(self, i, code):
        code.stmt('pass')


@builtin
class Substring(Builtin):
    name = 'substring$'

    def write_code(self, i, code):
        stop = code.pop()
        start = code.pop()
        string = code.pop()
        code.push('utils.bibtex_substring({}, {}, {})', (string, start, stop))


@builtin
class Stack(Builtin):
    name = 'stack$'

    def write_code(self, i, code):
        code.stmt('i.print_stack()')


@builtin
class Swap(Builtin):
    name = 'swap$'

    def write_code(self, i, code):
        a1 = code.pop()
        a2 = code.pop()
        code.push_var(a1)
        code.push_var(a2)


@builtin
class TextLength(Builtin):
    name = 'text.length$'

    def write_code(self, i, code):
        a1 = code.pop()
        code.push('utils.bibtex_len({})', (a1,))


@builtin
class TextPrefix(Builtin):
    name = 'text.prefix$'

    def write_code(self, i, code):
        length = code.pop()
        string = code.pop()
        code.push('utils.bibtex_prefix({}, {})', (string, length))


@builtin
class Top(Builtin):
    name = 'top$'

    def write_code(self, i, code):
        top = code.pop()
        code.stmt('utils.print_message({})', (top,))


@builtin
class Type(Builtin):
    name = 'type$'

    def write_code(self, i, code):
        code.push('i.current_entry.type')


@builtin
class Warning(Builtin):
    name = 'warning$'

    def write_code(self, i, code):
        top = code.pop()
        code.stmt('utils.print_warning({})', (top,))


@builtin
class While(Builtin):
    name = 'while$'

    def write_code(self, i, code):
        func = code.pop()
        cond = code.pop()
        code.stmt('while True:', stack_safe=False)
        with code.nested() as body:
            _execute(cond, i, code, body)
            body.stmt('if pop() <= 0: break', stack_safe=False)
            _execute(func, i, code, body)


@builtin
class Width(Builtin):
    name = 'width$'

    def write_code(self, i, code):
        string = code.pop()
        code.push('utils.bibtex_width({})', (string,))


@builtin
class Write(Builtin):
    name = 'write$'

    def write_code(self, i, code):
        string = code.pop()
        code.stmt('i.output({})', (string,))
