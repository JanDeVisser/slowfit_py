from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from .base import create_user

from ..views import index


class IndexPageTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = index(request)
        html = response.content.decode('utf8').strip()
        self.assertTrue(html.startswith('<!doctype html>'))
        self.assertIn('<title>Slowfit bike fit tracker</title>', html)
        self.assertTrue(html.endswith('</html>'))
        self.assertNotContains(response, 'id="Customers"')

    def test_home_page_with_auth_returns_correct_html(self):
        request = HttpRequest()
        request.user = self.user
        response = index(request)
        html = response.content.decode('utf8').strip()
        self.assertTrue(html.startswith('<!doctype html>'))
        self.assertIn('<title>Slowfit bike fit tracker</title>', html)
        self.assertTrue(html.endswith('</html>'))
        self.assertContains(response, 'id="Customers"')
