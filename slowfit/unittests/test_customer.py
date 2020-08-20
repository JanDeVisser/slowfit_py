from django.test import RequestFactory, TestCase
from .base import create_user, login
from ..models.fits import Customer

CUSTOMER_FIRST_NAME = "Testy"
CUSTOMER_LAST_NAME = "McTestface"
CUSTOMER_ADDRESS = "42, Test Terrace\nTestville, ON, T5T 7S7"
CUSTOMER_EMAIL = "testy.mctestface@test.com"
CUSTOMER_EMAIL_2 = "testy.mctestface_2@test.com"
CUSTOMER_PHONE_MAIN = "(555) 555-0001"
CUSTOMER_PHONE_ALT = "(555) 555-0002"
CUSTOMER_BIRTH_YEAR = 2000
CUSTOMER_BIRTH_MONTH = 7
CUSTOMER_BIRTH_DAY_OF_MONTH = 13
CUSTOMER_HEIGHT = 180
CUSTOMER_INSEAM = 80

CUSTOMER_DATA = {
    "firstName": CUSTOMER_FIRST_NAME,
    "lastName": CUSTOMER_LAST_NAME,
    "address": CUSTOMER_ADDRESS,
    "email": CUSTOMER_EMAIL,
    "phoneMain": CUSTOMER_PHONE_MAIN,
    "phoneAlt": CUSTOMER_PHONE_ALT,
    "dateOfBirth": f"{CUSTOMER_BIRTH_YEAR:04}-{CUSTOMER_BIRTH_MONTH:02}-{CUSTOMER_BIRTH_DAY_OF_MONTH:02}",
    "height": CUSTOMER_HEIGHT,
    "inseam": CUSTOMER_INSEAM,
}


def create_customer():
    customer = Customer(**CUSTOMER_DATA)
    customer.save()
    return customer.id


class CustomerTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        create_user()
        login(self.client)

    def test_customer_list(self):
        response = self.client.get("/customer/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "slowfit/customer_list.html")

    def test_create_customer(self):
        response = self.client.get("/customer/new/")
        self.assertTemplateUsed(response, "slowfit/customer_new.html")

        response = self.client.post("/customer/new/", data=CUSTOMER_DATA)
        self.assertGreaterEqual(response.status_code, 300)
        self.assertLess(response.status_code, 400)
        self.assertRegex(response.url, r"\/customer\/\d+")
        customer_id = response.url.split('/')[2]
        customer = Customer.objects.get(pk=customer_id)
        self.assertEqual(customer.lastName, CUSTOMER_LAST_NAME)

        response = self.client.get("/customer/")
        response.render()
        html = response.content.decode('utf8').strip()
        self.assertIn(CUSTOMER_LAST_NAME, html)

    def test_view_customer(self):
        customer_id = create_customer()

        response = self.client.get(f"/customer/{customer_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "slowfit/customer_detail.html")
        response.render()
        html = response.content.decode('utf8').strip()
        self.assertIn(CUSTOMER_PHONE_MAIN, html)

    def test_edit_customer(self):
        customer_id = create_customer()
        response = self.client.get(f"/customer/{customer_id}/edit/")
        self.assertTemplateUsed(response, "slowfit/customer_edit.html")

        updated_data = {}
        updated_data.update(CUSTOMER_DATA)
        updated_data["email"] = CUSTOMER_EMAIL_2
        response = self.client.post(f"/customer/{customer_id}/edit/", data=updated_data)
        self.assertGreaterEqual(response.status_code, 300)
        self.assertLess(response.status_code, 400)

        customer = Customer.objects.get(pk=customer_id)
        self.assertEquals(customer.lastName, CUSTOMER_LAST_NAME)
        self.assertEquals(customer.email, CUSTOMER_EMAIL_2)

    def test_birthday_customer(self):
        customer_id = create_customer()

        customer = Customer.objects.get(pk=customer_id)
        self.assertEquals(customer.dateOfBirth.year, CUSTOMER_BIRTH_YEAR)
        self.assertEquals(customer.dateOfBirth.month, CUSTOMER_BIRTH_MONTH)
        self.assertEquals(customer.dateOfBirth.day, CUSTOMER_BIRTH_DAY_OF_MONTH)

        updated_data = {}
        updated_data.update(CUSTOMER_DATA)
        updated_data["email"] = CUSTOMER_EMAIL_2
        self.client.post(f"/customer/{customer_id}/edit/", data=updated_data)

        customer = Customer.objects.get(pk=customer_id)
        self.assertEquals(customer.dateOfBirth.year, CUSTOMER_BIRTH_YEAR)
        self.assertEquals(customer.dateOfBirth.month, CUSTOMER_BIRTH_MONTH)
        self.assertEquals(customer.dateOfBirth.day, CUSTOMER_BIRTH_DAY_OF_MONTH)
