from __future__ import unicode_literals
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from utils.mongo import get_db_handle, clientpool, get_collection_instance
from bson.objectid import ObjectId
from bson.errors import InvalidId
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from datetime import date
from os import getenv


# Create your views here.


@login_required
def uilogout_request(request):
    if request.user is not None:
        logout(request)
        messages.info(request, "Logout Succesfully!!")
    else:
        messages.error(request, "You are not logged in")

    return redirect('uilogin')


def uilogin_request(request):

    form = AuthenticationForm(request=request, data=request.POST or None)

    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(
                request, f"You are now logged in as {username}")
            return redirect('uihome')
        else:
            messages.error(request, "Invalid username or password.")

    else:
        messages.error(request, "Invalid username or password.")

    return render(request, "uimain/uilogin.html", context={"form": form})


def uihome_request(request):
    if request.user.is_authenticated:
        pass
    else:
        return redirect('uilogin')

    return render(request, "uimain/uihome.html")
