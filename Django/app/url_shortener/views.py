from django.shortcuts import render
from django.http import HttpResponse

import os

def template(file: str):
    return os.path.join("url_shortener", file)

def index(request):
    return render(request, template("index.html"))

def redirect(request):
    return HttpResponse("REDIRECT")

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

def not_found(request):
    return render(request, template("not_found.html"))