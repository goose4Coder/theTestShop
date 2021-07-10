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
from django.contrib import messages
from django.conf import settings
from .models import *
from .utils import cartData
from .forms import CustomUserForm, CustomLoginForm, ShippingForm
from .token_generator import account_activation_token
import json
import stripe


class Site:
    context = 'dataSet'

    def view(controller):
        return controller.as_view()


class Store(ListView):
    template_name = 'main/view_products.html'
    title = ""
    model = Product
    products = Product.objects.order_by("price")
    context_object_name = Site.context
    num=False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            cart = cartData(self.request)
        except:
            if self.request.user.is_authenticated:
                Customer.objects.get_or_create(user=self.request.user)
                cart = cartData(self.request)
        context['title'] = self.title
        context['user'] = self.request.user
        context['cart_items'] = cart['cart_items']
        context['order'] = cart['order']
        context['items'] = cart['items']
        if self.num:
            context['number_plus'] = int(self.kwargs['page_number'])+1
            context['number_minus'] = int(self.kwargs['page_number']) - 1
        return context

    def get_queryset(self):
        paginator = Paginator(self.products, 1)
        return paginator.page(self.kwargs['page_number'])


class Index(Store):
    title = "Home"

    def get_queryset(self):
        return Product.objects.order_by('-price')[:6]


class Products(Store):
    num = True
    title = "Our products"


class Cart_Page(ListView):
    title = "cart"
    model = Product
    template_name = "main/cart.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            cart = cartData(self.request)
        except:
            if self.request.user.is_authenticated:
                Customer.objects.get_or_create(user=self.request.user)
                cart = cartData(self.request)
        context['title'] = self.title
        context['user'] = self.request.user
        context['cart_items'] = cart['cart_items']
        context['order'] = cart['order']
        context['items'] = cart['items']
        return context


class Stripe_Config(View):
    def get(self, request, *args, **kwargs):
        stripe_config = {'public_key': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


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
            if orderItem.product.quantity-1-orderItem.quantity > -1:
                orderItem.quantity = (orderItem.quantity + 1)
            else:
                messages.warning(request, "We don't have more of such products.")

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
        return render(request, 'main/confirm_template.html', {'message': verification_message, 'success': succes, 'cart_items': cart['cart_items']})


class Create_Checkout_Session(View):
    title = "create checkout session"

    def get(self, request, *args, **kwargs):
        context={}
        cart = cartData(self.request)
        context['title'] = self.title
        context['user'] = self.request.user
        context['cart_items'] = cart['cart_items']
        context['order'] = cart['order']
        context['items'] = cart['items']
        return render(request, "main/checkout.html", context)

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_session = session(int(Order.objects.get(customer=request.user.customer, complete=False).get_cart_total*100), reverse_lazy('stripe_result', kwargs={'result': 'success'}), reverse_lazy('stripe_result', kwargs={'result': 'fail'}))
        return redirect(checkout_session.url)


def session(amount, success, cancel):
    return stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'cartItems',
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000'+str(success),
        cancel_url='http://127.0.0.1:8000'+str(cancel),
    )


class Stripe_Result(View):
    def get(self, request, *args, **kwargs):
        context={}
        cart = cartData(self.request)
        context['title'] = 'checkout'+kwargs['result']
        context['success'] = True
        if kwargs['result'] is "fail":
            context['success'] = False
        context['user'] = self.request.user
        context['cart_items'] = cart['cart_items']
        context['order'] = cart['order']
        context['items'] = cart['items']
        return render(request, "main/confirm_template.html", context)


class Checkout(View):
    title = "Checkout"

    def get(self, request, *args, **kwargs):
        cart = cartData(request)
        context = {}
        context['title'] = self.title
        context['user'] = self.request.user
        context['cart_items'] = cart['cart_items']
        context['order'] = cart['order']
        context['items'] = cart['items']
        if request.user.is_authenticated:
            try:
                checkShipping= ShippingAddress.objects.get(customer=request.user.customer)
            except:
                checkShipping=None
            if checkShipping is not None:
                return redirect(reverse_lazy('create_checkout_session', args={}))
            else:
                return redirect(reverse_lazy('shipping', args={}))

        else:
            return render(request, "main/sorry.html", context)

    def post(self, request, **kwargs):
        return JsonResponse("agg", safe=False)


class Shipping(FormView):
    context_object_name = "order"
    title = "Checkout"
    template_name = "main/shipping.html"
    form_class = ShippingForm
    success_url = reverse_lazy('checkout', kwargs={})

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = cartData(self.request)
        context['title'] = self.title
        context['user'] = self.request.user
        context['cart_items'] = cart['cart_items']
        context['title'] = cart['order']
        context['items'] = cart['items']
        context['name'] = 'Sign up'
        return context

    def form_valid(self, form):
        try:
            checkShipping = ShippingAddress.objects.get(customer=self.request.user.customer)
        except:
            checkShipping = None
        if checkShipping is not None:
            checkShipping.delete()
        response = super().form_valid(form)
        order=Order.objects.get(customer=self.request.user.customer, complete=False)
        ShippingAddress.objects.create(
            customer=self.request.user.customer,
            order=order,
            address=form.cleaned_data['address'],
            city=form.cleaned_data['city'],
            state=form.cleaned_data['state'],
            zipcode=form.cleaned_data['zipcode'],
        )
        return response
