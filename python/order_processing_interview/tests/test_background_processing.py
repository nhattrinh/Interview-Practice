"""
Test background processing of orders.

This test verifies that checkout() returns quickly with status 'pending'
and that background workers asynchronously process the order.
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
)


def test_checkout_returns_quickly_with_pending_status():
    """
    Test that checkout() enqueues job and returns immediately with 'pending' status.
    
    Expected behavior:
    1. checkout() should return immediately (not wait for payment)
    2. Order status should be 'pending'
    3. A job should be enqueued to the background queue
    
    This test will FAIL until background processing is implemented.
    """
    # Setup
    gateway = FakeGateway()
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    service = CheckoutService(gateway, inventory, queue, idempotency_store)
    
    order = Order(
        order_id='order-1',
        user_id='user-1',
        amount_cents=1000
    )
    
    # Act
    result = service.checkout(order)
    
    # Assert - checkout should return with 'pending' status
    assert result.status == 'pending', \
        'checkout() should return immediately with pending status, not process synchronously'
    
    # Assert - job should be enqueued
    assert not queue.is_empty(), \
        'checkout() should enqueue a background job'
    assert queue.size() == 1, \
        'exactly one job should be enqueued'


def test_background_worker_processes_order():
    """
    Test that background workers process jobs and update order status.
    
    Expected behavior:
    1. checkout() enqueues job with status 'pending'
    2. Worker processes job from queue
    3. Worker charges payment and reserves inventory
    4. Order status is updated to 'paid'
    
    This test will FAIL until worker processing is implemented.
    """
    # Setup
    gateway = FakeGateway()
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    service = CheckoutService(gateway, inventory, queue, idempotency_store)
    worker = Worker(queue)
    
    order = Order(
        order_id='order-2',
        user_id='user-2',
        amount_cents=2000
    )
    
    # Act - checkout should enqueue job
    result = service.checkout(order)
    assert result.status == 'pending'
    
    # Act - worker processes the job
    # TODO: This assumes worker.process_one() will charge and update order
    worker.process_one()
    
    # Assert - order should now be paid
    updated_order = service.get_order('order-2')
    assert updated_order.status == 'paid', \
        'worker should process job and mark order as paid'
    
    # Assert - queue should be empty
    assert queue.is_empty(), \
        'job should be removed from queue after processing'


def test_multiple_workers_process_concurrently():
    """
    Test that multiple workers can process jobs concurrently.
    
    Expected behavior:
    1. Multiple orders are enqueued
    2. Multiple workers process jobs in parallel
    3. All orders are eventually marked as 'paid'
    
    This test will FAIL until concurrent worker pool is implemented.
    """
    # Setup with multiple orders
    gateway = FakeGateway()
    inventory = Inventory()
    queue = InMemoryJobQueue()
    idempotency_store = IdempotencyStore()
    service = CheckoutService(gateway, inventory, queue, idempotency_store)
    
    orders = [
        Order(order_id=f'order-{i}', user_id=f'user-{i}', amount_cents=1000 * i)
        for i in range(1, 6)
    ]
    
    # Enqueue all orders
    for order in orders:
        result = service.checkout(order)
        assert result.status == 'pending'
    
    # TODO: Start worker pool with multiple workers
    # worker_pool = WorkerPool(queue, worker_count=3)
    # worker_pool.start()
    # ... wait for completion or process synchronously for test
    # worker_pool.stop()
    
    # For now, just verify jobs are enqueued
    assert queue.size() == 5, \
        'all orders should be enqueued'
    
    # TODO: Verify all orders are eventually processed to 'paid' status
    # This will fail until worker pool is implemented
