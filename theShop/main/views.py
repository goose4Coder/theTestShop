from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.core.paginator import Paginator
from .models import *

class Site():
    context='dataSet'
    def view(controller):
        return controller.as_view()

class Store(ListView):
    template_name='main/view_products.html'
    model=Product
    products=Product.objects.all()
    context_object_name=Site.context
    def get_queryset(self):
        paginator=Paginator(self.products,10)
        return paginator.get_page(self.kwargs['page_number'])
class Index(Store):
    def get_context_data(self,object_list=None,**kwargs):
        context= super().get_context_data(**kwargs)
        context['title']='home'
        return context
    def get_queryset(self):
        return Product.order_by('-price')[:5]
class Products(Store):
    def get_context_data(self,object_list=None,**kwargs):
        context= super().get_context_data(**kwargs)
        context['title']='Our products'
        return context
