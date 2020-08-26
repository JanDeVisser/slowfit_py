from .base import SlowfitTestCase


class HomePageTest(SlowfitTestCase):
    def test_login(self):
        self.login()
