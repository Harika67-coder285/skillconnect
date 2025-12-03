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
