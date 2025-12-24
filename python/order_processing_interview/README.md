# Order Processing Interview Project

## Overview
60-minute technical interview focused on building a scalable order processing system with background workers, idempotency, and retry mechanisms.

**Time Allocation:**
- 10-15 minutes: System design discussion
- 40-45 minutes: Implementation

**Technology Stack:**
- Python 3.11+
- Standard library only
- pytest for testing

## Current Implementation (Baseline)

The project currently provides a naive synchronous implementation:

### Core Components

**orders/models.py:**
- `Order` dataclass: Represents an order with `order_id`, `user_id`, `amount_cents`, and `status`
- `Receipt` dataclass: Tracks payment attempts with `order_id`, `charged` flag, and `attempt` count

**orders/gateway.py:**
- `PaymentGateway` interface: Abstract base for payment processing
- `FakeGateway`: Test implementation that simulates failures for the first N attempts per order_id

**orders/inventory.py:**
- `Inventory.reserve()`: Naive implementation that always returns True (no real inventory tracking)

**orders/queueing.py:**
- `InMemoryJobQueue`: Simple list-based queue (not thread-safe, needs implementation)

**orders/idempotency.py:**
- `IdempotencyStore`: Stub that does nothing (needs implementation)

**orders/worker.py:**
- `Worker`: Processes jobs sequentially (needs concurrent worker pool implementation)

**orders/service.py:**
- `CheckoutService.checkout()`: Currently charges inline synchronously (needs background processing)

**orders/clock.py:**
- `FakeClock`: Tick-based time simulation for testing (no sleeps)

## Interview Requirements

Your task is to enhance this system to meet production requirements:

### 1. Concurrency
**Goal:** Move payment charging and inventory reservation to background workers

**Requirements:**
- Implement a configurable worker pool with adjustable worker count
- Provide `start()` and `stop()` methods for worker lifecycle management
- Implement graceful shutdown that completes in-flight jobs

### 2. Scaling
**Goal:** Keep memory usage bounded under high load

**Requirements:**
- Use a bounded queue for job storage
- Implement backpressure when queue is full
- Ensure system doesn't consume unbounded memory

### 3. Reliability
**Goal:** Guarantee at-least-once processing without duplicate charges

**Requirements:**
- Implement at-least-once job processing semantics
- Add idempotency layer to prevent duplicate charges
- Ensure same `order_id` is never charged twice, even if job runs multiple times

### 4. Retries and Dead Letter Queue (DLQ)
**Goal:** Handle transient failures gracefully

**Requirements:**
- Retry failed payment attempts up to 3 times
- Use exponential backoff between retries (with `FakeClock`, no actual sleeps)
- Move jobs to DLQ after exceeding retry limit
- Mark orders as 'failed' when moved to DLQ

### 5. Object-Oriented Design
**Goal:** Enable easy extension and testing

**Requirements:**
- Use Strategy pattern for payment gateways
- Allow injection of custom fraud checks
- Support swapping implementations without changing core logic
- Enable testing with mock implementations

## Test Suite

The project includes failing tests that define the expected behavior:

### test_background_processing.py
**Objective:** Verify asynchronous order processing

- `checkout()` should return immediately with order status 'pending'
- Job should be enqueued to background queue
- Workers should process job and update order status to 'paid'

### test_idempotency_no_double_charge.py
**Objective:** Prevent duplicate charges

- Enqueue the same order job twice
- Gateway's `charge()` method should be called at most once for that order_id
- Idempotency store should track processed orders

### test_retries_and_dlq.py
**Objective:** Handle failures with retries and DLQ

- Configure gateway to fail 5 times
- System should retry 3 times (4 total attempts)
- After max retries, job should move to DLQ
- Order status should be marked as 'failed'

### test_oop_strategies.py
**Objective:** Demonstrate strategy pattern

- Define a custom payment gateway in test code
- Inject custom gateway via interface
- System should work without core logic changes

## Implementation Notes

### FakeClock Usage
- Use `FakeClock` for all time-based operations
- Call `clock.tick(seconds)` to advance time
- No `time.sleep()` or `asyncio.sleep()` calls
- Enables fast, deterministic testing

### Fake Payment Gateway
- `FakeGateway` simulates transient failures
- Configure failure count per order_id
- Deterministic behavior for testing

### Testing Strategy
- All tests should initially fail
- Implement TODOs to make tests pass
- Do not modify test expectations

## Getting Started

```bash
# Install dependencies
pip install -e ".[test]"

# Run tests
pytest tests/

# Run specific test
pytest tests/test_background_processing.py -v
```

## Success Criteria

Your implementation is complete when:
1. All tests pass
2. Workers process jobs concurrently
3. Memory usage is bounded (queue has max size)
4. No duplicate charges occur (idempotency works)
5. Failed jobs move to DLQ after retries
6. Custom strategies can be injected (OOP)

Good luck!
