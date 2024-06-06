
from django.db import models
from django.utils import timezone

class User(models.Model):
    user_id = models.BigAutoField(primary_key =True)


class Inventory(models.Model):
    inventory_id = models.BigAutoField(primary_key=True)
    inventory_quantity = models.IntegerField(default=0)
    warehouse_id = models.ForeignKey("Warehouse", on_delete=models.CASCADE)
    fruit_id = models.ForeignKey("Fruit", on_delete=models.CASCADE)

class Fruit(models.Model):
    fruit_id = models.BigAutoField(primary_key=True)
    fruit_name = models.CharField(max_length=50)
    fruit_day_plus = models.IntegerField(default=0)

class Warehouse(models.Model):
    warehouse_id = models.BigAutoField(primary_key = True)
    warehouse_name = models.CharField(max_length = 100)
    warehouse_longitude = models.CharField(max_length= 100)
    warehouse_latitude = models.CharField(max_length=100)
    warehouse_address = models.CharField(max_length = 200)
    user_id = models.ForeignKey("User",on_delete=models.CASCADE)

class Barcode(models.Model):
    barcode_id = models.BigAutoField(primary_key=True)
    origin_id = models.ForeignKey("Origin",on_delete=models.CASCADE)
    fruit_id = models.ForeignKey("Fruit",on_delete=models.CASCADE)

class Inbound(models.Model):
    inbound_id = models.BigAutoField(primary_key=True)
    inbound_time = models.DateTimeField(default = timezone.now)
    inbound_quantity = models.IntegerField(default = 0)
    release_until = models.DateTimeField(default = timezone.now)
    inbound_price = models.IntegerField(default =0)
    barcode_id = models.ForeignKey("Barcode",on_delete = models.CASCADE)

class Release(models.Model):
    release_id = models.BigAutoField(primary_key = True)
    release_time = models.DateTimeField(default = timezone.now)
    release_quantity = models.IntegerField(default = 0)
    release_price = models.IntegerField(default=0)
    barcode_id = models.ForeignKey("Barcode",on_delete=models.CASCADE)

class Origin(models.Model):
    origin_id = models.BigAutoField(primary_key=True)
    origin_location = models.CharField(max_length =200)
    origin_address = models.CharField(max_length = 200)
    origin_longitude = models.CharField(max_length = 100, default = 0)
    origin_latitude = models.CharField(max_length = 100, default = 0)

