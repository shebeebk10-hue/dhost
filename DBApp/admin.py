from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Shop, Invoice

admin.site.register(Shop)
admin.site.register(Invoice)