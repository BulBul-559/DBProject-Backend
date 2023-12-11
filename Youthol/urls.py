from django.urls import path

from . import views

urlpatterns = [
    path("SignIn/", views.SignIn),
    path("SignUp/", views.SignUp),
    path("getUserInfo/", views.GetUserInfo),
]