from .models import *


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # cookieData = cookieCart(request)
        # cartItems = cookieData['cartItems']
        # order = cookieData['order']
        # items = cookieData['items']
        cartItems = 0
        items = {}
        order = {}

    return {'cart_items': cartItems, 'order': order, 'items': items}
