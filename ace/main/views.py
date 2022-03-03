# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
# Imports
from utils.mongo import get_db_handle
from django.http import HttpResponse
import base64
#from django.contrib.auth import authenticate


# Create Views
def showdbs(request):
    #auth_header = request.META['Authorization']
    #encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
    #decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
    #username = decoded_credentials[0]
    #password = decoded_credentials[1]
    username = request.user.username

    client = get_db_handle(str(username), "Password123")
    dbs = []
    for db in client.list_databases():
        dbs.append(db)
    #return HttpResponse(request)
    return render(request,"main/home.html",context={"dbs" : dbs})

def logout(request):
    return render(request,'main/login.html')

def login(request):
    return render(request,"main/login.html")

def showCollections(request, db):
    username = request.user.username
    client = get_db_handle(str(username), "Password123")

    #print(db)
    collections = client[db].list_collection_names()
    

    #print(client['Microbot_MappingsDB'].list_collection_names())

    return render(request, "main/pagecollection.html", context = {"db": db, "collections" : collections})

def tezt(request):
    return render(request,"tezt.html")





def index(request):
    return render(request,'main/index.html')
    
'''
def register(request):
    if request=='POST':
        form = UserCreationForm(request.POST)

            username = form.cleaned_data['username']
        
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            -> login(request, user)
            return redirect('index')

    
    context = {'form':form}
    return render(request,'registration/register.html',context)
'''
