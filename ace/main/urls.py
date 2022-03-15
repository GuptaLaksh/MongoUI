from . import views
from django.urls import path


from main.views import (
    showdbs,
    login_request,
    logout_request,
    showCollections,
    showdocs,
    _delete,
    _view,
)

urlpatterns = [
    path('', views.showdbs, name="showdbs"),
    path('login/', views.login_request, name="login"),
    path('db/<db>', views.showCollections, name="showcollections"),
    path('db/<db>/<collection>', views.showdocs, name="showdocs"),
    path('logout/', views.logout_request, name='logout'),
    path('<db>/<collection>/<pk>/delete', views._delete, name='_delete'),
    path('<db>/<collection>/<pk>/view', views._view, name='_view'),
    path('<db>/<collection>/<pk>/insert', views._insert, name='_insert'),


]
