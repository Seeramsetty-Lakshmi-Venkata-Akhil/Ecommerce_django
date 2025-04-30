from django.db import transaction  # For managing database transactions
from rest_framework import serializers  # Provides serialization/deserialization functionality
from .models import Order, OrderProduct  # Import Order and OrderProduct models
from products.models import Products, User  # Import related models like Products and User
from .services import OrderService  # Import additional service layer logic if needed

# Serializer for individual order items (OrderProduct model)
class OrderProductSerializer(serializers.ModelSerializer):
    """
    Handles serialization/deserialization for individual order items with associated product details.
    """
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),  # Allow linking a product using its primary key
        source='product'  # Maps to the 'product' field in the OrderProduct model
    )
    product_name = serializers.CharField(
        source='product.name',  # Access the name of the related product
        read_only=True  # This field is for output only
    )

    class Meta:
        model = OrderProduct  # Specifies the model this serializer is for
        fields = ['product_id', 'product_name', 'quantity', 'price_at_purchase']  # Fields to include in serialization
        read_only_fields = ['price_at_purchase', 'product_name']  # Read-only fields cannot be modified

# Main serializer for the Order model
class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model. Handles both creation and retrieval of orders.
    """
    # Write-only field to input order details (product IDs, quantities, etc.)
    order_products = OrderProductSerializer(
        many=True,  # Allows multiple order items to be passed
        write_only=True  # Field can only be used in input requests, not responses
    )

    # Read-only field to output related products in an order
    products = OrderProductSerializer(
        many=True,  # Handles a list of order items
        source='order_products',  # Maps to the 'order_products' relationship in the Order model
        read_only=True  # Output-only field
    )

    # Input field to link a user by their ID
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),  # Ensure the provided user ID is valid and exists in the database
        source='user',  # Maps to the 'user' field in the Order model
        write_only=True  # Can only be used for input, not output
    )

    # Read-only field to provide user details in the response
    user = serializers.SerializerMethodField(read_only=True)  # Custom field to format user data for output

    def get_user(self, obj):
        """
        Fetch and format user details for the order response.
        """
        return {
            "id": obj.user.id,  # User's ID
            "username": obj.user.name  # User's name
        }

    class Meta:
        model = Order  # Specifies the Order model for this serializer
        fields = [
            'id', 'user_id', 'user', 'order_products', 'products', 'status',
            'subtotal', 'discount', 'tax_amount', 'shipping_cost', 'total', 'created_at'
        ]  # Fields to include in serialization/deserialization
        read_only_fields = [
            'id', 'subtotal', 'total', 'created_at', 'products',
        ]  # Fields that cannot be modified


    def validate(self, data):
        """Only require products during creation, not updates"""
        if self.instance is None:  # Creation (POST)
            if not data.get('order_products'): # Check if the 'order_products' field is empty
                raise serializers.ValidationError("At least one product is required") # Raise an error if no products provided
        return data  # Return the validated data


    def create(self, validated_data):
        """
        Custom create method to handle the creation of an order and its associated items.
        Uses an atomic transaction for data integrity.
        """
        with transaction.atomic():  # Begin a transaction block
            # Extract order_products from the validated data and remove it from the main order data
            products_data = validated_data.pop('order_products')

            # Use `select_related` to optimize fetching the related user object during order creation
            order = Order.objects.select_related('user').create(**validated_data)

            # Create OrderProduct entries for each product in the order
            for product_data in products_data:
                OrderProduct.objects.create(
                    order=order,  # Link to the newly created order
                    product=product_data['product'],  # Assign the product
                    quantity=product_data['quantity']  # Set the quantity
                )

            # Calculate totals for the order (subtotal, tax, discounts, etc.)
            order.calculate_totals()
            order.save()  # Save the updated order data

            return order  # Return the created order instance
