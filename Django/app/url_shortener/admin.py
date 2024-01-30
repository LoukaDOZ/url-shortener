from django.contrib import admin

from .models import User, URL

admin.site.register(User)
admin.site.register(URL)
