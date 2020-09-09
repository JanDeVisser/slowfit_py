from django.test import RequestFactory, TestCase
from .base import create_user, login
from ..imports.jsonimport import JSONImportSession
from ..models.base import BikeType, Material, Country
from ..models.bikes import Brand, Frame, FrameSize


class JSONImport(TestCase):
    def test_import_biketype(self):
        user = create_user()
        session = JSONImportSession(user, "bikedata")
        session.import_model_data("biketype")
        biketypes = BikeType.objects.all()
        self.assertGreater(len(biketypes), 0)
        road = BikeType.objects.filter(name='Road').first()
        self.assertIsNotNone(road)
        self.assertEquals(road.name, "Road")

    def test_import_all_generic_models(self):
        user = create_user()
        session = JSONImportSession(user, "bikedata")
        session.import_all_model_data()
        self.assertGreater(len(BikeType.objects.all()), 0)
        self.assertGreater(len(Material.objects.all()), 0)
        self.assertGreater(len(Country.objects.all()), 0)
        canada = Country.objects.filter(isoCode="CA").first()
        self.assertIsNotNone(canada)
        self.assertEquals(canada.name, "Canada")

    def test_import_brand(self):
        user = create_user()
        session = JSONImportSession(user, "bikedata")
        session.import_all_model_data()
        session.import_brand("3t")
        self.assertEquals(len(Brand.objects.all()), 1)
        self.assertEquals(len(Frame.objects.all()), 1)
        self.assertEquals(len(FrameSize.objects.all()), 5)

        strada = Frame.objects.filter(name="Strada").first()
        self.assertIsNotNone(strada)
        self.assertEquals(strada.yearFrom, 2018)
