import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from .models import Freelancer, Recruiter, OTP
from django.conf import settings
import json
# ---------- Pages ----------
def home(request): return render(request, "index.html")
def browse_page(request): return render(request, "browse.html")
def how_it_works_page(request): return render(request, "howitworks.html")
from django.shortcuts import render, redirect
from .models import Freelancer, Recruiter

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import Freelancer, Recruiter


def dashboard(request):
    user_id = request.session.get("user_id")
    account_type = request.session.get("account_type")

    if not user_id or not account_type:
        return redirect("login_page")

    # Fetch user
    if account_type == "freelancer":
        user = Freelancer.objects.get(id=user_id)
    else:
        user = Recruiter.objects.get(id=user_id)
    return render(request, "dashboard.html", {"app_user": user})


def login_page(request): return render(request, "login.html")
def register_page(request): return render(request, "signup.html")

def verify_otp_page(request):
    email = request.GET.get("email")
    if not email:
        return redirect('register_page')
    return render(request, "verify_otp.html", {"email": email})

# ---------- Register User ----------





# ---------- Verify OTP ----------
@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        entered_otp = request.POST.get("otp")

        if not email or not entered_otp:
            return JsonResponse({"status": "error", "message": "Email and OTP are required."})

        otp_record = OTP.objects.filter(email=email).order_by('-created_at').first()
        if not otp_record:
            return JsonResponse({"status": "error", "message": "No OTP found for this email."})

        if timezone.now() > otp_record.created_at + timedelta(minutes=10):
            otp_record.delete()
            return JsonResponse({"status": "error", "message": "OTP expired. Please signup again."})

        if str(otp_record.code) != str(entered_otp):
            return JsonResponse({"status": "error", "message": "Incorrect OTP."})

        # Activate user
        if Freelancer.objects.filter(email=email).exists():
            user = Freelancer.objects.get(email=email)
            user.is_active = False
            user.save()
        elif Recruiter.objects.filter(email=email).exists():
            user = Recruiter.objects.get(email=email)
            user.is_active = False
            user.save()

        otp_record.delete()
        return JsonResponse({"status": "success", "message": "OTP verified. Redirecting to login..."})

    return JsonResponse({"status": "error", "message": "Invalid request."})



from django.core.mail import send_mail
import random

# ---------- Register User ----------

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .models import Freelancer, Recruiter, OTP
from django.core.mail import send_mail
import random
import pdfplumber
import re
from django.http import JsonResponse


@csrf_exempt
def register_user(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        account_type = request.POST.get("account_type")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Freelancer-specific fields
        experience_level = request.POST.get("experience_level")
        resume = request.FILES.get("resume")
        linkedin = request.POST.get("linkedin")
        hourly_rate = request.POST.get("hourly_rate")
        education = request.POST.get("education")
        tech_stack = request.POST.get("tech_stack")
        skills = request.POST.get("skills")
        dob = request.POST.get("dob")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        photo = request.FILES.get("photo")

        # Basic validation
        if not all([account_type, full_name, email, password]):
            return JsonResponse({"status": "error", "message": "Please fill all required fields."})

        if Freelancer.objects.filter(email=email).exists() or Recruiter.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "User with this email already exists."})

        try:
            hashed_password = make_password(password)

            if account_type == "freelancer":
                # Optional: calculate service fee if you want
                SERVICE_FEE_PERCENT = 10
                expected_hourly_rate = float(hourly_rate) if hourly_rate else 0
                service_fee = expected_hourly_rate * SERVICE_FEE_PERCENT / 100
                net_hourly_rate = expected_hourly_rate - service_fee

                user = Freelancer.objects.create(
                    full_name=full_name,
                    email=email,
                    password=hashed_password,
                    experience_level=experience_level,
                    resume=resume,
                    linkedin=linkedin,
                    hourly_rate=hourly_rate if hourly_rate else None,
                    education=education,
                    tech_stack=tech_stack,
                    skills=skills,
                    dob=dob if dob else None,
                    phone=phone,
                    address=address,
                    photo=photo,
                    is_active=False
                )

            elif account_type == "recruiter":
                user = Recruiter.objects.create(
                    full_name=full_name,
                    email=email,
                    password=hashed_password,
                    is_active=False
                )
            else:
                return JsonResponse({"status": "error", "message": "Invalid account type."})

            # Generate OTP
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(email=email, code=otp_code)

            # Send OTP email
            send_mail(
                subject="SkillConnect OTP Verification",
                message=f"Hello {full_name},\nYour OTP for SkillConnect signup is: {otp_code}",
                from_email="noreply@skillconnect.com",
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request."})

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import Freelancer, Recruiter

from django.shortcuts import redirect

def logout_user(request):
    request.session.flush()   # clears all session data
    return redirect('login_page')
from django.shortcuts import render, redirect
from .models import Freelancer
from django.core.files.storage import FileSystemStorage


# ---------------- Login ----------------
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import Freelancer, Recruiter

def login_user(request):
    if request.method == "GET":
        return render(request, "login.html")  # Show login page

    # POST
    account_type = request.POST.get("accountType")
    email = request.POST.get("email")
    password = request.POST.get("password")

    if not all([account_type, email, password]):
        return render(request, "login.html", {"error": "Fill all fields."})

    try:
        # Fetch user based on account type
        if account_type == "freelancer":
            user = Freelancer.objects.get(email=email)
        elif account_type == "recruiter":
            user = Recruiter.objects.get(email=email)
        else:
            return render(request, "login.html", {"error": "Invalid account type."})

        # Check password
        if not check_password(password, user.password):
            return render(request, "login.html", {"error": "Invalid email or password."})

        # Set session
        request.session['user_id'] = user.id
        request.session['user_name'] = getattr(user, 'full_name', '')
        request.session['account_type'] = account_type

        if account_type == "freelancer" and not user.is_active:
            return redirect("complete_profile")  # freelancer profile incomplete
        return redirect("dashboard")  # recruiter or freelancer completed profile

    except (Freelancer.DoesNotExist, Recruiter.DoesNotExist):
        return render(request, "login.html", {"error": "Invalid email or password."})


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Freelancer

def complete_profile(request):
    """
    Only for freelancers whose profile is incomplete (is_active=False)
    """
    user_id = request.session.get("user_id")
    account_type = request.session.get("account_type")

    if not user_id or account_type != "freelancer":
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "message": "Unauthorized. Please login."})
        return redirect("login_page")

    user = Freelancer.objects.get(id=user_id)

    if request.method == "POST":
        try:
            # Get form data
            user.experience_level = request.POST.get("experience_level")
            user.resume = request.FILES.get("resume") or user.resume
            user.tech_stack = request.POST.get("tech_stack")
            user.skills = request.POST.get("skills")
            user.education = request.POST.get("education")
            user.hourly_rate = request.POST.get("hourly_rate")
            user.linkedin = request.POST.get("linkedin")
            user.dob = request.POST.get("dob")
            user.phone = request.POST.get("phone")
            user.address = request.POST.get("address")
            user.photo = request.FILES.get("photo") or user.photo

            user.is_active = True  # mark profile as complete
            user.save()

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"status": "success", "message": "Profile updated successfully!"})
            else:
                return redirect("dashboard")

        except Exception as e:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": str(e)})
            else:
                return render(request, "complete_profile.html", {"user": user, "error": str(e)})

    return render(request, "complete-profile.html", {"user": user})
from django.shortcuts import render, redirect
from .models import Freelancer, Recruiter

def edit_profile(request):
    user_id = request.session.get("user_id")
    account_type = request.session.get("account_type")

    if not user_id or not account_type:
        return redirect("login_page")

    # Get the user object
    if account_type == "freelancer":
        user = Freelancer.objects.get(id=user_id)
    else:
        user = Recruiter.objects.get(id=user_id)

    if request.method == "POST":
        # Update fields from form submission
        user.full_name = request.POST.get("full_name", user.full_name)
        user.email = request.POST.get("email", user.email)
        if account_type == "freelancer":
            user.experience_level = request.POST.get("experience_level", user.experience_level)
            user.hourly_rate = request.POST.get("hourly_rate", user.hourly_rate)
            user.education = request.POST.get("education", user.education)
            user.tech_stack = request.POST.get("tech_stack", user.tech_stack)
            user.skills = request.POST.get("skills", user.skills)
            user.linkedin = request.POST.get("linkedin", user.linkedin)
            if "photo" in request.FILES:
                user.photo = request.FILES["photo"]
            if "resume" in request.FILES:
                user.resume = request.FILES["resume"]

        # Save changes
        user.save()
        return redirect("dashboard")

    return render(request, "edit_profile.html", {"app_user": user, "account_type": account_type})
# users/views.py
from django.shortcuts import render

def my_projects(request):
    return render(request, "my_projects.html")

def client_requests(request):
    return render(request, "client_requests.html")

def messages(request):
    return render(request, "messages.html")
def settings_page(request):
    return render(request, "settings_page.html")
# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Freelancer, Recruiter

def edit_profile_picture(request):
    user_id = request.session.get("user_id")
    account_type = request.session.get("account_type")

    if not user_id or not account_type:
        return redirect("login_page")

    # Get user object
    user = Freelancer.objects.get(id=user_id) if account_type == "freelancer" else Recruiter.objects.get(id=user_id)

    if request.method == "POST" and "photo" in request.FILES:
        user.photo = request.FILES["photo"]
        user.save()
        return redirect("dashboard")
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import User  # Assuming your user model is named User

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from .models import Freelancer  # import your freelancer model

def update_profile(request):
    freelancer_id = request.session.get('user_id')  # session key storing logged-in freelancer ID
    if not freelancer_id:
        # Not logged in
        return redirect(f"{reverse('login_page')}?next={request.path}")

    # Get the freelancer object
    try:
        freelancer = Freelancer.objects.get(id=freelancer_id)
    except Freelancer.DoesNotExist:
        return redirect(f"{reverse('login_page')}?next={request.path}")

    if request.method == "POST":
        # Update profile fields
        freelancer.full_name = request.POST.get("full_name", freelancer.full_name)
        freelancer.email = request.POST.get("email", freelancer.email)
        freelancer.experience_level = request.POST.get("experience_level", freelancer.experience_level)
        freelancer.hourly_rate = request.POST.get("hourly_rate", freelancer.hourly_rate)
        freelancer.tech_stack = request.POST.get("tech_stack", freelancer.tech_stack)
        freelancer.skills = request.POST.get("skills", freelancer.skills)
        freelancer.linkedin = request.POST.get("linkedin", freelancer.linkedin)

        # Update profile picture
        if "photo" in request.FILES:
            freelancer.photo = request.FILES["photo"]

        # Update resume
        if "resume" in request.FILES:
            freelancer.resume = request.FILES["resume"]

        # Update password if provided
        password = request.POST.get("password")
        if password:
            freelancer.password = make_password(password)

        freelancer.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("settings_page")

    return render(request, "settings_page.html", {"app_user": freelancer})
