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
from main.forms import CollectionForm, DatabaseForm, DocumentForm, QueryForm, ExportForm, Loginform
from django.urls import reverse_lazy
from datetime import date
from os import getenv
import json
import csv


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
    form = Loginform(request=request, data=request.POST)

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
                    return redirect('showdbs')
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
    return render(request, "main/database.html", context=context)


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
    print(request.GET)
    collections = get_collection_instance(clientInstance, db, collection)
    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']

    documents = collections.find({})
    query = None

    form = QueryForm(request.POST or None)
    print(request.POST)

    if request.method == 'POST':

        if form.is_valid():

            key = form.cleaned_data.get('key')
            value = form.cleaned_data.get('value')
            query = form.cleaned_data.get('query')
            projection = form.cleaned_data.get('projection')

            if key != "" and value != "":
                query = '{"' + key + '":"' + value + '"}'
                documents = collections.find(json.loads(query))

            if query != "" and projection == "":
                val = "" + query + ""
                print(val)
                documents = collections.find(json.loads(val))
            elif query != "" and projection != "":
                documents = collections.find(
                    json.loads(query), json.loads(projection))

    tuplist = []

    for document in documents:
        tuplist.append((document['_id'], document))

    #print("tuplist:", tuplist)

    doclist = []
    for id, doc in tuplist:
        doclist.append(doc)
    #print("doclist:", doclist)

    keylist = []

    for doc in doclist:
        for key in doc.keys():
            if key not in keylist:
                keylist.append(key)

    keylist.sort()
    #print("keylist:", keylist)

    for key in keylist:
        for doc in doclist:
            if key not in doc:
                doc[key] = ""

    doclistnew = []
    for doc in doclist:
        doc1 = sorted(doc.items())
        doclistnew.append(dict(doc1))

    tuplistnew = []
    for doc in doclistnew:
        tuplistnew.append((doc["_id"], doc))

    exportform = ExportForm(request.POST or None)

    if request.method == 'POST':

        if 'export' in request.POST:

            if exportform.is_valid():
                formatoptions = exportform.cleaned_data.get('options')
                # print(formatoptions)
                mongo_docs = doclistnew
                if formatoptions == "csv":
                    response = HttpResponse(content_type='text/csv')
                    writer = csv.writer(response)
                    writer.writerow(mongo_docs)
                    datetoday = str(date.today())
                    fname = "" + collection + "_" + datetoday + ".csv"
                    # print(fname)
                    response['Content-Disposition'] = 'attachement; filename="{}"'.format(
                        fname)
                    return response
                elif formatoptions == "json":

                    json_data = json.dumps(mongo_docs, default=str)
                    datetoday = str(date.today())
                    fname = "" + collection + "_" + datetoday + ".json"
                    # print(fname)
                    response = HttpResponse(
                        json_data, content_type='text/json')
                    response['Content-Disposition'] = 'attachement; filename="{}"'.format(
                        fname)

                    return response

    #print("doclist:", doclist)
    #print("doclistnew:", doclistnew)

    context = {"form": form, "exportform": exportform, "db": db, "collection": collection,
               "tuplist": tuplistnew, "primelist": primelist, "keylist": keylist, "doclist": doclistnew}

    return render(request, "main/documents.html", context=context)


@login_required
def _deletedatabase(request, db):
    clientInstance = clientpool[request.user.username]
    clientInstance.drop_database(db)

    return redirect('showdbs')


@login_required
def _insertdatabase(request):
    clientInstance = clientpool[request.user.username]
    e = None
    data = {}

    url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/default.json'

    json_data = open(url)
    data = json.loads(json_data.read())

    form = DatabaseForm(request.POST or None, initial={
        "dictionary": (json.dumps(data, indent=4))})

    if request.method == 'POST':

        if request.POST["action"] == 'Validate':

            if form.is_valid():

                databaseName = form.cleaned_data.get('databaseName')
                collectionName = form.cleaned_data.get('collectionName')
                dictionary = form.cleaned_data.get('dictionary')
                databaseName = clientInstance[databaseName]
                collection = databaseName[collectionName]

                try:
                    json.loads(dictionary)
                    e = "Validated, Go ahead and Insert this Document :)"
                except ValueError as ex:
                    e = ex

        if request.POST["action"] == 'Insert':

            if form.is_valid():

                databaseName = form.cleaned_data.get('databaseName')
                collectionName = form.cleaned_data.get('collectionName')
                dictionary = form.cleaned_data.get('dictionary')

                databaseName = clientInstance[databaseName]
                collection = databaseName[collectionName]

                if 'myfile' in request.FILES:
                    myfile = request.FILES['myfile']
                    contentfile = json.load(myfile)
                    try:
                        collection.insert_one(contentfile)
                    except:
                        collection.insert_many(contentfile)

                    url = reverse_lazy('showdbs')
                    return HttpResponseRedirect(url)
                elif dictionary != "":
                    try:
                        json.loads(dictionary)
                        collection.insert_one(json.loads(dictionary))
                        url = reverse_lazy('showdbs')
                        return HttpResponseRedirect(url)
                    except ValueError as ex:
                        e = ex

    context = {"form": form, "e": e}
    return render(request, "side/add_database.html", context)


@login_required
def _renamedatabase(request, db):
    clientInstance = clientpool[request.user.username]

    if request.method == 'POST':

        newname = request.POST.get('newname')
        print(newname)

        clientInstance.admin.command('copydb',
                                     fromdb=db,
                                     todb=newname,
                                     fromhost=getenv("MONGO_HOST"))

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
    e = None

    url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/default.json'

    json_data = open(url)
    data = json.loads(json_data.read())

    form = CollectionForm(request.POST or None, initial={
        "dictionary": (json.dumps(data, indent=4))})

    if request.method == 'POST':
        if request.POST["action"] == 'Validate':

            if form.is_valid():

                collectionName = form.cleaned_data.get('collectionName')
                dictionary = form.cleaned_data.get('dictionary')

                Mycol = clientInstance[db][collectionName]

                try:
                    json.loads(dictionary)
                    e = "Validated, Go ahead and Insert this Document :)"
                except ValueError as ex:
                    e = ex

        if request.POST["action"] == 'Insert':

            if form.is_valid():
                collectionName = form.cleaned_data.get('collectionName')
                dictionary = form.cleaned_data.get('dictionary')

                Mycol = clientInstance[db][collectionName]

                if 'myfile' in request.FILES:
                    myfile = request.FILES['myfile']
                    contentfile = json.load(myfile)
                    try:
                        Mycol.insert_one(contentfile)
                    except:
                        Mycol.insert_many(contentfile)

                    url = reverse_lazy('showcollections', kwargs={'db': db})
                    return HttpResponseRedirect(url)
                elif dictionary != "":
                    try:
                        json.loads(dictionary)
                        Mycol.insert_one(json.loads(dictionary))
                        url = reverse_lazy(
                            'showcollections', kwargs={'db': db})
                        return HttpResponseRedirect(url)
                    except ValueError as ex:
                        e = ex

    context = {"form": form, "db": db, "e": e}
    return render(request, "side/add_collection.html", context)


@login_required
def _renamecollection(request, db, collection):
    clientInstance = clientpool[request.user.username]

    if request.method == 'POST':
        newname = request.POST.get["newname"]

        # print(newname)
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

    e = None
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

    if request.method == 'POST':

        if request.POST["action"] == 'Validate':

            if form.is_valid():

                dictionary = form.cleaned_data.get('dictionary')
                try:
                    json.loads(dictionary)
                    e = "Validated, Go ahead and Insert this Document :)"
                except ValueError as ex:
                    e = ex

        if request.POST["action"] == 'Insert':

            if form.is_valid():

                dictionary = form.cleaned_data.get('dictionary')
                if 'myfile' in request.FILES:
                    myfile = request.FILES['myfile']
                    contentfile = json.load(myfile)
                    collections.insert_one(contentfile)
                    url = reverse_lazy('showdocs', kwargs={
                        'db': db, 'collection': collection})
                    return HttpResponseRedirect(url)
                elif dictionary != "":
                    try:
                        json.loads(dictionary)
                        collections.insert_one(json.loads(dictionary))
                        url = reverse_lazy('showdocs', kwargs={
                            'db': db, 'collection': collection})
                        return HttpResponseRedirect(url)
                    except ValueError as ex:
                        e = ex

    context = {"db": db, "collection": collection, "form": form, "e": e}
    return render(request, "side/insert.html", context)


@login_required
def _insertdocumentBulk(request, db, collection):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)

    e = None
    form = DocumentForm(request.POST or None, request.FILES or None)

    #form = DocumentForm(request.POST or None)
    if request.method == 'POST':

        if request.POST["action"] == 'Validate':

            if form.is_valid():

                dictionary = form.cleaned_data.get('dictionary')
                try:
                    json.loads(dictionary)
                    e = "Validated, Go ahead and Insert this Document :)"

                except ValueError as ex:
                    e = ex

        if request.POST["action"] == 'Insert':

            if form.is_valid():

                dictionary = form.cleaned_data.get('dictionary')

                if 'myfile' in request.FILES:
                    myfile = request.FILES['myfile']
                    contentfile = json.load(myfile)
                    collections.insert_many(contentfile)
                    url = reverse_lazy('showdocs', kwargs={
                        'db': db, 'collection': collection})
                    return HttpResponseRedirect(url)
                elif dictionary != "":
                    try:
                        json.loads(dictionary)
                        collections.insert_many(json.loads(dictionary))
                        url = reverse_lazy('showdocs', kwargs={
                            'db': db, 'collection': collection})
                        return HttpResponseRedirect(url)
                    except ValueError as ex:
                        e = ex

    context = {"db": db, "collection": collection, "form": form, "e": e}
    return render(request, "side/insert.html", context)


@login_required
def _editdocument(request, db, collection, pk):
    clientInstance = clientpool[request.user.username]
    collections = get_collection_instance(clientInstance, db, collection)

    e = None
    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']
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
        if request.POST["action"] == 'Validate':

            if form.is_valid():

                dictionary = form.cleaned_data.get('dictionary')
                try:
                    json.loads(dictionary)
                    e = "Validated, Go ahead and Save this Document :)"
                except ValueError as ex:
                    e = ex

        if request.POST["action"] == 'Save':

            if form.is_valid():

                dictionary = form.cleaned_data.get('dictionary')
                try:
                    json.loads(dictionary)
                    dictionary = json.loads(dictionary)
                    collections.find_one_and_replace(query, dictionary)
                    url = reverse_lazy('showdocs', kwargs={
                        'db': db, 'collection': collection})
                    return HttpResponseRedirect(url)
                except ValueError as ex:
                    e = ex

    context = {"jsontext": jsontext, "db": db,
               "collection": collection, "form": form, "pk": pk, "primelist": primelist, "e": e}
    return render(request, "side/edit.html", context)
