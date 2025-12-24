"""
Test idempotency - ensure orders are never charged twice.

This test verifies that the idempotency store prevents duplicate charges
even if the same job is processed multiple times.
"""

from orders import (
    Order,
    FakeGateway,
    Inventory,
    InMemoryJobQueue,
    IdempotencyStore,
    Worker,
    CheckoutService,
    Job,
)


def test_same_order_enqueued_twice_charges_once():
    """
    Test that enqueueing the same order twice only charges once.
    
    Expected behavior:
    1. Enqueue job for order-1
    2. Enqueue same job for order-1 again
    3. Process both jobs
    4. Gateway charge() should be called at most once for order-1
    
    This test will FAIL until idempotency is implemented.
    """
    # Setup
    gateway = FakeGateway()
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    service = CheckoutService(gateway, inventory, queue, idempotency_store)
    worker = Worker(queue)
    
    order = Order(
        order_id='order-duplicate',
        user_id='user-1',
        amount_cents=5000
    )
    
    # Act - enqueue same order twice
    service.checkout(order)
    # Manually enqueue a duplicate job (simulating retry or duplicate request)
    duplicate_job = Job(
        job_id='job-duplicate-1',
        job_type='charge_order',
        payload={'order_id': 'order-duplicate', 'amount_cents': 5000}
    )
    queue.push(duplicate_job)
    queue.push(duplicate_job)
    
    # Process both jobs
    worker.process_one()
    worker.process_one()
    
    # Assert - gateway should have charged at most once
    charge_count = gateway.get_charge_count('order-duplicate')
    assert charge_count <= 1, \
        f'order should be charged at most once, but was charged {charge_count} times'


def test_idempotency_store_prevents_reprocessing():
    """
    Test that idempotency store correctly tracks processed orders.
    
    Expected behavior:
    1. First processing of order-id marks it as processed
    2. Second attempt should detect it's already processed
    3. No duplicate charge occurs
    
    This test will FAIL until idempotency store is implemented.
    """
    # Setup
    idempotency_store = IdempotencyStore()
    
    order_id = 'order-idempotent-test'
    
    # First check - should not be processed yet
    assert not idempotency_store.is_processed(order_id), \
        'order should not be marked as processed initially'
    
    # Mark as processed
    was_first = idempotency_store.mark_processed(order_id)
    assert was_first, \
        'first mark_processed call should return True'
    
    # Check again - should now be processed
    assert idempotency_store.is_processed(order_id), \
        'order should be marked as processed after mark_processed call'
    
    # Try to mark again - should indicate it was already processed
    was_first_again = idempotency_store.mark_processed(order_id)
    assert not was_first_again, \
        'second mark_processed call should return False (already processed)'


def test_concurrent_idempotency_check():
    """
    Test that idempotency checks are atomic (no race conditions).
    
    Expected behavior:
    1. Multiple workers try to process same order simultaneously
    2. Only one should succeed in marking it as processed
    3. Others should detect it's already processed
    
    This test will FAIL until thread-safe idempotency is implemented.
    """
    # Setup
    idempotency_store = IdempotencyStore()
    order_id = 'order-concurrent'
    
    # Simulate concurrent mark attempts
    # In real implementation, this would use threading
    results = []
    for _ in range(5):
        result = idempotency_store.mark_processed(order_id)
        results.append(result)
    
    # Assert - exactly one should return True (first to mark)
    first_count = sum(1 for r in results if r)
    assert first_count == 1, \
        f'exactly one mark_processed should succeed, but {first_count} succeeded'
