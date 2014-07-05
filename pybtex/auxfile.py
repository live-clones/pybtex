# Copyright (c) 2006, 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
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

"""parse LaTeX aux file
"""

from __future__ import with_statement

import re

import pybtex.io
from pybtex.exceptions import PybtexError
from pybtex.errors import report_error


class AuxDataError(PybtexError):
    def __init__(self, message, context):
        super(AuxDataError, self).__init__(message, context.filename)
        self.context = context
    
    def get_context(self):
        marker = '^' * len(self.context.line)
        return self.context.line + '\n' + marker

    def __unicode__(self):
        base_message = super(AuxDataError, self).__unicode__()
        return u'in line {lineno}: {message}'.format(
            message=base_message,
            lineno=self.context.lineno,
        )


class AuxDataContext(object):
    lineno = None
    line = None
    filename = None

    def __init__(self, filename):
        self.filename = filename


class AuxData(object):
    command_re = re.compile(r'\\(citation|bibdata|bibstyle|@input){(.*)}')
    context = None
    style = None
    data = None
    citations = None

    def __init__(self, encoding):
        self.encoding = encoding
        self.citations = []
        self._canonical_keys = {}

    def handle_citation(self, keys):
        for key in keys.split(','):
            key_lower = key.lower()
            if key_lower in self._canonical_keys:
                existing_key = self._canonical_keys[key_lower]
                if key != existing_key:
                    msg = 'case mismatch error between cite keys {0} and {1}'
                    report_error(AuxDataError(msg.format(key, existing_key), self.context))
            self.citations.append(key)
            self._canonical_keys[key_lower] = key

    def handle_bibstyle(self, style):
        if self.style is not None:
            report_error(AuxDataError(r'illegal, another \bibstyle command', self.context))
        else:
            self.style = style

    def handle_bibdata(self, bibdata):
        if self.data is not None:
            report_error(AuxDataError(r'illegal, another \bibdata command', self.context))
        else:
            self.data = bibdata.split(',')

    def handle_input(self, filename):
        self.parse_file(filename)

    def handle(self, command, value):
        action = getattr(self, 'handle_%s' % command.lstrip('@'))
        action(value)

    def parse_file(self, filename):
        previous_context = self.context
        self.context = AuxDataContext(filename)

        with pybtex.io.open_unicode(filename, encoding=self.encoding) as aux_file:
            for lineno, line in enumerate(aux_file):
                self.context.lineno = lineno + 1
                self.context.line = line.strip()
                match = self.command_re.match(line)
                if match:
                    command, value = match.groups()
                    self.handle(command, value)
        self.context = previous_context


def parse_file(filename, encoding):
    """Parse a file and return an AuxData object."""

    data = AuxData(encoding)
    data.parse_file(filename)
    if data.data is None:
        raise AuxDataError(r'found no \bibdata command in %s' % filename)
    if data.style is None:
        raise AuxDataError(r'found no \bibstyle command in %s' % filename)
    return data
