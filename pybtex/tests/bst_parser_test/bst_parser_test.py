import pkgutil
from itertools import izip_longest

from pybtex.bibtex import bst


test_data = (
    'plain',
    'apacite',
    'jurabib',
)


def check_bst_parser(dataset_name):
    module = __import__('pybtex.tests.bst_parser_test.{0}'.format(dataset_name), globals(), locals(), 'bst')
    correct_result = module.bst
    bst_data = pkgutil.get_data('pybtex.tests.data', dataset_name + '.bst').decode('latin1')
    actual_result = bst.parse_string(bst_data)

    for correct_element, actual_element in izip_longest(actual_result, correct_result):
        assert correct_element == actual_element, '\n{0}\n{1}'.format(correct_element, actual_element)


def test_bst_parser():
    for dataset_name in test_data:
        yield check_bst_parser, dataset_name
