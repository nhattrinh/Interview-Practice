"""Rate limiting for notifications."""
class RateLimiter:
    """
    Rate limiter using token bucket algorithm.
    
    Should enforce max 5 notifications per 60 seconds per (user_id, channel) pair.
    """
    
    def __init__(self, max_tokens: int = 5, window_seconds: float = 60.0):
        """
        Initialize rate limiter.
        
        Args:
            max_tokens: Maximum number of tokens (notifications) allowed in window
            window_seconds: Time window in seconds
        """
        self.max_tokens = max_tokens
        self.window_seconds = window_seconds
        # TODO: Rate limiting - Add data structures to track tokens per (user_id, channel)
        # Hint: You'll need to track tokens and last refill time for each (user_id, channel)
    
    def allow(self, user_id: str, channel: str, now: float) -> bool:
        """
        Check if a notification is allowed under rate limits.
        
        Args:
            user_id: User ID
            channel: Channel (email, sms, etc)
            now: Current time (timestamp from FakeClock or time.time())
        
        Returns:
            True if notification is allowed, False if rate limited
        """
        # TODO: Rate limiting - Implement token bucket algorithm
        # For now, always return True (no rate limiting)
        return True
