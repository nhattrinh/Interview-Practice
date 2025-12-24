"""Tests for rate limiting."""
from notif.models import Event
from notif.service import NotificationService, FakeClock
from notif.sender import NotificationSender
from notif.rate_limit import RateLimiter


def test_rate_limit_per_user_channel():
    """
    Test that rate limiting enforces max 5 notifications per 60s per (user, channel).
    
    CURRENT STATUS: FAILS
    - RateLimiter.allow() always returns True
    - Need to implement token bucket algorithm
    """
    clock = FakeClock(start_time=1000.0)
    sender = NotificationSender()
    rate_limiter = RateLimiter(max_tokens=5, window_seconds=60.0)
    service = NotificationService(
        sender=sender,
        rate_limiter=rate_limiter,
        clock=clock,
        workers=1
    )
    
    # Enqueue 10 events for same user and channel within same time window
    for i in range(10):
        event = Event(
            id=f'event_{i}',
            user_id='user_1',
            channel='email',
            payload={'subject': f'Test {i}', 'body': 'Hello'}
        )
        service.enqueue(event)
    
    # Process all events (single-threaded for this test)
    for _ in range(10):
        service.process_once()
    
    # Only first 5 should be delivered (rate limit = 5 per 60s)
    delivered = service.get_delivered_count()
    assert delivered == 5, \
        f'Expected exactly 5 delivered due to rate limit, got {delivered}'


def test_rate_limit_resets_after_window():
    """
    Test that rate limit window resets, allowing more notifications.
    
    CURRENT STATUS: FAILS
    - RateLimiter not implemented
    """
    clock = FakeClock(start_time=1000.0)
    sender = NotificationSender()
    rate_limiter = RateLimiter(max_tokens=5, window_seconds=60.0)
    service = NotificationService(
        sender=sender,
        rate_limiter=rate_limiter,
        clock=clock,
        workers=1
    )
    
    # Send 5 events at time 1000
    for i in range(5):
        event = Event(
            id=f'event_batch1_{i}',
            user_id='user_1',
            channel='email',
            payload={'subject': f'Batch1 {i}', 'body': 'Hello'}
        )
        service.enqueue(event)
    
    for _ in range(5):
        service.process_once()
    
    assert service.get_delivered_count() == 5
    
    # Advance time by 61 seconds (past the 60s window)
    clock.advance(61.0)
    
    # Send 5 more events - should be allowed since window reset
    for i in range(5):
        event = Event(
            id=f'event_batch2_{i}',
            user_id='user_1',
            channel='email',
            payload={'subject': f'Batch2 {i}', 'body': 'Hello'}
        )
        service.enqueue(event)
    
    for _ in range(5):
        service.process_once()
    
    # Total delivered should be 10 (5 + 5 after window reset)
    assert service.get_delivered_count() == 10, \
        f'Expected 10 delivered after window reset, got {service.get_delivered_count()}'


def test_rate_limit_separate_per_user():
    """
    Test that rate limits are tracked separately per user.
    
    CURRENT STATUS: FAILS
    - RateLimiter not implemented
    """
    clock = FakeClock(start_time=1000.0)
    sender = NotificationSender()
    rate_limiter = RateLimiter(max_tokens=5, window_seconds=60.0)
    service = NotificationService(
        sender=sender,
        rate_limiter=rate_limiter,
        clock=clock,
        workers=1
    )
    
    # Send 5 events for user_1
    for i in range(5):
        event = Event(
            id=f'event_user1_{i}',
            user_id='user_1',
            channel='email',
            payload={'subject': f'User1 {i}', 'body': 'Hello'}
        )
        service.enqueue(event)
    
    # Send 5 events for user_2 (different user, should have separate limit)
    for i in range(5):
        event = Event(
            id=f'event_user2_{i}',
            user_id='user_2',
            channel='email',
            payload={'subject': f'User2 {i}', 'body': 'Hello'}
        )
        service.enqueue(event)
    
    # Process all events
    for _ in range(10):
        service.process_once()
    
    # Both users should get their 5 notifications (separate rate limits)
    assert service.get_delivered_count() == 10, \
        f'Expected 10 delivered (5 per user), got {service.get_delivered_count()}'


def test_rate_limit_separate_per_channel():
    """
    Test that rate limits are tracked separately per channel.
    
    CURRENT STATUS: FAILS
    - RateLimiter not implemented
    """
    clock = FakeClock(start_time=1000.0)
    sender = NotificationSender()
    rate_limiter = RateLimiter(max_tokens=5, window_seconds=60.0)
    service = NotificationService(
        sender=sender,
        rate_limiter=rate_limiter,
        clock=clock,
        workers=1
    )
    
    # Send 5 email events for user_1
    for i in range(5):
        event = Event(
            id=f'event_email_{i}',
            user_id='user_1',
            channel='email',
            payload={'subject': f'Email {i}', 'body': 'Hello'}
        )
        service.enqueue(event)
    
    # Send 5 SMS events for user_1 (same user, different channel)
    for i in range(5):
        event = Event(
            id=f'event_sms_{i}',
            user_id='user_1',
            channel='sms',
            payload={'text': f'SMS {i}'}
        )
        service.enqueue(event)
    
    # Process all events
    for _ in range(10):
        service.process_once()
    
    # Both channels should get their 5 notifications (separate rate limits)
    assert service.get_delivered_count() == 10, \
        f'Expected 10 delivered (5 per channel), got {service.get_delivered_count()}'
