from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import auth

def home(request):
    if request.user.is_authenticated:
        u = User.objects.get(username=request.user)
        print(u.profile)
    return render(request, 'map/home.html')


    
# Create your views here.
