# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from utils.mongo import get_db_handle, clientpool, get_collection_instance
from bson.objectid import ObjectId


# Create Views

@login_required
def logout_request(request):
    if request.user is not None:
        clientInstance = clientpool[request.user.username]
        clientInstance.close()
        clientpool[request.user.username] = None
        logout(request)
        messages.info(request, "Logout Succesfully!!")
    else:
        messages.error(request, "You are not logged in")

    return redirect('login')


def login_request(request):
    form = AuthenticationForm(request=request, data=request.POST)

    print(clientpool)
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':

        form = AuthenticationForm(request=request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            clientInstance = get_db_handle(username, password)

            if clientInstance is not None:

                clientpool[username] = clientInstance
                if not User.objects.filter(username=username).exists():
                    User.objects.create_user(
                        username=username, password=password)

                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.info(
                        request, f"You are now logged in as {username}")
                    return redirect('/')
                else:
                    messages.error(request, "Invalid username or password.")
            else:
                messages.error(request, "Invalid username or password.")

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "main/login.html", context={"form": form})


@login_required
def showdbs(request):
    clientInstance = clientpool[request.user.username]
    return render(request, "main/home.html", context={"dbs": clientInstance.list_databases()})


@login_required
def showCollections(request, db):
    clientInstance = clientpool[request.user.username]
    collectionlist = []
    tuplist = []
    for collection in clientInstance[db].list_collection_names():
        collectionlist.append((collection, clientInstance[db][collection]))

    for collection, instance in collectionlist:
        tuplist.append(
            dict({'name': collection, 'count': instance.estimated_document_count()}))

    context = {
        "db": db, "tuplist": tuplist}
    return render(request, "main/pagecollection.html", context=context)


@login_required
def showdocs(request, db, collection):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)
    # print(collections.estimated_document_count())
    documents = collections.find({})
    tuplist = []
    for document in documents:
        tuplist.append((document['_id'], document))

    return render(request, "main/documents.html", context={"db": db, "collection": collection, "tuplist": tuplist})


@login_required
def _deletedatabase(request, db):
    clientInstance = clientpool[request.user.username]
    clientInstance.drop_database(db)

    return redirect('showdbs')


@login_required
def _insertdatabase(request):
    return HttpResponse("Inserted Database!!")


@login_required
def _deletecollection(request, db, collection):
    clientInstance = clientpool[request.user.username]
    clientInstance[db].drop_collection(collection)
    return redirect('showcollections', db=db)


@login_required
def _insertcollection(request, db):
    return HttpResponse("Inserted Collection !!")


@login_required
def _deletedocument(request, db, collection, pk):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)
    collections.find_one_and_delete({"_id": ObjectId(pk)})

    return redirect('showdocs', db=db, collection=collection)


@login_required
def _viewdocument(request, db, collection, pk):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)
    jsontext = collections.find_one({"_id": ObjectId(pk)})
    print(jsontext)
    context = {"jsontext": jsontext, "db": db, "collection": collection}
    return render(request, "main/views.html", context)


@login_required
def _insertdocument(request, db, collection):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)

    context = {"db": db, "collection": collection}
    return render(request, "main/insert.html", context)
