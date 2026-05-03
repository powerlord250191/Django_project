import os.path
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.contrib.messages.context_processors import messages
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.utils.translation import gettext_lazy, ngettext

from .models import Profile
from .forms import UserProfileForm, ProfileForm, AvatarForm


class HelloView(View):
    welcome_message = gettext_lazy("Welcome hello world!")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str: str | int = request.GET.get("items") or 0
        items: int = int(items_str)
        products_line: ngettext = ngettext(
            "one products",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
        )


class AboutmeView(TemplateView):
    template_name: str = "myauth/about-me.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        context['user_profile']: dict[str] = self.request.user
        context['profile']: dict[str] = profile
        context['avatar_form']: dict[str] = AvatarForm(instance=profile)
        context['profile_form']: dict[str] = ProfileForm(instance=profile)
        context['user_form']: dict[str] = UserProfileForm(instance=self.request.user)
        return context


class UsersListview(LoginRequiredMixin, ListView):
    model: User = User
    template_name: str = "myauth/users-list.html"
    context_object_name: str = "users"
    paginate_by: int = 20

    def get_queryset(self):
        queryset: str = User.objects.all().select_related('profile')

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        return queryset.order_by('username')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", '')
        return context


class UserDetailView(LoginRequiredMixin, DetailView):
    model: User = User
    template_name: str = "myauth/user-detail.html"
    context_object_name: str = "target_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = Profile.objects.get_or_create(user=self.object)
        context["profile"] = profile
        context["can_edit"] = (
                self.request.user == self.object or
                self.request.user.is_staff or
                self.request.user.is_superuser
        )
        return context


class UserAvatarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model: Profile = Profile
    form_class: AvatarForm = AvatarForm
    http_method_names: list[str] = ["post"]

    def test_func(self):
        profile = self.get_object()
        return (
                self.request.user.is_staff or
                self.request.user.is_superuser or
                self.request.user == profile.user
        )

    def get_object(self, queryset=None):
        user_id: int = self.kwargs.get("user_id")
        user: User|None = get_object_or_404(User, id=user_id)
        profile, created = Profile.objects.get_or_create(user=user)
        return profile

    def form_valid(self, form):
        profile = self.get_object()
        if profile.avatar:
            try:
                if os.path.isfile(profile.avatar.path):
                    os.remove(profile.avatar.path)
            except:
                pass

        profile.avatar = form.cleaned_data["avatar"]
        profile.save()

        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "avatar_url": profile.avatar.url if profile.avatar else "/static/profile_avatar/—Pngtree—character default avatar_5407167.png",
                "message": "Аватар успешно обновлён"
            })
        return redirect(redirect("myauth:user-detail", pk=profile.user.id))

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': "Ошибка при загрузке аватара"
            }, status=400)

        return redirect('myauth:user-detail', pk=self.get_object().user.id)


class UserAvatarDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        user: User|None = get_object_or_404(User, id=self.kwargs.get('user_id'))
        profile, created = Profile.objects.get_or_create(user=user)
        return (
                self.request.user.is_staff or
                self.request.user.is_superuser or
                self.request.user == user
        )

    def post(self, request, user_id):
        user: User|None = get_object_or_404(User, id=user_id)
        profile, created = Profile.objects.get_or_create(user=user)

        if profile.avatar:
            try:
                if os.path.isfile(profile.avatar.path):
                    os.remove(profile.avatar.path)
            except:
                pass
            profile.avatar = None
            profile.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'messages': 'Аватар удалён',
            })

        return redirect('myauth: user-detail', pk=user.id)


class RegisterView(CreateView):
    form_class: UserCreationForm = UserCreationForm
    template_name: str = "myauth/register.html"
    success_url: str = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)

        Profile.objects.create(user=self.object)

        username: str = form.cleaned_data.get("username")
        password: str = form.cleaned_data.get("password1")

        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model: Profile = Profile
    form_class: ProfileForm = ProfileForm
    template_name: str = "myauth/edit-profile.html"

    def get_object(self, queryset=None):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_success_url(self):
        return reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлён!")
        return super().form_valid(form)


class UpdateAvatarView(LoginRequiredMixin, View):

    def post(self, request):
        profile: Profile|None = get_object_or_404(Profile, user=request.user)

        if "avatar" in request.FILES:
            if profile.avatar:
                if os.path.isfile(profile.avatar.path):
                    os.remove(profile.avatar.path)

            profile.avatar = request.FILES['avatar']
            profile.save()

            return JsonResponse(
                {
                    "success": True,
                    "avatar_url": profile.avatar.url,
                    "message": "Аватар успешно обновлён"
                },
            )
        return JsonResponse(
            {
                "success": False,
                "message": "Файл не загружен",
            }, status=400
        )


class DeleteAvatarView(LoginRequiredMixin, View):

    def post(self, request):
        profile: Profile|None = get_object_or_404(Profile, user=request.user)

        if profile.avatar:
            if os.path.isfile(profile.avatar.path):
                os.remove(profile.avatar.path)
            profile.avatar = None
            profile.save()

            return JsonResponse({
                "success": True,
                "message": "Аватар удален",
            })

        return JsonResponse({
            "success": False,
            "message": "Аватар не найден",
        }, status=404)


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin")
        return render(request, "myauth/login.html")

    username: str = request.POST["username"]
    password: str = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/admin/")
    return render(request, "myauth/login.html", {"error": "Invalid login credentials"})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
