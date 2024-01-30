from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import User, URL

import os

# Utils
def template(file: str):
    return os.path.join("url_shortener", file)

# Routes
def index(request):
    return redirect("shorten/", permanent=True)

def redirect_to_target_url(request, url_id):
    query = URL.objects.filter(_id=url_id)

    if(len(query) == 0):
        return render(request, template("not_found.html"))

    return redirect(query[0].target, permanent=True)

def shorten(request):
    return render(request, template("index.html"))

def login(request):
    return render(request, template("login.html"))

def register(request):
    return render(request, template("login.html"), {"tab": "register"})

def my_urls(request):
    return HttpResponse("URLS")

def logout(request):
    return HttpResponse("LOGOUT")

def not_found(request, unknown_path = ""):
    return render(request, template("not_found.html"))