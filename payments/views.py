# ✅ Import necessary Django REST framework components
from rest_framework.views import APIView         # Base class for DRF views
from rest_framework.response import Response    # Standard API response
from rest_framework import status               # HTTP status codes

# ✅ Import Django utilities for database transactions and error handling
from django.db import transaction, IntegrityError  # DB transaction & errors

# ✅ Import serializers and models for handling payment data
from .serializers import PaymentSerializer  # Import our serializer
from .models import Payment                     # Payment model

# ✅ Import service layer responsible for handling payment interactions
from .services import PaymentService            # Service layer for payments

# ✅ Import logging for debugging and tracing API activity
import logging                                   # Logging for debugging & tracing

logger = logging.getLogger(__name__)  # Configure module-level logger

class CreatePaymentView(APIView):  # API endpoint to initiate payments
    def post(self, request):
        """
        Handles payment creation:
        - Validates request data using PaymentSerializer.
        - Saves a pending Payment record in the database.
        - Initiates payment creation via the payment gateway.
        - Updates transaction_id with the gateway order ID.
        - Responds with summary payment details.
        """
        data = request.data  # Extract webhook payload
        logger.info(f"Webhook received: {data}")  # ✅ Print for debugging
        serializer = PaymentSerializer(data=request.data)  # Deserialize input data
        serializer.is_valid(raise_exception=True)  # Validate or return 400 response

        try:
            with transaction.atomic():  # Ensure atomic DB and gateway operations
                payment = serializer.save()  # Create initial pending Payment

                gateway = PaymentService.get_gateway()  # Get current gateway instance
                try:
                    gateway_order = gateway.create_payment_order(
                        amount=payment.amount,       # Amount in major units (e.g. INR)
                        currency=payment.currency,   # Currency (e.g. "INR")
                        payment_id=str(payment.id)   # Our internal Payment ID
                    )
                    # ✅  log to see Razorpay's full response in console/logs
                    logger.info(f"Razorpay Response at Payment Creation: {gateway_order}")
                except Exception as e:
                    logger.error(f"Payment gateway error: {str(e)}")  # Log gateway failure
                    raise ValueError("Payment gateway error. Please try again later.")

                # ✅ Store Razorpay's response in the database
                payment.transaction_id = gateway_order.get('id')
                payment.raw_response = gateway_order  # ✅ Ensure full response is saved
                payment.save()

            # Return confirmation response
            return Response({
                "payment_id": str(payment.id),
                "gateway_order_id": gateway_order.get("id"),
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_link": gateway_order.get("short_url")  # ✅ Hosted checkout link
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            logger.error("Database integrity error during payment creation.")  # Log DB issues
            return Response({"error": "Database integrity error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ValueError as e:
            logger.warning(f"Payment processing issue: {str(e)}")  # Log business logic error
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCallbackView(APIView):
    """
    Webhook endpoint for Razorpay payment callbacks:
    - Receives payment confirmation updates from Razorpay.
    - Validates payment authenticity using signature verification.
    - Ensures payment hasn’t already been processed.
    - Updates payment status and stores transaction metadata.
    - Calls `finalize_payment()` to complete associated order processing.
    """

    def post(self, request):
        """
        Handles Razorpay webhook callbacks for payment confirmation:
        - Extracts and logs callback data.
        - Verifies Razorpay signature for security.
        - Updates payment status in the database.
        - Finalizes order processing if payment is successful.
        """
        data = request.data  # ✅ Extract webhook payload from Razorpay
        logger.info(f"Payment callback received: {data}")  # ✅ Log webhook event for debugging

        gateway = PaymentService.get_gateway()  # ✅ Get Razorpay gateway instance

        # ✅ Extract and validate payment ID
        payment_id = data.get("razorpay_payment_id")
        if not payment_id:
            logger.warning("Missing Razorpay payment ID.")
            return Response({"error": "Payment ID missing."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Retrieve payment record from the database
        try:
            payment = Payment.objects.get(transaction_id=payment_id)
        except Payment.DoesNotExist:
            logger.warning(f"Invalid payment ID received: {payment_id}")
            return Response({"error": "Invalid payment ID."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Prevent duplicate processing
        if payment.status == 'success':
            logger.info(f"Payment {payment_id} already marked as success.")
            return Response({"status": "already processed"}, status=status.HTTP_200_OK)

        # ✅ Verify Razorpay signature
        verification_data = {
            "razorpay_order_id": data.get("razorpay_order_id"),
            "razorpay_payment_id": data.get("razorpay_payment_id"),
            "razorpay_signature": data.get("razorpay_signature")
        }

        logger.info(f"Verifying payment with: {verification_data}")

        if not gateway.verify_payment(verification_data):
            logger.error(f"Payment verification failed for {payment_id}.")
            return Response({"error": "Verification failed."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # ✅ Fetch latest payment status directly from Razorpay API
        payment_details = gateway.client.payment.fetch(payment_id)
        payment_status = payment_details.get("status", "failed")

        # ✅ Update payment record with final status (Captured = Success)
        payment.status = 'success' if payment_status == "captured" else 'failed'
        payment.transaction_id = payment_id  # ✅ Ensure transaction_id matches Razorpay's actual payment ID
        payment.raw_response = data  # ✅ Store webhook payload for reference
        payment.save()  # ✅ Commit changes to database

        logger.info(f"Payment {payment.id} status updated to {payment.status}")

        # ✅ Trigger order finalization
        PaymentService.finalize_payment(payment)

        return Response({"status": payment.status}, status=status.HTTP_200_OK)

    def get(self, request):
        """
        Handles GET requests to `/callback/`.
        This is for **debugging purposes only**. In production, callbacks should always use POST.
        """
        logger.info("GET callback hit")  # ✅ Log GET request activity
        print("Payment callback GET hit.", request.query_params)  # ✅ Debugging output
        return Response({"message": "GET callback received. This should be POST in production."})
