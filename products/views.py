from django.shortcuts import render
from django.http import  HttpResponse

from products.models import Products

from django.db import transaction

def greet(request):
    data = Products.objects.all()
    if data.exists():
        product = data[0]
        print("Before:", product.name)  # Output: ShivaShakti
        product.name = "ShivShakti"
        product.save()  # Explicitly save the updated object
        product.refresh_from_db()  # Reload the object to confirm the change
        print("After:", product.name)  # Should now output: ShivaShakti
    else:
        print("No products found.")
    return HttpResponse("Hey we found World")
