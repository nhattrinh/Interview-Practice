# Chat Fanout Interview

A 60-minute interview project focusing on chat room message broadcasting with proper concurrency handling.

## Time Allocation
- 10–15 min: Discussion and requirements
- 40–45 min: Coding implementation

## Problem Statement

Build an in-process chat server that can broadcast messages to multiple users in a room. The system must handle slow users gracefully without blocking fast users.

## Requirements

### 1. Concurrency/Non-blocking Broadcasting
Broadcasting should not be blocked by slow users. One slow user must not prevent fast users from receiving messages immediately.

**Test**: `test_non_blocking_broadcast.py`
- Setup: One slow user (requires 3 ticks per message) and one fast user
- Action: Broadcast a message
- Expected: Fast user receives the message in the same tick; slow user receives it later

### 2. Scaling with Per-User Buffers
Support large rooms by introducing per-user outgoing message buffers with configurable maximum sizes. Do not perform blocking per-user work inline during broadcast.

**Test**: `test_per_user_buffer_drop_policy.py`
- Setup: Buffer size = 3, slow user
- Action: Broadcast 10 messages rapidly
- Expected: Only the last 3 messages are delivered; drop counter is incremented by 7

### 3. Backpressure/Drop Policy
When a user's buffer is full, apply a clear drop policy:
- Drop the **oldest** messages from the buffer
- Increment a metric counter for dropped messages
- Expose metrics for monitoring

**Test**: Covered in `test_per_user_buffer_drop_policy.py`

### 4. OOP/Transport Abstraction
The transport layer must be pluggable. Tests should be able to introduce custom transport implementations without modifying the server code.

**Test**: `test_transport_abstraction.py`
- Action: Create a custom transport in the test file
- Expected: Server works without any code changes

### 5. Correctness/Message Ordering
Preserve per-user message ordering. For each user, the sequence numbers of delivered messages must be monotonically increasing.

**Test**: `test_ordering_per_user.py`
- Action: Broadcast multiple messages and tick until delivered
- Expected: Each user's delivered messages have increasing `seq` values

## Architecture

### Components

#### `chat/models.py`
- `Message` dataclass with fields: `id`, `room_id`, `user_id`, `text`, `seq`

#### `chat/transport.py`
- `Transport` abstract interface with `send(user_id, message)` method
- `SlowTransport`: Simulates slow users by requiring N ticks before accepting the next send
- `InMemoryTransport`: Stores delivered messages per user for testing

#### `chat/membership.py`
- `RoomMembershipStore`: Manages room membership with `add_user`, `remove_user`, `list_users`
- Naive dictionary-based implementation

#### `chat/room.py`
- `ChatRoom`: Handles message broadcasting
- `broadcast(message)`: **TODO** - Currently loops over users synchronously (blocking)
- Must be refactored to use per-user buffers and worker queues

#### `chat/server.py`
- `ChatServer`: Main server coordinating rooms, membership, and transport
- `tick()`: **TODO** - Drives deterministic progress for async work
- Must implement worker queues for non-blocking delivery

#### `chat/clock.py`
- Tick-based simulation utilities (no wall-clock sleeps)

## Constraints

- **Python 3.11** only
- **stdlib + pytest** only (no external libraries)
- **Single quotes** for all Python strings
- **In-process simulation** (no websockets, no threads)
- **Tick-based progression** (no `time.sleep()`)
- **Tests must fail initially** - Do not implement TODOs

## Getting Started

```bash
# Install dependencies
pip install -e '.[dev]'

# Run tests (should fail initially)
pytest -v
```

## Implementation Notes

The naive baseline implementation has synchronous blocking behavior. The interview task is to refactor it to:

1. Use per-user outgoing message buffers
2. Implement a worker queue system driven by `tick()` calls
3. Apply proper backpressure and drop policies
4. Maintain the transport abstraction
5. Ensure message ordering per user

Good luck!
