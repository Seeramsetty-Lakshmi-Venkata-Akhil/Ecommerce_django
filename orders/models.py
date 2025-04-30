from django.db import models  # Django's ORM library for defining and managing database models
from django.core.exceptions import ValidationError  # Allows raising errors for invalid data
from decimal import Decimal  # Used for precise calculations of monetary values
from django.core.validators import MinValueValidator  # Ensures fields have minimum values (e.g., no negative values)
from django.utils import timezone  # Provides timezone-aware datetime objects
from django.db import transaction  # Enables atomic transactions to ensure data consistency
from products.models import User, Products  # Import the User and Product models from the products app


class AuditData(models.Model):
    """
    Abstract base model that provides automatic timestamp tracking for creation and updates.
    All models inheriting from this will automatically get these audit fields.

    Fields:
        created_at: Automatically set to the current datetime when the record is first created
        updated_at: Automatically updated to the current datetime whenever the record is saved
    """
    created_at = models.DateTimeField(
        auto_now_add=True,  # Automatically adds the current datetime when the record is created
        verbose_name="Created At",  # User-friendly name shown in the admin interface
        help_text="The date and time when this record was first created"  # Explains what this field tracks
    )
    updated_at = models.DateTimeField(
        auto_now=True,  # Automatically updates the datetime whenever the record is saved
        verbose_name="Updated At",  # User-friendly name shown in the admin interface
        help_text="The date and time when this record was last updated"  # Explains what this field tracks
    )

    class Meta:
        abstract = True  # Ensures this model is not turned into a database table but can be inherited by others


class Order(AuditData):
    """
    Represents a customer order in the e-commerce system.
    Tracks the complete order lifecycle from creation to fulfillment.

    Key Features:
    - Financial calculations with frozen prices
    - Status-based workflow
    - Inventory management integration
    - Comprehensive validation

    Business Rules:
    1. Every order must contain at least one product
    2. Discounts cannot exceed the order subtotal
    3. Totals can never be negative
    4. Status changes must follow defined workflow
    """

    class OrderStatus(models.TextChoices):
        """
        Enumeration of all possible order states with descriptive labels.
        Defines the complete lifecycle of an order.
        """
        PENDING = 'pending', 'Pending Confirmation'  # Waiting for customer confirmation
        CONFIRMED = 'confirmed', 'Confirmed'  # Order is confirmed and ready for processing
        DELIVERED = 'delivered', 'Delivered'  # Order has been successfully delivered
        CANCELLED = 'cancelled', 'Cancelled'  # Order was cancelled
        RETURNED = 'returned', 'Returned'  # Order was returned by the customer

    # Class-level constants
    TERMINAL_STATUSES = [
        OrderStatus.DELIVERED,  # Final state: Order delivered successfully
        OrderStatus.CANCELLED,  # Final state: Order cancelled
        OrderStatus.RETURNED  # Final state: Order returned
    ]

    # Relationships 1:N
    user = models.ForeignKey(
        User,  # Establishes a many-to-one relationship between Order and User
        on_delete=models.PROTECT,  # Prevents deleting the User if orders exist
        related_name='orders',  # Allows reverse lookup to fetch all orders for a user
        verbose_name="Customer",  # User-friendly name shown in the admin interface
        help_text="The customer who placed this order"  # Explains the purpose of this field
    )

    products = models.ManyToManyField( #M:M
        Products,  # Establishes a many-to-many relationship with Product
        through='OrderProduct',  # Specifies an intermediary table for storing additional details like quantity
        related_name='orders',  # Allows reverse lookup to fetch all orders associated with a product
        verbose_name="Ordered Products",  # User-friendly name shown in the admin interface
        help_text="The products included in this order"  # Explains the purpose of this field
    )

    # Financial Fields
    subtotal = models.DecimalField(
        max_digits=12,  # Allows up to 12 digits in total
        decimal_places=2,  # Supports precision up to 2 decimal places
        editable=False,  # Prevents manual changes to this field
        default=0,  # Initializes the field with a value of 0
        verbose_name="Subtotal",  # User-friendly name shown in the admin interface
        help_text="Sum of all items before adjustments"  # Explains what this field represents
    )

    discount = models.DecimalField(
        max_digits=12,  # Allows up to 12 digits in total
        decimal_places=2,  # Supports precision up to 2 decimal places
        default=0,  # Initializes the field with a value of 0
        validators=[MinValueValidator(0)],  # Ensures that discount values cannot be negative
        verbose_name="Discount Amount",  # User-friendly name shown in the admin interface
        help_text="Absolute discount value (not percentage)"  # Explains what this field represents
    )

    tax_amount = models.DecimalField(
        max_digits=12,  # Allows up to 12 digits in total
        decimal_places=2,  # Supports precision up to 2 decimal places
        default=0,  # Initializes the field with a value of 0
        validators=[MinValueValidator(0)],  # Ensures that tax values cannot be negative
        verbose_name="Tax Amount",  # User-friendly name shown in the admin interface
        help_text="Calculated tax for this order"  # Explains what this field represents
    )

    shipping_cost = models.DecimalField(
        max_digits=12,  # Allows up to 12 digits in total
        decimal_places=2,  # Supports precision up to 2 decimal places
        default=0,  # Initializes the field with a value of 0
        validators=[MinValueValidator(0)],  # Ensures that shipping cost cannot be negative
        verbose_name="Shipping Cost",  # User-friendly name shown in the admin interface
        help_text="Calculated shipping charges"  # Explains what this field represents
    )

    total = models.DecimalField(
        max_digits=12,  # Allows up to 12 digits in total
        decimal_places=2,  # Supports precision up to 2 decimal places
        editable=False,  # Prevents manual changes to this field
        default=0,  # Initializes the field with a value of 0
        verbose_name="Total Amount",  # User-friendly name shown in the admin interface
        help_text="Final amount after all adjustments"  # Explains what this field represents
    )

    # Status Tracking
    status = models.CharField(
        max_length=15,  # Limits the length of the status to 15 characters
        choices=OrderStatus.choices,  # Restricts values to the predefined status choices
        default=OrderStatus.PENDING,  # Sets the initial value to 'pending'
        verbose_name="Order Status",  # User-friendly name shown in the admin interface
        help_text="Current state in fulfillment workflow"  # Explains what this field represents
    )

    completed_at = models.DateTimeField(
        null=True,  # Allows the field to be empty
        blank=True,  # Makes the field optional in forms
        verbose_name="Completed At",  # User-friendly name shown in the admin interface
        help_text="When order reached terminal status"  # Explains what this field represents
    )

    class Meta:
        indexes = [
            models.Index(fields=['status']),  # Optimizes queries by status
            models.Index(fields=['user', 'created_at']),  # Optimizes user-specific order queries
            models.Index(fields=['created_at']),  # Optimizes queries by creation time
        ]
        ordering = ['-created_at']  # Default ordering by newest first
        verbose_name = "Order"  # Singular name for the admin panel
        verbose_name_plural = "Orders"  # Plural name for the admin panel

    def clean(self):
        """
        Validate the order meets all business rules before saving.
        Called automatically during model validation.
        """
        # Business Rule 1: Every order must contain at least one product
        if self.pk and not self.order_products.exists():
            # Validation error if the order has no associated products
            raise ValidationError("Order must contain at least one product")

        # Business Rule 2: Ensure the discount does not exceed the subtotal
        if self.discount > self.subtotal:
            raise ValidationError({
                'discount': "Discount cannot exceed order subtotal"
            })

        # Business Rule 3: Validate valid status transitions for updates only
        if self.pk:  # If the order exists in the database
            # Fetch the current order instance from the database
            original = Order.objects.get(pk=self.pk)
            # Ensure the status transition is allowed
            self.validate_status_transition(original)

    def validate_status_transition(self, original):
        """
        Internal method to validate status changes.
        Prevents invalid workflow transitions and ensures order validity.
        """
        # Rule 1: Prevent changes from terminal states
        if (original.status in self.TERMINAL_STATUSES and  # Original status is terminal
                self.status != original.status):  # New status differs from terminal status
            # Raise an error to prevent changes from terminal states
            raise ValidationError(
                f"Cannot change status from {original.get_status_display()}"
            )

        # Rule 2: Ensure terminal statuses require at least one product
        if self.status in self.TERMINAL_STATUSES and not self.order_products.exists():
            # Raise an error if the order has no products and is set to terminal status
            raise ValidationError(
                "Orders marked as delivered, returned, or cancelled must include at least one product.")


    def save(self, *args, **kwargs):
        """
        Custom save handler with:
        - Atomic transactions for data integrity
        - Status tracking
        - Automatic total calculation
        """
        with transaction.atomic():  # Ensures all database operations are atomic
            # Handle terminal state transitions
            if self.pk:  # The order already exists (updating)
                # Fetch the original order from the database
                original = Order.objects.get(pk=self.pk)
                if self.status in self.TERMINAL_STATUSES:  # If new status is terminal
                    if original.status not in self.TERMINAL_STATUSES:  # If original was non-terminal
                        self.completed_at = timezone.now()  # Set the completion timestamp
                else:  # If the new status is non-terminal
                    self.completed_at = None  # Reset the completion timestamp

            # Handle order creation (no primary key yet)
            if not self.pk:
                super().save(*args, **kwargs)  # Save the initial record to generate a primary key
                self.calculate_totals()  # Calculate financial totals after creation
                return super().save(  # Save again to store the calculated fields
                    update_fields=['subtotal', 'total', 'completed_at']  # Only update specific fields
                )

            # For updates: Recalculate totals and save the updated record
            self.calculate_totals()  # Recalculate totals for financial fields
            super().save(*args, **kwargs)  # Save the record

    def calculate_totals(self):
        """
        Recalculate all financial fields:
        - Subtotal from order items
        - Total with all adjustments
        Ensures totals are never negative.
        """
        # Calculate subtotal for this order as the sum of line totals (quantity × price_at_purchase)
        self.subtotal = sum(
            item.line_total() for item in
            self.order_products.select_related('product').all()  # Prefetch related all products of this order for efficiency
        ) if hasattr(self, 'order_products') else Decimal('0')  # Default to 0 if no products

        # Calculate the total amount, ensuring no negative totals
        self.total = max(
            (self.subtotal - self.discount) + self.tax_amount + self.shipping_cost,  # Total formula
            Decimal('0')  # Prevents negative values
        )

    def get_product_quantities(self):
        """
        Get list of products and their quantities in this order.
        Returns:
            list: of (product, quantity) tuples
        """
        return [
            (op.product, op.quantity)  # Create a tuple of product and quantity
            for op in self.order_products.select_related('product').all()  # Prefetch related products
        ]


    def __str__(self):
        """Human-readable representation of the order"""
        return f"Order #{self.id} ({self.get_status_display()}) - ₹{self.total:.2f}" #rounding upto two decimals


class OrderProduct(models.Model):
    """
    Intermediary model representing a product line item within an order.
    Freezes the product price at time of purchase and tracks quantity.

    Key Features:
    - Price snapshot at time of purchase
    - Quantity validation
    - Inventory management integration
    """

    order = models.ForeignKey(
        Order,  # Links the order to this line item (one-to-many relationship)
        on_delete=models.CASCADE,  # Deletes this line item if the parent order is deleted
        related_name='order_products',  # Enables reverse lookup from Order to all its associated line items
        verbose_name="Order",  # Admin-friendly label for the field
        help_text="The order containing this product"  # Provides context for admin users
    )

    product = models.ForeignKey(
        Products,  # Links the product being ordered to this line item
        on_delete=models.PROTECT,  # Prevents deleting the product if it is referenced in an order
        related_name='order_products',  # Enables reverse lookup from Product to all its associated line items
        verbose_name="Product",  # Admin-friendly label for the field
        help_text="The product being ordered"  # Provides context for admin users
    )

    quantity = models.PositiveIntegerField(
        default=1,  # Default value is one product unit
        validators=[MinValueValidator(1)],  # Ensures the quantity is at least one
        verbose_name="Quantity",  # Admin-friendly label for the field
        help_text="Number of units ordered"  # Provides context for admin users
    )

    price_at_purchase = models.DecimalField(
        max_digits=12,  # Allows up to 12 total digits in the price
        decimal_places=2,  # Tracks price with up to 2 decimal places for precision
        editable=False,  # Prevents manual editing of this field
        verbose_name="Price At Purchase",  # Admin-friendly label for the field
        help_text="Snapshot of product price when ordered"  # Provides context for admin users
    )

    class Meta:
        unique_together = ('order', 'product')  # Ensures each product is listed only once per order
        verbose_name = "Order Product"  # Singular name for the admin interface
        verbose_name_plural = "Order Products"  # Plural name for the admin interface

    def clean(self):
        """
        Validate the line item meets business rules.
        """
        # Validate sufficient stock
        if hasattr(self, 'product') and self.quantity > self.product.stock_quantity:
            raise ValidationError({
                'quantity': f"Only {self.product.stock_quantity} available in stock"
            })

    def save(self, *args, **kwargs):
        """
        Custom save handler that:
        1. Validates the line item
        2. Captures current product price on creation
        3. Updates parent order totals
        """
        self.full_clean()  # Ensure validation runs before saving

        # First save - capture current price
        if not self.pk:  # Check if this is the first time saving the line item
            self.price_at_purchase = self.product.price  # Freeze the product price at purchase

        super().save(*args, **kwargs)  # Perform the actual save operation

        # Update parent order totals
        self.order.calculate_totals()  # Recalculate the parent order totals
        self.order.save()  # Save the updated parent order

    def line_total(self):
        """
        Calculate the total price for this line item.
        Returns:
            Decimal: quantity × price_at_purchase
        """
        return self.quantity * self.price_at_purchase  # Multiply quantity by the frozen price

    def __str__(self):
        """Human-readable representation"""
        return f"{self.quantity} × {self.product.name} @ ₹{self.price_at_purchase:.2f}"
