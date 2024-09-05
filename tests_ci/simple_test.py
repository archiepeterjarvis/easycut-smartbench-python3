import unittest

from kivy.app import App



class SimpleTest(unittest.TestCase):

    def test_simple_test(self):
        self._app = App()
        self._app.width = 800
        self._app.height = 480
        assert True
        print("TEST PASSED!")
