__author__ = "Jeremy Nelson"
__license__ = "Apache 2"

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(".").split()[:2][0]
sys.path.append(ROOT_DIR)

import src.sinopia.github as github


class TestIssues(unittest.TestCase):

    def test_no_params(self):
        result = github.issues_query()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
