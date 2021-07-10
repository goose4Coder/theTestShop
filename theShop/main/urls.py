from .views import *
from django.urls import path, include

urlpatterns = [
    path('', Site.view(Index), name='index'),
    path('products/<page_number>/', Site.view(Products),name='view_products'),
    path('update_item/', Site.view(Update_Item), name='update_item'),
    path('register/', Site.view(Register), name='register'),
    path('login/', Site.view(Login), name='login'),
    path('cart/', Site.view(Cart_Page), name='cart'),
    path('checkout/', Site.view(Checkout), name='checkout'),
    path('shipping/', Site.view(Shipping), name='shipping'),
    path('stripe_config/', Site.view(Stripe_Config), name='stripe_config'),
    path('create_checkout_session/', Site.view(Create_Checkout_Session), name='create_checkout_session'),
    path('stripe_result/<str:result>/', Site.view(Stripe_Result), name='stripe_result'),
    path('activate/<uidb64>/<token>/', Site.view(Verification), name='activate'),
    path('captcha/', include('captcha.urls')),

]
