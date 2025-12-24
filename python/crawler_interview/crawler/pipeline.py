'''Main pipeline for orchestrating the crawling process.'''
from typing import Iterable, List
from urllib.parse import urlparse

from crawler.clock import FakeClock
from crawler.fetch import FakeFetcher
from crawler.parse import ParserRegistry, ParsedPage
from crawler.storage import StorageBackend
from crawler.politeness import PolitenessPolicy


class Pipeline:
    '''Pipeline for fetching, parsing, and storing web pages.
    
    TODO: Implement concurrent processing, streaming, and bounded backpressure.
    Currently processes URLs sequentially and returns all results in memory.
    '''
    
    def __init__(
        self,
        fetcher: FakeFetcher,
        parser_registry: ParserRegistry,
        storage: StorageBackend,
        politeness: PolitenessPolicy,
        clock: FakeClock,
        max_workers: int = 1
    ):
        '''Initialize the pipeline.
        
        Args:
            fetcher: FakeFetcher instance
            parser_registry: ParserRegistry instance
            storage: StorageBackend instance
            politeness: PolitenessPolicy instance
            clock: FakeClock instance
            max_workers: Maximum concurrent workers (TODO: not implemented)
        '''
        self._fetcher = fetcher
        self._parser_registry = parser_registry
        self._storage = storage
        self._politeness = politeness
        self._clock = clock
        self._max_workers = max_workers
    
    def process(self, urls: Iterable[str]) -> List[ParsedPage]:
        '''Process an iterable of URLs.
        
        TODO: Implement:
        1. Concurrent fetching and parsing (use max_workers)
        2. Streaming results to storage (don't build large in-memory list)
        3. Bounded queue between fetch and parse stages
        4. Duplicate URL detection
        5. Politeness policy enforcement
        
        Currently: Sequential processing, returns all pages in memory.
        
        Args:
            urls: Iterable of URLs to process
            
        Returns:
            List of ParsedPage objects (TODO: should stream, not return list)
        '''
        # TODO: Implement concurrency with thread pool or asyncio
        # TODO: Implement streaming (yield/store incrementally)
        # TODO: Implement bounded queue for backpressure
        # TODO: Check for duplicate URLs
        # TODO: Check politeness policy before fetching
        
        # Naive sequential implementation
        results = []
        for url in urls:
            try:
                # Fetch HTML
                html = self._fetcher.fetch(url, self._clock.now())
                
                # Determine content type (naive: check extension)
                content_type = 'text/html'
                if url.endswith('.json'):
                    content_type = 'application/json'
                
                # Parse
                parsed = self._parser_registry.parse(html, url, content_type)
                
                # Store
                self._storage.store(parsed)
                results.append(parsed)
                
            except ValueError as e:
                # Simulated fetch failure - skip
                pass
        
        return results
