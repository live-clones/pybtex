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


from io import StringIO


class Line(object):
    def __init__(self, python):
        self.python = python

    def write(self, stream, level):
        stream.write(u' ' * (4 * level) + self.python + '\n')


class PushStatement(Line):
    def __init__(self, expr):
        self.expr = expr

    def write(self, stream, level):
        line = 'push({})'.format(self.expr)
        stream.write(u' ' * (4 * level) + line + '\n')


class PopStatement(Line):
    def __init__(self, expr):
        self.expr = expr

    def write(self, stream, level):
        line = '{} = pop()'.format(self.expr)
        stream.write(u' ' * (4 * level) + line + '\n')


class PythonCode(object):
    def __init__(self, level=0):
        self.statements = []
        self.level = level

    def line(self, python):
        self.statements.append(Line(python))

    def push(self, expr):
        self.statements.append(PushStatement(expr))

    def pop(self, expr):
        self.statements.append(PopStatement(expr))

    def nested(self):
        block = PythonCode(self.level + 1)
        self.statements.append(block)
        return block

    def function(self, name='_tmp_'):
        self.write('def {}:' + name)
        return nested()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def write(self, stream, level=0):
        for statement in self.statements:
            statement.write(stream, self.level + level)

    def getvalue(self):
        stream = StringIO()
        self.write(stream)
        return stream.getvalue()

    def compile(self):
        return compile(self.getvalue(), '<BST>', 'exec')
