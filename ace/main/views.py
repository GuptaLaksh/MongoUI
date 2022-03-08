# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from calendar import c
from http import client
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
# Imports
from utils.mongo import get_db_handle
from django.http import HttpResponse
import base64
#from django.contrib.auth import authenticate


c = None

# Create Views


def logout_request(request):
    logout(request)
    messages.info(request, "Logout Succesfully!!")
    return redirect('login')


def login_request(request):
    dbs = []
    form = AuthenticationForm(request=request, data=request.POST)
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            global c
            c = get_db_handle(username, password)

            for db in c.list_databases():
                dbs.append(db)
            if user is not None:
                login(request, user)

                messages.info(request, f"You are now logged in as {username}")
                print(f"You are now logged in as {username}")

                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
                print(request, "Invalid username or password.")

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "main/login.html", context={"dbs": dbs, "form": form})


def showdbs(request):

    dbs = []
    for db in c.list_databases():
        dbs.append(db)
    # return HttpResponse(request)
    return render(request, "main/home.html", context={"dbs": dbs})


def showCollections(request, db):
    collections = c[db].list_collection_names()
    return render(request, "main/pagecollection.html", context={"db": db, "collections": collections})

    # print(client['Microbot_MappingsDB'].list_collection_names())


def showdocs(request, db, collection):
    collections = c[db][collection]
    documents = collections.find({})

    for document in documents:
        print(document)
    return render(request, "main/documents.html", context={"db": db, "collection": collection, "collections": collections, "documents": documents})
