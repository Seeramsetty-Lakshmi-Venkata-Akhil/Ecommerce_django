from django.db import models  # Importing Django's model library for database ORM operations

class User(models.Model):
    # Represents a user/customer in the system
    name = models.CharField(
        max_length=100  # Limits the length of the name to 100 characters
    )
    def __str__(self):
        # Returns the user's name when displaying instances in admin or debugging
        return self.name


class AuditData(models.Model):
    """
    Base model to automatically track creation and update timestamps.
    Provides reusable fields for other models to inherit from.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,  # Automatically sets to current datetime when the record is created
        verbose_name="Created At",  # Label for admin and UI
        help_text="The date and time when this record was first created"  # Helps explain field usage
    )
    updated_at = models.DateTimeField(
        auto_now=True,  # Updates the datetime to now whenever the record is modified
        verbose_name="Updated At",  # Label for admin and UI
        help_text="The date and time when this record was last updated"  # Helps explain field usage
    )

    class Meta:
        abstract = True  # Ensures this model is not represented as a database table


class Category(AuditData):
    """
    Represents product categories (e.g., Electronics, Clothing).
    Inherits timestamp fields from AuditData.
    """
    name = models.CharField(
        max_length=100,  # Restricts the category name to 100 characters
        unique=True  # Enforces uniqueness to prevent duplicate category names
    )

    def __str__(self):
        # Returns the category name when displaying instances in admin or debugging
        return self.name


class Products(AuditData):
    """
    Represents a sellable item in the e-commerce platform.
    Tracks product attributes like name, price, availability, and stock.
    """
    name = models.CharField(
        max_length=100,  # Restricts the product name to 100 characters
        help_text="The name of the product"  # Provides clarity about the field's purpose
    )
    price = models.DecimalField(
        max_digits=10,  # Allows up to 10 digits in total (including before and after the decimal point)
        decimal_places=2,  # Restricts the price to 2 decimal places for monetary values
        help_text="Current selling price (₹)"  # Clarifies the field represents the product's price
    )
    description = models.TextField(
        blank=True,  # Makes this field optional (empty values allowed)
        help_text="Optional description of the product"  # Explains what this field contains
    )
    is_available = models.BooleanField(
        default=True,  # Sets the default value to available
        help_text="Toggle to make the product available or unavailable for orders"  # Provides clarity about the field's usage
    )
    category = models.ForeignKey(
        Category,  # Establishes a many-to-one relationship with Category model
        on_delete=models.SET_NULL,  # Sets the category to null if the referenced category is deleted
        null=True,  # Allows this field to be empty
        blank=True,  # Makes this field optional in forms
        related_name='products',  # Enables reverse lookup from Category to its Products (e.g., category.products)
        help_text="Category this product belongs to"  # Explains what this field represents
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,  # Sets default stock to 0
        verbose_name="Stock Quantity",  # Label for admin and UI
        help_text="Tracks the number of units available in inventory"  # Clarifies the field's purpose
    )

    class Meta:
        ordering = ['-created_at']  # Displays newest products first in query results

    def __str__(self):
        # Returns a meaningful representation of the product for admin or debugging
        return f"{self.name} (₹{self.price})"
