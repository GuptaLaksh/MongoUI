from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from os import getenv


# Create your views here.


def patch_login_request(request):
    return render(request, "patchmain/patchlogin.html")


def patch_home_request(request):
    return render(request, "patchmain/patch_homepage.html")


def patch_admin_request(request):
    return render(request, "patchmain/patch_adminpage.html")


def patch_logout_request(request):
    return redirect("patchlogin")
