from timeit import default_timer
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import GroupForm, ProductForm
from .models import Product, Order, ProductImage


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products: list[tuple[str, int]] = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context: dict[str, str | int] = {
            "time_running": default_timer(),
            "products": products,
            "items": 2,
        }
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context: dict = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form: GroupForm = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name: str = "shopapp/product-details.html"
    # model = Product
    queryset: str = Product.objects.prefetch_related("images")
    context_object_name: str = "product"


class ProductsListView(ListView):
    template_name: str = 'shopapp/products-list.html'
    queryset = Product.objects.filter(archived=False)
    context_object_name: str = "products"


class ProductCreateView(LoginRequiredMixin, CreateView, UserPassesTestMixin):
    def test_func(self):
        # return self.request.user.groups.filter(name="secret-group").exists()
        return self.request.user.is_superuser

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    model: Product = Product
    # fields = "name", "price", "description", "discount", "preview"
    form_class: ProductForm = ProductForm
    success_url: str = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UpdateView):
    model: Product = Product
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix: str = "_update_form"
    form_class: ProductForm = ProductForm

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model: Product = Product
    success_url: str = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url: str = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset: tuple[Order] = (Order.objects
                .select_related("user")
                .prefetch_related("products")
                )


class OrderDetailView(DetailView, PermissionRequiredMixin):
    permission_required: str = "shopapp.view_order"
    queryset: tuple[Order] = (Order.objects
                .select_related("user")
                .prefetch_related("products")
                )


class OrderUpdateView(UpdateView):
    model: Order = Order
    fields: tuple[str] = 'delivery_address', 'promocode', 'user', 'products'
    template_name_suffix: str = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model: Order = Order
    success_url: str = reverse_lazy("shopapp:orders_list")

    def form_valid(self, form):
        success_url: str = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class CreateOrderView(CreateView):
    model: Order = Order
    fields: tuple[str] = 'delivery_address', 'promocode', 'user', 'products'
    success_url: str = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products: list = Product.objects.order_by("pk").all()
        products_data: list[dict[str, str]] = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
                "preview": product.preview,
            }
            for product in products
        ]
        return JsonResponse({"products": products_data})
