from django.urls import path
from .views import OrderListCreateView, OrderDetailView

urlpatterns = [
    # Order collection endpoints
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    # Order detail endpoints
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]