"""Tests for OOP extensibility via factory/registry pattern."""
from notif.models import Event, Notification, DeliveryResult
from notif.service import NotificationService, FakeClock
from notif.sender import NotificationSender


class PushNotification(Notification):
    """Push notification - new channel type defined in test."""
    
    def to_message(self) -> str:
        """Convert to push message."""
        title = self.event.payload.get('title', 'No title')
        body = self.event.payload.get('body', '')
        return f'Push to {self.event.user_id}: {title} - {body}'


def test_add_new_notification_type_via_registry():
    """
    Test that a new notification type can be added without modifying service code.
    
    CURRENT STATUS: FAILS
    - No factory/registry pattern implemented
    - Service has hardcoded channel -> class mapping
    - Need to add factory with registration API
    """
    clock = FakeClock()
    sender = NotificationSender()
    service = NotificationService(sender=sender, clock=clock, workers=1)
    
    # TODO: Service should have a method like register_notification_type()
    # or a factory that can be extended
    # Example API: service.register_notification_type('push', PushNotification)
    
    # For now, this will fail because 'push' channel is not recognized
    event = Event(
        id='push_event_1',
        user_id='user_1',
        channel='push',  # New channel type!
        payload={'title': 'New Message', 'body': 'You have a notification'}
    )
    service.enqueue(event)
    service.process_once()
    
    # Should be delivered successfully
    # Currently fails because service doesn't recognize 'push' channel
    assert service.get_delivered_count() == 1, \
        'Push notification should be delivered after registering new type'


def test_factory_pattern_extensibility():
    """
    Test that notification factory allows extension without modifying core service.
    
    CURRENT STATUS: FAILS
    - Need to implement factory pattern in models.py
    - Need to refactor service.py to use factory instead of hardcoded if/else
    """
    clock = FakeClock()
    sender = NotificationSender()
    service = NotificationService(sender=sender, clock=clock, workers=1)
    
    # Register custom notification type
    # TODO: Implement something like:
    # from notif.models import NotificationFactory
    # NotificationFactory.register('push', PushNotification)
    
    # Create events for different channels
    events = [
        Event(
            id='email_1',
            user_id='user_1',
            channel='email',
            payload={'subject': 'Email Test', 'body': 'Hello'}
        ),
        Event(
            id='sms_1',
            user_id='user_1',
            channel='sms',
            payload={'text': 'SMS Test'}
        ),
        Event(
            id='push_1',
            user_id='user_1',
            channel='push',  # Custom channel
            payload={'title': 'Push Test', 'body': 'Hello'}
        ),
    ]
    
    for event in events:
        service.enqueue(event)
    
    # Process all
    for _ in range(3):
        service.process_once()
    
    # All three should be delivered (including custom push type)
    assert service.get_delivered_count() == 3, \
        f'Expected 3 delivered (including custom push), got {service.get_delivered_count()}'


def test_multiple_custom_notification_types():
    """
    Test registering multiple custom notification types.
    
    CURRENT STATUS: FAILS
    - No factory/registry pattern
    """
    
    class SlackNotification(Notification):
        """Slack notification."""
        def to_message(self) -> str:
            channel = self.event.payload.get('channel', '#general')
            text = self.event.payload.get('text', '')
            return f'Slack to {channel}: {text}'
    
    class WebhookNotification(Notification):
        """Webhook notification."""
        def to_message(self) -> str:
            url = self.event.payload.get('url', 'unknown')
            data = self.event.payload.get('data', {})
            return f'Webhook to {url}: {data}'
    
    clock = FakeClock()
    sender = NotificationSender()
    service = NotificationService(sender=sender, clock=clock, workers=1)
    
    # Register multiple custom types
    # TODO: Implement registration API
    # service.register_notification_type('slack', SlackNotification)
    # service.register_notification_type('webhook', WebhookNotification)
    
    events = [
        Event(
            id='slack_1',
            user_id='user_1',
            channel='slack',
            payload={'channel': '#engineering', 'text': 'Deploy complete'}
        ),
        Event(
            id='webhook_1',
            user_id='user_1',
            channel='webhook',
            payload={'url': 'https://example.com/hook', 'data': {'status': 'ok'}}
        ),
    ]
    
    for event in events:
        service.enqueue(event)
    
    for _ in range(2):
        service.process_once()
    
    # Both custom types should be delivered
    assert service.get_delivered_count() == 2, \
        f'Expected 2 delivered (multiple custom types), got {service.get_delivered_count()}'


def test_factory_preserves_existing_channels():
    """
    Test that adding factory pattern doesn't break existing email/sms channels.
    
    CURRENT STATUS: PASSES (baseline)
    - Should continue to pass after implementing factory
    """
    clock = FakeClock()
    sender = NotificationSender()
    service = NotificationService(sender=sender, clock=clock, workers=1)
    
    events = [
        Event(
            id='email_1',
            user_id='user_1',
            channel='email',
            payload={'subject': 'Test', 'body': 'Hello'}
        ),
        Event(
            id='sms_1',
            user_id='user_1',
            channel='sms',
            payload={'text': 'Hello'}
        ),
    ]
    
    for event in events:
        service.enqueue(event)
    
    service.process_once()
    service.process_once()
    
    # Both existing channels should work
    assert service.get_delivered_count() == 2, \
        f'Expected 2 delivered (existing channels), got {service.get_delivered_count()}'
