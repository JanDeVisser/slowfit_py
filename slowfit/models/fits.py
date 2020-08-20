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
    date = models.DateTimeField('Date of Visit')
    purpose = models.CharField("Purpose of Visit", max_length=100, blank=False, null=False)
    experience = models.TextField("Cycling Experience", blank=True, null=True)
    goals = models.TextField("Athletic Goals", blank=True, null=True)
    injuries = models.TextField("Injuries and Limitations", blank=True, null=True)
    weight = models.PositiveSmallIntegerField("Weight in kg", blank=True, null=True)
    customerConcerns = models.TextField("Rider's Specific Concerns", blank=True, null=True)
    fitterConcerns = models.TextField("Fitter's Concerns", blank=True, null=True)
    currentBike = models.ForeignKey(FrameSize, verbose_name="Current Bike", on_delete=models.PROTECT, null=True, blank=True)
    pedalSystem = models.TextField("Pedal System", choices=PEDAL_SYSTEM, null=True, blank=True)
    hx = models.PositiveSmallIntegerField("Current Handlebar Reach (mm)", null=True, blank=True)
    hy = models.PositiveSmallIntegerField("Current Handlebar Stack (mm)", null=True, blank=True)
    sx = models.SmallIntegerField("Current Saddle X", null=True, blank=True)
    sy = models.PositiveSmallIntegerField("Current Saddle Y", null=True, blank=True)
    crankLength = models.PositiveSmallIntegerField("Current Crank Length", choices=CRANK_LENGTH, null=True, blank=True)
    saddle = models.CharField("Current Saddle", blank=True, max_length=30, null=True)
    saddleHeight = models.PositiveSmallIntegerField("Current Saddle Height", null=True, blank=True)
    saddleSetback = models.SmallIntegerField("Current Saddle Setback/Offset", null=True, blank=True)
    saddleBarDrop = models.SmallIntegerField("Current Saddle to Bar drop",
                                             help_text=
                                             "positive: saddle higher than bar, negative: bar higher than saddle",
                                             null=True, blank=True)

    def get_absolute_url(self):
        return reverse('visit-view', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.customer.fullname} - {self.date}: {self.purpose}"


class FitSheet(BaseModel, AssetOwner, Annotateable):
    class Meta:
        order_with_respect_to = 'visit'

    fit_type = None

    visit = models.ForeignKey(Visit, on_delete=models.CASCADE)
    bikeUsed = models.ForeignKey(FrameSize, verbose_name="Bike Used", on_delete=models.PROTECT, blank=True, null=True)
    hx = models.PositiveSmallIntegerField("Selected Handlebar Reach (mm)", blank=True, null=True)
    hy = models.PositiveSmallIntegerField("Selected Handlebar Stack (mm)", blank=True, null=True)
    sx = models.SmallIntegerField("Selected Current Saddle X", blank=True, null=True)
    sy = models.PositiveSmallIntegerField("Selected Current Saddle Y", blank=True, null=True)
    crankLength = models.PositiveSmallIntegerField("Selected Current Crank Length", choices=CRANK_LENGTH, blank=True, null=True)
    saddle = models.CharField("Selected Saddle", blank=True, max_length=30, null=True)
    saddleHeight = models.PositiveSmallIntegerField("Selected Saddle Height", blank=True, null=True)
    saddleSetback = models.SmallIntegerField("Selected Saddle Setback/Offset", blank=True, null=True)
    saddleBarDrop = models.SmallIntegerField("Selected Saddle to Bar Drop",
                                             help_text=
                                             "positive: saddle higher than bar, negative: bar higher than saddle",
                                             blank=True, null=True)


class Trial(BaseModel, AssetOwner, Annotateable):
    class Meta:
        order_with_respect_to = 'fitSheet'

    fitSheet = models.ForeignKey(FitSheet, on_delete=models.CASCADE)
    hx = models.PositiveSmallIntegerField("Handlebar Reach (mm)")
    hy = models.PositiveSmallIntegerField("Handlebar Stack (mm)")
    sx = models.SmallIntegerField("Saddle X")
    sy = models.PositiveSmallIntegerField("Saddle Y")

    def get_absolute_url(self):
        return reverse('fitsheet-view-tab', kwargs={'pk': self.fitSheet.id, 'tab': 'trials'})


class RoadFitSheet(FitSheet):
    fit_type = "Road"
    webX = models.PositiveSmallIntegerField("Selected Handlebar Web X (Reach)", blank=True, null=True)
    webY = models.PositiveSmallIntegerField("Selected Handlebar Web Y (Stack)", blank=True, null=True)
    barWidth = models.PositiveSmallIntegerField("Selected Handlebar Width", blank=True, null=True)
    barDrop = models.PositiveSmallIntegerField("Selected Handlebar Drop", blank=True, null=True)
    barReach = models.PositiveSmallIntegerField("Selected Handlebar Reach", blank=True, null=True)

    def get_absolute_url(self):
        return reverse('fitsheet-view', kwargs={'pk': self.pk})


class TTFitSheet(FitSheet):
    fit_type = "Time Trial/Triathlon"
    aeroBar = models.CharField("Selected Aerobar", blank=True, max_length=30, null=True)
    padWidth = models.PositiveSmallIntegerField("Pad Width (mm)", blank=True, null=True)
    extensions = models.CharField("Selected Extensions", blank=True, max_length=30, null=True)

    def get_absolute_url(self):
        return reverse('fitsheet-view', kwargs={'pk': self.pk})

