from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User

import slowfit.util


class RegisteredClasses:
    _classes = {}

    @staticmethod
    def register_class(cls):
        n: str = cls.__name__
        parts = n.lower().split('.')
        RegisteredClasses._classes.update({'.'.join(parts[pix:]): cls for pix in range(0, len(parts))})

    @staticmethod
    def get_class(n):
        return RegisteredClasses._classes.get(n.lower()) if n else None

    @staticmethod
    def dump_classes():
        print(RegisteredClasses._classes)


class RegisteredModel:
    def __init_subclass__(cls, **kwargs):
        RegisteredClasses.register_class(cls)


class BaseModel(models.Model, RegisteredModel):
    class Meta:
        abstract = True

    name = models.CharField("Name", max_length=30, blank=False)
    description = models.CharField("Description", max_length=200, blank=True)

    def __str__(self):
        return f"{self.name}"

    def has_notes(self):
        return isinstance(self, Annotateable)

    def has_assets(self):
        return isinstance(self, AssetOwner)


class Note(models.Model):
    class Meta:
        ordering = ['noteForModel', 'noteForID', '-posted']

    posted = models.DateTimeField(auto_now_add=True)
    noteForModel = models.CharField(max_length=30)
    noteForID = models.IntegerField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField()


class Annotateable:
    def add_note(self, text, user) -> Note:
        note = Note(noteForModel=self.__class__.__name__, noteForID=self.id, author=user, text=text)
        note.save()
        return note

    def notes(self) -> Note:
        return Note.objects.filter(noteOfModel=self.__class__.__name__, noteOfID=self.id)


def asset_directory(instance, filename):
    return f"assets/{instance.assetOfModel}_{instance.assetOfID}"


class Asset(models.Model):
    class Meta:
        ordering = ['assetOfModel', 'assetOfID', 'name']

    assetOfModel = models.CharField(max_length=30)
    assetOfID = models.IntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=30, blank=True)
    mimeType = models.CharField(max_length=40, blank=True)
    asset = models.FileField(upload_to=asset_directory)

    def is_image(self):
        return self.mimeType.startswith("image/")

    def update(self, name, data):
        if self.asset:
            self.asset.delete(False)
        src = ContentFile(data.read() if hasattr(data, "read") and callable(data.read) else data)
        self.asset.save(name=name, content=src, save=True)
        return self


class AssetOwner:
    def add_asset(self, name, tag, data) -> Asset:
        asset = Asset(assetOfModel=self.__class__.__name__, assetOfID=self.id, name=name, tags=tag,
                      mimeType=slowfit.util.mimetype_for_file(name))
        asset.save()
        asset.update(name, data)
        return asset

    def upsert_asset(self, name, tag, data) -> Asset:
        asset = self.asset_by_tag(tag)
        if not asset:
            asset = Asset(assetOfModel=self.__class__.__name__, assetOfID=self.id, name=name, tags=tag,
                          mimeType=slowfit.util.mimetype_for_file(name))
            asset.save()
        asset.update(name, data)
        return asset

    def asset_by_tag(self, tag) -> Asset:
        assets = self.assets_by_tag(tag)
        if assets and len(assets) > 1:
            raise ValueError("asset_by_tag: model '%s' of class '%s' has more than one asset with tag '%s'",
                             str(self), self.__class__.__name__, tag)
        return assets[0] if assets else None

    def assets_by_tag(self, tag) -> models.QuerySet:
        return self.assets().filter(tags=tag)

    def assets(self) -> models.QuerySet:
        return Asset.objects.filter(assetOfModel=self.__class__.__name__, assetOfID=self.id)


class Country(models.Model, RegisteredModel):
    name = models.CharField(max_length=30)
    isoCode = models.CharField(max_length=5)
    isoCode3 = models.CharField(max_length=5)

    def flag(self, size="sm"):
        return f"/static/image/flags/{size}/{self.isoCode}.png"

    def __str__(self):
        return f"{self.name}"


class BikeType(BaseModel):
    pass


class Material(BaseModel):
    pass
