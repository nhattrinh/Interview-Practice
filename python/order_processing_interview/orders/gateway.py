"""Payment gateway interface and fake implementation."""

from abc import ABC, abstractmethod
from typing import Dict

from .models import Receipt


class PaymentGateway(ABC):
    """Abstract interface for payment processing."""
    
    @abstractmethod
    def charge(self, order_id: str, amount_cents: int) -> Receipt:
        """
        Charge the specified amount for an order.
        
        Args:
            order_id: Unique identifier for the order
            amount_cents: Amount to charge in cents
            
        Returns:
            Receipt with charge result
            
        Raises:
            Exception: If payment fails
        """
        pass


class FakeGateway(PaymentGateway):
    """
    Fake payment gateway that simulates transient failures.
    
    Fails the first N attempts per order_id, then succeeds.
    This enables deterministic testing of retry logic.
    """
    
    def __init__(self, fail_count_per_order: Dict[str, int] = None):
        """
        Initialize fake gateway.
        
        Args:
            fail_count_per_order: Dict mapping order_id to number of times 
                                 it should fail before succeeding
        """
        self.fail_count_per_order = fail_count_per_order or {}
        self.attempt_count: Dict[str, int] = {}
        self.charge_count: Dict[str, int] = {}
    
    def charge(self, order_id: str, amount_cents: int) -> Receipt:
        """
        Simulate charging payment.
        
        Fails deterministically based on configuration.
        """
        # Track attempt count
        current_attempt = self.attempt_count.get(order_id, 0) + 1
        self.attempt_count[order_id] = current_attempt
        
        # Check if we should fail this attempt
        fail_count = self.fail_count_per_order.get(order_id, 0)
        
        if current_attempt <= fail_count:
            # Simulate transient failure
            raise Exception(f'Payment gateway error for order {order_id} (attempt {current_attempt})')
        
        # Success - track that we charged
        self.charge_count[order_id] = self.charge_count.get(order_id, 0) + 1
        
        return Receipt(
            order_id=order_id,
            charged=True,
            attempt=current_attempt
        )
    
    def get_charge_count(self, order_id: str) -> int:
        """Get number of successful charges for an order."""
        return self.charge_count.get(order_id, 0)
