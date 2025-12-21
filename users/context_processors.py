from users.models import Freelancer, Recruiter

def app_user(request):
    user_id = request.session.get("user_id")
    account_type = request.session.get("account_type")

    if not user_id or not account_type:
        return {"app_user": None}

    try:
        if account_type == "freelancer":
            user = Freelancer.objects.get(id=user_id)
        else:
            user = Recruiter.objects.get(id=user_id)
        return {"app_user": user}
    except:
        return {"app_user": None}
from .models import Job

def recruiter_job_count(request):
    job_count = 0

    if request.session.get("account_type") == "recruiter":
        recruiter_id = request.session.get("user_id")
        if recruiter_id:
            job_count = Job.objects.filter(recruiter_id=recruiter_id).count()

    return {
        "job_count": job_count
    }
from .models import Freelancer, Notification

def freelancer_notifications(request):
    if request.session.get("account_type") == "freelancer":
        try:
            freelancer = Freelancer.objects.get(id=request.session.get("user_id"))
            notifications = Notification.objects.filter(
                freelancer=freelancer,
                is_read=False
            )
            return {
                "freelancer_notifications": notifications,
                "notification_count": notifications.count()
            }
        except Freelancer.DoesNotExist:
            pass

    return {
        "freelancer_notifications": [],
        "notification_count": 0
    }
