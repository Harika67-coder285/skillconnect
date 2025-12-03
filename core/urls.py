from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from users.views import (
    register_user, verify_otp,
    home, how_it_works_page, login_user,browse_page,
    dashboard, login_page, register_page, verify_otp_page,logout_user,complete_profile,my_projects,messages,client_requests,edit_profile_picture,settings_page,update_profile
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('register/', register_user, name="register_user"),
path('login/', login_user, name='login_user'),
path("logout/", logout_user, name="logout_user"),

    path('verify-otp/', verify_otp, name="verify_otp"),
    path('browse/', browse_page, name="browse"),
    path('how-it-works/', how_it_works_page, name="how_it_works"),
    path('dashboard/', dashboard, name="dashboard"),
    path('login-page/', login_page, name="login_page"),
    path('register-page/', register_page, name="register_page"),
    path('verify-otp-page/', verify_otp_page, name="verify_otp_page"),
    path('complete-profile/', complete_profile, name='complete_profile'),
    path('my-projects/', my_projects, name='my_projects'),
    path('client-requests/', client_requests, name='client_requests'),
    path("edit-profile-picture/", edit_profile_picture, name="edit_profile_picture"),
    path('settings_page/',settings_page,name="settings_page"),
    path('update_profile/',update_profile,name="update_profile")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
