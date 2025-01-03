"""
Test tee module
===============

"""

import unittest
import os
from shutil import rmtree
import sys

from ..tee import MultiFile

from ...io.redirect_stdout import stdout_redirected


class TestUtil(unittest.TestCase):
    """Test fluiddyn.util.util module."""

    @classmethod
    def setUpClass(cls):
        cls._work_dir = "test_fluiddyn_io_tee"
        if not os.path.exists(cls._work_dir):
            os.mkdir(cls._work_dir)

        os.chdir(cls._work_dir)

    @classmethod
    def tearDownClass(cls):
        os.chdir("..")
        rmtree(cls._work_dir)

    def test_tee(self):

        mf = MultiFile([sys.stdout])
        with stdout_redirected():
            mf.write("")


if __name__ == "__main__":
    unittest.main()
