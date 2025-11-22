from django.contrib import admin
from django.urls import path
from users.views import register_user, login_user, send_otp, verify_otp, home,how_it_works_page,browse_page,dashboard_page,login_page,register_page,verify_otp_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),  # ROOT URL
    path('register/', register_user),
    path('login/', login_user),
    path('send-otp/', send_otp),
    path('verify-otp/', verify_otp),
    path("", home, name="home"),
path("browse/", browse_page, name="browse"),
path("how-it-works/", how_it_works_page, name="how_it_works"),
path("dashboard/", dashboard_page, name="dashboard"),
path("login-page/", login_page, name="login_page"),
path("register-page/", register_page, name="register_page"),
path("verify-otp-page/", verify_otp_page, name="verify_otp_page"),
]
