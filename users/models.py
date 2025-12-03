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


