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

"""bibliography processor
"""

from __future__ import absolute_import
from os import path


class Engine(object):
    @classmethod
    def make_bibliography(cls, aux_filename, style=None, output_encoding=None, bib_format=None, **kwargs):
        from pybtex import auxfile
        if bib_format is None:
            from pybtex.database.input.bibtex import Parser as bib_format

        aux_data = auxfile.parse_file(aux_filename, output_encoding)
        if style is None:
            style = aux_data.style
        base_filename = path.splitext(aux_filename)[0]
        bib_filenames = [filename + bib_format.default_suffix for filename in aux_data.data]
        return cls.format_from_files(
            bib_filenames,
            style=aux_data.style,
            citations=aux_data.citations,
            output_encoding=output_encoding,
            output_filename=base_filename,
            add_output_suffix=True,
        )

    @classmethod
    def format_from_string(cls, bib_string, *args, **kwargs):
        return cls.format_from_strings([bib_string], *args, **kwargs)

    @classmethod
    def format_from_strings(cls, bib_strings, *args, **kwargs):
        from io import StringIO
        inputs = [StringIO(bib_string) for bib_string in bib_strings]
        return cls.format_from_files(inputs, *args, **kwargs)

    @classmethod
    def format_from_file(cls, filename, *args, **kwargs):
        return cls.format_from_files([filename], *args, **kwargs)

    @classmethod
    def format_from_files(*args, **kwargs):
        raise NotImplementedError


class PybtexEngine(Engine):
    @classmethod
    def format_from_files(
        cls,
        bib_files_or_filenames,
        style,
        citations=['*'],
        bib_format=None,
        bib_encoding=None,
        output_backend=None,
        output_encoding=None,
        min_crossrefs=2,
        output_filename=None,
        add_output_suffix=False,
        **kwargs
    ):
        from pybtex.plugin import find_plugin

        bib_parser = find_plugin('pybtex.database.input', bib_format)
        bib_data = bib_parser(
            encoding=bib_encoding,
            wanted_entries=citations,
            min_crossrefs=min_crossrefs,
        ).parse_files(bib_files_or_filenames)

        style_cls = find_plugin('pybtex.style.formatting', style)
        style = style_cls(
                label_style=kwargs.get('label_style'),
                name_style=kwargs.get('name_style'),
                sorting_style=kwargs.get('sorting_style'),
                abbreviate_names=kwargs.get('abbreviate_names'),
                min_crossrefs=min_crossrefs,
        )
        formatted_bibliography = style.format_bibliography(bib_data, citations)

        output_backend = find_plugin('pybtex.backends', output_backend)
        if add_output_suffix:
            output_filename = output_filename + output_backend.default_suffix
        if not output_filename:
            import io
            output_filename = io.StringIO()
        return output_backend(output_encoding).write_to_file(formatted_bibliography, output_filename)


def make_bibliography(*args, **kwargs):
    return PybtexEngine().make_bibliography(*args, **kwargs)


def format_from_file(*args, **kwargs):
    return PybtexEngine().format_from_file(*args, **kwargs)


def format_from_files(*args, **kwargs):
    return PybtexEngine().format_from_files(*args, **kwargs)


def format_from_string(*args, **kwargs):
    return PybtexEngine().format_from_string(*args, **kwargs)


def format_from_strings(*args, **kwargs):
    return PybtexEngine().format_from_strings(*args, **kwargs)
