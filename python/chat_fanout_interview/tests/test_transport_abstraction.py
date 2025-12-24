"""Test that transport layer is properly abstracted and pluggable."""

import pytest
from chat.server import ChatServer
from chat.transport import Transport
from chat.models import Message
from typing import List, Dict


def test_custom_transport_works_without_server_changes():
    """Server should work with a custom transport without code changes.
    
    This test defines a completely new transport and verifies
    that the server works without any modifications.
    """
    
    # Define a custom transport in the test
    class CustomTestTransport(Transport):
        """A custom transport that logs all send attempts."""
        
        def __init__(self):
            self.delivered: Dict[str, List[Message]] = {}
            self.send_attempts: List[tuple] = []
            
        def send(self, user_id: str, message: Message) -> bool:
            """Log send attempt and deliver message."""
            self.send_attempts.append((user_id, message.id))
            
            if user_id not in self.delivered:
                self.delivered[user_id] = []
            self.delivered[user_id].append(message)
            return True
            
        def get_delivered(self, user_id: str) -> List[Message]:
            """Get delivered messages for a user."""
            return self.delivered.get(user_id, [])
    
    # Use custom transport with server
    transport = CustomTestTransport()
    server = ChatServer(transport)
    
    # Setup room
    server.join_room('room1', 'user1')
    server.join_room('room1', 'user2')
    
    room = server.get_or_create_room('room1')
    
    # Broadcast a message
    msg = Message(
        id=server.next_message_id(),
        room_id='room1',
        user_id='sender',
        text='Test message',
        seq=1
    )
    room.broadcast(msg)
    
    # Verify custom transport was used
    assert len(transport.send_attempts) == 2, 'Should have 2 send attempts'
    
    # Verify messages were delivered through custom transport
    user1_msgs = transport.get_delivered('user1')
    user2_msgs = transport.get_delivered('user2')
    
    assert len(user1_msgs) == 1, 'User1 should have 1 message'
    assert len(user2_msgs) == 1, 'User2 should have 1 message'
    assert user1_msgs[0].text == 'Test message'
    assert user2_msgs[0].text == 'Test message'


def test_transport_with_conditional_delivery():
    """Transport can implement custom delivery logic.
    
    This ensures the abstraction allows for complex transport behavior.
    """
    
    class ConditionalTransport(Transport):
        """Only delivers to users whose ID starts with 'vip_'."""
        
        def __init__(self):
            self.delivered: Dict[str, List[Message]] = {}
            self.rejected_count = 0
            
        def send(self, user_id: str, message: Message) -> bool:
            if user_id.startswith('vip_'):
                if user_id not in self.delivered:
                    self.delivered[user_id] = []
                self.delivered[user_id].append(message)
                return True
            else:
                self.rejected_count += 1
                return False
                
        def get_delivered(self, user_id: str) -> List[Message]:
            return self.delivered.get(user_id, [])
    
    transport = ConditionalTransport()
    server = ChatServer(transport)
    
    # Add VIP and regular users
    server.join_room('room1', 'vip_alice')
    server.join_room('room1', 'regular_bob')
    
    room = server.get_or_create_room('room1')
    
    msg = Message(
        id=server.next_message_id(),
        room_id='room1',
        user_id='sender',
        text='VIP announcement',
        seq=1
    )
    room.broadcast(msg)
    
    # VIP user should receive
    vip_msgs = transport.get_delivered('vip_alice')
    assert len(vip_msgs) == 1, 'VIP should receive message'
    
    # Regular user should not receive
    regular_msgs = transport.get_delivered('regular_bob')
    assert len(regular_msgs) == 0, 'Regular user should not receive message'
    
    # Rejection should be tracked
    assert transport.rejected_count == 1, 'Should have 1 rejection'
