from django import forms
from .models import Fruit,Origin,Inventory,Warehousing,Shipping,Warehouse, Barcode
from users import models as User

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
    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.fields['warehouse'].queryset = Warehouse.objects.filter(user_id=user_id)

    class Meta:
        model = Warehousing
        fields = ['warehousing_time', 'warehousing_quantity', 'warehousing_price', 'warehouse', 'barcode']

    def save(self, commit=True):
        warehousing = super().save(commit=False)
        warehousing.user = self.user_instance
        if commit:
            warehousing.save()
        return warehousing

class ShippingForm(forms.ModelForm):
    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.fields['warehouse'].queryset = Warehouse.objects.filter(user_id=user_id)
    class Meta:
        model = Shipping
        fields = ['Shipping_price','Shipping_quantity','Shipping_time',"warehouse",'barcode']
        widgets = {
            'Shipping_time': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type' : "datetime-local",
                }

            ),'Shipping_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),'Shipping_price': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            )
        }

    def save(self, commit=True):
        warehousing = super().save(commit=False)
        warehousing.user = self.user_instance
        if commit:
            warehousing.save()
        return warehousing
class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['warehouse_address','warehouse_name','warehouse_capacity','user']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        # self.fields['warehouse'].queryset = Warehouse.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        self.instance.user = self.user
        return cleaned_data

class BarcodeForm(forms.ModelForm):
    class Meta:
        model = Barcode
        fields = '__all__'