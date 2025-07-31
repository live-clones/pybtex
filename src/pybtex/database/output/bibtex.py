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


import codecs

from pybtex.bibtex.exceptions import BibTeXError
from pybtex.bibtex.utils import scan_bibtex_string
from pybtex.database.output import BaseWriter


class Writer(BaseWriter):
    """Outputs BibTeX markup"""

    unicode_io = True

    def quote(self, s):
        r"""
        >>> w = Writer()
        >>> print(w.quote("The World"))
        "The World"
        >>> print(w.quote(r"The \emph{World}"))
        "The \emph{World}"
        >>> print(w.quote(r'The "World"'))
        {The "World"}
        >>> try:
        ...     print(w.quote(r"The {World"))
        ... except BibTeXError as error:
        ...     print(error)
        String has unmatched braces: The {World
        """

        self.check_braces(s)
        if '"' not in s:
            return f'"{s}"'
        return f"{{{s}}}"

    def check_braces(self, s):
        """
        Raise an exception if the given string has unmatched braces.

        >>> w = Writer()
        >>> w.check_braces("Cat eats carrots.")
        >>> w.check_braces("Cat eats {carrots}.")
        >>> w.check_braces("Cat eats {carrots{}}.")
        >>> w.check_braces("")
        >>> w.check_braces("end}")
        >>> try:
        ...     w.check_braces("{")
        ... except BibTeXError as error:
        ...     print(error)
        String has unmatched braces: {
        >>> w.check_braces("{test}}")
        >>> try:
        ...     w.check_braces("{{test}")
        ... except BibTeXError as error:
        ...     print(error)
        String has unmatched braces: {{test}

        """

        tokens = list(scan_bibtex_string(s))
        if tokens:
            end_brace_level = tokens[-1][1]
            if end_brace_level != 0:
                msg = f"String has unmatched braces: {s}"
                raise BibTeXError(msg)

    def _encode(self, text):
        r"""Encode text as LaTeX.

        >>> w = Writer(encoding="ASCII")
        >>> print(w._encode("1970–1971."))
        1970--1971.

        >>> w = Writer(encoding="UTF-8")
        >>> print(w._encode("1970–1971."))
        1970–1971.

        >>> w = Writer(encoding="UTF-8")
        >>> print(w._encode("100% noir"))
        100\% noir
        """  # noqa: RUF002

        return codecs.encode(text, f"ulatex+{self.encoding}")

    def _encode_with_comments(self, text):
        r"""Encode text as LaTeX, preserve comments.

        >>> w = Writer(encoding="ASCII")
        >>> print(w._encode_with_comments("1970–1971.  %% † RIP †"))
        1970--1971.  %% \dag\ RIP \dag

        >>> w = Writer(encoding="UTF-8")
        >>> print(w._encode_with_comments("1970–1971.  %% † RIP †"))
        1970–1971.  %% † RIP †
        """  # noqa: RUF002
        return "%".join(self._encode(part) for part in text.split("%"))

    def _write_field(self, stream, type, value):
        stream.write(f",\n    {type} = {self.quote(self._encode(value))}")

    def _format_name(self, stream, person):
        def join(names):
            return " ".join([name for name in names if name])

        first = person.get_part_as_text("first")
        middle = person.get_part_as_text("middle")
        prelast = person.get_part_as_text("prelast")
        last = person.get_part_as_text("last")
        lineage = person.get_part_as_text("lineage")
        s = ""
        if last:
            s += join([prelast, last])
        if lineage:
            s += f", {lineage}"
        if first or middle:
            s += ", "
            s += join([first, middle])
        return s

    def _write_persons(self, stream, persons, role):
        # persons = getattr(entry, role + 's')
        if persons:
            names = " and ".join(
                self._format_name(stream, person) for person in persons
            )
            self._write_field(stream, role, names)

    def _write_preamble(self, stream, preamble):
        if preamble:
            stream.write(
                f"@preamble{{{self.quote(self._encode_with_comments(preamble))}}}\n\n"
            )

    def write_stream(self, bib_data, stream):
        self._write_preamble(stream, bib_data.preamble)

        first = True
        for key, entry in bib_data.entries.items():
            if not first:
                stream.write("\n")
            first = False

            stream.write(f"@{entry.original_type}")
            stream.write(f"{{{key}")
            #            for role in ('author', 'editor'):
            for role, persons in entry.persons.items():
                self._write_persons(stream, persons, role)
            for type, value in entry.fields.items():
                self._write_field(stream, type, value)
            stream.write("\n}\n")
