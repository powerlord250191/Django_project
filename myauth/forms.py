from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, FileInput, ImageField, TextInput, EmailInput, Textarea
from .models import Profile


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = "first_name", "last_name", "email"
        widgets = {
            "first_name": TextInput(attrs={"class": "form-control"}),
            "last_name": TextInput(attrs={"class": "form-control"}),
            "email": EmailInput(attrs={"class": "form-control"}),
        }


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = "user", "bio", "avatar"
        widgets = {
            "avatar": FileInput(attrs={"class": "form-control-file", "accept": "image/*"}),
            "bio": Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class AvatarForm(ModelForm):
    class Meta:
        model = Profile
        fields = "avatar",
        widgets = {
            "avatar": FileInput(attrs={
                "class": "form-control-file",
                'accept': "image/*",
                "id": "avatar-input"
            })
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError("Размер файла должен быть не больше 5MB")
        return avatar
