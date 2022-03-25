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
from bson.errors import InvalidId
from django.http import HttpResponseRedirect
from django.shortcuts import render
from main.forms import CollectionForm, DatabaseForm, DocumentForm
from django.urls import reverse_lazy
import json
from ast import literal_eval
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


"""
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

    context = {"form": form}

    return render(request, 'login.html', context=context)
"""


def login_request(request):
    form = AuthenticationForm(request=request, data=request.POST)

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
    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']
    context = {"dbs": clientInstance.list_databases(), "primelist": primelist}
    return render(request, "main/home.html", context=context)


@login_required
def showCollections(request, db):
    clientInstance = clientpool[request.user.username]
    collectionlist = []
    tuplist = []
    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']
    for collection in clientInstance[db].list_collection_names():
        collectionlist.append((collection, clientInstance[db][collection]))

    for collection, instance in collectionlist:
        tuplist.append(
            dict({'name': collection, 'count': instance.estimated_document_count()}))

    context = {
        "db": db, "tuplist": tuplist, "primelist": primelist}

    return render(request, "main/pagecollection.html", context=context)


@login_required
def showdocs(request, db, collection):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)
    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']
    documents = collections.find({})
    tuplist = []
    newlist = {}
    for document in documents:
        tuplist.append((document['_id'], document))

    print(type(tuplist))
    print(tuplist)

    keylist = []
    for id, doc in tuplist:
        for key in doc:
            if key not in keylist:
                keylist.append(key)

    # id, tuplist(all_keys, all_values)

    context = {"db": db, "collection": collection,
               "tuplist": tuplist, "primelist": primelist, "keylist": keylist}

    return render(request, "main/documents.html", context=context)


@login_required
def _deletedatabase(request, db):
    clientInstance = clientpool[request.user.username]
    clientInstance.drop_database(db)

    return redirect('showdbs')


@login_required
def _insertdatabase(request):
    clientInstance = clientpool[request.user.username]

    data = {}

    url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/default.json'

    json_data = open(url)
    data = json.loads(json_data.read())

    form = DatabaseForm(request.POST or None, initial={
        "dictionary": (json.dumps(data, indent=4))})

    if request.method == 'POST':

        if form.is_valid():

            databaseName = form.cleaned_data.get('databaseName')
            collectionName = form.cleaned_data.get('collectionName')
            dictionary = form.cleaned_data.get('dictionary')
            dictionary = literal_eval(dictionary)
            databaseName = clientInstance[databaseName]
            collection = databaseName[collectionName]
            collection.insert_one(dictionary)
            print(dictionary)

            return HttpResponseRedirect('/')

    context = {"form": form}
    return render(request, "side/add_database.html", context)


@login_required
def _renamedatabase(request, db):
    clientInstance = clientpool[request.user.username]

    if request.method == 'POST':
        newname = request.POST.get["newname"]
        print(newname)
        clientInstance.admin.command('copydb',
                                     fromdb=db,
                                     todb=newname)
    return redirect('showdbs')


@login_required
def _deletecollection(request, db, collection):
    clientInstance = clientpool[request.user.username]
    datab = clientInstance[db].drop_collection(collection)
    return redirect('showcollections', db=db)


@login_required
def _insertcollection(request, db):
    clientInstance = clientpool[request.user.username]
    data = {}

    url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/default.json'

    json_data = open(url)
    data = json.loads(json_data.read())

    form = CollectionForm(request.POST or None, initial={
        "dictionary": (json.dumps(data, indent=4))})

    if request.method == 'POST':

        if form.is_valid():

            collectionName = form.cleaned_data.get('collectionName')
            dictionary = form.cleaned_data.get('dictionary')
            dictionary = literal_eval(dictionary)
            Mycol = clientInstance[db][collectionName]
            Mycol.insert_one(dictionary)
            print(dictionary)
            print(collectionName)
            url = reverse_lazy('showcollections', kwargs={'db': db})
            return HttpResponseRedirect(url)

    context = {"form": form, "db": db}
    return render(request, "side/add_collection.html", context)


@login_required
def _renamecollection(request, db, collection):
    clientInstance = clientpool[request.user.username]

    if request.method == 'POST':
        newname = request.POST.get["newname"]

        print(newname)
        clientInstance[db][collection].rename(newname)

    return redirect('showcollections', db=db)


@login_required
def _deletedocument(request, db, collection, pk):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)
    try:
        query = {"_id": ObjectId(pk)}
    except InvalidId:
        query = {"_id": (pk)}

    collections.find_one_and_delete(query)

    return redirect('showdocs', db=db, collection=collection)


@login_required
def _viewdocument(request, db, collection, pk):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)

    try:
        query = {"_id": ObjectId(pk)}
    except InvalidId:
        query = {"_id": (pk)}

    jsontext = collections.find_one(query)

    jsontext.pop("_id")

    jsontext = json.dumps(jsontext, indent=4)

    try:
        ObjectId(pk)
        newvar = '{"_id": ObjectId(' + (pk) + '),'
    except InvalidId:
        newvar = '{"_id":' + (pk) + ','

    jsontext = newvar + jsontext[1:]

    if jsontext is None:
        query = {"_id": int(pk)}
        jsontext = collections.find_one(query)

    context = {"query": query, "jsontext": jsontext, "db": db,
               "collection": collection, "pk": pk}
    return render(request, "side/views.html", context)


@login_required
def _insertdocument(request, db, collection):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)

    data = {}

    url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/' + collection + '.json'

    try:
        json_data = open(url)
    except FileNotFoundError:
        url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/default.json'
        json_data = open(url)

    data = json.loads(json_data.read())
    form = DocumentForm(request.POST or None, initial={
                        "dictionary": (json.dumps(data, indent=4))})

    #form = DocumentForm(request.POST or None)
    if request.method == 'POST':

        if form.is_valid():

            dictionary = form.cleaned_data.get('dictionary')
            collections.insert_one(literal_eval(dictionary))
            url = reverse_lazy('showdocs', kwargs={
                               'db': db, 'collection': collection})
            return HttpResponseRedirect(url)

    context = {"db": db, "collection": collection, "form": form}
    return render(request, "side/insert.html", context)


@login_required
def _editdocument(request, db, collection, pk):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)

    try:
        query = {"_id": ObjectId(pk)}
    except InvalidId:
        query = {"_id": (pk)}

    jsontext = collections.find_one(query)

    if jsontext.get("_id") is not None:
        jsontext.pop("_id")

    form = DocumentForm(request.POST or None, initial={
                        "dictionary": json.dumps(jsontext, indent=4)})

    #form = DocumentForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():

            dictionary = form.cleaned_data.get('dictionary')

            dictionary = literal_eval((dictionary))

            try:
                idnew = ObjectId(pk)
            except InvalidId:
                idnew = (pk)
            dictionary["_id"] = idnew
            collections.find_one_and_replace(jsontext, dictionary)

            #url = reverse_lazy('showdocs', kwargs={'db': db, 'collection': collection})
            # return HttpResponseRedirect(url)

    context = {"jsontext": jsontext, "db": db,
               "collection": collection, "form": form, "pk": pk}
    return render(request, "side/edit.html", context)
