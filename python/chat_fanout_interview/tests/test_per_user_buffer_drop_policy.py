"""Test per-user buffer with drop policy when buffer is full."""

from chat.server import ChatServer
from chat.transport import SlowTransport
from chat.models import Message


def test_buffer_drops_oldest_messages_when_full():
    """When buffer is full, oldest messages should be dropped.
    
    This test will fail because the naive implementation doesn't have
    per-user buffers or drop policies.
    """
    # Create a slow transport
    transport = SlowTransport(ticks_per_send=10)  # Very slow
    server = ChatServer(transport)
    
    # Setup room with one slow user
    server.join_room('room1', 'slow_user')
    room = server.get_or_create_room('room1')
    
    # Broadcast 10 messages rapidly
    messages = []
    for i in range(10):
        msg = Message(
            id=server.next_message_id(),
            room_id='room1',
            user_id='sender',
            text=f'Message {i}',
            seq=i
        )
        messages.append(msg)
        room.broadcast(msg)
    
    # Tick until all messages are delivered (or dropped)
    for _ in range(200):  # Enough ticks to deliver 3 messages
        server.tick()
        transport.tick()
    
    # With buffer size 3, only last 3 messages should be delivered
    delivered = transport.get_delivered('slow_user')
    
    # Should have received only 3 messages (buffer size)
    assert len(delivered) == 3, f'Expected 3 messages, got {len(delivered)}'
    
    # Should be the LAST 3 messages (7, 8, 9)
    assert delivered[0].text == 'Message 7', f'Expected Message 7, got {delivered[0].text}'
    assert delivered[1].text == 'Message 8', f'Expected Message 8, got {delivered[1].text}'
    assert delivered[2].text == 'Message 9', f'Expected Message 9, got {delivered[2].text}'


def test_drop_counter_tracks_dropped_messages():
    """Drop counter should track the number of dropped messages.
    
    This test will fail because metrics are not implemented.
    """
    transport = SlowTransport(ticks_per_send=10)
    server = ChatServer(transport)
    
    server.join_room('room1', 'slow_user')
    room = server.get_or_create_room('room1')
    
    # Broadcast 10 messages
    for i in range(10):
        msg = Message(
            id=server.next_message_id(),
            room_id='room1',
            user_id='sender',
            text=f'Message {i}',
            seq=i
        )
        room.broadcast(msg)
    
    # Check drop counter
    # This will fail because there's no metrics system yet
    assert hasattr(server, 'get_dropped_count'), 'Server should have get_dropped_count method'
    dropped = server.get_dropped_count('slow_user')
    assert dropped == 7, f'Expected 7 dropped messages, got {dropped}'
