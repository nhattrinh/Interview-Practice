"""Test that message ordering is preserved per user."""

from chat.server import ChatServer
from chat.transport import InMemoryTransport, SlowTransport
from chat.models import Message


def test_delivered_messages_have_increasing_seq():
    """Each user should receive messages in order (increasing seq).
    
    This test will fail if the implementation doesn't preserve ordering.
    """
    transport = InMemoryTransport()
    server = ChatServer(transport)
    
    # Setup room with multiple users
    server.join_room('room1', 'user1')
    server.join_room('room1', 'user2')
    server.join_room('room1', 'user3')
    
    room = server.get_or_create_room('room1')
    
    # Broadcast multiple messages with explicit sequence numbers
    for seq in range(10):
        msg = Message(
            id=server.next_message_id(),
            room_id='room1',
            user_id='sender',
            text=f'Message {seq}',
            seq=seq
        )
        room.broadcast(msg)
    
    # Check that each user received messages in order
    for user_id in ['user1', 'user2', 'user3']:
        delivered = transport.get_delivered(user_id)
        assert len(delivered) == 10, f'User {user_id} should have 10 messages'
        
        # Verify sequence numbers are increasing
        seq_values = [msg.seq for msg in delivered]
        assert seq_values == sorted(seq_values), f'User {user_id} messages not in order: {seq_values}'
        assert seq_values == list(range(10)), f'User {user_id} has wrong sequence: {seq_values}'


def test_ordering_with_slow_users():
    """Even with slow users and buffering, ordering must be preserved.
    
    This test will fail if async delivery breaks ordering.
    """
    # Use a slow transport to test async delivery
    transport = SlowTransport(ticks_per_send=2)
    server = ChatServer(transport)
    
    server.join_room('room1', 'slow_user')
    room = server.get_or_create_room('room1')
    
    # Broadcast messages
    for seq in range(5):
        msg = Message(
            id=server.next_message_id(),
            room_id='room1',
            user_id='sender',
            text=f'Message {seq}',
            seq=seq
        )
        room.broadcast(msg)
    
    # Tick until all delivered
    for _ in range(20):
        server.tick()
        transport.tick()
    
    delivered = transport.get_delivered('slow_user')
    
    # All messages should be delivered in order
    seq_values = [msg.seq for msg in delivered]
    assert seq_values == sorted(seq_values), f'Messages not in order: {seq_values}'
    
    # Should be consecutive
    for i in range(len(seq_values) - 1):
        assert seq_values[i + 1] == seq_values[i] + 1, f'Gap in sequence at {i}: {seq_values}'
