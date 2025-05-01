import uuid  # For generating unique unique identifiers for each payment
from django.db import models  # Django ORM models base
from django.core.validators import MinValueValidator  # Ensures positive amounts
from orders.models import Order  # Import related Order model

class Payment(models.Model):  # Main Payment model
    PAYMENT_STATUS = [  # Choices for payment state
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    PAYMENT_METHODS = [  # Choices for payment method
        ('wallet', 'Wallet'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
    ]

    id = models.UUIDField(
        primary_key=True,        # Use UUID as primary key
        default=uuid.uuid4,       # Generate new UUID by default
        editable=False            # Prevent editing in forms/admin
    )
    order = models.ForeignKey(
        Order,                    # Link to Order model
        on_delete=models.CASCADE, # Delete payments when order is deleted
        related_name='payments',  # Access payments via order.payments
        db_index=True             # Indexing for faster queries
    )
    gateway = models.CharField(
        max_length=50,            # Store gateway name up to 50 chars
        help_text="Name of the payment gateway used"  # Admin documentation
    )
    method = models.CharField(
        max_length=20,            # Store method choice key
        choices=PAYMENT_METHODS,  # Restrict to defined methods
        help_text="Payment method"  # Admin documentation
    )

    transaction_id = models.CharField(
        max_length=255,           # Store external transaction ID
        blank=True,               # Allow blank in forms for pending payments
        null=True,                # Allow NULL in database until finalized
        unique=True,              # Enforce uniqueness when provided
        help_text="Gateway-issued transaction ID (must be set when status=success)"
    )
    amount = models.DecimalField(
        max_digits=10,            # Total digits allowed
        decimal_places=2,         # Two decimal places
        validators=[MinValueValidator(0.01)],  # Must be >= 0.01
        help_text="Amount charged"  # Admin documentation
    )
    currency = models.CharField(
        max_length=3,             # ISO currency code length
        default="INR",           # Default currency
        help_text="ISO 4217 currency code"  # Admin documentation
    )
    status = models.CharField(
        max_length=20,            # Store status choice key
        choices=PAYMENT_STATUS,   # Restrict to defined statuses
        default='pending',        # Default to pending state
        help_text="Current payment status"  # Admin documentation
    )
    created_at = models.DateTimeField(
        auto_now_add=True         # Timestamp when record is created
    )
    updated_at = models.DateTimeField(
        auto_now=True             # Timestamp on each save
    )
    raw_response = models.JSONField(
        default=dict,             # Store full gateway JSON response
        help_text="Full JSON payload from gateway"  # Admin documentation
    )

    class Meta:
        indexes = [
            models.Index(fields=['status']),      # Speed up filtering by status
            models.Index(fields=['created_at']),  # Speed up date-based queries
        ]
        ordering = ['-created_at']  # Default ordering: newest first

    def __str__(self):
        # Display status and transaction or UUID in admin/logs
        return f"{self.get_status_display()} payment {self.transaction_id or self.id}"

    @property
    def is_success(self):
        # Convenience property to check if payment succeeded
        return self.status == 'success'