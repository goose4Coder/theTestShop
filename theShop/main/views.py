from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.views.generic import ListView, DetailView, CreateView, View, CreateView, FormView
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text, force_bytes
from .models import *
from .utils import cartData
from .forms import CustomUserForm, CustomLoginForm
from .token_generator import account_activation_token
import json


class Site:
    context = 'dataSet'

    def view( controller):
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
    def post(self, request, **kwargs):
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


class Register(CreateView):
    template_name = 'main/register_login.html'
    form_class = CustomUserForm
    title = "Sign up"
    success_url = '/'

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = cartData(self.request)
        context['title'] = self.title
        context['user'] = self.request.user
        context['cart_items'] = cart['cart_items']
        context['order'] = cart['order']
        context['items'] = cart['items']
        context['name'] = 'Sign up'
        return context

    def form_valid(self, form):
        returnValue = super().form_valid(form)
        user = form.save()
        user.is_active = False
        token = account_activation_token.make_token(user)
        user.save()
        message = render_to_string('main/message.html', {'User': user, 'domain': get_current_site(self.request), 'token': token, 'uid': urlsafe_base64_encode(force_bytes(user.id)), })
        send_mail('confirmation_link', message, from_email=None, recipient_list=[str(user.email)], fail_silently=True)
        return returnValue


class Login(FormView):
    title = "Sign in"
    template_name = "main/register_login.html"
    form_class = CustomLoginForm
    success_url = reverse_lazy('index', kwargs={})

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = cartData(self.request)
        context['title'] = self.title
        context['user'] = self.request.user
        context['cart_items'] = cart['cart_items']
        context['order'] = cart['order']
        context['items'] = cart['items']
        context['name'] = 'Sign in'
        return context

    def form_valid(self, form):
        user = User.objects.get(username=form.cleaned_data['username'])
        if form.is_valid():
            if user is not None:
                login(self.request, user)

        return super().form_valid(form)


class Verification(View):
    def get(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, kwargs['token']):
            verification_message = 'Thank you for your email confirmation. Now you can login your account.'
            succes = True
        else:
            verification_message = 'Activation link is invalid!'
            succes = False
        if succes:
            user.is_active = True
            user.save()
        cart = cartData(self.request)
        return render(request, 'main/confirm_template.html', {'message': verification_message, 'succes': succes, 'cart_items': cart['cart_items']})


