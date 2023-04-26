from django.db import models
from django.contrib.auth.models import User

class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Laptop(models.Model):
    name = models.CharField(max_length=50)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    processor = models.CharField(max_length=50,default='Unknown')
    ram = models.CharField(max_length=50,default='Unknown')
    storage = models.CharField(max_length=50,default='Unknown')
    display_size = models.CharField(max_length=50,default='Unknown')
    weight = models.CharField(max_length=50,default='Unknown')
    battery_life = models.CharField(max_length=50,default='Unknown')
    gpu=models.CharField(max_length=50,default='Unknown')

    def __str__(self):
        return self.name

class Customer(User):
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.username

class Order(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('C', 'Complete'),
        ('R', 'Refunded'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

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
