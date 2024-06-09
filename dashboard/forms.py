from django import forms
from .models import Fruit,Origin,Inventory,Warehousing,Shipping,Warehouse, Barcode
from users import models as user_models



class FruitForm(forms.ModelForm):
    class Meta:
        model = Fruit
        fields = '__all__'


class OriginForm(forms.ModelForm):
    class Meta:
        model = Origin
        fields = '__all__'


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = '__all__'


class WarehousingForm(forms.ModelForm):
    class Meta:
        model = Warehousing
        fields = '__all__'


class ShippingForm(forms.ModelForm):
    class Meta:
        model = Shipping
        fields = '__all__'


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = '__all__'

#
# class UserForm(forms.ModelForm):
#     class Meta:
#         model = user_models
#         fields = '__all__'

class BarcodeForm(forms.ModelForm):
    class Meta:
        model = Barcode
        fields = '__all__'

