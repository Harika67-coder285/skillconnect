import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from .models import Freelancer, Recruiter, OTP,Job,Application
from django.conf import settings
import json
# ---------- Pages ----------
def chatbox(request):
    return render(request,"chatbox.html")
def home(request): return render(request, "index.html")
def browse_page(request): return render(request, "browse.html")
from django.shortcuts import render
from .models import Freelancer

def browse_freelancers(request):
    # Only recruiters should access
    if request.session.get("account_type") != "recruiter":
        return render(request, "unauthorized.html")

    freelancers = Freelancer.objects.filter(is_active=True)

    # ---- Filters from GET params ----
    skill = request.GET.get("skill")
    experience = request.GET.get("experience")
    location = request.GET.get("address")
    min_rate = request.GET.get("min_rate")
    max_rate = request.GET.get("max_rate")

    if skill:
        freelancers = freelancers.filter(skills__icontains=skill)

    if experience:
        freelancers = freelancers.filter(experience_level=experience)

    if location:
        freelancers = freelancers.filter(location__icontains=location)

    if min_rate:
        freelancers = freelancers.filter(hourly_rate__gte=min_rate)

    if max_rate:
        freelancers = freelancers.filter(hourly_rate__lte=max_rate)

    context = {
        "freelancers": freelancers,
    }

    return render(request, "browse.html", context)

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

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Configure your Gemini API key here
genai_client = genai.Client(api_key=GEMINI_API_KEY)

import time
@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"reply": "Please type a message!"})

        bot_reply = "Sorry, something went wrong."
        for attempt in range(3):  # Retry up to 3 times
            try:
                response = genai_client.models.generate_content(
                    model="models/gemini-2.5-flash",  # Free, fast model
                    contents=[user_message]
                )
                bot_reply = response.text
                break  # Success, exit retry loop
            except Exception as e:
                if "503" in str(e):
                    bot_reply = "Bot is busy, retrying..."
                    time.sleep(2)  # wait 2 sec before retry
                    continue
                else:
                    bot_reply = f"Error: {str(e)}"
                    break

        return JsonResponse({"reply": bot_reply})
    
    return JsonResponse({"reply": "Invalid request"}, status=400)
def post_job(request):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter = Recruiter.objects.get(id=request.session["user_id"])

    if request.method == 'POST':
        Job.objects.create(
            recruiter=recruiter,
            title=request.POST['title'],
            description=request.POST['description'],
            skills=request.POST['skills'],
            work_type=request.POST['work_type'],
            duration=request.POST['duration'],
            experience_level=request.POST['experience_level'],
            payment_type=request.POST['payment_type'],
            attachment=request.FILES.get('attachment')
        )
        return redirect('my_jobs')

    return render(request, 'post_job.html')
from django.shortcuts import render, redirect, get_object_or_404
from .models import Application

def recruiter_applications(request, job_id):
    applications = Application.objects.filter(job_id=job_id)

    return render(request, "job_applications.html", {
        "applications": applications
    })


def update_application_status(request, app_id):
    if request.method == "POST":
        application = get_object_or_404(Application, id=app_id)
        new_status = request.POST.get("status")

        application.status = new_status
        application.save()

    return redirect("recruiter_applications", job_id=application.job.id)

def applications(request):
    if request.session.get("account_type") != "recruiter":
        return redirect("home")

    return render(request, "applications.html")

def apply_job(request, job_id):
    if request.session.get("account_type") != "freelancer":
        return redirect("login_page")

    freelancer = Freelancer.objects.get(id=request.session["user_id"])
    job = Job.objects.get(id=job_id)

    JobApplication.objects.create(
        job=job,
        freelancer=freelancer,
        resume=freelancer.resume
    )

    return redirect("browse")
def my_jobs(request):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter = Recruiter.objects.get(id=request.session["user_id"])
    jobs = Job.objects.filter(recruiter=recruiter)

    context = {
        "jobs": jobs,
        "job_count": jobs.count()  # ✅ FIX
    }
    return render(request, "my_jobs.html", context)

def job_applications(request, job_id):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter_id = request.session.get("user_id")
    job = Job.objects.get(id=job_id, recruiter_id=recruiter_id)

    applications = Application.objects.filter(job=job)

    return render(request, "job_applications.html", {"job": job, "applications": applications})

def edit_job(request, job_id):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    job = Job.objects.get(id=job_id)

    if request.method == "POST":
        job.title = request.POST.get("title")
        job.description = request.POST.get("description")
        job.save()
        return redirect("my_jobs")

    return render(request, "edit_job.html", {"job": job})
from django.shortcuts import get_object_or_404

def delete_job(request, job_id):
    # Allow only recruiters
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter_id = request.session.get("user_id")

    # Get job only if it belongs to this recruiter
    job = get_object_or_404(
        Job,
        id=job_id,
        recruiter_id=recruiter_id
    )

    if request.method == "POST":
        job.delete()
        return redirect("my_jobs")

    return render(request, "confirm_delete_job.html", {"job": job})
from django.shortcuts import render
from .models import Freelancer

def search_freelancers(request):
    freelancers = Freelancer.objects.filter(is_active=True)

    skill = request.GET.get('skill')
    experience = request.GET.get('experience')
    location = request.GET.get('location')
    hourly_rate = request.GET.get('hourly_rate')

    if skill:
        freelancers = freelancers.filter(skills__icontains=skill)

    if experience:
        freelancers = freelancers.filter(experience_level=experience)

    if location:
        freelancers = freelancers.filter(location__icontains=location)

    if hourly_rate:
        freelancers = freelancers.filter(hourly_rate__lte=hourly_rate)

    context = {
        'freelancers': freelancers
    }
    return render(request, 'search_freelancers.html', context)

def update_application_status(request, app_id):
    application = Application.objects.get(id=app_id)

    if request.method == 'POST':
        application.status = request.POST['status']
        application.save()

    return redirect('view_applications', job_id=application.job.id)

def interviews(request):
    if request.session.get("account_type") != "recruiter":
        return redirect("home")

    interviews = Interview.objects.select_related(
        "application",
        "application__freelancer",
        "application__job"
    ).all()

    return render(request, "interviews.html", {
        "interviews": interviews
    })

from .models import Interview

def schedule_interview(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.method == "POST":
        Interview.objects.create(
            application=application,
            interview_date=request.POST.get("date"),
            interview_time=request.POST.get("time"),
            mode=request.POST.get("mode")
        )

        application.status = "interview"
        application.save()

        return redirect("recruiter_applications", job_id=application.job.id)

    return render(request, "schedule_interview.html", {
        "application": application
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Freelancer, Contract, Recruiter
from .models import Notification

from .models import Notification

def create_direct_contract(request, freelancer_id):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter = Recruiter.objects.get(id=request.session["user_id"])
    freelancer = Freelancer.objects.get(id=freelancer_id)

    if request.method == "POST":
        contract = Contract.objects.create(
            recruiter=recruiter,
            freelancer=freelancer,
            payment_type=request.POST["payment_type"],
            agreed_amount=request.POST["amount"],
            start_date=request.POST["start_date"],
            status="pending",
            is_active=False
        )

        # 🔔 Notify freelancer
        Notification.objects.create(
            freelancer=freelancer,
            message=f"{recruiter.full_name} sent you a contract offer"
        )

        return redirect("contracts")

    return render(request, "create_direct_contract.html", {"freelancer": freelancer})

def accept_contract(request, contract_id):
    if request.session.get("account_type") != "freelancer":
        return redirect("login_page")

    contract = Contract.objects.get(id=contract_id)
    contract.status = "accepted"
    contract.is_active = True
    contract.save()

    return redirect("freelancer_contracts")


def reject_contract(request, contract_id):
    if request.session.get("account_type") != "freelancer":
        return redirect("login_page")

    contract = Contract.objects.get(id=contract_id)
    contract.status = "rejected"
    contract.is_active = False
    contract.save()

    return redirect("freelancer_contracts")
def recruiter_contracts(request):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter = Recruiter.objects.get(id=request.session["user_id"])
    contracts = Contract.objects.filter(recruiter=recruiter)

    return render(request, "contracts.html", {
        "contracts": contracts
    })

def freelancer_contracts(request):
    if request.session.get("account_type") != "freelancer":
        return redirect("login_page")

    freelancer_id = request.session["user_id"]

    contracts = Contract.objects.filter(freelancer_id=freelancer_id)

    return render(request, "freelancer_contracts.html", {
        "contracts": contracts
    })


def contract_action(request, contract_id):
    if request.session.get("account_type") != "freelancer":
        return redirect("login_page")

    contract = Contract.objects.get(id=contract_id)

    action = request.GET.get("action")

    if action == "accept":
        contract.status = "accepted"
        contract.is_active = True
        contract.save()

    elif action == "reject":
        contract.status = "rejected"
        contract.is_active = False
        contract.save()

    return redirect("freelancer_contracts")

def recruiter_dashboard(request):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter = Recruiter.objects.get(id=request.session["user_id"])

    jobs = Job.objects.filter(recruiter=recruiter)
    applications = Application.objects.filter(job__recruiter=recruiter)

    context = {
        'jobs_count': jobs.count(),
        'applications_count': applications.count(),
        'accepted': applications.filter(status='accepted').count(),
        'pending': applications.exclude(status__in=['accepted','rejected']).count(),
        'rejected': applications.filter(status='rejected').count(),
    }

    return render(request, 'recruiter_dashboard.html', context)

def reports(request):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter = Recruiter.objects.get(id=request.session["recruiter_id"])

    payments = Payment.objects.filter(contract__recruiter=recruiter)

    total_paid = payments.filter(status="paid").aggregate(models.Sum("amount"))["amount__sum"] or 0
    pending = payments.filter(status="pending").aggregate(models.Sum("amount"))["amount__sum"] or 0

    return render(request, "reports.html", {
        "payments": payments,
        "total_paid": total_paid,
        "pending": pending
    })

from django.contrib.auth.decorators import login_required
from .models import Contract

@login_required
def hired_talent(request):
    contracts = Contract.objects.filter(
        recruiter=request.user
    ).select_related('freelancer')

    return render(request, 'hired_talent.html', {
        'contracts': contracts
    })
def analysis(request):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter = Recruiter.objects.get(id=request.session["recruiter_id"])

    jobs = Job.objects.filter(recruiter=recruiter)
    applications = Application.objects.filter(job__recruiter=recruiter)

    return render(request, "analysis.html", {
        "job_count": jobs.count(),
        "proposal_count": applications.count(),
        "accepted": applications.filter(status="accepted").count(),
        "rejected": applications.filter(status="rejected").count(),
        "pending": applications.exclude(status__in=["accepted", "rejected"]).count(),
    })

from django.shortcuts import render
from django.db.models import Count
from .models import Job, Application, Recruiter

def recruiter_analysis(request):
    recruiter = Recruiter.objects.get(email=request.session.get("email"))

    jobs = Job.objects.filter(recruiter=recruiter)

    total_jobs = jobs.count()

    total_proposals = Application.objects.filter(job__in=jobs).count()

    pending_proposals = Application.objects.filter(
        job__in=jobs,
        status__in=['applied', 'shortlisted', 'interview']
    ).count()

    accepted_proposals = Application.objects.filter(
        job__in=jobs,
        status='accepted'
    ).count()

    rejected_proposals = Application.objects.filter(
        job__in=jobs,
        status='rejected'
    ).count()

    context = {
        'total_jobs': total_jobs,
        'total_proposals': total_proposals,
        'pending_proposals': pending_proposals,
        'accepted_proposals': accepted_proposals,
        'rejected_proposals': rejected_proposals,
    }

    return render(request, 'recruiter_analysis.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from .models import Message, Recruiter, Freelancer
from django.db.models import Q


def chat_view(request, recruiter_id=None, freelancer_id=None):
    recruiter = None
    freelancer = None

    if recruiter_id:
        recruiter = get_object_or_404(Recruiter, id=recruiter_id)

    if freelancer_id:
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)

    messages = Message.objects.filter(
        Q(sender_recruiter=recruiter, receiver_freelancer=freelancer) |
        Q(sender_freelancer=freelancer, receiver_recruiter=recruiter)
    ).order_by('created_at')

    if request.method == "POST":
        text = request.POST.get("message")
        file = request.FILES.get("file")

        Message.objects.create(
            sender_recruiter=recruiter,
            sender_freelancer=freelancer,
            receiver_recruiter=recruiter,
            receiver_freelancer=freelancer,
            message=text,
            file=file
        )
        return redirect(request.path)

    return render(request, "chatbot.html", {
        "messages": messages,
        "recruiter": recruiter,
        "freelancer": freelancer
    })
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Payment, Contract


def financial_reports(request, recruiter_id):
    today = timezone.now()
    week_start = today - timedelta(days=7)

    # Weekly summary
    weekly_payments = Payment.objects.filter(
        contract__recruiter_id=recruiter_id,
        paid_on__gte=week_start
    )

    weekly_total_paid = weekly_payments.filter(status='paid').aggregate(
        total=models.Sum('amount')
    )['total'] or 0

    weekly_pending = weekly_payments.filter(status='pending').aggregate(
        total=models.Sum('amount')
    )['total'] or 0

    # Transaction history
    transactions = Payment.objects.filter(
        contract__recruiter_id=recruiter_id
    ).order_by('-paid_on')

    # Overall totals
    total_paid = Payment.objects.filter(
        contract__recruiter_id=recruiter_id,
        status='paid'
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    total_pending = Payment.objects.filter(
        contract__recruiter_id=recruiter_id,
        status='pending'
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    return render(request, "reports.html", {
        "weekly_total_paid": weekly_total_paid,
        "weekly_pending": weekly_pending,
        "transactions": transactions,
        "total_paid": total_paid,
        "total_pending": total_pending
    })
from django.shortcuts import render
from django.db.models import Sum
from .models import Contract, Timesheet


def work_dashboard(request, recruiter_id):
    # Active contracts
    active_contracts = Contract.objects.filter(
        recruiter_id=recruiter_id,
        is_active=True
    )

    # Completed contracts
    completed_contracts = Contract.objects.filter(
        recruiter_id=recruiter_id,
        is_active=False
    )

    return render(request, "work_dashboard.html", {
        "active_contracts": active_contracts,
        "completed_contracts": completed_contracts,
    })

def contracts(request):
    if request.session.get("account_type") != "recruiter":
        return redirect("login_page")

    recruiter = Recruiter.objects.get(id=request.session["user_id"])
    contracts = Contract.objects.filter(recruiter=recruiter)

    return render(request, "contracts.html", {
        "contracts": contracts
    })
def messages(request):
    return render(request, "messages.html")

def contract_timesheets(request, contract_id):
    timesheets = Timesheet.objects.filter(contract_id=contract_id)

    total_hours = timesheets.aggregate(
        total=Sum('hours_worked')
    )['total'] or 0

    return render(request, "timesheets.html", {
        "timesheets": timesheets,
        "total_hours": total_hours
    })
from .models import Message

def chat(request, recruiter_id, freelancer_id):
    messages = Message.objects.filter(
        sender_recruiter_id=recruiter_id,
        receiver_freelancer_id=freelancer_id
    ) | Message.objects.filter(
        sender_freelancer_id=freelancer_id,
        receiver_recruiter_id=recruiter_id
    )

    messages = messages.order_by("created_at")

    if request.method == "POST":
        Message.objects.create(
            sender_recruiter_id=recruiter_id,
            receiver_freelancer_id=freelancer_id,
            message=request.POST.get("message"),
            file=request.FILES.get("file")
        )
        return redirect("chat", recruiter_id=recruiter_id, freelancer_id=freelancer_id)

    return render(request, "chat.html", {
        "messages": messages
    })
from .models import Contract, Freelancer

def freelancer_notifications(request):
    if request.session.get("account_type") == "freelancer":
        freelancer_id = request.session.get("user_id")
        count = Contract.objects.filter(
            freelancer_id=freelancer_id,
            status="pending"
        ).count()
        return {"pending_contracts_count": count}

    return {"pending_contracts_count": 0}
