"""Chat server coordinating rooms, membership, and transport."""

from typing import Dict
from .room import ChatRoom
from .membership import RoomMembershipStore
from .transport import Transport
from .clock import Clock


class ChatServer:
    """Main chat server coordinating rooms, membership, and message transport.
    
    Uses tick-based simulation for deterministic progress.
    """
    
    def __init__(self, transport: Transport):
        """Initialize chat server.
        
        Args:
            transport: Transport for message delivery
        """
        self.transport = transport
        self.membership = RoomMembershipStore()
        self.rooms: Dict[str, ChatRoom] = {}
        self.clock = Clock()
        self._message_counter = 0
        
    def get_or_create_room(self, room_id: str) -> ChatRoom:
        """Get existing room or create new one.
        
        Args:
            room_id: Room identifier
            
        Returns:
            ChatRoom instance
        """
        if room_id not in self.rooms:
            self.rooms[room_id] = ChatRoom(room_id, self.membership, self.transport)
        return self.rooms[room_id]
        
    def join_room(self, room_id: str, user_id: str):
        """Add a user to a room.
        
        Args:
            room_id: Room identifier
            user_id: User identifier
        """
        self.membership.add_user(room_id, user_id)
        
    def leave_room(self, room_id: str, user_id: str):
        """Remove a user from a room.
        
        Args:
            room_id: Room identifier
            user_id: User identifier
        """
        self.membership.remove_user(room_id, user_id)
        
    def next_message_id(self) -> str:
        """Generate next message ID."""
        self._message_counter += 1
        return f'msg_{self._message_counter}'
        
    def tick(self):
        """Advance server state by one tick.
        
        TODO: This should drive worker queues to process pending
        message deliveries. Currently does nothing because the naive
        implementation in ChatRoom.broadcast() is synchronous.
        
        Need to implement:
        - Per-user outgoing message buffers
        - Worker queue system to process buffered messages
        - Proper integration with transport layer
        """
        self.clock.tick()
        
        # TODO: Process worker queues here
        # Should attempt to deliver buffered messages for each user
        # Should respect transport.send() return value (True/False)
        # Should handle buffer overflow with drop policy
