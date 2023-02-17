from django.urls import path
from account import views

urlpatterns = [
    path('login/',views.login_view, name="login"),
    path('register/',views.register, name="register"),
    path('logout/',views.logout_view, name="logout"),
    path('update-profile/',views.update_profile, name="update_profile")

]
