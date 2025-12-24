# Notification Service Interview

## Overview
A notification service that processes events and sends notifications via email/SMS channels.

Currently, the system uses a naive implementation with:
- Simple list-based queue (not thread-safe)
- Single-threaded processing loop
- No rate limiting
- No retry logic
- No deduplication

## Installation
```bash
pip install -e .
```

## Run Tests
```bash
pytest -q
```

## Interview Tasks
Your goal is to extend this system to meet production requirements. You have 40-45 minutes of coding time.

### Task 1: Concurrency & Graceful Shutdown
**Goal:** Process notifications using a worker pool (threading or asyncio).

Requirements:
- Support configurable number of worker threads/tasks
- Implement graceful shutdown: `stop()` must wait for in-flight work to complete
- Ensure no enqueued items are lost during shutdown
- All tests in `test_concurrency_and_shutdown.py` must pass

**Where to implement:**
- `notif/service.py`: Replace `process_once()` with worker pool
- Look for `# TODO: Concurrency` markers

### Task 2: Bounded Queue & Backpressure
**Goal:** Prevent unbounded memory growth with a maximum queue size.

Requirements:
- Implement `max_queue_size` parameter in NotificationService
- When queue is full, `enqueue()` should raise `QueueFullError`
- Add counter for dropped/rejected events
- Update queue implementation in `notif/queueing.py`

**Where to implement:**
- `notif/queueing.py`: Make queue bounded
- `notif/service.py`: Handle backpressure
- Look for `# TODO: Backpressure` markers

### Task 3: Rate Limiting
**Goal:** Implement per (user_id, channel) rate limiting using token bucket algorithm.

Requirements:
- Maximum 5 notifications per 60 seconds per (user_id, channel)
- When rate-limited, do not send; return `DeliveryResult(ok=False, reason='rate_limited')`
- Use token bucket algorithm
- All tests in `test_rate_limit.py` must pass

**Where to implement:**
- `notif/rate_limit.py`: Implement `RateLimiter.allow()` method
- Look for `# TODO: Rate limiting` markers

### Task 4: Retry & Deduplication
**Goal:** Handle transient failures and prevent duplicate sends.

Requirements:
- Deduplicate by `Event.id`: same event enqueued twice = at most one successful send
- Retry transient failures up to 3 attempts with exponential backoff
- Exponential backoff: 1s, 2s, 4s between retries
- Make time/backoff injectable for testing (no real sleeps in tests)
- All tests in `test_retry_and_dedup.py` must pass

**Where to implement:**
- `notif/retry.py`: Implement `RetryPolicy.next_delay()` method
- `notif/service.py`: Add deduplication tracking and retry logic
- Look for `# TODO: Retry` and `# TODO: Dedup` markers

### Task 5: OOP Extensibility
**Goal:** Make it easy to add new notification channels without modifying core service code.

Requirements:
- Use factory/registry pattern for notification types
- Adding a new channel (e.g., `PushNotification`) should only require:
  1. Create new `Notification` subclass
  2. Register it via public API
  3. No changes to `NotificationService` internals
- All tests in `test_oop_extensibility.py` must pass

**Where to implement:**
- `notif/models.py`: Add factory/registry for notification types
- `notif/service.py`: Use factory instead of hardcoded channel mapping
- Look for `# TODO: Factory` markers

## Testing Guidelines
- All tests use `FakeClock` to control time (no real sleeps)
- Tests should complete in under 2 seconds total
- No flaky timing-dependent behavior

## Current Implementation Status
❌ All tests currently FAIL - this is expected!
Your job is to implement the TODOs to make them pass.
