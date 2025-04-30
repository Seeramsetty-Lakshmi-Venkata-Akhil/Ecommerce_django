from rest_framework import serializers

class PaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    total_amount = serializers.FloatField()
