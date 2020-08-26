from django.test import RequestFactory, TestCase
from .base import create_user, login
from .test_customer import create_customer
from ..models.fits import Visit

VISIT_DATE = "2020-09-01 09:00:00"
VISIT_PURPOSE = "Testy wants to get riding"
VISIT_EXPERIENCE = "Testy has seen a bike before"
VISIT_GOALS = "Be able to ride to the pub"
VISIT_INJURIES = "Testy is healthy"
VISIT_WEIGHT = 0
VISIT_CUSTOMER_CONCERNS = "Cycling is difficult"
VISIT_FITTER_CONCERNS = "He's gonna be fine"
VISIT_CURRENTBIKE = ""
VISIT_PEDALSYSTEM = "Look"
VISIT_HX = 514
VISIT_HY = 640
VISIT_SX = 700
VISIT_SY = 0
VISIT_CRANKLENGTH = 170
VISIT_SADDLE = "Fizik Antares"
VISIT_SADDLEHEIGHT = 795
VISIT_SADDLESETBACK = 30
VISIT_SADDLEBARDROP = 150

VISIT_DATA = {
    "date": VISIT_DATE,
    "purpose": VISIT_PURPOSE,
    "experience": VISIT_EXPERIENCE,
    "goals": VISIT_GOALS,
    "injuries": VISIT_INJURIES,
    "weight": VISIT_WEIGHT,
    "customerConcerns": VISIT_CUSTOMER_CONCERNS,
    "fitterConcerns": VISIT_FITTER_CONCERNS,
    "currentBike": VISIT_CURRENTBIKE,
    "pedalSystem": VISIT_PEDALSYSTEM,
    "hx": VISIT_HX,
    "hy": VISIT_HY,
    "sx": VISIT_SX,
    "sy": VISIT_SY,
    "crankLength": VISIT_CRANKLENGTH,
    "saddle": VISIT_SADDLE,
    "saddleHeight": VISIT_SADDLEHEIGHT,
    "saddleSetback": VISIT_SADDLESETBACK,
    "saddleBarDrop": VISIT_SADDLEBARDROP,
}


def create_visit(customer_id):
    kwargs = dict(VISIT_DATA)
    kwargs["customer_id"] = customer_id
    kwargs["currentBike"] = None
    visit = Visit(**kwargs)
    visit.save()
    return visit.id


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
        response = self.client.post(f"/visit/new/{self.customer_id}/", data=VISIT_DATA)

        self.assertEquals(response.status_code, 302)
        self.assertRegex(response.url, r"\/visit\/\d+")
        visit_id = response.url.split('/')[2]
        visit = Visit.objects.get(pk=visit_id)
        self.assertEqual(visit.purpose, VISIT_PURPOSE)

    def test_new_visit_in_customer_view(self):
        _ = create_visit(self.customer_id)

        response = self.client.get(f"/customer/{self.customer_id}/")

        self.assertIn(VISIT_PURPOSE, response.content.decode())

    def test_view_visit(self):
        visit_id = create_visit(self.customer_id)

        response = self.client.get(f"/visit/{visit_id}/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "slowfit/visit_detail.html")
        self.assertIn(VISIT_CUSTOMER_CONCERNS, response.content.decode())
