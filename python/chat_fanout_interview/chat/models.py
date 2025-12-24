"""Data models for chat messages."""

from dataclasses import dataclass


@dataclass
class Message:
    """Represents a chat message.
    
    Attributes:
        id: Unique message identifier
        room_id: Room where the message was sent
        user_id: User who sent the message
        text: Message content
        seq: Sequence number for ordering
    """
    id: str
    room_id: str
    user_id: str
    text: str
    seq: int
