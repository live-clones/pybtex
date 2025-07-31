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


import re
import sys
from pathlib import Path
from shutil import rmtree
from subprocess import PIPE, Popen
from tempfile import mkdtemp

from pybtex.database import BibliographyData, Entry, Person
from pybtex.database.output import bibtex
from pybtex.errors import report_error
from pybtex.exceptions import PybtexError

writer = bibtex.Writer(encoding="ascii")


def write_aux(filename, citations):
    with Path(filename).open("w") as aux_file:
        aux_file.writelines(f"\\citation{{{citation}}}\n" for citation in citations)
        aux_file.write("\\bibdata{test}\n")
        aux_file.write("\\bibstyle{test}\n")


def write_bib(filename, database):
    writer.write_file(database, filename)


def write_bst(filename, style):
    with Path(filename).open("w") as bst_file:
        bst_file.write(style)
        bst_file.write("\n")


def run_bibtex(style, database, citations=None):
    if citations is None:
        citations = list(database.entries.keys())
    tmpdir = mkdtemp(prefix="pybtex_test_")
    try:
        tmpdir_path = Path(tmpdir)
        write_bib(tmpdir_path / "test.bib", database)
        write_aux(tmpdir_path / "test.aux", citations)
        write_bst(tmpdir_path / "test.bst", style)
        bibtex = Popen(("bibtex", "test"), cwd=tmpdir, stdout=PIPE, stderr=PIPE)
        stdout, stderr = bibtex.communicate()
        if bibtex.returncode:
            report_error(PybtexError(stdout))
        with (Path(tmpdir) / "test.bbl").open() as bbl_file:
            return bbl_file.read()
    finally:
        rmtree(tmpdir)


def execute(code, database=None):
    if database is None:
        database = BibliographyData(entries={"test_entry": Entry("article")})
    bst = (
        """
        ENTRY {name format} {} {}
        FUNCTION {article}
        {
            %s write$ newline$
        }
        READ
        ITERATE {call.type$}
    """.strip()
        % code
    )
    return " ".join(run_bibtex(bst, database).splitlines())


def format_name(name, format):
    return execute(f'"{name}" #1 "{format}" format.name$')


def parse_name(name):
    space = re.compile(r"[\s~]+")
    formatted_name = format_name(name, "{ff}|{vv}|{ll}|{jj}")
    parts = [space.sub(" ", part.strip()) for part in formatted_name.split("|")]
    first, von, last, junior = parts
    return Person(first=first, prelast=von, last=last, lineage=junior)


def main():
    args = sys.argv[1:2]
    if len(args) != 1:
        print("usage: run_bibtex 'some bibtex code'")
        sys.exit(1)
    code = args[0]
    print(execute(code))


if __name__ == "__main__":
    main()
