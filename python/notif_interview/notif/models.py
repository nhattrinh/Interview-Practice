"""Data models for events and notifications."""
from dataclasses import dataclass
from typing import Dict


@dataclass
class Event:
    """An event that triggers a notification."""
    id: str
    user_id: str
    channel: str
    payload: Dict


@dataclass
class DeliveryResult:
    """Result of attempting to deliver a notification."""
    ok: bool
    reason: str = ''


class Notification:
    """Base class for all notification types."""
    
    def __init__(self, event: Event):
        self.event = event
    
    def to_message(self) -> str:
        """Convert notification to a message string."""
        raise NotImplementedError('Subclasses must implement to_message()')


class EmailNotification(Notification):
    """Email notification."""
    
    def to_message(self) -> str:
        """Convert to email message."""
        subject = self.event.payload.get('subject', 'No subject')
        body = self.event.payload.get('body', '')
        return f'Email to {self.event.user_id}: {subject} - {body}'


class SMSNotification(Notification):
    """SMS notification."""
    
    def to_message(self) -> str:
        """Convert to SMS message."""
        text = self.event.payload.get('text', '')
        return f'SMS to {self.event.user_id}: {text}'


# TODO: Factory - Add notification factory/registry pattern here
# Currently, channel -> notification class mapping is hardcoded in service.py
# Interviewee should create a factory that allows registering new notification types
