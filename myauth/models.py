from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


def user_avatar_directory_path(instance: User, filename: str) -> str:
    return f"users/user_{instance.pk}/avatar/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name="about me")
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to=user_avatar_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=[
            'jpg',
            'jpeg',
            'png',
            'gif',
        ])],
        verbose_name="Avatar",
    )

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return "./static/profile_avatar/—Pngtree—character default avatar_5407167.png"
