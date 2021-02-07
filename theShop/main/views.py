from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import *

class Site():
    context='dataSet'
    def view(controller):
        return controller.as_view()

class Store(ListView):
    template_name='main/view_products.html'
    model=Product
    context_object_name=Site.context

class index(Store):
    def get_context_data(self,object_list=None,**kwargs):
        context= super().get_context_data(**kwargs)
        context['title']='home'
        return context
