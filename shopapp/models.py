from django.contrib.auth.models import User
from django.db import models


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return f"products/product_{instance.pk}/preview/{filename}"


def product_images_directory_path(instance: "Product", filename: str) -> str:
    return f"products/product_{instance.product.pk}/images/{filename}"


class Product(models.Model):
    class Meta:
        ordering: list[str] = ["name", "price"]

    name: models.CharField = models.CharField(max_length=100)
    description: models.TextField = models.TextField(null=False, blank=True)
    price: models.DecimalField = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount: models.SmallIntegerField = models.SmallIntegerField(default=0)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    archived: models.BooleanField = models.BooleanField(default=False)
    created_by: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="products",
        null=False,
        blank=False,
        default=1,
    )
    preview: models.ImageField = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    def __str__(self):
        return f"Product(pk={self.pk}, name={self.name!r})"


class ProductImage(models.Model):
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image: models.ImageField = models.ImageField(upload_to=product_images_directory_path)
    description: models.CharField = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    delivery_address: models.TextField = models.TextField(null=True, blank=True)
    promocode: models.CharField = models.CharField(max_length=20, null=False, blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.PROTECT)
    products: models.ManyToManyField = models.ManyToManyField(Product, related_name="orders")
    receipt: models.FileField = models.FileField(null=True, upload_to='orders/receipts/')
