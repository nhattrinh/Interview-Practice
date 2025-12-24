"""Transport layer abstraction for message delivery."""

from abc import ABC, abstractmethod
from typing import Dict, List
from .models import Message


class Transport(ABC):
    """Abstract transport interface for sending messages to users."""
    
    @abstractmethod
    def send(self, user_id: str, message: Message) -> bool:
        """Send a message to a user.
        
        Args:
            user_id: Target user identifier
            message: Message to send
            
        Returns:
            True if message was accepted, False if transport is not ready
        """
        pass


class SlowTransport(Transport):
    """Transport that simulates slow users by requiring N ticks before accepting next send.
    
    Does not use sleep; instead tracks ticks and only accepts sends when ready.
    """
    
    def __init__(self, ticks_per_send: int):
        """Initialize slow transport.
        
        Args:
            ticks_per_send: Number of ticks required before accepting next send
        """
        self.ticks_per_send = ticks_per_send
        self._user_ticks: Dict[str, int] = {}  # tracks ticks until ready per user
        self._delivered: Dict[str, List[Message]] = {}  # stores delivered messages
        
    def send(self, user_id: str, message: Message) -> bool:
        """Attempt to send a message to a user.
        
        Returns True only if the required ticks have passed since the last send.
        """
        ticks_remaining = self._user_ticks.get(user_id, 0)
        
        if ticks_remaining > 0:
            return False  # not ready yet
            
        # Accept the message
        if user_id not in self._delivered:
            self._delivered[user_id] = []
        self._delivered[user_id].append(message)
        
        # Set ticks until ready for next send
        self._user_ticks[user_id] = self.ticks_per_send
        
        return True
        
    def tick(self):
        """Advance simulation by one tick."""
        for user_id in self._user_ticks:
            if self._user_ticks[user_id] > 0:
                self._user_ticks[user_id] -= 1
                
    def get_delivered(self, user_id: str) -> List[Message]:
        """Get all delivered messages for a user."""
        return self._delivered.get(user_id, [])


class InMemoryTransport(Transport):
    """Transport that immediately stores delivered messages per user.
    
    Always accepts messages (simulates fast users).
    """
    
    def __init__(self):
        """Initialize in-memory transport."""
        self._delivered: Dict[str, List[Message]] = {}
        
    def send(self, user_id: str, message: Message) -> bool:
        """Send a message to a user (always succeeds immediately)."""
        if user_id not in self._delivered:
            self._delivered[user_id] = []
        self._delivered[user_id].append(message)
        return True
        
    def get_delivered(self, user_id: str) -> List[Message]:
        """Get all delivered messages for a user."""
        return self._delivered.get(user_id, [])
