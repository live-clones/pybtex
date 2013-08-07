#!/usr/bin/env python

# Copyright (c) 2013  Andrey Golovizin
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


from pybtex.cmdline import CommandLine, make_option

class PybtexFormatCommandLine(CommandLine):
    prog = 'pybtex-format'
    args = '[options] in_filename out_filename'
    description = 'convert between bibliography database formats'
    long_description = """

pybtex-format formats bibliography database as human-readable text.
    """.strip()
    num_args = 2

    options = (
        (None, (
            make_option(
                '-f', '--from', dest='from_format',
                help='input format (%plugin_choices)', metavar='FORMAT',
                type='load_plugin', plugin_group='pybtex.database.input',
            ),
            make_option(
                '-b', '--output-backend', dest='output_backend',
                help='output backend (%plugin_choices)',
                type='load_plugin',
                plugin_group='pybtex.backends',
                metavar='BACKEND',
            ),
            make_option(
                '--min-crossrefs',
                type='int', dest='min_crossrefs',
                help='include item after NUMBER crossrefs; default 2',
                metavar='NUMBER',
            ),
            make_option(
                '--keyless-bibtex-entries',
                action='store_true', dest='keyless_entries',
                help='allow BibTeX entries without keys and generate unnamed-<number> keys for them'
            ),
        )),
        ('encoding options', (
            make_option(
                '-e', '--encoding',
                action='store', type='string', dest='encoding',
                help='default encoding',
                metavar='ENCODING',
            ),
            make_option(
                '--input-encoding',
                action='store', type='string', dest='input_encoding',
                metavar='ENCODING',
            ),
            make_option(
                '--output-encoding',
                action='store', type='string', dest='output_encoding',
                metavar='ENCODING',
            ),
        )),
    )
    option_defaults = {
        'keyless_entries': False,
    }

    def run(self, options, args):
        from pybtex.database.format import format_database

        format_database(args[0], args[1],
                options.from_format,
                options.output_backend,
                input_encoding=options.input_encoding or options.encoding,
                output_encoding=options.output_encoding or options.encoding,
                parser_options = {'keyless_entries': options.keyless_entries},
                min_crossrefs=options.min_crossrefs
        )


main = PybtexFormatCommandLine()


if __name__ == '__main__':
    main()
