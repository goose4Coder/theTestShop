from .views import *
from django.urls import path,include

urlpatterns = [
    path('', Site.view(Index),name='index'),
    path('products/<int:page_number>', Site.view(Products),name='index'),
]
