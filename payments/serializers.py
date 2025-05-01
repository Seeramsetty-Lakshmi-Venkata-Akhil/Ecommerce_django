from rest_framework import serializers  # Import Django REST framework serializers module
from .models import Payment  # Import the Payment model for serialization
from orders.models import Order  # Import Order model to validate order-related fields


class PaymentSerializer(serializers.ModelSerializer):  # Serializer to convert Payment model into JSON format
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),  # Ensures only valid Order IDs can be referenced
        help_text="Existing Order ID"  # Description for better documentation in API views
    )

    gateway = serializers.CharField(
        max_length=50,  # Restrict length to 50 characters for gateway name
        help_text="Name of the payment gateway (e.g., Stripe, PayPal)"  # Describes what this field represents
    )

    class Meta:
        model = Payment  # Link serializer to the Payment model
        fields = [  # Define the fields to be serialized
            'id', 'order', 'gateway', 'method',
            'amount', 'currency', 'status',
            'transaction_id', 'created_at'
        ]
        read_only_fields = [  # These fields should not be editable by the client
            'id', 'status', 'transaction_id', 'created_at'
        ]

    def validate_order(self, value):
        """
        Validation: Ensures the order is in a payable state before allowing payment processing.
        - Only orders in 'pending' or 'partial' status can have payments created.
        - Raises an error if the order is not eligible for payment.
        """
        if value.status not in [Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL]:  # Use constants correctly
              # Use predefined constants for consistency
            raise serializers.ValidationError("Order is not in a payable state.")
        return value  # Return the validated order instance

    def validate_amount(self, value):
        """
        Validation: Ensures the payment amount does not exceed the remaining payable amount of the order.
        - Retrieves the order instance using the provided order ID.
        - Calculates the remaining balance for the order.
        - Raises an error if the payment exceeds the allowable amount.
        """
        order_id = self.initial_data.get('order')  # Get order ID from request data
        if order_id:
            try:
                order = Order.objects.get(pk=order_id)  # Fetch Order instance from DB
            except Order.DoesNotExist:  # Handle case where order does not exist
                raise serializers.ValidationError("Invalid Order ID.")

            remaining = order.total - order.paid_amount  # Calculate remaining amount to be paid
            if value > remaining:  # Ensure payment does not exceed the allowed amount
                raise serializers.ValidationError(
                    f"Amount exceeds remaining balance: {remaining}"
                )
        return value  # Return the validated amount
