from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic

from .models import User, URL
from .forms import ShortenForm

import os
import random
import time
from datetime import datetime

# Utils
URL_LIFETIME = 604800 # 7 days in seconds
URL_ID_LEN = 8
URL_ID_CHARS = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmopqrstuvwxyz0123456789"

def template(file: str):
    return os.path.join("url_shortener", file)

def get_error(form, key: str):
    errors = form.errors.as_data()
    if key not in errors:
        return None
    
    data = errors[key]
    if len(data) == 0:
        return None
    
    return data[0].message

def get_url_id():
    url_id = ""
    for i in range(URL_ID_LEN):
        rand = random.randint(0, len(URL_ID_CHARS) - 1)
        url_id += URL_ID_CHARS[rand]
    return url_id

def get_url_expiration():
    return int(time.time()) + URL_LIFETIME

def date_to_str(date: int):
    return datetime.fromtimestamp(date).strftime("%d/%m/%Y %H:%M")

# Generic views
class UserURLView(generic.ListView):
    template_name = "url_shortener/my_urls.html"
    context_object_name = "urls"
    queryset = URL.objects.filter(username="hello")

# Routes
def index(request):
    return redirect("shorten/", permanent=True)

def redirect_to_target_url(request, url_id):
    query = URL.objects.filter(_id=url_id)

    if(len(query) == 0):
        return render(request, template("not_found.html"))

    return redirect(query[0].target, permanent=True)

def shorten(request):
    if request.method == "POST":
        form = ShortenForm(request.POST)
        if form.is_valid():

            url_id = get_url_id()
            while len(URL.objects.filter(_id=url_id)) > 0:
                url_id = get_url_id()

            url = URL(
                _id = url_id,
                target = form.cleaned_data["url"],
                expiration = get_url_expiration()
            )
            url.save()

            return render(request, template("shortened.html"), {
                "shortened_url": request.build_absolute_uri(f"/r/{url_id}"),
                "expiration_date": date_to_str(url.expiration)
            })
        else:
            return render(request, template("index.html"), {
                "input_error": get_error(form, "url")
            })

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