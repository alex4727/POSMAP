from django.contrib import admin
from .models import *
# Register your models here.

class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'address']

class PoolAdmin(admin.ModelAdmin):
    list_display = ['place', 'number', 'load', 'departure_date']

admin.site.register(Place, PlaceAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(Profile)