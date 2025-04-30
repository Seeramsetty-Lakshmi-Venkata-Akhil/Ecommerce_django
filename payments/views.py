from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from payments.payment_serializer import PaymentSerializer
from rest_framework.response import Response

from payments.payment_service import PaymentService


# Create your views here.
class Paymentview(APIView):
    def post(self, request):
        try:
            serializer = PaymentSerializer(data=request.data)

            if serializer.is_valid():
                order_id = serializer.validated_data.get('order_id')
                amount = serializer.validated_data.get('total_amount')

                # #call the order service and check whether the order exists
                payment_service = PaymentService()
                payment_link = payment_service.initiate_payment(order_id, amount)
                return Response({'payment_link': payment_link}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



