from django.http.response import HttpResponse
from django.shortcuts import render,HttpResponse


# Create your views here.

def index(request):
    return render(request, 'index/index.html')

def about(request):
    return render(request, 'index/about.html')