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


class PythonCode(object):
    def __init__(self):
        self.stream = StringIO()
        self.indentation = 0

    def write(self, line):
        self.stream.write(u' ' * self.indentation + line + '\n')

    def indent(self):
        self.indentation += 4
        return self

    def function(self, name='_tmp_'):
        self.write('def {}:' + name)
        return self.indent()

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self.indentation -= 4

    def compile(self):
        return compile(self.stream.getvalue(), '<BST>', 'exec')
