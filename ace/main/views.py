from __future__ import unicode_literals
from platform import python_branch
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
from main.forms import CollectionForm, DatabaseForm, DocumentForm, QueryForm, newUserForm
from django.urls import reverse, reverse_lazy
from datetime import date
from main.models import User
from os import getenv
from pymongo import errors
import json
import csv
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage


class ContactWizard(SessionWizardView):
    def done(self, form_list, **kwargs):
        return render(self.request, 'done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })


@login_required
def logout_request(request):

    user = request.session.get('user')
    if user is None:
        return redirect('login')

    clientInstance = clientpool[user]
    clientInstance.close()
    clientpool[user] = None

    del request.session['user']
    # request.session.flush()
    messages.info(request, "Logout Succesfully!!")

    #messages.warning(request, "You are not logged in")

    return redirect('uilogin')


'''
@login_required
def _deleteuser(request, username):

    user = request.session.get('user')
    print(user)
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    primelist = ['micro_admin_user', 'micro_user', 'micro_usertest',
                 'ml_svc_mbad', 'ml_svc_mbap', 'ml_svc_mbcf', 'ml_svc_mbrt']

    if username not in primelist:
        try:
            print(username)
            #clientInstance.admin.command("dropUser", username)
        except errors.OperationFailure:
            pass

    return redirect('userspage')
'''


@login_required
def userlist_request(request):

    user = request.session.get('user')

    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    primelist = ['micro_admin_user', 'micro_user', 'micro_usertest',
                 'ml_svc_mbad', 'ml_svc_mbap', 'ml_svc_mbcf', 'ml_svc_mbrt']

    if request.method == "POST":

        if 'username' in request.POST:

            username = request.POST.get('username')
            print(request.POST)
            if username not in primelist:
                print(username)
                clientInstance.admin.command("dropUser", username)
                return redirect('userspage')

    dblist = []

    for dbx in clientInstance.list_databases():
        dblist.append(dbx['name'])

    userlist = []

    try:
        userinfo = clientInstance['admin'].command('usersInfo')
    except errors.OperationFailure:

        return redirect('showdbs')

    users = userinfo['users']

    idlist = []
    for identity in users:
        name = identity['user']
        roles = identity['roles']
        idlist.append((name, roles))

        #print(name, identity['roles'])

    # print(clientInstance['admin'].command('usersInfo'))

    context = {"userlist": userlist, "dbs": clientInstance.list_databases(),
               "current_user": user, "idlist": idlist, "primelist": primelist}
    # print(userlist)

    return render(request, "main/admin/userslist.html", context)


@login_required
def useredit_request(request, username):

    user = request.session.get('user')

    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    userinfo = clientInstance['admin'].command('usersInfo')

    users = userinfo['users']

    idlist = {}
    for identity in users:
        name = identity['user']
        roles = identity['roles']
        idlist[name] = roles

    dblist = []

    for dbx in clientInstance.list_databases():
        dblist.append(dbx['name'])

    print("idlist:", idlist)
    rolesss = idlist[username]

    selected = {}

    for db in dblist:
        selected[db] = []

    for rol in rolesss:
        if rol['db'] in selected.keys():
            selected[rol['db']].append(rol['role'])

    print("selected:", selected)

    if request.method == 'POST':

        dbs = clientInstance.list_databases()

        roles = []
        for db in dbs:
            db_name = db['name']
            name = 'readWrite-'+str(db_name)
            name1 = 'read-'+str(db_name)
            name2 = 'dbAdmin-'+str(db_name)
            type = request.POST.get(name)
            type1 = request.POST.get(name1)
            type2 = request.POST.get(name2)

            if type == 'on':
                roles.append({'role': 'readWrite', 'db': db_name})
            if type1 == 'on':
                roles.append({'role': 'read', 'db': db_name})
            if type2 == 'on':
                roles.append({'role': 'dbAdmin', 'db': db_name})

        clientInstance.admin.command("updateUser", username, roles=roles)

        return redirect('userspage')

    context = {"dbs": dblist,
               "current_user": user, "username": username, "selected": selected}
    return render(request, "main/admin/user_edit.html", context=context)


@login_required
def create_user_request(request):

    user = request.session.get('user')
    print(user)
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    # if user do not have permission redirect to showdbs
    # if not admin:
    #    return redirect('showdbs')

    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']

    form = newUserForm(request.POST or None)

    print(request.POST)
    if request.method == 'POST':

        newUser = request.POST.get('newUser')
        pwd = request.POST.get('pwd')

        dbs = clientInstance.list_databases()

        roles = []
        for db in dbs:
            db_name = db['name']
            name = 'readWrite-'+str(db_name)
            name1 = 'read-'+str(db_name)
            name2 = 'dbAdmin-'+str(db_name)
            type = request.POST.get(name)
            type1 = request.POST.get(name1)
            type2 = request.POST.get(name2)
            if type == 'on':
                roles.append({'role': 'readWrite', 'db': db_name})

            if type1 == 'on':
                roles.append({'role': 'read', 'db': db_name})

            if type2 == 'on':
                roles.append({'role': 'dbAdmin', 'db': db_name})

        clientInstance.admin.command(
            'createUser', newUser,
            pwd=pwd,
            roles=roles
        )

        return redirect('userspage')

    context = {"dbs": clientInstance.list_databases(), "form": form,
               "current_user": user, "primelist": primelist}
    return render(request, "main/admin/create_user.html", context=context)


@login_required
def login_request(request):
    if request.session.get('user') is not None:
        return redirect('showdbs')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        clientInstance = get_db_handle(username, password)
        print(clientInstance)

        if clientInstance is not None:
            try:
                check_user = User.objects.get(username=username)
            except:
                check_user = User.objects.create(username=username)

            print(check_user)

            request.session['user'] = username
            clientpool[username] = clientInstance

            params = {"current_user": username}
            return redirect('showdbs')
        else:
            messages.error(request, 'Please enter valid Username or Password.')

    return render(request, 'main/login.html')


@login_required
def showdbs(request):
    user = request.session.get('user')
    print(user)
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    baseHref = reverse_lazy('showdbs')

    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']

    if request.method == "POST":

        db = request.POST.get('db')
        if db not in primelist:
            try:
                clientInstance.drop_database(db)
            except errors.OperationFailure:
                messages.warning("You don't have authorized permissions!")
                return redirect('showdbs')

    context = {"baseHref": baseHref, "dbs": clientInstance.list_databases(
    ), "primelist": primelist, "current_user": user}
    return render(request, "main/database.html", context=context)


@login_required
def showCollections(request, db):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]
    collectionlist = []
    tuplist = []
    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']

    if request.method == "POST":

        if 'collection' in request.POST:

            if db not in primelist:

                collection = request.POST.get('collection')

                try:
                    clientInstance[db].drop_collection(collection)
                except errors.OperationFailure:
                    messages.warning("You don't have authorized permissions!")
                    return redirect('showcollections', db=db)

    for collection in clientInstance[db].list_collection_names():
        collectionlist.append((collection, clientInstance[db][collection]))

    for collection, instance in collectionlist:
        tuplist.append(
            dict({'name': collection, 'count': instance.estimated_document_count()}))

    context = {"dbs": clientInstance.list_databases(),
               "db": db, "tuplist": tuplist, "primelist": primelist, "current_user": user}

    return render(request, "main/pagecollection.html", context=context)


@login_required
def showdocs(request, db, collection):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    collections = get_collection_instance(clientInstance, db, collection)
    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']

    newdblist = ['Microbot_LookupsDB', 'Microbot_MappingsDB']
    dblist = []

    scroll_list = []

    for dbx in clientInstance.list_databases():
        dblist.append(dbx['name'])
        # print(dbx)

    # print(dblist)

    for dbx in dblist:
        scroll_list.append(
            (dbx, list(clientInstance[dbx].list_collection_names())))

    documents = collections.find({})
    tuplist1 = []

    for document in documents:
        tuplist1.append((document['_id'], document))

    # print("tuplist:", tuplist)

    doclist1 = []
    for id, doc in tuplist1:
        doclist1.append(doc)

    print("doclist1:", doclist1)

    keylist1 = []

    for doc in doclist1:
        for key in doc.keys():
            if key not in keylist1:
                keylist1.append(key)

    print("keylist1:", keylist1)
    custlist = []
    if db in newdblist:

        for doc in doclist1:
            custlist.append(doc['customer_id'])

        print("custlist:", custlist)

    grouplist = []

    if db in ['Microbot_LookupsDB']:
        for doc in doclist1:
            grouplist.append(doc['group'])

    documents = collections.find({})
    query = None

    key = request.GET.get('key' or None)
    value = request.GET.get('value' or None)
    query = request.GET.get('query' or None)
    projection = request.GET.get('projection' or None)
    customer_id = request.GET.get('customer_id' or None)
    group = request.GET.get('group' or None)
    format = request.GET.get('format')

    print("rg:", request.GET)

    print(request.GET.get('key'))
    print(request.GET.get('value'))
    print(request.GET.get('query'))
    print(request.GET.get('projection'))
    print(request.GET.get('customer_id'))
    print(request.GET.get('group'))

    querydict = {}
    if key is not None:
        querydict[key] = value

    if customer_id is not None:
        querydict['customer_id'] = customer_id

    if group is not None:
        querydict['group'] = group

    print("qd:", querydict)

    if query == None and querydict != {}:
        documents = collections.find(querydict, projection)
        # elif query != None and querydict != {}:
    #documents = collections.find({"$and": [querydict, query]}, projection)

    print("key", key)
    form = QueryForm(request.POST or None, initial={
        "key": key, "value": value, "query": query, "projection": projection})

    print("rp:", request.POST)

    print(request.POST)

    if request.method == 'POST':

        if 'ids[]' in request.POST:

            ids = request.POST.getlist('ids[]')

            queries = []

            for id in ids:
                try:
                    query = {"_id": ObjectId(id)}
                except InvalidId:
                    query = {"_id": (id)}

                queries.append(query)

            for query in queries:
                collections.find_one_and_delete(query)
                print("multidelete")

            return redirect('showdocs', db=db, collection=collection)

        if 'id' in request.POST:

            id = request.POST.get('id')
            try:
                query = {"_id": ObjectId(id)}
            except InvalidId:
                query = {"_id": (id)}

            # print(query)

            try:
                collections.find_one_and_delete(query)
            except errors.OperationFailure:
                return redirect('showdocs', db=db, collection=collection)

        if 'export' in request.POST:
            format = request.POST.get('format')
            url = reverse_lazy('showdocs', kwargs={
                "db": db, "collection": collection}) + "?" + "&format=" + format

            mongo_docs = []
            for document in documents:
                mongo_docs.append(document)

            # print(mongo_docs)

            if format == "CSV":
                response = HttpResponse(content_type='text/csv')
                writer = csv.writer(response)
                writer.writerow(mongo_docs)
                datetoday = str(date.today())
                fname = "" + collection + "_" + datetoday + ".csv"
                # print(fname)
                response['Content-Disposition'] = 'attachement; filename="{}"'.format(
                    fname)
                return response
            elif format == "JSON":

                json_data = json.dumps(mongo_docs, default=str)
                datetoday = str(date.today())
                fname = "" + collection + "_" + datetoday + ".json"
                # print(fname)
                response = HttpResponse(
                    json_data, content_type='text/json')
                response['Content-Disposition'] = 'attachement; filename="{}"'.format(
                    fname)

                return response

        elif 'find' in request.POST:

            if form.is_valid():
                key = form.cleaned_data.get('key')
                value = form.cleaned_data.get('value')
                query = form.cleaned_data.get('query')
                projection = form.cleaned_data.get('projection')
                customer_id = request.POST.get('customer_id' or None)
                group = request.POST.get('group' or None)

                url = reverse_lazy('showdocs', kwargs={
                    "db": db, "collection": collection}) + "?"

                if key != "":
                    url = url + "key=" + key + "&"

                if value != "":
                    url = url + "value=" + value + "&"

                if customer_id != None:
                    url = url + "customer_id=" + customer_id + "&"

                if group != None:
                    url = url + "group=" + group + "&"

                if query != "":
                    url = url + "query=" + query + "&"

                if projection != "":
                    url = url + "projection=" + projection

                print(url)
                return redirect(url)

    tuplist = []

    for document in documents:
        tuplist.append((document['_id'], document))

    # print("tuplist:", tuplist)

    doclist = []
    for id, doc in tuplist:
        doclist.append(doc)
    # print("doclist:", doclist)

    keylist = []

    for doc in doclist:
        for key in doc.keys():
            if key not in keylist:
                keylist.append(key)

    keylist.sort()
    # print("keylist:", keylist)

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

    # print("doclist:", doclist)
    # print("doclistnew:", doclistnew)

    context = {"count": len(doclistnew), "scroll_list": scroll_list, "form": form, "dbs": clientInstance.list_databases(), "db": db, "collection": collection,
               "tuplist": tuplistnew, "primelist": primelist, "keylist": keylist, "doclist": doclistnew, "current_user": user, "custlist": custlist,
               "grouplist": grouplist, "customer_id": customer_id, "group": group}

    print(request.POST)
    return render(request, "main/documents.html", context=context)


'''def _searchdocs(request, db, collection):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    collections = get_collection_instance(clientInstance, db, collection)
    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']

    dblist = []

    scroll_list = []

    for dbx in clientInstance.list_databases():
        dblist.append(dbx['name'])
        # print(dbx)

    # print(dblist)

    for dbx in dblist:
        scroll_list.append(
            (dbx, list(clientInstance[dbx].list_collection_names())))

    documents = collections.find({})
    query = None

    form = QueryForm(request.POST or None)

    if request.method == "POST":
        option = request.POST.get('options')

        mongo_docs = []
        for document in documents:
            mongo_docs.append(document)

        # print(mongo_docs)

        if option == "CSV":
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            writer.writerow(mongo_docs)
            datetoday = str(date.today())
            fname = "" + collection + "_" + datetoday + ".csv"
            # print(fname)
            response['Content-Disposition'] = 'attachement; filename="{}"'.format(
                fname)
            return response
        elif option == "JSON":

            json_data = json.dumps(mongo_docs, default=str)
            datetoday = str(date.today())
            fname = "" + collection + "_" + datetoday + ".json"
            # print(fname)
            response = HttpResponse(
                json_data, content_type='text/json')
            response['Content-Disposition'] = 'attachement; filename="{}"'.format(
                fname)

            return response

    tuplist = []

    for document in documents:
        tuplist.append((document['_id'], document))

    # print("tuplist:", tuplist)

    doclist = []
    for id, doc in tuplist:
        doclist.append(doc)
    # print("doclist:", doclist)

    keylist = []

    for doc in doclist:
        for key in doc.keys():
            if key not in keylist:
                keylist.append(key)

    keylist.sort()
    # print("keylist:", keylist)

    for key in keylist:
        for doc in doclist:
            if key not in doc:
                doc[key] = ""
    custlist = []
    if 'customer_id' in keylist:

        for doc in doclist:
            custlist.append(doc['customer_id'])

        #print("custlist:", custlist)

    grouplist = []

    if 'group' in keylist:

        for doc in doclist:
            grouplist.append(doc['group'])
    doclistnew = []
    for doc in doclist:
        doc1 = sorted(doc.items())
        doclistnew.append(dict(doc1))

    tuplistnew = []
    for doc in doclistnew:
        tuplistnew.append((doc["_id"], doc))

    context = {"scroll_list": scroll_list, "form": form, "dbs": clientInstance.list_databases(), "db": db, "collection": collection,
               "tuplist": tuplistnew, "primelist": primelist, "keylist": keylist, "doclist": doclistnew, "current_user": user, "custlist": custlist,
               "grouplist": grouplist}
    return render(request, "main/documents.html", context)'''


'''
@login_required
def _deletedatabase(request, db):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    primelist = ['Microbot_AuthUsersDB', 'Microbot_LookupsDB',
                 'Microbot_MappingsDB', 'Microbot_ProcessLogsDB', 'admin', 'config', 'local']

    if db not in primelist:
        try:
            clientInstance.drop_database(db)
        except errors.OperationFailure:
            messages.warning("You don't have authorized permissions!")
            return redirect('showdbs')

    return redirect('showdbs')
'''


@login_required
def _insertdatabase(request):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]
    e = None
    data = {}

    url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/default.json'

    json_data = open(url)
    contentfile = json.loads(json_data.read())

    filename = request.GET.get('preview')
    dbname = request.GET.get('dbname')
    colname = request.GET.get('colname')

    print("filename:", filename)
    fss = FileSystemStorage()
    print("fss:", fss)
    if filename is not None:
        file = fss.open(filename)
        contentfile = json.load(file)
        print("contentfile:", contentfile)

    form = DatabaseForm(request.POST or None, request.FILES or None, initial={
        "databaseName": dbname, "collectionName": colname,
        "dictionary": json.dumps(contentfile, indent=4)})

    if request.method == 'POST':

        if request.POST["action"] == 'Preview':

            if form.is_valid():

                databaseName = form.cleaned_data.get('databaseName')
                collectionName = form.cleaned_data.get('collectionName')
                database = clientInstance[databaseName]
                collection = database[collectionName]

                if 'myfile' in request.FILES:
                    if request.method == 'POST':
                        myfile = request.FILES['myfile']
                        fss = FileSystemStorage()
                        file = fss.save(myfile.name, myfile)
                        file_url = fss.url(file)
                        print(myfile.name)
                        print(file_url)

                    url = reverse_lazy('_insertdatabase')
                    url = url + '?dbname=' + databaseName + '&colname=' + \
                        collectionName + '&preview=' + str(myfile.name)
                    return HttpResponseRedirect(url)

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

                filename = request.GET.get('preview')
                databaseName = form.cleaned_data.get('databaseName')
                collectionName = form.cleaned_data.get('collectionName')
                dictionary = form.cleaned_data.get('dictionary')
                databaseName = clientInstance[databaseName]
                collection = databaseName[collectionName]

                if dictionary != "":
                    try:
                        json.loads(dictionary)
                        try:
                            try:
                                collection.insert_one(json.loads(dictionary))
                            except TypeError:
                                collection.insert_many(json.loads(dictionary))

                            if filename is not None:
                                fss = FileSystemStorage()
                                uploadpath = fss.path(filename)
                                print("up:", uploadpath)
                                fss.delete(uploadpath)

                        except errors.OperationFailure:
                            return redirect('showdbs')
                        url = reverse_lazy('showdbs')
                        return HttpResponseRedirect(url)
                    except ValueError as ex:
                        e = ex

    context = {"form": form, "e": e, "current_user": user}
    return render(request, "side/add_database.html", context)


@login_required
def _renamedatabase(request, db):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]
    if request.method == 'POST':

        newname = request.POST.get('newname')
        print(newname)

        clientInstance.admin.command('copydb',
                                     fromdb=db,
                                     todb=newname,
                                     fromhost=getenv("MONGO_HOST"))

    return redirect('showdbs')


'''
@login_required
def _deletecollection(request, db, collection):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]
    try:
        clientInstance[db].drop_collection(collection)
    except errors.OperationFailure:
        messages.warning("You don't have authorized permissions!")
        return redirect('showcollections', db=db)

    return redirect('showcollections', db=db)
'''


@login_required
def _insertcollection(request, db):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    data = {}
    e = None

    url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/default.json'

    json_data = open(url)
    contentfile = json.loads(json_data.read())

    filename = request.GET.get('preview')

    colname = request.GET.get('colname')

    fss = FileSystemStorage()

    if filename is not None:
        file = fss.open(filename)
        contentfile = json.load(file)
        print("contentfile:", contentfile)

    form = CollectionForm(request.POST or None, request.FILES or None, initial={
        "collectionName": colname,
        "dictionary": json.dumps(contentfile, indent=4)})

    if request.method == 'POST':
        if request.POST["action"] == 'Preview':

            if form.is_valid():

                collectionName = form.cleaned_data.get('collectionName')
                Mycol = clientInstance[db][collectionName]

                if 'myfile' in request.FILES:
                    if request.method == 'POST':
                        myfile = request.FILES['myfile']
                        fss = FileSystemStorage()
                        file = fss.save(myfile.name, myfile)
                        file_url = fss.url(file)
                        print(myfile.name)
                        print(file_url)

                    url = reverse_lazy('_insertcollection', kwargs={'db': db})
                    url = url + '?colname=' + collectionName + \
                        '&preview=' + str(myfile.name)
                    return HttpResponseRedirect(url)

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

                filename = request.GET.get('preview')
                collectionName = form.cleaned_data.get('collectionName')
                dictionary = form.cleaned_data.get('dictionary')

                Mycol = clientInstance[db][collectionName]

                if dictionary != "":
                    try:
                        json.loads(dictionary)
                        try:
                            try:
                                Mycol.insert_one(json.loads(dictionary))
                            except TypeError:
                                Mycol.insert_many(json.loads(dictionary))

                            if filename is not None:
                                fss = FileSystemStorage()
                                uploadpath = fss.path(filename)
                                print(filename)
                                print("up:", uploadpath)
                                fss.delete(uploadpath)

                        except errors.OperationFailure:
                            url = reverse_lazy(
                                'showcollections', kwargs={'db': db})
                            return HttpResponseRedirect(url)
                        url = reverse_lazy(
                            'showcollections', kwargs={'db': db})
                        return HttpResponseRedirect(url)
                    except ValueError as ex:
                        e = ex

    context = {"form": form, "db": db, "e": e, "current_user": user}
    return render(request, "side/add_collection.html", context)


@login_required
def _renamecollection(request, db, collection):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]

    if request.method == 'POST':
        newname = request.POST.get["newname"]

        # print(newname)
        clientInstance[db][collection].rename(newname)

    return redirect('showcollections', db=db)


'''
@login_required
def _deletedocument(request, db, collection, pk):
    print(request.POST)
    user = request.session.get('user')
    if user is None:
        return redirect('login')

    clientInstance = clientpool[user]
    collections = get_collection_instance(clientInstance, db, collection)

    try:
        query = {"_id": ObjectId(pk)}
    except InvalidId:
        query = {"_id": (pk)}

    print(query)

    try:
        collections.find_one_and_delete(query)
        print("working...")
    except errors.OperationFailure:
        messages.warning("You don't have access")
        return redirect('showdocs', db=db, collection=collection)

    return redirect('showdocs', db=db, collection=collection)
'''


def _deletemultidocument(request, db, collection):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]
    collections = get_collection_instance(clientInstance, db, collection)

    if request.method == 'POST':

        ids = request.POST.getlist('ids[]')

        queries = []

        for id in ids:
            try:
                query = {"_id": ObjectId(id)}
            except InvalidId:
                query = {"_id": (id)}

            queries.append(query)

        for query in queries:
            collections.find_one_and_delete(query)
            print("multidelete")

        return redirect('showdocs', db=db, collection=collection)

    return redirect('showdocs', db=db, collection=collection)


@login_required
def _viewdocument(request, db, collection, pk):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]
    collections = get_collection_instance(clientInstance, db, collection)

    try:
        query = {"_id": ObjectId(pk)}
    except InvalidId:
        query = {"_id": (pk)}

    print("Query:", query)
    jsontext = collections.find_one(query)
    print(jsontext)

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
               "collection": collection, "pk": pk, "current_user": user}
    return render(request, "side/views.html", context)


@login_required
def _insertdocument(request, db, collection):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]
    collections = get_collection_instance(clientInstance, db, collection)

    e = None
    data = {}

    url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/' + collection + '.json'

    try:
        json_data = open(url)
    except FileNotFoundError:
        url = '/home/itpauser/donkeyUI/ace/static/mappingTemplates/default.json'
        json_data = open(url)

    contentfile = json.loads(json_data.read())

    filename = request.GET.get('preview')

    fss = FileSystemStorage()

    if filename is not None:
        file = fss.open(filename)
        contentfile = json.load(file)
        print("contentfile:", contentfile)

    form = DocumentForm(request.POST or None, request.FILES or None, initial={
                        "dictionary": (json.dumps(contentfile, indent=4))})

    if request.method == 'POST':

        if request.POST["action"] == 'Preview':

            if form.is_valid():

                if 'myfile' in request.FILES:
                    if request.method == 'POST':
                        myfile = request.FILES['myfile']
                        fss = FileSystemStorage()
                        file = fss.save(myfile.name, myfile)
                        file_url = fss.url(file)
                        print(myfile.name)
                        print(file_url)

                    url = reverse_lazy('_insertdocument', kwargs={
                        'db': db, 'collection': collection})
                    url = url + '?preview=' + str(myfile.name)
                    return HttpResponseRedirect(url)

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

                filename = request.GET.get('preview')
                dictionary = form.cleaned_data.get('dictionary')

                if dictionary != "":
                    try:
                        json.loads(dictionary)
                        try:
                            try:
                                collections.insert_one(json.loads(dictionary))
                            except TypeError:
                                collections.insert_many(json.loads(dictionary))

                            if filename is not None:
                                fss = FileSystemStorage()
                                uploadpath = fss.path(filename)
                                print(filename)
                                print("up:", uploadpath)
                                fss.delete(uploadpath)

                        except errors.OperationFailure:
                            url = reverse_lazy('showdocs', kwargs={
                                'db': db, 'collection': collection})
                            return HttpResponseRedirect(url)
                        url = reverse_lazy('showdocs', kwargs={
                            'db': db, 'collection': collection})
                        return HttpResponseRedirect(url)
                    except ValueError as ex:
                        e = ex

    context = {"db": db, "collection": collection,
               "form": form, "e": e, "current_user": user}
    return render(request, "side/insert.html", context)


'''
@login_required
def _insertdocumentBulk(request, db, collection):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]
    collections = get_collection_instance(clientInstance, db, collection)

    e = None

    contentfile = []

    filename = request.GET.get('preview')

    fss = FileSystemStorage()

    if filename is not None:
        file = fss.open(filename)
        contentfile = json.load(file)
        print("contentfile:", contentfile)

    form = DocumentForm(request.POST or None, request.FILES or None, initial={
                        "dictionary": (json.dumps(contentfile, indent=4))})

    # form = DocumentForm(request.POST or None)
    if request.method == 'POST':
        if request.POST["action"] == 'Preview':

            if form.is_valid():

                if 'myfile' in request.FILES:
                    if request.method == 'POST':
                        myfile = request.FILES['myfile']
                        fss = FileSystemStorage()
                        file = fss.save(myfile.name, myfile)
                        file_url = fss.url(file)
                        print(myfile.name)
                        print(file_url)

                    url = reverse_lazy('_insertdocumentBulk', kwargs={
                        'db': db, 'collection': collection})
                    url = url + '?preview=' + str(myfile.name)
                    return HttpResponseRedirect(url)

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
                filename = request.GET.get('preview')
                if dictionary != "":
                    try:
                        json.loads(dictionary)
                        try:
                            try:
                                collections.insert_many(json.loads(dictionary))
                            except TypeError:
                                e = "You have a single document as an input. Try inserting single document instead!"
                                url = reverse_lazy('_insertdocumentBulk', kwargs={
                                    'db': db, 'collection': collection})
                                return HttpResponseRedirect(url)

                            if filename is not None:
                                fss = FileSystemStorage()
                                uploadpath = fss.path(filename)
                                print(filename)
                                print("up:", uploadpath)
                                fss.delete(uploadpath)

                        except errors.OperationFailure:
                            url = reverse_lazy('showdocs', kwargs={
                                'db': db, 'collection': collection})
                            return HttpResponseRedirect(url)
                        url = reverse_lazy('showdocs', kwargs={
                            'db': db, 'collection': collection})
                        return HttpResponseRedirect(url)
                    except ValueError as ex:
                        e = ex
    context = {"db": db, "collection": collection,
               "form": form, "e": e, "current_user": user}
    return render(request, "side/insert.html", context)
'''


@login_required
def _editdocument(request, db, collection, pk):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    clientInstance = clientpool[user]
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

    # form = DocumentForm(request.POST or None)

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
               "collection": collection, "form": form, "pk": pk, "primelist": primelist, "e": e, "current_user": user}
    return render(request, "side/edit.html", context)
