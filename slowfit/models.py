from django.db import models
from django.contrib.auth.models import User
from time import datetime


class BaseModel(models.Model):
	name = models.CharField()
	description = models.TextField()


class Note(models.Model):
    posted  = models.DateTimeField(auto_now_add=True)
	noteFor = models.ForeignKey(BaseModel)
    by      = models.ForeignKey(User)
    text    = models.TextField()


def asset_directory(instance, filename):
	return f"assets/{instance.assetOf.name}"


class Asset(models.Model):
	assetOf     = models.ForeignKey(BaseModel)
	name        = models.CharField()
	description = models.TextField()
	tags        = models.TextField()
	mimeType    = models.TextField()
	asset       = models.FileField(upload_to=asset_directory)


class Country(models.Model):
	name     = models.CharField()
	isoCode  = models.CharField()
	isoCode3 = models.CharField()

    def flag(self, size):
        return f"/image/flags/{size}/{self.isoCode}.png"


class BikeType(BaseModel):
	pass


class Material(BaseModel):
	pass


class Brand(BaseModel):
	country     = models.ForeignKey(Country)
	URL         = models.URLField()
	imported    = models.ForeignKey(ImportLog)


class Frame(BaseModel):
	brand       = models.ForeignKey(Brand)
	bikeType    = models.ForeignKey(BikeType)
	material    = models.ForeignKey(Material)
	URL         = models.URLField()
	yearFrom    = models.PositiveSmallIntegerField()
	yearTo      = models.PositiveSmallIntegerField()
	imported    = models.ForeignKey(ImportLog)


class FrameSize(BaseModel):
	frame       = models.ForeignKey(Frame)
	HTAngle     = models.FloatField()