# core/views.py
from django.shortcuts import render, redirect
from django.conf import settings
from srcnn_project.supabase_client import supabase  
import os
## can be a package
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
# supabase = settings.supabase

import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login

import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK once
cred = credentials.Certificate("srcnn_project/firebase.json")
firebase_admin.initialize_app(cred)

def home(request):
    return render(request, "home.html")

def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        supabase.auth.sign_up({"email": email, "password": password})
        return redirect("login")
    return render(request, "signup.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if user:
            request.session["user"] = user.user.id
            return redirect("home")
    return render(request, "login.html")


def login_page(request):
    return render(request, "login.html")

def logout_view(request):
    request.session.flush()
    return redirect("login")

from django.shortcuts import render
from .forms import ImageUploadForm
from .ml.predictor import predict_pneumonia
import os
from django.conf import settings

def predict_view(request):
    result = None
    confidence = None

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]

            # Save temporarily
            img_path = os.path.join(settings.MEDIA_ROOT, image.name)
            with open(img_path, "wb+") as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # Predict
            result, confidence = predict_pneumonia(img_path)
            print(result, confidence)

    else:
        form = ImageUploadForm()

    return render(request, "upload.html", {"form": form, "result": result, "confidence": confidence})

import json
from django.http import JsonResponse
from firebase_admin import auth as firebase_auth

def firebase_login(request):
    data = json.loads(request.body)
    token = data.get("token")

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email")

        # You can now log in or create a Django user
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(username=uid, defaults={"email": email})
        
        # Optionally log them in using Django's session auth
        from django.contrib.auth import login
        login(request, user)

        return JsonResponse({"message": "Login successful", "email": email})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect("login")

@csrf_exempt
def google_login(request):
    """Receive Firebase ID token and log user into Django session"""
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get("token")

        try:
            decoded = auth.verify_id_token(token)
            email = decoded.get("email")
            name = decoded.get("name", "User")

            # Create user in Django if not exists
            user, created = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": name})

            # Log the user into Django session
            login(request, user)

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "dashboard.html", {"user": request.user})

def test_page(request):
    from django.shortcuts import render
    return render(request, "javascript_test.html")
