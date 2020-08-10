import datetime

from django.db import models
from django.urls import reverse

from .base import Annotateable
from .base import AssetOwner
from .base import BaseModel
from .bikes import FrameSize


class Customer(BaseModel, AssetOwner, Annotateable):
    class Meta:
        ordering = ['lastName', 'firstName']

    firstName = models.CharField("First Name", max_length=30)
    lastName = models.CharField("Last Name", max_length=30)
    address = models.TextField("Address", null=True, blank=True)
    email = models.EmailField("EMail Address", unique=True, max_length=60)
    phoneMain = models.CharField("Main Phone Number", unique=True, max_length=20)
    phoneAlt = models.CharField("Alternative Phone Number", null=True, max_length=20, blank=True)
    dateOfBirth = models.DateField("Date of Birth", null=True, blank=True)
    height = models.PositiveSmallIntegerField("Height in cm", null=True, blank=True)
    inseam = models.PositiveSmallIntegerField("Inseam in cm", null=True, blank=True)
    armLength = models.PositiveSmallIntegerField("Arm Length in cm", null=True, blank=True)

    @property
    def age(self):
        delta = datetime.date.today() - self.dateOfBirth
        return delta.year

    @property
    def fullname(self):
        return f"{self.firstName} {self.lastName}"

    def get_absolute_url(self):
        return reverse('customer-view', kwargs={'pk': self.pk})

    def __str__(self):
        return self.fullname


CRANK_LENGTH = [
    (165, "165mm"),
    (167.5, "167.5mm"),
    (170, "170mm"),
    (172.5, "172.5mm"),
    (175, "175mm"),
]

PEDAL_SYSTEM = [
    ("Shimano Road", "Shimano Road"),
    ("Shimano SPD", "Shimano SPD"),
    ("Look", "Look"),
    ("Time", "Time"),
    ("Speedplay", "Speedplay"),
]


class Visit(BaseModel, AssetOwner, Annotateable):
    class Meta:
        get_latest_by = "date"
        order_with_respect_to = 'customer'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField('date of visit')
    purpose = models.CharField("purpose of visit", max_length=100, blank=False, null=False)
    experience = models.TextField("cycling experience", blank=True, null=True)
    goals = models.TextField("athletic goals", blank=True, null=True)
    injuries = models.TextField("injuries and limitations", blank=True, null=True)
    weight = models.PositiveSmallIntegerField("weight in kg", blank=True, null=True)
    customerConcerns = models.TextField("rider's specific concerns", blank=True, null=True)
    fitterConcerns = models.TextField("fitter's concerns", blank=True, null=True)
    currentBike = models.ForeignKey(FrameSize, verbose_name="current bike", on_delete=models.PROTECT, null=True, blank=True)
    pedalSystem = models.TextField("pedal system", choices=PEDAL_SYSTEM, null=True, blank=True)
    hx = models.PositiveSmallIntegerField("current handlebar reach (mm)", null=True, blank=True)
    hy = models.PositiveSmallIntegerField("current handlebar stack (mm)", null=True, blank=True)
    sx = models.SmallIntegerField("current saddle X", null=True, blank=True)
    sy = models.PositiveSmallIntegerField("current saddle Y", null=True, blank=True)
    crankLength = models.PositiveSmallIntegerField("current crank length", choices=CRANK_LENGTH, null=True, blank=True)
    saddle = models.CharField("current saddle", blank=True, max_length=30, null=True)
    saddleHeight = models.PositiveSmallIntegerField("current saddle height", null=True, blank=True)
    saddleSetback = models.SmallIntegerField("current saddle setback/offset", null=True, blank=True)
    saddleBarDrop = models.SmallIntegerField("current saddle to bar drop",
                                             help_text=
                                             "positive: saddle higher than bar, negative: bar higher than saddle",
                                             null=True, blank=True)


class FitSheet(BaseModel, AssetOwner, Annotateable):
    class Meta:
        order_with_respect_to = 'visit'

    visit = models.ForeignKey(Visit, on_delete=models.CASCADE)
    bikeUsed = models.ForeignKey(FrameSize, verbose_name="bike used", on_delete=models.PROTECT)
    hx = models.PositiveSmallIntegerField("selected handlebar reach (mm)")
    hy = models.PositiveSmallIntegerField("selected handlebar stack (mm)")
    sx = models.SmallIntegerField("selected current saddle X")
    sy = models.PositiveSmallIntegerField("selected current saddle Y")
    crankLength = models.PositiveSmallIntegerField("selected current crank length", choices=CRANK_LENGTH)
    saddle = models.CharField("selected saddle", blank=True, max_length=30)
    saddleHeight = models.PositiveSmallIntegerField("selected saddle height")
    saddleSetback = models.SmallIntegerField("selected saddle setback/offset")
    saddleBarDrop = models.SmallIntegerField("selected saddle to bar drop",
                                             help_text=
                                             "positive: saddle higher than bar, negative: bar higher than saddle")


class Trial(BaseModel, AssetOwner, Annotateable):
    class Meta:
        order_with_respect_to = 'fitSheet'

    fitSheet = models.ForeignKey(FitSheet, on_delete=models.CASCADE)
    hx = models.PositiveSmallIntegerField("handlebar reach (mm)")
    hy = models.PositiveSmallIntegerField("handlebar stack (mm)")
    sx = models.SmallIntegerField("saddle X")
    sy = models.PositiveSmallIntegerField("saddle Y")


class RoadFitSheet(FitSheet):
    webX = models.PositiveSmallIntegerField("selected handlebar web X (reach)", blank=True)
    webY = models.PositiveSmallIntegerField("selected handlebar web Y (stack)", blank=True)
    barWidth = models.PositiveSmallIntegerField("selected handlebar width", blank=True)
    barDrop = models.PositiveSmallIntegerField("selected handlebar drop", blank=True)
    barReach = models.PositiveSmallIntegerField("selected handlebar reach", blank=True)


class TTFitSheet(FitSheet):
    aeroBar = models.CharField("selected aerobar", blank=True, max_length=30)
    padWidth = models.PositiveSmallIntegerField("pad width (mm)", blank=True)
    extensions = models.CharField("selected extensions", blank=True, max_length=30)
