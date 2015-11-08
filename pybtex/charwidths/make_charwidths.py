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


"""
Make a table of character widths to use with bibtex width$ function.
"""


def make_table(font_filename, output):
    import sys
    from datetime import datetime
    from freetype import Face
    from pprint import pformat

    font_face = Face(font_filename)
    date = datetime.now().strftime('%Y-%m-%d')
    cmd = ' '.join(sys.argv)
    charwidths = extract_widths(font_face)

    print >>output, '# vim:fileencoding=utf8'
    print >>output

    print >>output, '# GENERATED FILE - DO NOT EDIT.'
    print >>output, '# Generated by {0}'.format(cmd)
    print >>output, '# Date: {0}'.format(date)
    print >>output, '# Font family: {0}'.format(font_face.family_name)
    print >>output, '# Font style: {0}'.format(font_face.style_name)
    print >>output, '# Font version: {0}'.format(get_font_version(font_face))
    print >>output
    print >>output, 'charwidths = {0}'.format(pformat(charwidths).encode('UTF-8'))


def get_font_version(font_face):
    from freetype import TT_NAME_ID_VERSION_STRING
    for i in range(font_face.sfnt_name_count):
        name = font_face.get_sfnt_name(i)
        if name.name_id == TT_NAME_ID_VERSION_STRING:
            return name.string
    return 'unknown'


def extract_widths(font_face):
    widths =  dict(iter_charwidths(font_face))
    widths.update(bibtex_widths)
    return widths


def iter_charwidths(font_face):
    from freetype import FT_LOAD_NO_SCALE

    font_face.set_char_size(10*64)
    charcode, gindex = font_face.get_first_char()
    while gindex:
        font_face.load_glyph(gindex, FT_LOAD_NO_SCALE)
        yield unichr(charcode), font_face.glyph.metrics.horiAdvance
        charcode, gindex = font_face.get_next_char(charcode, gindex)
        

bibtex_widths = {
    ' ': 278,
    '!': 278,
    '"': 500,
    '#': 833,
    '$': 500,
    '%': 833,
    '&': 778,
    "'": 278,
    '(': 389,
    ')': 389,
    '*': 500,
    '+': 778,
    ',': 278,
    '-': 333,
    '.': 278,
    '/': 500,
    '0': 500,
    '1': 500,
    '2': 500,
    '3': 500,
    '4': 500,
    '5': 500,
    '6': 500,
    '7': 500,
    '8': 500,
    '9': 500,
    ':': 278,
    ';': 278,
    '<': 278,
    '=': 778,
    '>': 472,
    '?': 472,
    '@': 778,
    'A': 750,
    'B': 708,
    'C': 722,
    'D': 764,
    'E': 681,
    'F': 653,
    'G': 785,
    'H': 750,
    'I': 361,
    'J': 514,
    'K': 778,
    'L': 625,
    'M': 917,
    'N': 750,
    'O': 778,
    'P': 681,
    'Q': 778,
    'R': 736,
    'S': 556,
    'T': 722,
    'U': 750,
    'V': 750,
    'W': 1028,
    'X': 750,
    'Y': 750,
    'Z': 611,
    '[': 278,
    '\\': 500,
    ']': 278,
    '^': 500,
    '_': 278,
    '`': 278,
    'a': 500,
    'b': 556,
    'c': 444,
    'd': 556,
    'e': 444,
    'f': 306,
    'g': 500,
    'h': 556,
    'i': 278,
    'j': 306,
    'k': 528,
    'l': 278,
    'm': 833,
    'n': 556,
    'o': 500,
    'p': 556,
    'q': 528,
    'r': 392,
    's': 394,
    't': 389,
    'u': 556,
    'v': 528,
    'w': 722,
    'x': 528,
    'y': 528,
    'z': 444,
    '{': 500,
    '|': 1000,
    '}': 500,
    '~': 500,
}


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print >>sys.stderr, 'Usage: {0} `kpsewhich cmunrm.otf`'.format(sys.argv[0])
        sys.exit(1)
    make_table(sys.argv[1], sys.stdout)
