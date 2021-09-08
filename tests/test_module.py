import unittest

import stactools.usgs_nlcd


class TestModule(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(stactools.usgs_nlcd.__version__)
