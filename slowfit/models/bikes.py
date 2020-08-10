from django.db import models

from .base import Annotateable
from .base import AssetOwner
from .base import BaseModel
from .base import Country
from .imports import ImportLog


class Brand(BaseModel, Annotateable, AssetOwner):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, verbose_name="Country")
    URL = models.URLField("Website", null=True)
    imported = models.ForeignKey(ImportLog, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name}"

    def logo(self):
        if not hasattr(self, "_logo"):
            self._logo = self.asset_by_tag("_logo")
        return self._logo

    def get_avatar_context(self):
        return {
            "tag": "_logo",
            "owner": self,
            "owner_kind": self.__class__.__name__,
            "fallback": "static/image/bicycle.png",
            "button_label": "Logo"
        }


class Frame(BaseModel, Annotateable, AssetOwner):
    class Meta:
        ordering = ['brand', 'name']

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Brand")
    bikeType = models.ForeignKey('BikeType', on_delete=models.SET_NULL, null=True, verbose_name="Bike Type")
    material = models.ForeignKey('Material', on_delete=models.SET_NULL, null=True, verbose_name="Material")
    URL = models.URLField("Webpage", null=True, blank=True)
    yearFrom = models.PositiveSmallIntegerField("First Model Year", null=True)
    yearTo = models.PositiveSmallIntegerField("Last Model Year", null=True)
    imported = models.ForeignKey(ImportLog, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    def get_avatar_context(self, context: dict):
        return context.update({
            "tag": "_avatar",
            "fallback": "static/image/bicycle.png",
            "button_label": "Avatar"
        })


class FrameSize(BaseModel, Annotateable, AssetOwner):
    class Meta:
        ordering = ['frame', 'name']

    frame = models.ForeignKey(Frame, on_delete=models.CASCADE)
    headTubeAngle = models.FloatField()
    stack = models.PositiveSmallIntegerField()
    reach = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.frame} {self.name}"
