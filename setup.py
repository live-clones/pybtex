#!/usr/bin/env python

# Copyright (C) 2006-2018  Andrey Golovizin
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


import os
import sys
from distutils.command.sdist import sdist
from distutils.dep_util import newer

from pybtex import __version__
from setuptools import find_packages, setup

progname = 'pybtex'


class Sdist(sdist):

    def run(self):
        from pybtex.database.convert import convert
        bibtex_yaml = os.path.join('examples', 'xampl.yaml')
        bibtexml = os.path.join('examples', 'xampl.bibtexml')
        bibtex = os.path.join('examples', 'xampl.bib')
        if not os.path.exists(bibtex_yaml) or newer(bibtex, bibtex_yaml):
            convert(bibtex, bibtex_yaml)
        if not os.path.exists(bibtexml) or newer(bibtex, bibtexml):
            convert(bibtex, bibtexml)

        sys.path.insert(0, os.path.join(ROOT, 'docs'))
        from pybtex_doctools.man import generate_manpages
        generate_manpages(os.path.join(ROOT, 'docs'))

        sdist.run(self)


ROOT = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(ROOT, 'README')).read()

install_requires = ['PyYAML>=3.01', 'latexcodec>=1.0.4', 'six']

setup(
    name=progname,
    version=__version__,
    description='A BibTeX-compatible bibliography processor in Python',
    long_description=README,
    author='Andrey Golovizin',
    author_email='ag@sologoc.com',
    url='https://pybtex.org/',
    license='MIT',
    platforms=['platform-independent'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Utilities',
    ],
    install_requires=install_requires,
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*',
    packages=find_packages(exclude=['docs']),
    include_package_data=True,
    cmdclass={'sdist': Sdist},
    entry_points={
        'console_scripts': [
            'pybtex = pybtex.__main__:main',
            'pybtex-convert = pybtex.database.convert.__main__:main',
            'pybtex-format = pybtex.database.format.__main__:main',
        ],
        'pybtex.database.input': [
            'bibtex = pybtex.database.input.bibtex:Parser',
            'bibtexml = pybtex.database.input.bibtexml:Parser',
            'yaml = pybtex.database.input.bibyaml:Parser',
        ],
        'pybtex.database.input.aliases': [
            'bibyaml = pybtex.database.input.bibyaml:Parser',
        ],
        'pybtex.database.input.suffixes': [
            '.bib = pybtex.database.input.bibtex:Parser',
            '.xml = pybtex.database.input.bibtexml:Parser',
            '.bibtexml = pybtex.database.input.bibtexml:Parser',
            '.bibyaml = pybtex.database.input.bibyaml:Parser',
            '.yaml = pybtex.database.input.bibyaml:Parser',
        ],
        'pybtex.database.output': [
            'bibtex = pybtex.database.output.bibtex:Writer',
            'bibtexml = pybtex.database.output.bibtexml:Writer',
            'yaml = pybtex.database.output.bibyaml:Writer',
        ],
        'pybtex.database.output.aliases': [
            'bibyaml = pybtex.database.output.bibyaml:Writer',
        ],
        'pybtex.database.output.suffixes': [
            '.bib = pybtex.database.output.bibtex:Writer',
            '.xml = pybtex.database.output.bibtexml:Writer',
            '.bibtexml = pybtex.database.output.bibtexml:Writer',
            '.bibyaml = pybtex.database.output.bibyaml:Writer',
            '.yaml = pybtex.database.output.bibyaml:Writer',
        ],
        'pybtex.backends': [
            'latex = pybtex.backends.latex:Backend',
            'html = pybtex.backends.html:Backend',
            'plaintext = pybtex.backends.plaintext:Backend',
            'markdown = pybtex.backends.markdown:Backend',
        ],
        'pybtex.backends.aliases': [
            'text = pybtex.backends.plaintext:Backend',
            'md = pybtex.backends.markdown:Backend',
        ],
        'pybtex.backends.suffixes': [
            '.bbl = pybtex.backends.latex:Backend',
            '.tex = pybtex.backends.latex:Backend',
            '.latex = pybtex.backends.latex:Backend',
            '.html = pybtex.backends.html:Backend',
            '.txt = pybtex.backends.plaintext:Backend',
            '.md = pybtex.backends.markdown:Backend',
        ],
        'pybtex.style.labels': [
            'number = pybtex.style.labels.number:LabelStyle',
            'alpha = pybtex.style.labels.alpha:LabelStyle',
        ],
        'pybtex.style.names': [
            'plain = pybtex.style.names.plain:NameStyle',
            'lastfirst = pybtex.style.names.lastfirst:NameStyle',
        ],
        'pybtex.style.names.aliases': [
            'last_first = pybtex.style.names.lastfirst:NameStyle',
        ],
        'pybtex.style.sorting': [
            'none = pybtex.style.sorting.none:SortingStyle',
            'author_year_title = pybtex.style.sorting.author_year_title:SortingStyle',
        ],
        'pybtex.style.formatting': [
            'plain = pybtex.style.formatting.plain:Style',
            'unsrt = pybtex.style.formatting.unsrt:Style',
            'alpha = pybtex.style.formatting.alpha:Style',
            'unsrtalpha = pybtex.style.formatting.unsrtalpha:Style',
        ],
    },
    zip_safe=True,
)
