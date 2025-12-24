"""Tests for retry logic and deduplication."""
from notif.models import Event
from notif.service import NotificationService, FakeClock
from notif.sender import NotificationSender
from notif.retry import RetryPolicy


def test_retry_transient_failures():
    """
    Test that service retries transient failures up to max attempts.
    
    CURRENT STATUS: FAILS
    - Service doesn't implement retry logic
    - RetryPolicy.next_delay() returns 0
    - Need to implement retry with exponential backoff
    """
    clock = FakeClock(start_time=0.0)
    sender = NotificationSender()
    retry_policy = RetryPolicy(max_attempts=3, base_delay=1.0)
    service = NotificationService(
        sender=sender,
        retry_policy=retry_policy,
        clock=clock,
        workers=1
    )
    
    # Configure sender to fail twice then succeed
    event_id = 'event_retry_test'
    sender.configure_failures(event_id, num_failures=2)
    
    event = Event(
        id=event_id,
        user_id='user_1',
        channel='email',
        payload={'subject': 'Test', 'body': 'Hello'}
    )
    service.enqueue(event)
    
    # Process with retries
    # Attempt 1: fail, schedule retry with 1s delay
    service.process_once()
    assert service.get_delivered_count() == 0, 'First attempt should fail'
    
    # Advance clock for retry delay
    clock.advance(1.0)
    
    # Attempt 2: fail again, schedule retry with 2s delay
    service.process_once()
    assert service.get_delivered_count() == 0, 'Second attempt should fail'
    
    # Advance clock for retry delay
    clock.advance(2.0)
    
    # Attempt 3: succeed
    service.process_once()
    assert service.get_delivered_count() == 1, 'Third attempt should succeed'


def test_retry_exponential_backoff():
    """
    Test that retry delays follow exponential backoff: 1s, 2s, 4s.
    
    CURRENT STATUS: FAILS
    - RetryPolicy.next_delay() returns 0
    - Need to implement exponential backoff
    """
    retry_policy = RetryPolicy(max_attempts=3, base_delay=1.0)
    
    # Check delays for each attempt
    assert retry_policy.next_delay(0) == 1.0, 'First retry should be 1s'
    assert retry_policy.next_delay(1) == 2.0, 'Second retry should be 2s'
    assert retry_policy.next_delay(2) == 4.0, 'Third retry should be 4s'


def test_max_retry_attempts_exceeded():
    """
    Test that after max attempts, event is marked as failed (not retried forever).
    
    CURRENT STATUS: FAILS
    - No retry logic implemented
    """
    clock = FakeClock(start_time=0.0)
    sender = NotificationSender()
    retry_policy = RetryPolicy(max_attempts=3, base_delay=1.0)
    service = NotificationService(
        sender=sender,
        retry_policy=retry_policy,
        clock=clock,
        workers=1
    )
    
    # Configure sender to always fail
    event_id = 'event_always_fail'
    sender.configure_failures(event_id, num_failures=999)  # Fail many times
    
    event = Event(
        id=event_id,
        user_id='user_1',
        channel='email',
        payload={'subject': 'Test', 'body': 'Hello'}
    )
    service.enqueue(event)
    
    # Try processing multiple times with time advances
    for attempt in range(5):
        service.process_once()
        clock.advance(10.0)  # Advance time for potential retry
    
    # Should not be delivered (all attempts failed)
    assert service.get_delivered_count() == 0, \
        'Event should not be delivered after max retry attempts'


def test_deduplication_same_event_id():
    """
    Test that duplicate events (same event.id) result in only one delivery.
    
    CURRENT STATUS: FAILS
    - No deduplication logic implemented
    """
    clock = FakeClock()
    sender = NotificationSender()
    service = NotificationService(sender=sender, clock=clock, workers=1)
    
    event_id = 'duplicate_event'
    
    # Enqueue same event ID twice
    event1 = Event(
        id=event_id,
        user_id='user_1',
        channel='email',
        payload={'subject': 'First', 'body': 'Hello'}
    )
    service.enqueue(event1)
    
    event2 = Event(
        id=event_id,  # Same ID!
        user_id='user_1',
        channel='email',
        payload={'subject': 'Second', 'body': 'Hello'}
    )
    service.enqueue(event2)
    
    # Process both
    service.process_once()
    service.process_once()
    
    # Should only deliver once (deduplicated)
    assert service.get_delivered_count() == 1, \
        f'Expected 1 delivery (deduplicated), got {service.get_delivered_count()}'


def test_deduplication_across_retries():
    """
    Test that retry attempts for the same event don't count as duplicates.
    
    CURRENT STATUS: FAILS
    - No retry or deduplication logic
    """
    clock = FakeClock(start_time=0.0)
    sender = NotificationSender()
    retry_policy = RetryPolicy(max_attempts=3, base_delay=1.0)
    service = NotificationService(
        sender=sender,
        retry_policy=retry_policy,
        clock=clock,
        workers=1
    )
    
    # Configure sender to fail once then succeed
    event_id = 'event_with_retry'
    sender.configure_failures(event_id, num_failures=1)
    
    event = Event(
        id=event_id,
        user_id='user_1',
        channel='email',
        payload={'subject': 'Test', 'body': 'Hello'}
    )
    service.enqueue(event)
    
    # First attempt: fails
    service.process_once()
    clock.advance(1.0)
    
    # Second attempt: succeeds
    service.process_once()
    
    # Should have exactly 1 successful delivery (not counted as duplicate)
    assert service.get_delivered_count() == 1, \
        f'Expected 1 delivery (retry not duplicate), got {service.get_delivered_count()}'


def test_deduplication_different_event_ids():
    """
    Test that events with different IDs are not deduplicated.
    
    CURRENT STATUS: PASSES (baseline behavior)
    - Should continue to pass after implementing deduplication
    """
    clock = FakeClock()
    sender = NotificationSender()
    service = NotificationService(sender=sender, clock=clock, workers=1)
    
    # Enqueue two events with different IDs
    event1 = Event(
        id='event_1',
        user_id='user_1',
        channel='email',
        payload={'subject': 'First', 'body': 'Hello'}
    )
    service.enqueue(event1)
    
    event2 = Event(
        id='event_2',  # Different ID
        user_id='user_1',
        channel='email',
        payload={'subject': 'Second', 'body': 'Hello'}
    )
    service.enqueue(event2)
    
    # Process both
    service.process_once()
    service.process_once()
    
    # Both should be delivered (different IDs)
    assert service.get_delivered_count() == 2, \
        f'Expected 2 deliveries (different IDs), got {service.get_delivered_count()}'
