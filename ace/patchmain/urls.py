from . import views
from django.urls import path


from patchmain.views import (
    patch_login_request,
    patch_home_request,
    patch_logout_request,
    patch_admin_request,

)

urlpatterns = [

    path('patchlogin/', views.patch_login_request, name="patchlogin"),
    path('patchadmin/', views.patch_admin_request, name="patchadmin"),
    path('patchlogout/', views.patch_logout_request, name='patchlogout'),
    path('', views.patch_home_request, name='patchhome'),


]
