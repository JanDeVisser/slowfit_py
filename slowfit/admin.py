from django.contrib import admin

# Register your models here.

from .models.base import Material
from .models.base import BikeType
from .models.base import Country
from .models.bikes import Brand
from .models.bikes import Frame
from .models.bikes import FrameSize

admin.site.register(Material)
admin.site.register(BikeType)
admin.site.register(Country)
admin.site.register(Brand)
admin.site.register(Frame)
admin.site.register(FrameSize)
