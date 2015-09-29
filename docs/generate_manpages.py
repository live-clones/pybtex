#!/usr/bin/env python

from os import path

from pybtex_doctools.man import generate_manpages

if __name__ == '__main__':
    generate_manpages(path.dirname(__file__))
