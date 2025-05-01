import logging  # Logging for debugging & tracing issues
from django.conf import settings  # Access project-wide settings
from django.db import transaction  # Ensure atomic operations
from orders.models import Order  # Import Order model for lookups
from .models import Payment  # Import Payment model
from .paymentGateway.razorpay import RazorpayGateway  # Import specific gateway class

# Initialize logger for error tracking & debugging
logger = logging.getLogger(__name__)


class PaymentService:
    """
    Service layer handling payment initialization and finalization logic.
    """

    @staticmethod
    def initiate_payment(order_id, amount, method):
        """
        Initiates a new payment for a given order.

        - Validates existence of the order.
        - Prevents duplicate payments for fully paid orders.
        - Creates a pending Payment record before gateway interaction.
        - Ensures the amount is valid.

        Returns the created payment instance.
        """
        try:
            order = Order.objects.get(pk=order_id)  # Fetch Order instance
        except Order.DoesNotExist:
            logger.warning(f"Payment initiation failed: Invalid order ID {order_id}")
            raise ValueError("Invalid order ID")

        # Prevent double payments on completed orders
        if order.status == 'paid':
            raise ValueError("Order already fully paid")

        # Validate non-zero payment amount
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")

        # Create pending payment record in DB
        payment = Payment.objects.create(
            order=order,
            gateway=settings.PAYMENT_GATEWAY,
            method=method,
            amount=amount,
            status='pending'
        )

        return payment  # Return Payment instance for further processing

    @staticmethod
    def finalize_payment(payment):
        """
        Finalizes a payment and updates the linked order.

        - Ensures atomic transaction to prevent race conditions.
        - Adjusts the paid amount for the order.
        - Updates order status ('paid' if fully settled, else 'partial').

        Returns the updated order instance.
        """
        order = payment.order

        with transaction.atomic():  # Ensure consistency in payment updates
            order.paid_amount += payment.amount  # Increase paid amount
            order.status = 'paid' if order.paid_amount >= order.total else 'partial'
            order.save()  # Persist updates in the database

        return order  # Return updated order instance

    @staticmethod
    def get_gateway():
        """
        Retrieves the appropriate payment gateway instance based on settings.

        - Supports Razorpay.
        - Raises an error if the configured gateway is unsupported.

        Returns the payment gateway instance.
        """
        if settings.PAYMENT_GATEWAY == 'razorpay':
            return RazorpayGateway()  # Return Razorpay gateway instance
        # elif settings.PAYMENT_GATEWAY == 'stripe':
        #     from .paymentGateway.stripe import StripeGateway
        #     return StripeGateway()
        # elif settings.PAYMENT_GATEWAY == 'phonepe':
        #     from .paymentGateway.phonepe import PhonePeGateway
        #     return PhonePeGateway()

        # Log and raise an error for unsupported gateways
        logger.error(f"Unsupported payment gateway: {settings.PAYMENT_GATEWAY}")
        raise NotImplementedError("Payment gateway not supported")
