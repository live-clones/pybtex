#!/usr/bin/env python

from pathlib import Path

from pybtex_doctools.man import generate_manpages

if __name__ == "__main__":
    generate_manpages(Path(__file__).parent)
