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
    # To show ordered products info when retrieving an order

    products = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    # This field accepts a list of product+quantity while creating the order (only input purpose)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_status', 'products', 'order_products', 'created_at', 'updated_at']
        # 'products' = input field
        # 'order_products' = output field (showing ordered products)

    def create(self, validated_data):
        """
        Custom create method to handle adding products while creating an order.
        """

        # Step 1: Extract 'products' data separately from the payload
        products_data = validated_data.pop('products', [])

        # Step 2: First create the Order object (without products)
        order = Order.objects.create(**validated_data)

        # Step 3: Loop over each product entry in the request
        for product_info in products_data:
            product_id = product_info.get('product')   # Get product id
            quantity = product_info.get('quantity', 1) # Default quantity = 1 if not provided

            # Step 4: Fetch the actual Product instance from the database
            try:
                product = Products.objects.get(id=product_id)
            except Products.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} does not exist.")

            # Step 5: Create an entry in the 'OrderProduct' through table
            OrderProduct.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )

        # Step 6: Finally return the created Order object
        return order
