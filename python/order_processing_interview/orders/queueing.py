"""In-memory job queue for background processing."""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class Job:
    """Represents a background job."""
    job_id: str
    job_type: str
    payload: Any


class InMemoryJobQueue:
    """
    Simple in-memory job queue using a list.
    
    WARNING: This implementation is not thread-safe and has no bounds.
    
    TODO: Implement the following for production use:
    - Thread-safe operations (locks or queue.Queue)
    - Bounded capacity with backpressure
    - Blocking/timeout on push when full
    - Blocking/timeout on pop when empty
    """
    
    def __init__(self):
        """Initialize empty queue."""
        self._jobs: List[Job] = []
    
    def push(self, job: Job) -> None:
        """
        Add a job to the queue.
        
        TODO: Add bounds checking and backpressure
        
        Args:
            job: Job to enqueue
        """
        self._jobs.append(job)
    
    def pop(self) -> Optional[Job]:
        """
        Remove and return a job from the queue.
        
        TODO: Add blocking behavior with timeout
        
        Returns:
            Job if available, None if queue is empty
        """
        if self._jobs:
            return self._jobs.pop(0)
        return None
    
    def size(self) -> int:
        """Return current queue size."""
        return len(self._jobs)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._jobs) == 0
