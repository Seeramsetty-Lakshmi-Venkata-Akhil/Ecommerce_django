from django.db import transaction  # Used to manage database operations as a single atomic unit
from decimal import Decimal  # Provides support for precise decimal arithmetic (useful for monetary values)
from .models import Order, OrderProduct  # Import the core models for orders and their related products
from products.models import Products  # Import the Products model to fetch product information


class OrderService:
    """
    A service layer to encapsulate core business logic related to orders.
    This layer abstracts database transactions and business rules from the views.
    """

    @staticmethod
    def create_order(user, products_data, **kwargs):
        """
        Creates a new order and its associated order products.
        Args:
            user: The user placing the order.
            products_data: A list of product and quantity details.
            **kwargs: Additional fields to populate the Order instance.
        Returns:
            The created Order instance.
        """
        with transaction.atomic():  # Ensure all database operations within this block succeed or are rolled back.
            # Create a new order for the specified user with any extra fields passed in kwargs
            order = Order.objects.create(user=user, **kwargs)

            # Loop through the list of products to create associated order items
            for product_data in products_data:
                product = product_data['product']  # Extract the product instance from the data
                OrderProduct.objects.create(  # Create a new OrderProduct entry
                    order=order,  # Link it to the newly created order
                    product=product,  # Link the specific product
                    quantity=product_data['quantity']  # Set the quantity for this order item
                )

            # Recalculate the financial totals for the order (subtotal, tax, discounts, total, etc.)
            order.calculate_totals()

            # Save the updated order with calculated totals to the database
            order.save()
            return order  # Return the fully created and saved order object

    @staticmethod
    def update_order_status(order, new_status):
        """
        Updates the status of an existing order with proper validation.
        Args:
            order: The Order instance to update.
            new_status: The new status to assign to the order.
        """
        with transaction.atomic():  # Ensure the status update happens safely in a single atomic block
            order.status = new_status  # Assign the new status value to the order
            order.full_clean()  # Validate the updated order data (e.g., ensure status is valid per model constraints)
            order.save()  # Save the updated order to the database


    @staticmethod
    def add_product_to_order(order, products_data):
        """
        Adds new products to an existing order or updates the quantity of existing products.
        Args:
            order: The Order instance being modified.
            products_data: A list of products and quantities to add to the order.
        """
        with transaction.atomic():  # Ensure consistency during the update process
            # Loop through the provided list of products and their quantities
            for item in products_data:
                product = item['product']  # Extract the product instance from the data
                quantity = item['quantity']  # Extract the quantity for this product

                # Check if the product is already in the order
                existing = order.order_products.filter(product=product).first()
                if existing:  # If the product already exists in the order
                    existing.quantity += quantity  # Increment the quantity by the specified amount
                    existing.save()  # Save the updated OrderProduct entry
                else:  # If the product does not exist in the order
                    OrderProduct.objects.create(  # Create a new OrderProduct entry
                        order=order,  # Link it to the existing order
                        product=product,  # Specify the product
                        quantity=quantity  # Set the quantity for this new entry
                    )

    @staticmethod
    def calculate_order_totals(order):
        """
        Recalculates and updates the financial totals for a given order.
        Args:
            order: The Order instance whose totals need recalculating.
        """
        order.calculate_totals()  # Call the model's method to perform the calculations (e.g., subtotal, tax, discounts)
        order.save()  # Save the recalculated totals to the database
