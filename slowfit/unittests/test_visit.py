from django.test import RequestFactory, TestCase
from .base import create_user, login
from .test_customer import create_customer
from ..models.fits import Visit
from ..testdata import visit as data


class VisitTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        create_user()
        login(self.client)
        self.customer_id = create_customer()

    def test_new_visit_page(self):
        response = self.client.get(f"/visit/new/{self.customer_id}/")

        self.assertTemplateUsed(response, "slowfit/visit_new.html")

    def test_create_new_visit(self):
        response = self.client.post(f"/visit/new/{self.customer_id}/", data=data.VISIT_DATA)

        self.assertEquals(response.status_code, 302)
        self.assertRegex(response.url, r"\/visit\/\d+")
        visit_id = response.url.split('/')[2]
        visit = Visit.objects.get(pk=visit_id)
        self.assertEqual(visit.purpose, data.VISIT_PURPOSE)

    def test_new_visit_in_customer_view(self):
        _ = data.create_visit(self.customer_id)

        response = self.client.get(f"/customer/{self.customer_id}/")

        self.assertIn(data.VISIT_PURPOSE, response.content.decode())

    def test_view_visit(self):
        visit_id = data.create_visit(self.customer_id)

        response = self.client.get(f"/visit/{visit_id}/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "slowfit/visit_detail.html")
        self.assertContains(response, data.VISIT_CUSTOMER_CONCERNS)
