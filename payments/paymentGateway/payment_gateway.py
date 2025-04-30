import json
from abc import ABC
from logging import exception

import razorpay
import razorpay.errors
from ecommerce_application import settings


class PaymentGateways(ABC):
    def get_payment(self, order_id, payment_id, amount):
        raise NotImplementedError


class RazorpayPaymentGateway(PaymentGateways):
    def __init__(self):
        self.client = razorpay.Client(
            auth= (settings.RAZORPAY_ID, settings.RAZORPAY_SECRET)
        )

    def get_payment(self, order_id, payment_id, amount):
        try:
            payment_data = {
                "amount": amount,
                "currency": "INR",
                "description": "For XYZ purpose",
                "customer": {
                    "name": "karan ",
                    "email": "karan.bhatia_1@scaler.com",
                    "contact": "+918295053001"
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
            }
            payment_link = self.client.payment_link.create(payment_data)
            return json.dumps(payment_link)
        except razorpay.errors.RazorpayError as e:
            raise RuntimeError(f"Failed to create payment link: {str(e)}")

# def verify_payment(self, paymentId):
    #     return self.client.payment_link.fetch(paymentId)
