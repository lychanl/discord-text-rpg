import unittest

from dtrpg import utils


class TestStringDifference(unittest.TestCase):
    def test_string_difference_identical(self):
        self.assertEqual(utils.difference_with_wildcards('abc', 'abc'), 0)

    def test_string_difference_identical_wildcards(self):
        self.assertEqual(utils.difference_with_wildcards('a*bc', 'a*bc'), 0)

    def test_string_difference_matching(self):
        self.assertEqual(utils.difference_with_wildcards('a*c', 'abc'), 0)
        self.assertEqual(utils.difference_with_wildcards('abc', 'a*c'), 0)

    def test_string_difference_matching_multiple(self):
        self.assertEqual(utils.difference_with_wildcards('a*f', 'abcdef'), 0)
        self.assertEqual(utils.difference_with_wildcards('abcdef', 'a*f'), 0)

    def test_string_difference_on_add(self):
        self.assertEqual(utils.difference_with_wildcards('a*gf', 'abcdef'), 1)
        self.assertEqual(utils.difference_with_wildcards('abcdef', 'a*gf'), 1)
