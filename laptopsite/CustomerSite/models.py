from django.db import models
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404

import decimal
from django.contrib.auth import authenticate, login


class Voucher(models.Model):
    id=models.CharField(max_length=20, primary_key=True)
    value=models.FloatField(default=0)
    description=models.TextField()
    quantity=models.IntegerField(default=0)
    def __str__(self):
        return str(self.value)


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Laptop(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL,null=True)
    
    price = models.DecimalField(max_digits=13, decimal_places=2,default=0)
    description = models.TextField()
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
    is_active=models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
       
  
            
class Image(models.Model):
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(null=True,blank=True)


class Customer(User):
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.username

  

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100)
 
    def __str__(self):
        return str(self.id)
 
    
                    

class OrderItem(models.Model):
    product = models.ForeignKey(Laptop, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return str(self.order)
 
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("C","Cancel"),
        ("D","Delivery"),
        ('S', 'Success'),
        ('F', 'Failed'),
        
    ]
    orders = models.ManyToManyField(Order)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - {self.order.laptop.name}"
    def Cancel(self):
        existing_transaction=Transaction.objects.filter(customer=self.customer,order=self.orders).first()
        if(existing_transaction is not None):
            if(existing_transaction.status=="O"):
                existing_transaction.status="C"
                existing_transaction.save()
                return True
            else:
                return False
        else:
            return False
    
        
    
class Manager(User):
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    citizenID = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.username






class CheckoutDetail(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    total_amount = models.CharField(max_length=10, blank=True,null=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.address