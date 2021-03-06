from . import views
from django.urls import path


from main.views import (
    login_request,

    showdbs,
    showCollections,
    showdocs,


    _insertdatabase,
    _renamedatabase,


    _insertcollection,
    _renamecollection,

    userlist_request,
    create_user_request,
    useredit_request,


    _deletemultidocument,
    _viewdocument,
    _editdocument,
    _insertdocument,


    logout_request,

)

urlpatterns = [


    path('login/', views.login_request, name="login"),
    path('users/', views.userlist_request, name="userspage"),
    path('users/createuser/', views.create_user_request, name="usercreation"),
    path('users/<username>/', views.useredit_request, name="user_edit"),
    #path('users/<username>/deleteuser', views._deleteuser, name="user_del"),


    path('', views.showdbs, name="showdbs"),
    path('db/<db>/', views.showCollections, name="showcollections"),
    path('db/<db>/<collection>/', views.showdocs, name="showdocs"),


    #path('db/<db>/deletedatabase',views._deletedatabase, name='_deletedatabase'),
    path('db/<db>/renamedatabase',
         views._renamedatabase, name='_renamedatabase'),
    path('db/insertdatabase',
         views._insertdatabase, name='_insertdatabase'),

    #path('db/<db>/<collection>/deletecollection',views._deletecollection, name='_deletecollection'),
    path('db/<db>/insertcollection',
         views._insertcollection, name='_insertcollection'),
    path('db/<db>/<collection>/renamecollection',
         views._renamecollection, name='_renamecollection'),



    #path('db/<db>/<collection>/<pk>/deletedocument/',views._deletedocument, name='_deletedocument'),
    #path('db/<db>/<collection>/deletemultidocument/',views._deletemultidocument, name='_deletemultidocument'),

    path('db/<db>/<collection>/<pk>/viewdocument/',
         views._viewdocument, name='_viewdocument'),
    path('db/<db>/<collection>/<pk>/editdocument/',
         views._editdocument, name='_editdocument'),
    path('db/<db>/<collection>/insertdocument/',
         views._insertdocument, name='_insertdocument'),
    #path('db/<db>/<collection>/insertdocumentBulk/',views._insertdocumentBulk, name='_insertdocumentBulk'),

    path('logout/', views.logout_request, name='logout'),



]
