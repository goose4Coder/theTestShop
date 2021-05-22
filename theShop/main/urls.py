from .views import *
from django.urls import path, include

urlpatterns = [
    path('', Site.view(Index), name='index'),
    path('products/<int:page_number>/', Site.view(Products),name='view_products'),
    path('update_item/', Site.view(Update_Item),name='update_item'),
    path('register/', Site.view(Register), name='register'),
    path('login/', Site.view(Login), name='login'),
    path('activate/<uidb64>/<token>/', Site.view(Verification), name='activate'),
    path('captcha/', include('captcha.urls')),

]
