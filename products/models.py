from django.db import models
from django.db.models import SET_NULL
from django.utils.timezone import datetime
from decimal import Decimal

# Create your models here.
class AuditData(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Set only once at creation
    updated_at = models.DateTimeField(auto_now=True)      # Update automatically on save
    class Meta:
        abstract = True


class User(AuditData):   # Inherit from AuditData
    name = models.CharField(max_length=100)


class Category(AuditData):   # Inherit from AuditData):
    name = models.CharField(max_length=100)


class Products(AuditData):   # Inherit from AuditData
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,related_name='products',null=True) #Allows NULL values in the database

    class Meta:
        verbose_name_plural = "Products"  # Correct plural form


class Order(AuditData):  # Final Order definition
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Products, through='OrderProduct', related_name='orders')

    def total_bill(self, discount=0, tax=0):
        total = Decimal('0')
        # Sum product prices * quantity
        for order_product in self.order_products.all():
            total += order_product.product.price * order_product.quantity
        total -= total * (Decimal(discount) / Decimal('100'))
        total += total * (Decimal(tax) / Decimal('100'))
        return total


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='order_products')
    quantity = models.PositiveIntegerField(default=1)  # Track product quantity
