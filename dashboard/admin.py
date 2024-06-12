from django.contrib import admin
from .models import *

admin.site.register(Warehouse)
admin.site.register(Fruit)
admin.site.register(Origin)
admin.site.register(Barcode)
admin.site.register(Warehousing)
admin.site.register(Shipping)
admin.site.register(Inventory)