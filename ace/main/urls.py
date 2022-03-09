from . import views
from django.urls import path

from main.views import (
    showdbs,
    login_request,
    logout_request,
    showCollections,
    showdocs
)

urlpatterns = [
    path('', views.showdbs, name="showdbs"),
    path('login/', views.login_request, name="login"),
    path('db/<db>', views.showCollections, name="showcollections"),
    path('db/<db>/<collection>', views.showdocs, name="showdocs"),
    path('logout/', views.logout_request, name='logout'),
    path('test/', views.test, name='test')
]
