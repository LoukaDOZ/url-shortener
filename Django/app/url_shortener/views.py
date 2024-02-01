from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password

from .models import URL, User
from .forms import ShortenForm, LoginForm, RegisterForm

import os
import random
import time
from datetime import datetime

# Utils
URL_LIFETIME = 604800 # 7 days in seconds
URL_ID_LEN = 8
URL_ID_CHARS = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmopqrstuvwxyz0123456789"

def get_error(form, key: str):
    errors = form.errors.as_data()
    if key not in errors:
        return None
    
    data = errors[key]
    if len(data) == 0:
        return None
    
    return data[0]

def get_error_message(form, key: str):
    err = get_error(form, key)
    return err.message if err else ""

def get_form_data(form, key: str, placeholder: object = None):
    return form.cleaned_data[key] if key in form.cleaned_data else placeholder

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

def template(file: str):
    return os.path.join("url_shortener", file)

def render_template(request, file: str, context: dict = {}):
    context["connected"] = request.user.is_authenticated
    return render(request, template(file), context)

# Generic views
class UserURLView(generic.ListView):
    template_name = "url_shortener/my_urls.html"
    context_object_name = "urls"
    queryset = URL.objects.filter(username="hello")

# Routes
def index(request):
    return redirect("/shorten/", permanent=True)

def redirect_to_target_url(request, url_id):
    query = URL.objects.filter(_id=url_id)

    if(len(query) == 0):
        return render_template(request, "not_found.html")

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

            return render_template(request, "shortened.html", {
                "shortened_url": request.build_absolute_uri(f"/r/{url_id}"),
                "expiration_date": date_to_str(url.expiration)
            })
        else:
            return render_template(request, "index.html", {
                "input_error": get_error_message(form, "url")
            })

    return render_template(request, "index.html")

def log_in(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = get_form_data(form, "username", "")
            raw_password = get_form_data(form, "password", "")

            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect("/shorten/", permanent=True)
        else:
            username_err = get_error(form, "username")
            password_err = get_error(form, "password")

            if username_err and username_err.code == "required":
                return render_template(request, "login.html", {
                    "login_username_error": username_err.message
                })

            if password_err and password_err.code == "required":
                return render_template(request, "login.html", {
                    "login_password_error": password_err.message
                })
            
            return render_template(request, "login.html", {
                "global_error": "Invalid credentials"
            })

    return render_template(request, "login.html")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = get_form_data(form, "username", "")
            raw_password = get_form_data(form, "password", "")
            hashed_password = make_password(raw_password)
            
            if len(User.objects.filter(username = username)) != 0:
                return render_template(request, "login.html", {
                    "tab": "register",
                    "global_error": "Username already exists"
                })
            
            user = User(
                username = username,
                password = hashed_password
            )
            user.save()
            login(request, user)
            return redirect("/shorten/", permanent=True)
        else:
            return render_template(request, "login.html", {
                "tab": "register",
                "register_username": get_form_data(form, "username", ""),
                "register_username_error": get_error_message(form, "username"),
                "register_password_error": get_error_message(form, "password"),
                "register_confirm_password_error": get_error_message(form, "confirm_password")
            })
    return redirect("/login/?tab=register", permanent=True)

def my_urls(request):
    return HttpResponse("URLS")

def log_out(request):
    logout(request)
    return redirect("/", permanent=True)

def not_found(request, unknown_path = ""):
    return render_template(request, "not_found.html")