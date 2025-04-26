from rest_framework import serializers
from products.models import Order, OrderProduct, Products

# Serializer for Product (used inside OrderProduct)
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'price']  # Only essential fields needed in order view

# Serializer for each Product inside an Order (with quantity)
class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nested product details inside each ordered item

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']  # Product and how many units ordered

# Serializer for Order
class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True, read_only=True)
    # Nested list of ordered products with their quantities

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_status', 'order_products', 'created_at']
        # Showing important order information
