from .views import predict_view, logout_view
from django.urls import path
from . import views

urlpatterns = [
    path("predict/", predict_view, name="predict"),
    path("logout/", logout_view, name="logout"),
    path("login/", views.login_page, name="login"),
    path("api/auth/login/", views.google_login, name="google_login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("test/", views.test_page),


]