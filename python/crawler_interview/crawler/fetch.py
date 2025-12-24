'''Fake HTTP fetcher for simulating network requests without actual I/O.'''
from typing import Dict, Tuple
from urllib.parse import urlparse


class FakeFetcher:
    '''Simulates HTTP fetching with configurable per-domain failures and latency.'''
    
    def __init__(
        self,
        html_bodies: Dict[str, str],
        domain_latency: Dict[str, float] = None,
        domain_failure_rate: Dict[str, float] = None
    ):
        '''Initialize the fake fetcher.
        
        Args:
            html_bodies: Mapping of URL to HTML content
            domain_latency: Per-domain simulated latency in seconds
            domain_failure_rate: Per-domain failure probability (0.0 to 1.0)
        '''
        self._html_bodies = html_bodies
        self._domain_latency = domain_latency or {}
        self._domain_failure_rate = domain_failure_rate or {}
        self._fetch_counter = 0
        self._per_domain_counters: Dict[str, int] = {}
    
    def fetch(self, url: str, now: float) -> str:
        '''Fetch HTML content for the given URL.
        
        This simulates a network fetch without actual I/O. Uses counters to
        simulate latency and failures deterministically.
        
        Args:
            url: URL to fetch
            now: Current time (from FakeClock)
            
        Returns:
            HTML content as string
            
        Raises:
            ValueError: If fetch fails (simulated failure)
        '''
        self._fetch_counter += 1
        
        # Extract domain
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        
        # Update per-domain counter
        self._per_domain_counters[domain] = self._per_domain_counters.get(domain, 0) + 1
        
        # Simulate failure based on counter (deterministic)
        failure_rate = self._domain_failure_rate.get(domain, 0.0)
        if failure_rate > 0 and self._per_domain_counters[domain] % int(1 / failure_rate) == 0:
            raise ValueError(f'Simulated fetch failure for {url}')
        
        # Return HTML body (latency is tracked via counter, not actual sleep)
        return self._html_bodies.get(url, f'<html><head><title>Page {url}</title></head><body>Content</body></html>')
    
    def get_fetch_count(self) -> int:
        '''Get total number of fetches performed.
        
        Returns:
            Total fetch count
        '''
        return self._fetch_counter
    
    def get_domain_fetch_count(self, domain: str) -> int:
        '''Get number of fetches for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Fetch count for domain
        '''
        return self._per_domain_counters.get(domain, 0)
