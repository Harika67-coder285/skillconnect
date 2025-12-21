from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
class User(models.Model):
    ACCOUNT_TYPES = (
        ('freelancer', 'Freelancer'),
        ('recruiter', 'Recruiter'),
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

# models.py
from django.db import models
from django.db import models

class Freelancer(models.Model):
    # Basic Info
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    # Freelancer Details
    experience_level = models.CharField(
        max_length=20,
        choices=[('fresher', 'Fresher'), ('experienced', 'Experienced'), ('expert', 'Expert')],
        blank=True,
        null=True
    )
    resume = models.FileField(upload_to='freelancer_resumes/', blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    tech_stack = models.CharField(max_length=255, blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, null=True)

    # 🔥 REQUIRED FOR SEARCH BY LOCATION
    location = models.CharField(max_length=100, blank=True, null=True)

    # Personal Info
    dob = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='freelancer_photos/', blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

class Recruiter(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

class OTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
class Job(models.Model):

    # ---------------- CHOICES ---------------- #

    WORK_TYPE_CHOICES = (
        ('short', 'Short-term'),
        ('long', 'Long-term'),
    )

    EXPERIENCE_CHOICES = (
        ('fresher', 'Fresher'),
        ('experienced', 'Experienced'),
    )

    PAYMENT_CHOICES = (
        ('hourly', 'Hourly Rate'),
        ('fixed', 'Fixed Price'),
    )

    DURATION_TYPE_CHOICES = (
        ('monthly', 'Month-wise'),
        ('fixed', 'Fixed Timeline'),
    )

    # ---------------- RELATION ---------------- #

    recruiter = models.ForeignKey(
        Recruiter,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    # ---------------- BASIC INFO ---------------- #

    title = models.CharField(max_length=200)
    description = models.TextField()

    # ---------------- JOB DETAILS ---------------- #

    skills = models.CharField(
        max_length=255,
        help_text="Comma separated skills (React, Python, SQL)",
        default=""
    )

    work_type = models.CharField(
        max_length=20,
        choices=WORK_TYPE_CHOICES,
        default='short'
    )

    duration_type = models.CharField(
        max_length=20,
        choices=DURATION_TYPE_CHOICES,
        default='fixed'
    )

    duration = models.CharField(
        max_length=50,
        help_text="Example: 3 months / 6 months",
        default="1 month"
    )

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='fresher'
    )

    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='fixed'
    )

    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # ---------------- SUPPORTING DOCUMENT ---------------- #

    attachment = models.FileField(
        upload_to="job_documents/",
        null=True,
        blank=True
    )

    # ---------------- STATUS ---------------- #

    is_active = models.BooleanField(default=True)

    # ---------------- TIMESTAMP ---------------- #

    created_at = models.DateTimeField(auto_now_add=True)

    # ---------------- STRING ---------------- #

    def __str__(self):
        return f"{self.title} ({self.recruiter.full_name})"

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="job_applications/")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.freelancer.full_name} → {self.job.title}"
class Application(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    freelancer = models.ForeignKey('Freelancer', on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )

    def __str__(self):
        return f"{self.freelancer.full_name} -> {self.job.title}"

class Contract(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    agreed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20)

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('completed', 'Completed'),
        ],
        default='pending'
    )

    is_active = models.BooleanField(default=False)

class Timesheet(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
class Interview(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    interview_date = models.DateField()
    interview_time = models.TimeField()
    mode = models.CharField(max_length=50, choices=[
        ('call','Call'),
        ('video','Video'),
        ('in_person','In Person')
    ])
class Message(models.Model):
    sender_recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, null=True, blank=True)
    sender_freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, null=True, blank=True)
    receiver_recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, related_name='received_recruiter', null=True, blank=True)
    receiver_freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='received_freelancer', null=True, blank=True)

    message = models.TextField()
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
class Payment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('paid','Paid'),
        ('pending','Pending')
    ])
class Notification(models.Model):
    freelancer = models.ForeignKey(
        Freelancer,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.freelancer.full_name}"
