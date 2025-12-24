"""Chat room implementation."""

from .models import Message
from .transport import Transport
from .membership import RoomMembershipStore


class ChatRoom:
    """Represents a chat room that can broadcast messages to users.
    
    Naive implementation: broadcast() loops over users synchronously.
    This will block on slow users.
    """
    
    def __init__(self, room_id: str, membership: RoomMembershipStore, transport: Transport):
        """Initialize chat room.
        
        Args:
            room_id: Room identifier
            membership: Membership store to get room users
            transport: Transport for sending messages
        """
        self.room_id = room_id
        self.membership = membership
        self.transport = transport
        
    def broadcast(self, message: Message):
        """Broadcast a message to all users in the room.
        
        TODO: This naive implementation loops over users synchronously
        and calls transport.send() for each user. This will block if any
        user is slow. Need to refactor to use per-user buffers and
        worker queues for non-blocking delivery.
        
        Args:
            message: Message to broadcast
        """
        users = self.membership.list_users(self.room_id)
        
        # Naive blocking implementation
        for user_id in users:
            self.transport.send(user_id, message)
