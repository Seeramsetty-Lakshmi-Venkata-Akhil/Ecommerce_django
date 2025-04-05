from django.urls import path
from products import views

urlpatterns = [
    path('api/', views.greet),  # Maps greet view
]
