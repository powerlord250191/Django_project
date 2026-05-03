from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    get_cookie_view,
    set_cookie_view,
    set_session_view,
    get_session_view,
    logout_view,
    AboutmeView,
    UpdateAvatarView,
    UpdateProfileView,
    DeleteAvatarView,
    UsersListview,
    RegisterView,
    FooBarView,
    UserDetailView,
    UserAvatarUpdateView,
    UserAvatarDeleteView,
    HelloView,
)

app_name: str = "myauth"

urlpatterns: list[path] = [
    # path("login/", login_view, name="login"),
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login"
    ),
    path("logout/", logout_view, name="logout"),
    path("hello/", HelloView.as_view(), name="hello"),
    # path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutmeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),
    path('edit-profile/', UpdateProfileView.as_view(), name='edit-profile'),
    path('update-avatar/', UpdateAvatarView.as_view(), name='update-avatar'),
    path('delete-avatar/', DeleteAvatarView.as_view(), name='delete-avatar'),
    path('users/', UsersListview.as_view(), name='users-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/update-avatar', UserAvatarUpdateView.as_view(), name='user-update-avatar'),
    path('users/<int:user_id>/delete-avatar', UserAvatarDeleteView.as_view(), name='user-delete-avatar'),

    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),

    path("session/set/", set_session_view, name="session-set"),
    path("session/get/", get_session_view, name="session-get"),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),

]
