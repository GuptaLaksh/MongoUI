from . import views
from django.urls import path


from main.views import (
    showdbs,
    login_request,
    logout_request,
    showCollections,
    showdocs,
    _deletedocument,
    _viewdocument,
    _insertdocument,
    _deletecollection,
    _insertcollection,
    _deletedatabase,
    _insertdatabase

)

urlpatterns = [
    path('', views.showdbs, name="showdbs"),
    path('login/', views.login_request, name="login"),
    path('db/<db>', views.showCollections, name="showcollections"),
    path('db/<db>/<collection>', views.showdocs, name="showdocs"),
    path('logout/', views.logout_request, name='logout'),

    path('db/<db>/<collection>/<pk>/deletedocument',
         views._deletedocument, name='_deletedocument'),
    path('db/<db>/<collection>/<pk>/viewdocument',
         views._viewdocument, name='_viewdocument'),
    path('db/<db>/<collection>/insertdocument',
         views._insertdocument, name='_insertdocument'),
    path('db/<db>/<collection>/deletecollection/',
         views._deletecollection, name='_deletecollection'),
    path('db/<db>/insertcollection/',
         views._insertcollection, name='_insertcollection'),
    path('db/<db>/deletedatabase/',
         views._deletedatabase, name='_deletedatabase'),
    path('db/insertdatabase/',
         views._insertdatabase, name='_insertdatabase'),


]
