# Copyright (c) 2015  Andrey Golovizin
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


"""Python code generator."""


import re

from io import StringIO


class Statement(object):
    def __init__(self, python, vars):
        self.python = python
        self.vars = vars

    def write(self, stream, level):
        code = self.python.format(*self.vars) if self.vars else self.python
        self.writeline(stream, level, code)

    def writeline(self, stream, level, line):
        stream.write(u' ' * (4 * level) + line + '\n')


class PushStatement(Statement):
    def __init__(self, var):
        self.var = var

    def write(self, stream, level):
        line = 'push({})'.format(self.var)
        self.writeline(stream, level, line)


class PopStatement(Statement):
    def __init__(self, var=None):
        self.var = var

    def write(self, stream, level):
        if self.var:
            line = '{} = pop()'.format(self.var)
        else:
            line = 'pop()'
        self.writeline(stream, level, line)


class PythonCode(Statement):
    def __init__(self):
        self.statements = []
        self.var_count = 0

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def new_var(self):
        var = 'a{}'.format(self.var_count)
        self.var_count += 1
        return var

    def stmt(self, python, *vars):
        self.statements.append(Statement(python, vars))

    def push(self, expr, *vars):
        var = self.new_var()
        self.stmt('{} = {}'.format(var, expr), *vars)
        self.push_var(var)

    def push_var(self, var):
        self.statements.append(PushStatement(var))

    def pop(self, discard=False):
        var = None if discard else self.new_var()
        if self.statements:
            last = self.statements[-1]
            if isinstance(last, PushStatement):
                self.statements.pop()
                if var and var != last.var:
                    self.stmt('{} = {}'.format(var, last.var))
                return var
        self.statements.append(PopStatement(var))
        return var

    def nested(self):
        block = PythonCode()
        self.statements.append(block)
        return block

    def function(self, name='_tmp_', hint=None, args=()):
        function = PythonFunction(self.new_var(), hint=hint, args=args)
        self.statements.append(function)
        return function

    def write(self, stream, level):
        for statement in self.statements:
            statement.write(stream, level + 1)

    def getvalue(self):
        stream = StringIO()
        self.write(stream, level=0)
        return stream.getvalue()

    def compile(self):
        python_code = self.getvalue()
        return compile(python_code, '<BST>', 'exec')


class PythonFunction(PythonCode):
    CRUFT = re.compile('[^A-Za-z0-9]')

    def __init__(self, name, hint=None, args=()):
        self.name = name
        if hint:
            self.name += '_' + self.escape(hint)
        self.args = args
        super(PythonFunction, self).__init__()

    def escape(self, hint):
        return '_'.join(part for part in self.CRUFT.split(hint) if part)

    def write(self, stream, level):
        decl = 'def {}({}):'.format(self.name, ', '.join(self.args))
        self.writeline(stream, level, decl)
        super(PythonFunction, self).write(stream, level)
