from django.shortcuts import render
from django.shortcuts import redirect

# Create your views here.


def uilogin_request(request):
    return render(request, "uimain/uilogin.html")


def uilogout_request(request):

    return redirect('uilogin')


def uihome_request(request):

    return render(request, "uimain/uihome.html")
