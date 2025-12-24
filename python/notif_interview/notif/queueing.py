"""In-memory queue for notifications."""
from typing import Optional, Any


class InMemoryQueue:
    """
    Simple list-based queue.
    
    WARNING: This implementation is NOT thread-safe!
    Multiple threads calling push/pop simultaneously will cause race conditions.
    """
    
    def __init__(self):
        self._items = []
    
    def push(self, item: Any) -> None:
        """Add item to queue."""
        # TODO: Backpressure - Add max_queue_size check here
        # Should raise QueueFullError when queue is full
        self._items.append(item)
    
    def pop(self) -> Optional[Any]:
        """Remove and return item from queue, or None if empty."""
        if not self._items:
            return None
        return self._items.pop(0)
    
    def size(self) -> int:
        """Return current queue size."""
        return len(self._items)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._items) == 0


class QueueFullError(Exception):
    """Raised when trying to add to a full queue."""
    pass
