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
        fields = ['origin_location', 'origin_address', 'origin_latitude',
                  'origin_longitude']
        widgets = {
            'origin_address': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'id': "sample5_address",
                    'placeholder': "주소",
                    'autocomplete': 'off',
                    'readonly': 'true'
                },

            ), 'origin_location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                }
            ), 'origin_latitude': forms.HiddenInput(),
            'origin_longitude': forms.HiddenInput(),

        }

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
                    'readonly' : 'true'
                },

            ), 'warehouse_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                }
            ), 'warehouse_capacity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'step': '0.01',
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
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['warehouse'].queryset = Warehouse.objects.filter(user_id=user)

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
            ),'user': forms.HiddenInput()
        }


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
            ),'barcode': forms.TextInput(
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