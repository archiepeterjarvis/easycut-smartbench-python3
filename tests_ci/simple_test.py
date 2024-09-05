import unittest

from kivy.app import App



class SimpleTest(unittest.TestCase):


    def setUp(self):
        self._app = App()
        self._app.width = 800
        self._app.height = 480
        print("Setup PASSED!")

    def test_simple_test(self):
        assert True
        print("TEST PASSED!")
