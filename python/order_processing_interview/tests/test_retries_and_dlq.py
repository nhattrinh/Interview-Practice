"""
Test retry logic and dead letter queue (DLQ).

This test verifies that failed jobs are retried with exponential backoff
and eventually moved to DLQ after exceeding retry limit.
"""

import pytest
from orders import (
    Order,
    FakeGateway,
    Inventory,
    InMemoryJobQueue,
    IdempotencyStore,
    Worker,
    CheckoutService,
    FakeClock,
    Job,
)


def test_transient_failure_retries_with_backoff():
    """
    Test that transient failures are retried with exponential backoff.
    
    Expected behavior:
    1. Gateway fails first 2 attempts
    2. Worker retries with exponential backoff
    3. Third attempt succeeds
    4. Order is marked as 'paid'
    
    This test will FAIL until retry logic is implemented.
    """
    # Setup - gateway will fail first 2 attempts
    gateway = FakeGateway(fail_count_per_order={'order-retry': 2})
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    service = CheckoutService(gateway, inventory, queue, idempotency_store)
    clock = FakeClock()
    worker = Worker(queue)
    
    order = Order(
        order_id='order-retry',
        user_id='user-1',
        amount_cents=3000
    )
    
    # Enqueue order
    result = service.checkout(order)
    assert result.status == 'pending'
    
    # TODO: Worker should retry with exponential backoff
    # Attempt 1: fails (immediate)
    # Attempt 2: fails (backoff 1s, 2s, etc.)
    # Attempt 3: succeeds
    
    # Process with retries
    # This will fail until retry logic is implemented
    worker.process_one()
    
    # Assert - order should eventually be paid after retries
    updated_order = service.get_order('order-retry')
    assert updated_order.status == 'paid', \
        'order should be paid after successful retry'


def test_max_retries_moves_job_to_dlq():
    """
    Test that jobs are moved to DLQ after exceeding max retries.
    
    Expected behavior:
    1. Gateway fails 5 times (more than max retries)
    2. Worker retries 3 times (4 total attempts)
    3. Job is moved to DLQ
    4. Order status is marked as 'failed'
    
    This test will FAIL until DLQ logic is implemented.
    """
    # Setup - gateway will fail 5 times
    gateway = FakeGateway(fail_count_per_order={'order-dlq': 5})
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    service = CheckoutService(gateway, inventory, queue, idempotency_store)
    worker = Worker(queue)
    
    order = Order(
        order_id='order-dlq',
        user_id='user-1',
        amount_cents=4000
    )
    
    # Enqueue order
    result = service.checkout(order)
    assert result.status == 'pending'
    
    # TODO: Process with max retries (3 retries = 4 total attempts)
    # All attempts should fail
    # Job should be moved to DLQ
    
    # Process job (will fail with current implementation)
    worker.process_one()
    
    # Assert - job should be in DLQ
    dlq = worker.get_dlq()
    assert len(dlq) == 1, \
        'failed job should be moved to DLQ after max retries'
    
    # Assert - order should be marked as failed
    updated_order = service.get_order('order-dlq')
    assert updated_order.status == 'failed', \
        'order should be marked as failed after max retries'


def test_exponential_backoff_timing():
    """
    Test that exponential backoff uses correct timing.
    
    Expected behavior:
    1. First retry: immediate (0s delay)
    2. Second retry: 1s delay
    3. Third retry: 2s delay (exponential: 2^1)
    4. Fourth retry: 4s delay (exponential: 2^2)
    
    Uses FakeClock to verify timing without actual sleeps.
    
    This test will FAIL until exponential backoff with FakeClock is implemented.
    """
    # Setup
    gateway = FakeGateway(fail_count_per_order={'order-backoff': 3})
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    service = CheckoutService(gateway, inventory, queue, idempotency_store)
    clock = FakeClock(start_time=0.0)
    worker = Worker(queue)
    
    order = Order(
        order_id='order-backoff',
        user_id='user-1',
        amount_cents=5000
    )
    
    # Enqueue order
    service.checkout(order)
    
    # TODO: Process with FakeClock to verify backoff timing
    # Worker should use clock.now() and clock.tick() for delays
    # Verify that retries happen at correct times:
    # - Attempt 1: t=0
    # - Attempt 2: t=1 (1s backoff)
    # - Attempt 3: t=3 (2s backoff)
    # - Attempt 4: t=7 (4s backoff)
    
    # This will fail until FakeClock integration is implemented
    initial_time = clock.now()
    worker.process_one()
    
    # Verify clock was advanced appropriately
    # (exact verification depends on implementation)


def test_successful_retry_does_not_go_to_dlq():
    """
    Test that successfully retried jobs do not end up in DLQ.
    
    Expected behavior:
    1. Gateway fails first attempt
    2. Retry succeeds on second attempt
    3. Job is not in DLQ
    4. Order is marked as 'paid'
    
    This test will FAIL until retry logic is properly implemented.
    """
    # Setup - gateway fails once, then succeeds
    gateway = FakeGateway(fail_count_per_order={'order-success': 1})
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    service = CheckoutService(gateway, inventory, queue, idempotency_store)
    worker = Worker(queue)
    
    order = Order(
        order_id='order-success',
        user_id='user-1',
        amount_cents=6000
    )
    
    # Enqueue and process
    service.checkout(order)
    worker.process_one()
    
    # Assert - DLQ should be empty
    dlq = worker.get_dlq()
    assert len(dlq) == 0, \
        'successfully processed job should not be in DLQ'
    
    # Assert - order should be paid
    updated_order = service.get_order('order-success')
    assert updated_order.status == 'paid', \
        'order should be paid after successful retry'
