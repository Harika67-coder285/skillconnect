# users/models.py

from django.db import models

from django.db import models
from django.contrib.auth.hashers import make_password

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
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class FreelancerDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_detail')
    education = models.CharField(max_length=255, blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)
    tech_stack = models.CharField(max_length=255, blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, null=True)


class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"OTP({self.email} - {self.otp})"