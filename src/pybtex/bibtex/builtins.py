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

"""Built-in functions for BibTeX interpreter.

CAUTION: functions should PUSH results, not RETURN
"""

from __future__ import print_function, unicode_literals

from functools import update_wrapper

import pybtex.io
from pybtex.bibtex import utils
from pybtex.bibtex.exceptions import BibTeXError
from pybtex.bibtex.names import format_name as format_bibtex_name
from pybtex.errors import report_error
from pybtex.utils import memoize


def print_warning(msg):
    report_error(BibTeXError(msg))


class Builtin(object):
    def __init__(self, function):
        self.f = function

    def execute(self, interpreter):
        self.f(interpreter)

    def __repr__(self):
        return "<builtin %s>" % self.f.__name__


builtins = {}


def builtin(name):
    def _builtin(function):
        builtin_obj = Builtin(function)
        update_wrapper(builtin_obj, function)
        builtins[name] = builtin_obj
        return builtin_obj

    return _builtin


@builtin(">")
def operator_more(interpreter):
    arg1 = interpreter.pop()
    arg2 = interpreter.pop()
    if arg2 > arg1:
        interpreter.push(1)
    else:
        interpreter.push(0)


@builtin("<")
def operator_less(interpreter):
    arg1 = interpreter.pop()
    arg2 = interpreter.pop()
    if arg2 < arg1:
        interpreter.push(1)
    else:
        interpreter.push(0)


@builtin("=")
def operator_equals(interpreter):
    arg1 = interpreter.pop()
    arg2 = interpreter.pop()
    if arg2 == arg1:
        interpreter.push(1)
    else:
        interpreter.push(0)


@builtin("*")
def operator_asterisk(interpreter):
    arg1 = interpreter.pop()
    arg2 = interpreter.pop()
    interpreter.push(arg2 + arg1)


@builtin(":=")
def operator_assign(interpreter):
    var = interpreter.pop()
    value = interpreter.pop()
    var.set(value)


@builtin("+")
def operator_plus(interpreter):
    arg1 = interpreter.pop()
    arg2 = interpreter.pop()
    interpreter.push(arg2 + arg1)


@builtin("-")
def operator_minus(interpreter):
    arg1 = interpreter.pop()
    arg2 = interpreter.pop()
    interpreter.push(arg2 - arg1)


@builtin("add.period$")
def add_period(interpreter):
    string = interpreter.pop()
    if string and string.rstrip("}")[-1] not in ".?!":
        string += "."
    interpreter.push(string)


@builtin("call.type$")
def call_type(interpreter):
    entry_type = interpreter.current_entry.type
    try:
        func = interpreter.vars[entry_type]
    except KeyError:
        print_warning(
            'entry type for "{0}" isn\'t style-file defined'.format(
                interpreter.current_entry_key,
            )
        )
        try:
            func = interpreter.vars["default.type"]
        except KeyError:
            return
    func.execute(interpreter)


@builtin("change.case$")
def change_case(interpreter):
    mode = interpreter.pop()
    string = interpreter.pop()

    if not mode:
        raise BibTeXError("empty mode string passed to change.case$")
    mode_letter = mode[0].lower()
    if mode_letter not in ("l", "u", "t"):
        raise BibTeXError("incorrect change.case$ mode: %s" % mode)

    interpreter.push(utils.change_case(string, mode_letter))


@builtin("chr.to.int$")
def chr_to_int(interpreter):
    string = interpreter.pop()
    try:
        value = ord(string)
    except TypeError:
        raise BibTeXError("%s passed to chr.to.int$", string)
    interpreter.push(value)


@builtin("cite$")
def cite(interpreter):
    interpreter.push(interpreter.current_entry_key)


@builtin("duplicate$")
def duplicate(interpreter):
    value = interpreter.pop()
    interpreter.push(value)
    interpreter.push(value)


@builtin("empty$")
def empty(interpreter):
    # FIXME error checking
    string = interpreter.pop()
    if string and not string.isspace():
        interpreter.push(0)
    else:
        interpreter.push(1)


@memoize
def _split_names(names):
    return utils.split_name_list(names)


@memoize
def _format_name(names, name_index, format):
    name = _split_names(names)[name_index - 1]
    return format_bibtex_name(name, format)


@builtin("format.name$")
def format_name(interpreter):
    format = interpreter.pop()
    name_index = interpreter.pop()
    names = interpreter.pop()
    interpreter.push(_format_name(names, name_index, format))


@builtin("if$")
def if_(interpreter):
    else_function = interpreter.pop()
    then_function = interpreter.pop()
    condition = interpreter.pop()
    if condition > 0:
        then_function.execute(interpreter)
    else:
        else_function.execute(interpreter)


@builtin("int.to.chr$")
def int_to_chr(interpreter):
    number = interpreter.pop()
    try:
        char = chr(number)
    except ValueError:
        raise BibTeXError("%i passed to int.to.chr$", number)
    interpreter.push(char)


@builtin("int.to.str$")
def int_to_str(interpreter):
    interpreter.push(str(interpreter.pop()))


@builtin("missing$")
def missing(interpreter):
    field = interpreter.pop()
    if interpreter.is_missing_field(field):
        interpreter.push(1)
    else:
        interpreter.push(0)


@builtin("newline$")
def newline(interpreter):
    interpreter.newline()


@builtin("num.names$")
def num_names(interpreter):
    names = interpreter.pop()
    interpreter.push(len(utils.split_name_list(names)))


@builtin("pop$")
def pop(interpreter):
    interpreter.pop()


@builtin("preamble$")
def preamble(interpreter):
    interpreter.push(interpreter.bib_data.preamble)


@builtin("purify$")
def purify(interpreter):
    string = interpreter.pop()
    interpreter.push(utils.bibtex_purify(string))


@builtin("quote$")
def quote(interpreter):
    interpreter.push('"')


@builtin("skip$")
def skip(interpreter):
    pass


@builtin("substring$")
def substring(interpreter):
    length = interpreter.pop()
    start = interpreter.pop()
    string = interpreter.pop()
    interpreter.push(utils.bibtex_substring(string, start, length))


@builtin("stack$")
def stack(interpreter):
    while interpreter.stack:
        print(interpreter.pop(), file=pybtex.io.stdout)


@builtin("swap$")
def swap(interpreter):
    tmp1 = interpreter.pop()
    tmp2 = interpreter.pop()
    interpreter.push(tmp1)
    interpreter.push(tmp2)


@builtin("text.length$")
def text_length(interpreter):
    string = interpreter.pop()
    interpreter.push(utils.bibtex_len(string))


@builtin("text.prefix$")
def text_prefix(interpreter):
    length = interpreter.pop()
    string = interpreter.pop()
    interpreter.push(utils.bibtex_prefix(string, length))


@builtin("top$")
def top(interpreter):
    print(interpreter.pop(), file=pybtex.io.stdout)


@builtin("type$")
def type_(interpreter):
    interpreter.push(interpreter.current_entry.type)


@builtin("warning$")
def warning(interpreter):
    msg = interpreter.pop()
    print_warning(msg)


@builtin("while$")
def while_(interpreter):
    body_function = interpreter.pop()
    condition_function = interpreter.pop()
    while True:
        condition_function.execute(interpreter)
        if interpreter.pop() <= 0:
            break
        body_function.execute(interpreter)


@builtin("width$")
def width(interpreter):
    string = interpreter.pop()
    interpreter.push(utils.bibtex_width(string))


@builtin("write$")
def write(interpreter):
    string = interpreter.pop()
    interpreter.output(string)
