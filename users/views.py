# users/views.py

import random
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from .models import User, OTP
from django.utils import timezone
import json
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render



temp_storage = {}  



def home(request):
    return render(request, "index.html")  # Make sure index.html is in templates folder
def browse_page(request):
    return render(request, "browse.html")

def how_it_works_page(request):
    return render(request, "howitworks.html")

def dashboard_page(request):
    return render(request, "dashboard.html")
def login_page(request):
    return render(request, "login.html")

def register_page(request):
    return render(request, "signup.html")

def verify_otp_page(request):
    return render(request,"verify_otp.html")

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
import json, random
from .models import User, FreelancerDetail

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")
        accountType = data.get("accountType")
        education = data.get("education", "")
        experience = data.get("experience", 0)
        techStack = data.get("techStack", "")
        skills = data.get("skills", "")

        if not email or not password or not full_name or not accountType:
            return JsonResponse({"status": "error", "message": "Missing required fields"})

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Email already registered"})

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Create user with is_verified=False
        user = User.objects.create(
            full_name=full_name,
            email=email,
            password=password,  # will be hashed in model save()
            account_type=accountType,
            otp=otp,
            is_verified=False
        )

        # If freelancer, create FreelancerDetail
        if accountType == "freelancer":
            FreelancerDetail.objects.create(
                user=user,
                education=education,
                experience=experience,
                tech_stack=techStack,
                skills=skills
            )

        # Save pending email in session
        request.session["pending_email"] = email

        # Send OTP email
        send_mail(
            "Your OTP for SkillConnect",
            f"Your OTP is: {otp}",
            "projectsinfo697@gmail.com",
            [email],
        )

        return JsonResponse({"status": "success", "message": "OTP sent"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        otp = data.get("otp")
        email = request.session.get("pending_email")

        if not email or not otp:
            return JsonResponse({"status": "error", "message": "Missing email or OTP"})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User not found"})

        if user.otp == otp:
            user.is_verified = True
            user.otp = ""  # clear OTP after verification
            user.save()

            # Clear session
            del request.session["pending_email"]

            return JsonResponse({"status": "success", "message": "OTP verified, signup complete"})

        return JsonResponse({"status": "error", "message": "Invalid OTP"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def register_user(request):
    """
    POST expected fields:
    full_name, email, password, account_type
    optional freelancer fields: education, experience, tech_stack, skills
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "msg": "Only POST allowed"}, status=405)

    data = request.POST or request.body
    # If you send JSON from frontend, parse JSON:
    if request.content_type == "application/json":
        import json
        body = json.loads(request.body.decode())
        full_name = body.get("full_name")
        email = body.get("email")
        password = body.get("password")
        account_type = body.get("account_type")
        education = body.get("education", "")
        experience = body.get("experience", None)
        tech_stack = body.get("tech_stack", "")
        skills = body.get("skills", "")
    else:
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        account_type = request.POST.get("account_type")
        education = request.POST.get("education", "")
        experience = request.POST.get("experience", None)
        tech_stack = request.POST.get("tech_stack", "")
        skills = request.POST.get("skills", "")

    if not (full_name and email and password and account_type):
        return JsonResponse({"status": "error", "msg": "Missing required fields"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"status": "error", "msg": "Email already exists"}, status=400)

    # hash password
    hashed = make_password(password)

    user = User.objects.create(
        full_name=full_name,
        email=email,
        password=hashed,
        account_type=account_type,
        is_verified=False
    )

    # If freelancer, save profile
    if account_type == "freelancer":
        FreelancerProfile.objects.create(
            user=user,
            education=education,
            experience=experience if experience != "" else None,
            tech_stack=tech_stack,
            skills=skills
        )

    # send OTP
    try:
        send_otp_email(email)
    except Exception as e:
        # If email sending fails, keep user but notify frontend
        return JsonResponse({"status": "error", "msg": f"Failed to send OTP: {str(e)}"}, status=500)

    return JsonResponse({"status": "success", "msg": "OTP sent", "email": email})

@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        email = data.get("email")
        password = data.get("password")
        account_type = data.get("accountType")

        # Check required fields
        if not email or not password or not account_type:
            return JsonResponse({"status": "error", "message": "All fields are required"})

        try:
            # Check if user exists with given email and account type
            user = User.objects.get(email=email, account_type=account_type)
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User does not exist"})

        # Verify password using Django's check_password
        if not check_password(password, user.password):
            return JsonResponse({"status": "error", "message": "Incorrect password"})

        # Return success with user info
        return JsonResponse({
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "account_type": user.account_type
            }
        })

    # If not POST request
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
