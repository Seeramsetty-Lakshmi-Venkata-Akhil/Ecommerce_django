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
    def __str__(self):
        # useful for displaying meaningful information in Django Admin and debugging.
        return self.name


class Category(AuditData):   # Inherit from AuditData):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Products(AuditData):   # Inherit from AuditData
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,related_name='products',null=True) #Allows NULL values in the database

    class Meta:
        verbose_name_plural = "Products"  # Correct plural form

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


class Order(AuditData):  # Inherit created_at and updated_at fields from AuditData
    # Define possible order statuses using Django's TextChoices
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'  # Order created but not yet paid
        SUCCESS = 'success', 'Success'  # Payment successful
        FAILED = 'failed', 'Failed'      # Payment failed

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    # User who placed the order
    products = models.ManyToManyField(Products, through='OrderProduct', related_name='orders')
    # Products included in the order (with quantity tracking)
    order_status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    # Current status of the order (pending/success/failed)

    def total_bill(self, discount=0, tax=0):
        """
        Calculates the total bill amount for the order.
        - Adds price * quantity for each product.
        - Applies optional discount (%) and tax (%).
        Returns the final payable amount as Decimal.
        """
        total = Decimal('0')
        # Sum up (price * quantity) for all ordered products
        for order_product in self.order_products.all():
            total += order_product.product.price * order_product.quantity
        # Apply discount if any
        if discount:
            total -= (total * Decimal(discount) / Decimal('100'))
        # Apply tax if any
        if tax:
            total += (total * Decimal(tax) / Decimal('100'))
        return total

    def __str__(self):
        product_names = ", ".join([product.name for product in self.products.all()])
        return f"Order #{self.id} by {self.user.name} - Products: {product_names}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='order_products')
    quantity = models.PositiveIntegerField(default=1)  # Track product quantity

    def __str__(self):
        return f"Order #{self.order.id} - {self.product.name} x {self.quantity}"

