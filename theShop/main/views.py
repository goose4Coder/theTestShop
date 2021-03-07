from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, View
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import *
from .utils import cartData
import json


class Site():
    context = 'dataSet'
    def view(controller):
        return controller.as_view()


class Store(ListView):
    template_name = 'main/view_products.html'
    title = ""
    model = Product
    products = Product.objects.all()
    context_object_name = Site.context

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = cartData(self.request)
        context['title'] = self.title
        context['user'] = self.request.user
        context['cart_items'] = cart['cart_items']
        context['order'] = cart['order']
        context['items'] = cart['items']
        return context

    def get_queryset(self):
        paginator = Paginator(self.products, 10)
        return paginator.get_page(self.kwargs['page_number'])


class Index(Store):
    title = "Home"
    def get_queryset(self):
        return Product.objects.order_by('-price')[:6]


class Products(Store):
    title = "Our products"


class Update_Item(View):
    def post(self,request, **kwargs):
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']
        customer = request.user.customer
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

        orderItem, created = OrderItem.objects.get_or_create(
            order=order, product=product)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        return JsonResponse('Item was added', safe=False)
