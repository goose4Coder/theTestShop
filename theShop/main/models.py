from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.conf import settings


class Customer(models.Model):
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    mail = models.EmailField(null=True)

    def __str__(self):
        return str(self.name)


class Product(models.Model):
    name = models.CharField(max_length=150,null=False)
    price = models.DecimalField(max_digits=5,decimal_places=2) #change in real projects for DecimalField(max_digits=5,decimal_places=2)!
    digital = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(null=False, blank=False,default="No description")
    quantity = models.IntegerField(default=0, null=False)
    active = models.BooleanField(default=False)
    class Meta:
        ordering = ['-id']

    @property
    def get_image_url(self):
        return format(settings.MEDIA_URL, self.image.url)

    def __str__(self):
        return str(self.name)


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.address)


class Report(models.Model):
    shipping_model= models.ForeignKey(ShippingAddress,on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT,null=True,default="not defined!")
    address = models.CharField(max_length=200, null=False,default="not defined!")
    city = models.CharField(max_length=200, null=False,default="not defined!")
    state = models.CharField(max_length=200, null=False,default="not defined!")
    zipcode = models.CharField(max_length=200, null=False,default="not defined!")
    date_added = models.DateTimeField(auto_now_add=False)

    def update_values(self):
        self.order=self.shipping_model.order
        self.address=self.shipping_model.address
        self.city=self.shipping_model.city
        self.state=self.shipping_model.state
        self.zipcode=self.shipping_model.zipcode
        self.date_added=self.shipping_model.date_added
