from django.urls import path

import products
from products import views

urlpatterns = [
    # Maps the 'greet' view, which could be an introductory or test endpoint.
    path('api/', views.greet),

    # Maps the 'get_products' view to retrieve and return all products.
    path('allProducts/', views.get_products),

    # Maps the 'get_product' view to retrieve a specific product based on its ID.
    path('products/<int:id>/', views.get_product),
]
