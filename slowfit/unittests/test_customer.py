from django.test import RequestFactory, TestCase
from .base import create_user, login
from ..models.fits import Customer
from ..testdata import customer as data


class CustomerTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        create_user()
        login(self.client)

    def test_customer_list(self):
        response = self.client.get("/customer/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "slowfit/customer_list.html")

    def test_create_customer_page(self):
        response = self.client.get("/customer/new/")
        self.assertTemplateUsed(response, "slowfit/customer_new.html")

    def test_create_customer(self):
        response = self.client.post("/customer/new/", data=data.CUSTOMER_DATA)
        self.assertEquals(response.status_code, 302)
        self.assertRegex(response.url, r"\/customer\/\d+")
        customer_id = response.url.split('/')[2]
        customer = Customer.objects.get(pk=customer_id)
        self.assertEqual(customer.lastName, data.CUSTOMER_LAST_NAME)

    def test_new_customer_in_list(self):
        _ = data.create_customer()
        response = self.client.get("/customer/")
        self.assertIn(data.CUSTOMER_LAST_NAME, response.content.decode())

    def test_view_customer(self):
        customer_id = data.create_customer()
        response = self.client.get(f"/customer/{customer_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "slowfit/customer_detail.html")
        self.assertIn(data.CUSTOMER_PHONE_MAIN, response.content.decode())

    def test_edit_customer_page(self):
        customer_id = data.create_customer()
        response = self.client.get(f"/customer/{customer_id}/edit/")
        self.assertTemplateUsed(response, "slowfit/customer_edit.html")

    def test_edit_customer(self):
        customer_id = data.create_customer()
        updated_data = {}
        updated_data.update(data.CUSTOMER_DATA)
        updated_data["email"] = data.CUSTOMER_EMAIL_2
        response = self.client.post(f"/customer/{customer_id}/edit/", data=updated_data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, f"/customer/{customer_id}/")
        customer = Customer.objects.get(pk=customer_id)
        self.assertEquals(customer.lastName, data.CUSTOMER_LAST_NAME)
        self.assertEquals(customer.email, data.CUSTOMER_EMAIL_2)

    def test_birthday_customer(self):
        customer_id = data.create_customer()

        customer = Customer.objects.get(pk=customer_id)
        self.assertEquals(customer.dateOfBirth.year, data.CUSTOMER_BIRTH_YEAR)
        self.assertEquals(customer.dateOfBirth.month, data.CUSTOMER_BIRTH_MONTH)
        self.assertEquals(customer.dateOfBirth.day, data.CUSTOMER_BIRTH_DAY_OF_MONTH)

        updated_data = {}
        updated_data.update(data.CUSTOMER_DATA)
        updated_data["email"] = data.CUSTOMER_EMAIL_2
        self.client.post(f"/customer/{customer_id}/edit/", data=updated_data)

        customer = Customer.objects.get(pk=customer_id)
        self.assertEquals(customer.dateOfBirth.year, data.CUSTOMER_BIRTH_YEAR)
        self.assertEquals(customer.dateOfBirth.month, data.CUSTOMER_BIRTH_MONTH)
        self.assertEquals(customer.dateOfBirth.day, data.CUSTOMER_BIRTH_DAY_OF_MONTH)
