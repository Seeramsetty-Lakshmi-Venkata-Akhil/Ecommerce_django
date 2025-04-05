from django.db import models
from django.utils.timezone import datetime

# Create your models here.
class Products(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default= datetime.now)

    class Meta:
        verbose_name_plural = "Products"  # Correct plural form
# Products.objects.all()