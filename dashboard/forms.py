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

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['warehouse_address','warehouse_name','warehouse_capacity','user','warehouse_latitude','warehouse_longitude']
        widgets = {
            'warehouse_address': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'id': "sample5_address",
                    'placeholder': "주소",
                    'autocomplete': 'off',
                }

            ), 'warehouse_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                }
            ), 'warehouse_capacity': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                }
            ),'warehouse_latitude': forms.HiddenInput(),
            'warehouse_longitude': forms.HiddenInput(),
            'user': forms.HiddenInput()
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        # self.fields['warehouse'].queryset = Warehouse.objects.filter(user=user)
    #
    # def clean(self):
    #     cleaned_data = super().clean()
    #     self.instance.user = self.user
    #     return cleaned_data

class WarehousingForm(forms.ModelForm):
    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.fields['warehouse'].queryset = Warehouse.objects.filter(user_id=user_id)

    class Meta:
        model = Warehousing
        fields = ['warehousing_time', 'warehousing_quantity', 'warehousing_price', 'warehouse', 'barcode']
        widgets = {
            'warehousing_time': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type': "datetime-local",
                }

            ), 'warehousing_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ), 'warehousing_price': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),'barcode': forms.NumberInput(
                attrs={
                    'class': "form-control",
                    'placeholder':"바코드를 스캔하거나 직접 입력하세요.",
                    'autocomplete': 'off',
                }
            )
        }

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
                    'type': "datetime-local",
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
                    'type': "datetime-local",
                }

            ),'Shipping_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),'Shipping_price': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),'barcode': forms.Select(
                 attrs={
                    'class':"form-control",
                    'placeholder':"바코드를 스캔하거나 직접 입력하세요.",
                     'autocomplete': 'off',
                }
            )
        }

class BarcodeForm(forms.ModelForm):
    class Meta:
        model = Barcode
        fields = ['barcode_id','fruit','origin']
        widgets = {
            'barcode_id': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    "placeholder": '바코드를 입력해주세요.',
                    'autocomplete': 'off',
                }

            )
            , 'fruit': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ), 'origin': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            )
        }