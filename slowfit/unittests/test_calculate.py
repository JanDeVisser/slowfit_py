import json

from django.urls import resolve
from django.test import RequestFactory, TestCase
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from .base import create_user, login
from ..calculate import calculate, FitCalculation


class CalculateTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()

    def test_calculate_with_stack_reach_no_candidates(self):
        stack = 540
        reach = 369
        hx = 475
        hy = 679
        calc = FitCalculation(hx=hx, hy=hy, max_spacers=0.0, min_stem_length=0.0, max_stem_length=0.0,
                              frame=None, frame_size=None, stack=stack, reach=reach)
        # calc.no_threshold()
        calc.all_or_best = calc.OnlyBest
        candidates = calc.calculate()
        self.assertEquals(len(candidates), 0)

    def test_calculate_with_stack_reach_one_candidate(self):
        stack = 605
        reach = 396
        hx = 514
        hy = 640
        calc = FitCalculation(hx=hx, hy=hy, max_spacers=0.0, min_stem_length=0.0, max_stem_length=0.0,
                              frame=None, frame_size=None, stack=stack, reach=reach)
        # calc.no_threshold()
        calc.all_or_best = calc.OnlyBest
        candidates = calc.calculate()
        self.assertEquals(len(candidates), 1)


class UtilsPageTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        create_user()
        login(self.client)

    def test_calculate_with_stack_reach_view(self):
        response = self.client.post("/calculate/", data={
            "hx": "514",
            "hy": "640",
            "stack": "605",
            "reach": "396",
            "all_or_best": "ONLYBEST"
        })
        data = json.loads(response.content.decode())
        self.assertEquals(len(data), 1)
