"""Notification sender with configurable failure modes."""
from typing import Dict
from notif.models import Notification, DeliveryResult


class NotificationSender:
    """
    Sends notifications to external services.
    
    This is a fake sender for testing that can be configured to fail N times
    for specific message IDs before succeeding.
    """
    
    def __init__(self):
        # Map of event_id -> remaining failure count
        self._failure_config: Dict[str, int] = {}
    
    def configure_failures(self, event_id: str, num_failures: int) -> None:
        """Configure sender to fail N times for given event_id before succeeding."""
        self._failure_config[event_id] = num_failures
    
    def send(self, notification: Notification) -> DeliveryResult:
        """
        Send a notification.
        
        Returns DeliveryResult indicating success or failure.
        For configured event IDs, will fail the configured number of times
        before succeeding (to test retry logic).
        """
        event_id = notification.event.id
        
        # Check if this event is configured to fail
        if event_id in self._failure_config:
            remaining_failures = self._failure_config[event_id]
            if remaining_failures > 0:
                self._failure_config[event_id] = remaining_failures - 1
                return DeliveryResult(ok=False, reason='transient_error')
        
        # Success case
        message = notification.to_message()
        # In real implementation, would actually send via API
        return DeliveryResult(ok=True, reason='')
