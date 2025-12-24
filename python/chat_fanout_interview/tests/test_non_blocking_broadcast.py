"""Test that broadcasting is non-blocking with respect to slow users."""

import pytest
from chat.server import ChatServer
from chat.transport import SlowTransport, InMemoryTransport
from chat.models import Message


def test_fast_user_receives_immediately_despite_slow_user():
    """Fast user should receive messages in the same tick, even with a slow user present.
    
    This test will fail with the naive blocking implementation because
    the broadcast loops synchronously and gets blocked by the slow user.
    """
    # Create a custom transport that has one slow user and one fast user
    class MixedTransport(InMemoryTransport):
        def __init__(self):
            super().__init__()
            self.slow_user_transport = SlowTransport(ticks_per_send=3)
            
        def send(self, user_id: str, message: Message) -> bool:
            if user_id == 'slow_user':
                return self.slow_user_transport.send(user_id, message)
            return super().send(user_id, message)
            
        def tick(self):
            self.slow_user_transport.tick()
            
        def get_delivered(self, user_id: str):
            if user_id == 'slow_user':
                return self.slow_user_transport.get_delivered(user_id)
            return super().get_delivered(user_id)
    
    transport = MixedTransport()
    server = ChatServer(transport)
    
    # Setup room with one fast and one slow user
    server.join_room('room1', 'fast_user')
    server.join_room('room1', 'slow_user')
    
    room = server.get_or_create_room('room1')
    
    # Broadcast a message
    msg = Message(
        id=server.next_message_id(),
        room_id='room1',
        user_id='sender',
        text='Hello',
        seq=1
    )
    room.broadcast(msg)
    
    # Fast user should receive immediately (same tick, no ticking needed)
    fast_delivered = transport.get_delivered('fast_user')
    assert len(fast_delivered) == 1, 'Fast user should receive message immediately'
    assert fast_delivered[0].text == 'Hello'
    
    # Slow user should NOT have received yet
    slow_delivered = transport.get_delivered('slow_user')
    assert len(slow_delivered) == 0, 'Slow user should not receive message yet'
    
    # After ticking, slow user should eventually receive
    for _ in range(5):
        server.tick()
        transport.tick()
        
    slow_delivered = transport.get_delivered('slow_user')
    assert len(slow_delivered) == 1, 'Slow user should receive message after ticking'
    assert slow_delivered[0].text == 'Hello'
