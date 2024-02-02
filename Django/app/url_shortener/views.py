from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.mixins import LoginRequiredMixin

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

def get_query_param(request, key: str, placeholder: object = None):
    return request.GET[key] if key in request.GET else placeholder

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
    cleaned_data = form.cleaned_data[key] if key in form.cleaned_data else None
    if cleaned_data:
        return cleaned_data
    
    return form.data[key] if key in form.data else placeholder

def get_url_id():
    def generate_url_id():
        url_id = ""
        for i in range(URL_ID_LEN):
            rand = random.randint(0, len(URL_ID_CHARS) - 1)
            url_id += URL_ID_CHARS[rand]
        return url_id
    
    url_id = generate_url_id()
    while len(URL.objects.filter(_id=url_id)) > 0:
        url_id = get_url_id()
    
    return url_id

def get_url_expiration():
    return int(time.time()) + URL_LIFETIME

def make_shortened_url(request, url_id: str):
    return request.build_absolute_uri(f"/r/{url_id}")

def date_to_str(date: int):
    return datetime.fromtimestamp(date).strftime("%d/%m/%Y %H:%M")

def template(file: str):
    return os.path.join("url_shortener", file)

def render_template(request, file: str, context: dict = {}):
    context["connected"] = request.user.is_authenticated
    return render(request, template(file), context)

def render_404(request):
    return render_template(request, "not_found.html")

# Generic views
class IndexView(generic.base.RedirectView):
    permanent = True
    query_string = True
    pattern_name = "shorten"
    http_method_names = ["get"]

    def http_method_not_allowed(self, request, *args, **kwargs):
        return render_404(self.request)

class RedirectToTargetView(generic.TemplateView):
    permanent = True
    query_string = True
    http_method_names = ["get"]

    def http_method_not_allowed(self, request, *args, **kwargs):
        return render_404(self.request)
    
    def get(self, request, url_id):
        query = URL.objects.filter(_id=url_id)

        if(len(query) == 0):
            return render_404(self.request)

        return redirect(query[0].target, permanent=True)

class UserURLView(LoginRequiredMixin, generic.ListView):
    login_url = "/login/"
    redirect_field_name = "next"

    template_name = template("my_urls.html")
    context_object_name = "urls"
    http_method_names = ["get"]

    def http_method_not_allowed(request, *args, **kwargs):
        return render_404(self.request)
    
    def get_queryset(self):
        return URL.objects.filter(username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["connected"] = self.request.user.is_authenticated

        for url in context["urls"]:
            url.shortened_url = make_shortened_url(self.request, url._id)
            url.expiration_date = date_to_str(url.expiration)
        return context

class NotFoundView(generic.base.TemplateView):
    template_name = template("not_found.html")
    http_method_names = ["get"]

    def http_method_not_allowed(request, *args, **kwargs):
        return render_404(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["connected"] = self.request.user.is_authenticated
        return context

# Routes
def redirect_to_target_url(request, url_id):
    query = URL.objects.filter(_id=url_id)

    if(len(query) == 0):
        return render_404(self.request)

    return redirect(query[0].target, permanent=True)

def shorten(request):
    guest = bool(get_query_param(request, "guest", False))

    if request.method == "POST":
        url_id = None
        target_url = None
        username = None

        pending_url_id = request.session.get("pending_url_id", None)
        pending_target_url = request.session.get("pending_target_url", None)
        
        if pending_url_id:
            url_id = pending_url_id
            target_url = pending_target_url
            del request.session["pending_url_id"]
            del request.session["pending_target_url"]
        else:        
            form = ShortenForm(request.POST)
            if form.is_valid():
                url_id = get_url_id()
                target_url = form.cleaned_data["url"]
            else:
                return render_template(request, "index.html", {
                    "url": get_form_data(form, "url", ""),
                    "input_error": get_error_message(form, "url")
                })

        if request.user.is_authenticated:
            username = User.objects.filter(username=request.user.username)[0]
        elif not pending_url_id:
            request.session["pending_url_id"] = url_id
            request.session["pending_target_url"] = target_url
            return redirect(f"/login/?shortening=true", permanent=True)

        url = URL(
            _id = url_id,
            target = target_url,
            expiration = get_url_expiration(),
            username = username
        )
        url.save()

        return render_template(request, "shortened.html", {
            "shortened_url": make_shortened_url(request, url._id),
            "expiration_date": date_to_str(url.expiration)
        })

    return render_template(request, "index.html")

def log_in(request):
    tab = get_query_param(request, "tab", "login")
    shortening = bool(get_query_param(request, "shortening", False))

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = get_form_data(form, "username", "")
            raw_password = get_form_data(form, "password", "")

            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect("/shorten/", permanent=(not shortening))
        else:
            username_err = get_error(form, "username")
            password_err = get_error(form, "password")

            if username_err and username_err.code == "required":
                return render_template(request, "login.html", {
                    "tab": "login",
                    "shortening": shortening,
                    "login_username": get_form_data(form, "username", ""),
                    "login_username_error": username_err.message
                })

            if password_err and password_err.code == "required":
                return render_template(request, "login.html", {
                    "tab": "login",
                    "shortening": shortening,
                    "login_username": get_form_data(form, "username", ""),
                    "login_password_error": password_err.message
                })
            
            return render_template(request, "login.html", {
                "tab": "login",
                "shortening": shortening,
                "login_username": get_form_data(form, "username", ""),
                "global_error": "Invalid credentials"
            })

    return render_template(request, "login.html", {
        "tab": tab,
        "shortening": shortening
    })

def register(request):
    shortening = bool(get_query_param(request, "shortening", "False"))

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = get_form_data(form, "username", "")
            raw_password = get_form_data(form, "password", "")
            hashed_password = make_password(raw_password)
            
            if len(User.objects.filter(username = username)) != 0:
                return render_template(request, "login.html", {
                    "tab": "register",
                    "shortening": shortening,
                    "register_username": get_form_data(form, "username", ""),
                    "global_error": "Username already exists"
                })
            
            user = User(
                username = username,
                password = hashed_password
            )
            user.save()
            login(request, user)
            return redirect("/shorten/", permanent=(not shortening))
        else:
            return render_template(request, "login.html", {
                "tab": "register",
                "shortening": shortening,
                "register_username": get_form_data(form, "username", ""),
                "register_username_error": get_error_message(form, "username"),
                "register_password_error": get_error_message(form, "password"),
                "register_confirm_password_error": get_error_message(form, "confirm_password")
            })
    
    return redirect("/login/?tab=register", permanent=True)

def log_out(request):
    logout(request)
    return redirect("/", permanent=True)