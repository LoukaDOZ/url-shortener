from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import urlencode

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
    connected_context(request, context)
    return render(request, template(file), context)

def render_404(request):
    return render_template(request, "not_found.html")

def connected_context(request, context):
    context["connected"] = hasattr(request, "user") and request.user.is_authenticated

# Generic views
class IndexView(generic.base.RedirectView):
    permanent = True
    query_string = True
    pattern_name = "shorten"
    http_method_names = ["get"]

    def http_method_not_allowed(self, request, *args, **kwargs):
        return render_404(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_context(self.request, context)
        return context

class RedirectToTargetView(generic.TemplateView):
    permanent = True
    query_string = True
    http_method_names = ["get"]

    def http_method_not_allowed(self, request, *args, **kwargs):
        return render_404(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_context(self.request, context)
        return context
    
    def get(self, request, url_id):
        query = URL.objects.filter(_id=url_id)

        if(len(query) == 0):
            return render_404(self.request)

        return redirect(query[0].target, permanent=True)

class ShortenView(generic.edit.FormView):
    template_name = template("index.html")
    form_class = ShortenForm
    success_url = "/shorten/"
    http_method_names = ["get", "post"]

    def http_method_not_allowed(request, *args, **kwargs):
        return render_404(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_context(self.request, context)
        return context

    def get(self, request, *args, **kwargs):
        shortening = bool(self.__get_query_param__("shortening", False))
        session_url_id = request.session.get("url_id", None)
        session_target_url = request.session.get("target_url", None)

        print("GET", shortening, session_url_id, session_target_url)

        if not shortening or not session_url_id or not session_target_url:
            return super().get(self, request, *args, **kwargs)

        return self.__pending_shortening__(request, session_url_id, session_target_url)

    def post(self, request, *args, **kwargs):
        shortening = bool(self.__get_query_param__("shortening", False))
        guest = bool(self.__get_query_param__("guest", False))
        session_url_id = request.session.get("url_id", None)
        session_target_url = request.session.get("target_url", None)

        print("POST", shortening, guest, session_url_id, session_target_url)

        if not shortening or not session_url_id or not session_target_url:
            return super().post(self, request, *args, **kwargs)
    
        return self.__pending_shortening__(request, session_url_id, session_target_url, guest)
    
    def form_valid(self, form):
        url_id = get_url_id()
        target_url = form.cleaned_data["url"]

        if not self.request.user.is_authenticated:
            self.request.session["url_id"] = url_id
            self.request.session["target_url"] = target_url
        
            next_url = urlencode({"next": "/shorten/?shortening=true"})
            return redirect(f"/login/?shortening=true&{next_url}", permanent=True)

        url = URL(
            _id=url_id,
            target=target_url,
            expiration=get_url_expiration(),
            username=User.objects.get(username=self.request.user.username)
        )
        url.save()

        return render_template(self.request, "shortened.html", {
            "shortened_url": make_shortened_url(self.request, url._id),
            "expiration_date": date_to_str(url.expiration)
        })
    
    def form_invalid(self, form):
        return render_template(self.request, "index.html", {
            "url": get_form_data(form, "url", ""),
            "input_error": get_error_message(form, "url")
        })
    
    def __pending_shortening__(self, request, session_url_id: str, session_target_url: str, guest: bool = False):
        del request.session["url_id"]
        del request.session["target_url"]
        username = User.objects.get(username=request.user.username) if not guest else None
        url = URL(
            _id=session_url_id,
            target=session_target_url,
            expiration=get_url_expiration(),
            username=username
        )
        url.save()

        return render_template(self.request, "shortened.html", {
            "shortened_url": make_shortened_url(request, url._id),
            "expiration_date": date_to_str(url.expiration)
        })
    
    def __get_query_param__(self, key: str, placeholder: object):
        return self.request.GET.get(key, placeholder)

class LoginView(generic.edit.FormView):
    template_name = template("login.html")
    form_class = LoginForm
    success_url = "/"
    http_method_names = ["get", "post"]

    def http_method_not_allowed(request, *args, **kwargs):
        return render_404(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_context(self.request, context)
        context["tab"] = self.__get_query_param__("tab", "login")
        context["login_url"] = self.__build_form_url__("/login/")
        context["register_url"] = self.__build_form_url__("/register/")
        context["shortening"] = bool(self.__get_query_param__("shortening", False))
        return context
    
    def form_valid(self, form, *args, **kwargs):
        username = get_form_data(form, "username", "")
        raw_password = get_form_data(form, "password", "")
        next_url = self.__get_query_param__("next", None)

        user = authenticate(self.request, username=username, password=raw_password)
        if user is not None:
            login(self.request, user)

            if next_url:
                return redirect(next_url, permanent=False)

            return redirect("/shorten/", permanent=True)
        else:
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        username_err = get_error(form, "username")
        password_err = get_error(form, "password")
        context = {
            "tab": "login",
            "login_username": get_form_data(form, "username", "")
        }

        if username_err and username_err.code == "required":
            context["login_username_error"] = username_err.message
        elif password_err and password_err.code == "required":
            context["login_password_error"] = password_err.message
        else:
            context["global_error"] = "Invalid credentials"

        return render_template(self.request, "login.html", context)
    
    def __get_query_param__(self, key: str, placeholder: object):
        return self.request.GET.get(key, placeholder)
    
    def __build_form_url__(self, path: str):
        shortening = bool(self.__get_query_param__('shortening', False))
        next_url = self.__get_query_param__('next', None)

        shortening_param = "shortening=true" if shortening else ""
        next_param = urlencode({"next":next_url}) if next_url else ""
        return f"{path}?{shortening_param}&{next_param}"

class RegisterView(generic.edit.FormView):
    template_name = ""
    form_class = RegisterForm
    success_url = "/"
    http_method_names = ["post"]

    def http_method_not_allowed(request, *args, **kwargs):
        return render_404(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_context(self.request, context)
        context["login_url"] = self.__build_form_url__("/login/")
        context["register_url"] = self.__build_form_url__("/register/")
        context["shortening"] = bool(self.__get_query_param__("shortening", False))
        return context
    
    def form_valid(self, form):
        username = get_form_data(form, "username", "")
        raw_password = get_form_data(form, "password", "")
        hashed_password = make_password(raw_password)
        next_url = self.__get_query_param__("next", None)
        
        if len(User.objects.filter(username = username)) != 0:
            return self.form_invalid(form, True)
        
        user = User(
            username = username,
            password = hashed_password
        )

        user.save()
        login(self.request, user)
        
        if next_url:
            return redirect(next_url, permanent=True)

        return redirect("/shorten/", permanent=True)
    
    def form_invalid(self, form, user_exists_err: bool = False):
        context = {
            "tab": "register",
            "register_username": get_form_data(form, "username", "")
        }

        if user_exists_err:
            context["global_error"] = "Username already exists"
        else:
            context["register_username_error"] = get_error_message(form, "username")
            context["register_password_error"] = get_error_message(form, "password")
            context["register_confirm_password_error"] = get_error_message(form, "confirm_password")

        return render_template(self.request, "login.html", context)
    
    def __get_query_param__(self, key: str, placeholder: object):
        return self.request.GET.get(key, placeholder)
    
    def __build_form_url__(self, path: str):
        shortening = bool(self.__get_query_param__('shortening', False))
        next_url = self.__get_query_param__('next', None)

        shortening_param = "shortening=true" if shortening else ""
        next_param = urlencode({"next":next_url}) if next_url else ""
        return f"{path}?{shortening_param}&{next_param}"

class LogoutView(generic.base.RedirectView):
    permanent = True
    query_string = True
    pattern_name = "index"
    http_method_names = ["get"]

    def http_method_not_allowed(self, request, *args, **kwargs):
        return render_404(self.request)

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super().get_redirect_url(*args, **kwargs)

class UserURLView(LoginRequiredMixin, generic.ListView):
    login_url = "/login/"
    redirect_field_name = "next"

    template_name = template("my_urls.html")
    context_object_name = "urls"
    http_method_names = ["get"]

    def http_method_not_allowed(request, *args, **kwargs):
        return render_404(request)
    
    def get_queryset(self):
        return URL.objects.filter(username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_context(self.request, context)

        for url in context["urls"]:
            url.shortened_url = make_shortened_url(self.request, url._id)
            url.expiration_date = date_to_str(url.expiration)
        return context

class NotFoundView(generic.base.TemplateView):
    template_name = template("not_found.html")
    http_method_names = ["get"]

    def http_method_not_allowed(request, *args, **kwargs):
        return render_404(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_context(self.request, context)
        return context

# Routes
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
                return render_template(request, "login.html", {
                    "tab": "login",
                    "shortening": shortening,
                    "login_username": get_form_data(form, "username", ""),
                    "global_error": "Invalid credentials"
                })
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