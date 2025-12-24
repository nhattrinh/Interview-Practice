'''Fake clock for deterministic time simulation in tests.'''


class FakeClock:
    '''A fake clock that allows deterministic time control in tests.'''
    
    def __init__(self, initial_time: float = 0.0):
        '''Initialize the fake clock.
        
        Args:
            initial_time: Starting time in seconds
        '''
        self._current_time = initial_time
    
    def now(self) -> float:
        '''Get the current time.
        
        Returns:
            Current time in seconds
        '''
        return self._current_time
    
    def advance(self, seconds: float) -> None:
        '''Advance the clock by the given number of seconds.
        
        Args:
            seconds: Number of seconds to advance
        '''
        self._current_time += seconds
