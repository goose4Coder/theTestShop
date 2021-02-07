from .views import *
from django.urls import path,include

urlpatterns = [
    path('', Site.view(index),name='index'),
]
