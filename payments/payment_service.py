import uuid

from payments.paymentGateway.payment_gateway import RazorpayPaymentGateway


class PaymentService:

    #what ever payment service we have we can generate payment with that service so take it as argument/parameter
    def __init__(self):
        self.client = RazorpayPaymentGateway()

    def verify_order(self, order_id):
        #call the order service and get the data and verify the order exists or not and return order details
        pass

    def initiate_payment(self, order_id, amount):
        order_details = self.verify_order(order_id)

        payment_id =uuid.uuid4()
        data = self.client.get_payment(order_id, payment_id, amount)
        # if completed update the model to success/fail also call order service update status api
        return data

