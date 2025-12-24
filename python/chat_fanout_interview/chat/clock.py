"""Clock utilities for tick-based simulation."""


class Clock:
    """Tick-based clock for deterministic simulation.
    
    No wall-clock sleeps; advances by explicit tick() calls.
    """
    
    def __init__(self):
        """Initialize clock at tick 0."""
        self._current_tick = 0
        
    def tick(self):
        """Advance the clock by one tick."""
        self._current_tick += 1
        
    def current_tick(self) -> int:
        """Get the current tick count."""
        return self._current_tick
