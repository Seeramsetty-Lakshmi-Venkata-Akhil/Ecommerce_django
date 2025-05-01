from abc import ABC, abstractmethod  # Base class for gateway interface

class BasePaymentGateway(ABC):
    @abstractmethod
    def create_payment_order(self, amount, currency, payment_id): pass  # Create order in gateway
    @abstractmethod
    def verify_payment(self, payment_data): pass  # Verify callback data
