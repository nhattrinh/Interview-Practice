"""Tests for concurrency and graceful shutdown."""
from notif.models import Event
from notif.service import NotificationService, FakeClock
from notif.sender import NotificationSender


def test_concurrent_processing_with_workers():
    """
    Test that service can process many events concurrently with multiple workers.
    
    CURRENT STATUS: FAILS
    - Service only has single-threaded process_once()
    - Need to implement worker pool
    """
    clock = FakeClock()
    sender = NotificationSender()
    service = NotificationService(sender=sender, clock=clock, workers=4)
    
    # Enqueue 200 events
    events = []
    for i in range(200):
        event = Event(
            id=f'event_{i}',
            user_id=f'user_{i % 20}',  # 20 unique users
            channel='email',
            payload={'subject': f'Test {i}', 'body': 'Hello'}
        )
        events.append(event)
        service.enqueue(event)

    # Start service with workers
    service.start()

    # TODO: Service should process events concurrently
    # Currently need to manually call process_once() which is single-threaded
    # This test expects workers to process automatically

    # Wait for processing to complete
    # In proper implementation, workers process in background
    # For now, simulate with loop (but this is NOT concurrent)
    max_iterations = 250
    for _ in range(max_iterations):
        if service._queue.is_empty():
            break
        # In real implementation, workers do this automatically

    service.stop()

    # All 200 events should be delivered exactly once
    assert service.get_delivered_count() == 200, \
        f'Expected 200 delivered, got {service.get_delivered_count()}'


def test_graceful_shutdown_completes_inflight_work():
    """
    Test that stop() waits for in-flight work to complete.
    
    CURRENT STATUS: FAILS
    - No worker pool, so no in-flight work concept
    - Need to implement graceful shutdown
    """
    clock = FakeClock()
    sender = NotificationSender()
    service = NotificationService(sender=sender, clock=clock, workers=2)
    
    # Enqueue some events
    for i in range(20):
        event = Event(
            id=f'event_{i}',
            user_id=f'user_{i}',
            channel='email',
            payload={'subject': f'Test {i}', 'body': 'Hello'}
        )
        service.enqueue(event)
    
    service.start()
    
    # Let workers start processing (simulate some progress)
    # In real implementation, workers run in background
    clock.advance(0.1)
    
    # Stop service - should wait for in-flight work
    service.stop()
    
    # All enqueued events should be delivered (nothing lost)
    # This tests that stop() doesn't abort in-flight work
    assert service.get_delivered_count() == 20, \
        f'Expected 20 delivered, got {service.get_delivered_count()}. Some events were lost during shutdown!'


def test_shutdown_completes_promptly():
    """
    Test that shutdown completes quickly (no hanging).
    
    CURRENT STATUS: FAILS
    - No worker pool to shutdown
    - Need to implement bounded shutdown time
    """
    clock = FakeClock()
    sender = NotificationSender()
    service = NotificationService(sender=sender, clock=clock, workers=4)
    
    # Enqueue events
    for i in range(10):
        event = Event(
            id=f'event_{i}',
            user_id=f'user_{i}',
            channel='sms',
            payload={'text': f'Message {i}'}
        )
        service.enqueue(event)
    
    service.start()
    
    # Stop should complete promptly
    start_time = clock.now()
    service.stop()
    elapsed = clock.now() - start_time
    
    # In tests with FakeClock, shutdown should be nearly instant
    # Real implementation with real workers should complete within 1 second
    assert elapsed < 1.0, f'Shutdown took {elapsed}s, should be <1s'
