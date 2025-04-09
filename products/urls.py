from django.urls import path

import products
from products import views

urlpatterns = [
    # Maps the 'greet' view, which could be an introductory or test endpoint.
    path('update_name/', views.greet),
    # Maps the 'get_products' view to retrieve and return all products Or can create new Products and save.
    path('products/', views.create_r_get_products),
    # Maps the 'get_product' view to retrieve a specific product based on its ID.
    path('products/<int:id>/', views.get_product),
    path("filter_products/", views.filter_products, name="filter_products"),
]
