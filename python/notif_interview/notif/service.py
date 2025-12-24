"""Main notification service."""
from typing import Optional, Set
from notif.models import Event, EmailNotification, SMSNotification, DeliveryResult
from notif.queueing import InMemoryQueue
from notif.sender import NotificationSender
from notif.rate_limit import RateLimiter
from notif.retry import RetryPolicy


class FakeClock:
    """
    Fake clock for testing without real time.sleep().
    Allows tests to advance time deterministically.
    """
    
    def __init__(self, start_time: float = 0.0):
        self._current_time = start_time
    
    def now(self) -> float:
        """Get current time."""
        return self._current_time
    
    def advance(self, seconds: float) -> None:
        """Advance clock by given seconds."""
        self._current_time += seconds
    
    def sleep(self, seconds: float) -> None:
        """Sleep for given seconds (just advances clock)."""
        self.advance(seconds)


class NotificationService:
    """
    Service that processes events and sends notifications.
    
    Current implementation is single-threaded and naive.
    Needs to be extended for production use.
    """
    
    def __init__(
        self,
        sender: Optional[NotificationSender] = None,
        rate_limiter: Optional[RateLimiter] = None,
        retry_policy: Optional[RetryPolicy] = None,
        clock: Optional[FakeClock] = None,
        workers: int = 1,
        max_queue_size: Optional[int] = None,
    ):
        """
        Initialize notification service.
        
        Args:
            sender: NotificationSender instance
            rate_limiter: RateLimiter instance
            retry_policy: RetryPolicy instance
            clock: FakeClock instance for testing
            workers: Number of worker threads (TODO: not implemented yet)
            max_queue_size: Maximum queue size (TODO: not implemented yet)
        """
        self.sender = sender or NotificationSender()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.retry_policy = retry_policy or RetryPolicy()
        self.clock = clock or FakeClock()
        self.workers = workers
        self.max_queue_size = max_queue_size
        
        self._queue = InMemoryQueue()
        self._running = False
        self._delivered: Set[str] = set()  # Track delivered event IDs
        
        # TODO: Dedup - Add tracking for in-flight and completed events
        # to prevent duplicate sends of same event.id
        
        # TODO: Concurrency - Add worker threads/tasks here
        # Replace single-threaded process_once() with worker pool
    
    def enqueue(self, event: Event) -> None:
        """
        Add event to processing queue.
        
        Args:
            event: Event to process
        
        Raises:
            QueueFullError: If queue is at max_queue_size (TODO: not implemented)
        """
        # TODO: Backpressure - Check max_queue_size and raise QueueFullError if full
        self._queue.push(event)
    
    def start(self) -> None:
        """
        Start the notification service.
        
        TODO: Concurrency - Start worker threads/tasks here
        Currently does nothing as processing happens in process_once()
        """
        self._running = True
        # TODO: Concurrency - Launch worker pool here
    
    def stop(self) -> None:
        """
        Stop the notification service gracefully.
        
        TODO: Concurrency - Implement graceful shutdown
        - Wait for in-flight work to complete
        - Don't lose enqueued items
        - Complete within reasonable time (<1s in tests)
        """
        self._running = False
        # TODO: Concurrency - Signal workers to stop and wait for completion
    
    def process_once(self) -> bool:
        """
        Process one event from queue (single-threaded, naive implementation).
        
        Returns:
            True if an event was processed, False if queue was empty
        
        TODO: Concurrency - This method should be replaced with worker pool
        Currently used for simple single-threaded testing
        """
        event = self._queue.pop()
        if event is None:
            return False
        
        # TODO: Dedup - Check if event.id already processed
        # If already delivered, skip it
        
        # Create notification based on channel
        # TODO: Factory - Replace this hardcoded mapping with factory pattern
        if event.channel == 'email':
            notification = EmailNotification(event)
        elif event.channel == 'sms':
            notification = SMSNotification(event)
        else:
            # Unknown channel, skip
            return True
        
        # TODO: Rate limiting - Check rate limiter before sending
        # If rate limited, record delivery result with reason='rate_limited'
        now = self.clock.now()
        if not self.rate_limiter.allow(event.user_id, event.channel, now):
            # Rate limited - should record this
            return True
        
        # TODO: Retry - Implement retry logic with exponential backoff
        # Currently just tries once
        result = self.sender.send(notification)
        
        if result.ok:
            self._delivered.add(event.id)
        
        return True
    
    def get_delivered_count(self) -> int:
        """Get count of successfully delivered notifications."""
        return len(self._delivered)
