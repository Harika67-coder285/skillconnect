from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from users.views import (
    register_user, verify_otp,
    home, how_it_works_page, login_user,browse_page,
    dashboard, login_page, register_page, verify_otp_page,logout_user,complete_profile,my_projects,messages,client_requests,edit_profile_picture,settings_page,update_profile,chatbox,chatbot, post_job,
    recruiter_applications,
    update_application_status,
    apply_job,my_jobs,job_applications,edit_job,delete_job,search_freelancers,hired_talent,create_direct_contract,recruiter_analysis,chat_view,financial_reports,work_dashboard,contract_timesheets,schedule_interview,chat,applications,interviews,contracts,reports,analysis,browse_freelancers,freelancer_contracts,contract_action
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('register/', register_user, name="register_user"),
path('login/', login_user, name='login_user'),
path("logout/", logout_user, name="logout_user"),
path("interviews/", interviews, name="interviews"),
    # Messages
    path("messages/", messages, name="messages"),

    # Contracts / Work
    path("contracts/", contracts, name="contracts"),

    # Reports
    path("reports/", reports, name="reports"),

    # Analysis
    path("analysis/", analysis, name="analysis"),
    path('verify-otp/', verify_otp, name="verify_otp"),
    path('browse/', browse_freelancers, name="browse"),
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
    path('update_profile/',update_profile,name="update_profile"),
    path("chat-box/",chatbox,name='chat-box'),
    path("chatbot/", chatbot, name="chatbot"),
    path("post-job/", post_job, name="post_job"),
     path("applications/", applications, name="applications"),
    path("applications/<int:job_id>/", recruiter_applications, name="recruiter_applications"),
path("application/update/<int:app_id>/", update_application_status, name="update_application_status"),

path("apply-job/<int:job_id>/", apply_job, name="apply_job"),
path("my-jobs/", my_jobs, name="my_jobs"),
path(
    "job/<int:job_id>/applications/",
    job_applications,
    name="job_applications"
),
path(
    "edit-job/<int:job_id>/",
    edit_job,
    name="edit_job"
),
path(
    "delete-job/<int:job_id>/",
    delete_job,
    name="delete_job"
),

 path(
        "chat/<int:recruiter_id>/<int:freelancer_id>/",
        chat_view,
        name="chat"
    ),
path('search-freelancers/', search_freelancers, name='search_freelancers'),
path('hired-talent/', hired_talent, name='hired_talent'),
path('direct-contract/<int:freelancer_id>/', create_direct_contract, name='direct_contract'),
path('recruiter/analysis/', recruiter_analysis, name='recruiter_analysis'),
path("freelancer/contracts/", freelancer_contracts, name="freelancer_contracts"),
path(
    "contract-action/<int:contract_id>/",
contract_action,
    name="contract_action"
),

path(
        "reports/<int:recruiter_id>/",
        financial_reports,
        name="financial_reports"
    ),
     path(
        "work/<int:recruiter_id>/",
       work_dashboard,
        name="work_dashboard"
    ),
    path(
        "timesheets/<int:contract_id>/",
 contract_timesheets,
        name="contract_timesheets"
    ),
    path("interview/schedule/<int:application_id>/", schedule_interview, name="schedule_interview"),
path("chat/<int:recruiter_id>/<int:freelancer_id>/", chat, name="chat"),
path("contracts/", contracts, name="contracts"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
