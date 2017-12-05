from __future__ import unicode_literals

from six.moves import zip_longest

from pybtex.bibtex import bst
from ..utils import read_file

test_data = (
    'plain',
    'apacite',
    'jurabib',
)


def check_bst_parser(dataset_name):
    module = __import__('tests.bst_parser_test.{0}'.format(dataset_name), globals(), locals(), 'bst')
    correct_result = module.bst
    bst_data = read_file(dataset_name + '.bst')
    actual_result = bst.parse_string(bst_data)

    for correct_element, actual_element in zip_longest(actual_result, correct_result):
        assert correct_element == actual_element, '\n{0}\n{1}'.format(correct_element, actual_element)


def test_bst_parser():
    for dataset_name in test_data:
        yield check_bst_parser, dataset_name
