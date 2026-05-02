from django.contrib.auth.models import Group
from django.forms import ModelForm, ImageField, ClearableFileInput, FileField
from .models import Product, Order
from shopapp.models import Product


class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_data = []
        for file in data:
            cleaned_file = super().clean(file, initial)
            if cleaned_file:
                cleaned_data.append(cleaned_file)

        return cleaned_data


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    images = MultipleFileField(
        required=False,
    )

    # images = ImageField(
    #     widget=ClearableFileInput(attrs={"multiple": True})
    # )
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = "delivery_address", "promocode", "user"


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = "name",
