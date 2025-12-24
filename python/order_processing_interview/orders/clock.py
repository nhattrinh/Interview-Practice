"""Fake clock for deterministic time-based testing."""


class FakeClock:
    """
    Simulated clock that advances via tick() calls instead of wall time.
    
    Enables fast, deterministic testing of time-based logic like
    exponential backoff without actual sleeps.
    """
    
    def __init__(self, start_time: float = 0.0):
        """
        Initialize clock.
        
        Args:
            start_time: Initial time value in seconds
        """
        self._current_time = start_time
    
    def now(self) -> float:
        """
        Get current time.
        
        Returns:
            Current time in seconds
        """
        return self._current_time
    
    def tick(self, seconds: float) -> None:
        """
        Advance the clock by specified seconds.
        
        Args:
            seconds: Amount of time to advance in seconds
        """
        self._current_time += seconds
    
    def reset(self, time: float = 0.0) -> None:
        """
        Reset clock to specified time.
        
        Args:
            time: Time to reset to in seconds
        """
        self._current_time = time
