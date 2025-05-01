import razorpay  # Razorpay SDK
from django.conf import settings  # Access keys from settings

from orders.views import logger
from .base import BasePaymentGateway  # Inherit interface
from razorpay.errors import SignatureVerificationError  # Specific exception

class RazorpayGateway(BasePaymentGateway):
    def __init__(self):
        # Initialize Razorpay client with credentials
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    def create_payment_order(self, amount, currency, payment_id):
        """
        Creates a Razorpay hosted payment link.

        - Uses `payment_link.create()` instead of `order.create()`.
        - Returns the Razorpay hosted payment page URL.
        """
        try:
            payment_data = {
                "amount": int(amount * 100),  # Convert ₹1000 to 100000 paise
                "currency": currency,
                "description": f"Payment for Order {payment_id}",
                "customer": {
                    "name": "Lakshmi Venkata Akhil",
                    "email": "testuser@example.com",
                    "contact": "+918885784666"
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
                "callback_url": "http://localhost:8000/api/payments/callback/",  # Webhook
                # "callback_method": "post"  # ✅ Set to POST instead of GET
            }

            payment_link = self.client.payment_link.create(payment_data)  # Use Payment Links API
            return payment_link  # Returns full Razorpay response with checkout URL

        except Exception as e:
            logger.error(f"Error creating Razorpay payment link: {str(e)}")
            raise ValueError("Failed to create payment link with Razorpay")

    def verify_payment(self, payment_data):
        # Verify callback signature; returns True if valid, False otherwise
        try:
            self.client.utility.verify_payment_signature(payment_data)
            return True
        except SignatureVerificationError:
            return False