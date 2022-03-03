from . import views
from django.urls import path

urlpatterns = [
    path('',views.showdbs,name="showdbs"),
    #path('',views.index,name='index'),
    #path('register',views.register,name='register')

    path('login/',views.login,name="login"),
    path('db/<db>',views.showCollections,name="base"),
    path('logout/',views.logout,name='logout')
    #path('tezt/',views.tezt,name="tezt")
]
