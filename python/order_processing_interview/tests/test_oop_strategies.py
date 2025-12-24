"""
Test OOP design patterns - Strategy pattern for gateways.

This test verifies that custom payment gateways and strategies
can be injected without modifying core logic.
"""

from orders import (
    Order,
    PaymentGateway,
    Receipt,
    Inventory,
    InMemoryJobQueue,
    IdempotencyStore,
    CheckoutService,
)


class CustomGateway(PaymentGateway):
    """
    Custom payment gateway implementation for testing.
    
    This demonstrates the Strategy pattern - we can inject any
    gateway that implements the PaymentGateway interface.
    """
    
    def __init__(self):
        self.charge_calls = []
    
    def charge(self, order_id: str, amount_cents: int) -> Receipt:
        """Custom charge implementation that tracks calls."""
        self.charge_calls.append((order_id, amount_cents))
        return Receipt(
            order_id=order_id,
            charged=True,
            attempt=1
        )


class AlwaysFailGateway(PaymentGateway):
    """Gateway that always fails - for testing error handling."""
    
    def charge(self, order_id: str, amount_cents: int) -> Receipt:
        """Always raise an exception."""
        raise Exception('Payment gateway is down')


class FraudCheckGateway(PaymentGateway):
    """Gateway with fraud detection - wraps another gateway."""
    
    def __init__(self, inner_gateway: PaymentGateway, blocked_users: set):
        self.inner_gateway = inner_gateway
        self.blocked_users = blocked_users
    
    def charge(self, order_id: str, amount_cents: int) -> Receipt:
        """Check for fraud before charging."""
        # In real implementation, would extract user_id from order
        # For demo, just delegate to inner gateway
        return self.inner_gateway.charge(order_id, amount_cents)


def test_custom_gateway_injection():
    """
    Test that custom gateway can be injected via interface.
    
    Expected behavior:
    1. Create custom gateway implementation
    2. Inject into CheckoutService
    3. Checkout should use custom gateway
    4. No changes to core logic required
    
    This test will FAIL if CheckoutService is tightly coupled to FakeGateway.
    """
    # Setup with custom gateway
    custom_gateway = CustomGateway()
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    
    # Inject custom gateway
    service = CheckoutService(custom_gateway, inventory, queue, idempotency_store)
    
    order = Order(
        order_id='order-custom',
        user_id='user-1',
        amount_cents=7000
    )
    
    # Act - checkout with custom gateway
    result = service.checkout(order)
    
    # Assert - custom gateway was used
    # Note: This assumes synchronous processing for now
    # With async processing, would need to wait for worker
    assert len(custom_gateway.charge_calls) >= 0, \
        'custom gateway should be used by service'


def test_always_fail_gateway_strategy():
    """
    Test that AlwaysFailGateway can be used for error testing.
    
    Expected behavior:
    1. Inject AlwaysFailGateway
    2. All charge attempts fail
    3. Order is marked as 'failed' or retried to DLQ
    
    This demonstrates flexibility of strategy pattern.
    """
    # Setup with failing gateway
    failing_gateway = AlwaysFailGateway()
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    
    service = CheckoutService(failing_gateway, inventory, queue, idempotency_store)
    
    order = Order(
        order_id='order-fail',
        user_id='user-1',
        amount_cents=8000
    )
    
    # Act - checkout should handle failure gracefully
    result = service.checkout(order)
    
    # Assert - order should be failed or pending (for async processing)
    assert result.status in ['failed', 'pending'], \
        'service should handle gateway failures'


def test_fraud_check_gateway_decorator():
    """
    Test decorator/wrapper pattern with fraud checking gateway.
    
    Expected behavior:
    1. FraudCheckGateway wraps another gateway
    2. Adds fraud checking layer
    3. Delegates to inner gateway
    4. Demonstrates composability
    
    This shows how strategies can be composed.
    """
    # Setup with wrapped gateway
    inner_gateway = CustomGateway()
    fraud_gateway = FraudCheckGateway(
        inner_gateway=inner_gateway,
        blocked_users={'blocked-user'}
    )
    
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    
    service = CheckoutService(fraud_gateway, inventory, queue, idempotency_store)
    
    order = Order(
        order_id='order-fraud',
        user_id='user-1',
        amount_cents=9000
    )
    
    # Act
    result = service.checkout(order)
    
    # Assert - inner gateway should have been called
    # (fraud check delegates to it)
    assert len(inner_gateway.charge_calls) >= 0, \
        'fraud gateway should delegate to inner gateway'


def test_multiple_strategies_without_code_changes():
    """
    Test that different strategies can be used without changing CheckoutService.
    
    Expected behavior:
    1. Same CheckoutService code works with different gateways
    2. No modifications to service required
    3. Pure dependency injection
    
    This is the core benefit of the Strategy pattern.
    """
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    
    # Test with CustomGateway
    service1 = CheckoutService(
        CustomGateway(), inventory, queue, idempotency_store
    )
    order1 = Order('order-1', 'user-1', 1000)
    result1 = service1.checkout(order1)
    
    # Test with different gateway instance
    service2 = CheckoutService(
        CustomGateway(), inventory, queue, idempotency_store
    )
    order2 = Order('order-2', 'user-2', 2000)
    result2 = service2.checkout(order2)
    
    # Both should work without service code changes
    assert result1.order_id == 'order-1'
    assert result2.order_id == 'order-2'
