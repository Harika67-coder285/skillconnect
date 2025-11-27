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

def dashboard(request):
    user_id = request.session.get("user_id")
    account_type = request.session.get("account_type")

    if not user_id or not account_type:
        return redirect("login_page")

    # fetch user
    if account_type == "freelancer":
        user = Freelancer.objects.get(id=user_id)
    else:
        user = Recruiter.objects.get(id=user_id)

    return render(request, "dashboard.html", {"user": user})

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
            user.is_active = True
            user.save()
        elif Recruiter.objects.filter(email=email).exists():
            user = Recruiter.objects.get(email=email)
            user.is_active = True
            user.save()

        otp_record.delete()
        return JsonResponse({"status": "success", "message": "OTP verified. Redirecting to login..."})

    return JsonResponse({"status": "error", "message": "Invalid request."})



from django.core.mail import send_mail
import random

# ---------- Register User ----------
@csrf_exempt
def register_user(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        account_type = request.POST.get("account_type")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        education = request.POST.get("education")
        experience = request.POST.get("experience")
        tech_stack = request.POST.get("tech_stack")
        skills = request.POST.get("skills")

        if not all([account_type, full_name, email, password]):
            return JsonResponse({"status": "error", "message": "Please fill all required fields."})

        # Check if user exists
        if Freelancer.objects.filter(email=email).exists() or Recruiter.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "User with this email already exists."})

        try:
            hashed_password = make_password(password)

            if account_type == "freelancer":
                user = Freelancer.objects.create(
                    full_name=full_name,
                    email=email,
                    password=hashed_password,
                    education=education,
                    experience=int(experience) if experience else 0,
                    tech_stack=tech_stack,
                    skills=skills,
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

            # Send OTP via email
            send_mail(
                subject="SkillConnect OTP Verification",
                message=f"Hello {full_name},\nYour OTP for SkillConnect signup is: {otp_code}",
                from_email="noreply@skillconnect.com",  # Replace with your email if needed
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

def login_user(request):
    if request.method == "GET":
        return render(request, "login.html")  # ensures CSRF cookie

    # POST
    account_type = request.POST.get("accountType")
    email = request.POST.get("email")
    password = request.POST.get("password")

    if not all([account_type, email, password]):
        return render(request, "login.html", {"error": "Fill all fields."})

    try:
        if account_type == "freelancer":
            user = Freelancer.objects.get(email=email)
        elif account_type == "recruiter":
            user = Recruiter.objects.get(email=email)
        else:
            return render(request, "login.html", {"error": "Invalid account type."})

        if not user.is_active:
            return render(request, "login.html", {"error": "Account not verified. Check email."})

        if check_password(password, user.password):
            # set session so dashboard can check
            request.session['user_id'] = user.id
            request.session['user_name'] = user.full_name
            request.session['account_type'] = account_type
            return redirect('dashboard')

        else:
            return render(request, "login.html", {"error": "Invalid email or password."})

    except (Freelancer.DoesNotExist, Recruiter.DoesNotExist):
        return render(request, "login.html", {"error": "Invalid email or password."})
from django.shortcuts import redirect

def logout_user(request):
    request.session.flush()   # clears all session data
    return redirect('login_page')
