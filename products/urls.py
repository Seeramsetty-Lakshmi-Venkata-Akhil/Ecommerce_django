from django.urls import path

import products
from products import views
from .views import PageViewSet
# from products.views import OrderDetailView, OrderListCreateView
#
urlpatterns = [
    # Maps the 'greet' view, which could be an introductory or test endpoint.
    path('update_name/', views.greet),
    # Maps the 'get_products' view to retrieve and return all products Or can create new Products and save.
    path('', views.create_r_get_products),
    # Maps the 'get_product' view to retrieve a specific product based on its ID.
    path('<int:id>/', views.get_product, name="get_product"),
    path("filter_products/", views.filter_products, name="filter_products"),
    path("update_product/<int:id>", views.update_product, name="update_product"),
    path("delete_product/<int:id>/", views.delete_product, name="delete_product"),
    path("filter_products_wth_pagination/", PageViewSet.as_view(), name="filter_products"),

#     path('orders/', OrderListCreateView.as_view(), name='order-list-create'), #List/Create orders (Class Based)
#     path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'), #Retrieve/Update/Delete order (Class Based)
]
