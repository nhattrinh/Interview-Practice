'''Politeness policy for rate limiting per-domain requests.'''
from typing import Dict


class PolitenessPolicy:
    '''Policy for enforcing per-domain rate limits.
    
    TODO: Implement per-domain rate limiting (max 2 requests per 10 seconds per domain).
    Currently always returns True as a stub implementation.
    '''
    
    def __init__(self, max_requests: int = 2, window_seconds: float = 10.0):
        '''Initialize the politeness policy.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        '''
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._domain_requests: Dict[str, list] = {}
    
    def allow(self, domain: str, now: float) -> bool:
        '''Check if a request to the domain is allowed at the given time.
        
        TODO: Implement per-domain rate limiting logic.
        Should track request timestamps per domain and enforce:
        - Max 2 requests per 10 seconds per domain
        - Use the 'now' parameter (from FakeClock) for deterministic testing
        
        Args:
            domain: Domain name to check
            now: Current time in seconds (from FakeClock)
            
        Returns:
            True if request is allowed, False otherwise
        '''
        # TODO: Implement rate limiting
        # For now, always allow (stub implementation)
        return True
    
    def record(self, domain: str, now: float) -> None:
        '''Record a request to the domain at the given time.
        
        TODO: Implement request tracking.
        
        Args:
            domain: Domain name
            now: Current time in seconds (from FakeClock)
        '''
        # TODO: Track request timestamps
        pass
