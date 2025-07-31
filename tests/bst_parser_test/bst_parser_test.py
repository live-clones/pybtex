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


from itertools import zip_longest

import pytest

from pybtex.bibtex import bst

from ..utils import get_data


@pytest.mark.parametrize("dataset_name", ["plain", "apacite", "jurabib"])
def test_bst_parser(dataset_name):
    module = __import__(
        f"tests.bst_parser_test.{dataset_name}", globals(), locals(), "bst"
    )
    correct_result = module.bst
    bst_data = get_data(dataset_name + ".bst")
    actual_result = bst.parse_string(bst_data)

    for correct_element, actual_element in zip_longest(actual_result, correct_result):
        assert correct_element == actual_element, (
            f"\n{correct_element}\n{actual_element}"
        )
