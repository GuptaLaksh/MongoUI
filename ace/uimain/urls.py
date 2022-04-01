
from . import views
from django.urls import path

from uimain.views import (
    uilogin_request,
    uihome_request,
    uilogout_request

)

urlpatterns = [

    path('uilogin/', views.uilogin_request, name="uilogin"),
    path('', views.uihome_request, name="uihome"),
    path('uilogout/', views.uilogout_request, name='uilogout')
]
