import io
import os
import unittest


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current_directory = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.current_directory)

    def setUp(self):
        self.buff = io.BytesIO()