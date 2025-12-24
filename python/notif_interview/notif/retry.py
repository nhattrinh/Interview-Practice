"""Retry policy for failed notifications."""


class RetryPolicy:
    """
    Retry policy with exponential backoff.
    
    Should retry up to max_attempts with exponentially increasing delays.
    """
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        """
        Initialize retry policy.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay in seconds (for exponential backoff: base * 2^attempt)
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
    
    def next_delay(self, attempt: int) -> float:
        """
        Calculate delay before next retry attempt.
        
        Args:
            attempt: Current attempt number (0-indexed)
        
        Returns:
            Delay in seconds before next retry
            Should implement exponential backoff: 1s, 2s, 4s for attempts 0, 1, 2
        """
        # TODO: Retry - Implement exponential backoff
        # For now, return 0 (no delay)
        return 0.0
