from django.urls import path
from payments import views
from payments.views import Paymentview


urlpatterns = [
    path('payment/',Paymentview.as_view(), name='payment'),
]