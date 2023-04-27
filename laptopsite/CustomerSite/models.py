from django.db import models
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Laptop(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=13, decimal_places=2,default=0)
    description = models.TextField()
    image = models.JSONField(default=list)
    processor = models.CharField(max_length=100,default='Unknown')
    ram = models.CharField(max_length=100,default='Unknown')
    hard_disk = models.CharField(max_length=100,default='Unknown')
    display_size = models.CharField(max_length=100,default='Unknown')
    weight = models.CharField(max_length=100,default='Unknown')
    battery_life = models.CharField(max_length=100,default='Unknown')
    VGA=models.CharField(max_length=100,default='Unknown')
    wireless=models.CharField(max_length=100,default='Unknown')
    warranty=models.IntegerField(default=24)
    quantity=models.IntegerField(default=0)
    def __str__(self):
        return self.name


class Customer(User):
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.username


class Order(models.Model):
    STATUS = [
        ('O', 'Order'),
        ('D', 'Delivery'),
        ('C', 'Complete'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=1, choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    pay = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.username} - {self.laptop.name}"

    def total_price(self):
        return self.quantity * self.laptop.price


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('S', 'Success'),
        ('F', 'Failed'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - {self.order.laptop.name}"
    
class Manager(User):
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    citizenID = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.username

class voucher(models.Model):
    id=models.CharField(max_length=20, primary_key=True)
    value=models.FloatField(default=0)
    description=models.TextField()
    quantity=models.IntegerField(default=0)
    def __str__(self):
        return self.id



