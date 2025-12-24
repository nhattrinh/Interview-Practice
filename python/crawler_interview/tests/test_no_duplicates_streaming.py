'''Test duplicate URL detection and streaming behavior.

This test verifies that the pipeline:
1. Deduplicates URLs (never processes the same URL twice)
2. Streams results incrementally without building large in-memory lists
'''
import pytest
from crawler.clock import FakeClock
from crawler.fetch import FakeFetcher
from crawler.parse import ParserRegistry
from crawler.storage import InMemoryStorage
from crawler.politeness import PolitenessPolicy
from crawler.pipeline import Pipeline


def url_generator_with_duplicates(num_unique: int, duplicates_per_url: int):
    '''Generate URLs with duplicates.
    
    Args:
        num_unique: Number of unique URLs
        duplicates_per_url: How many times to yield each URL
        
    Yields:
        URLs with duplicates
    '''
    for i in range(num_unique):
        url = f'http://example.com/page{i}'
        for _ in range(duplicates_per_url):
            yield url


def test_no_duplicate_urls_processed():
    '''Test that pipeline never processes duplicate URLs.
    
    This test should FAIL initially because Pipeline doesn't track seen URLs.
    '''
    # Setup: 20 unique URLs, each repeated 3 times = 60 total
    num_unique = 20
    duplicates_per_url = 3
    urls = url_generator_with_duplicates(num_unique, duplicates_per_url)
    
    # Create HTML bodies for unique URLs only
    html_bodies = {f'http://example.com/page{i}': f'<html><head><title>Page {i}</title></head></html>'
                   for i in range(num_unique)}
    
    clock = FakeClock()
    fetcher = FakeFetcher(html_bodies)
    parser = ParserRegistry()
    storage = InMemoryStorage()
    politeness = PolitenessPolicy()
    
    pipeline = Pipeline(fetcher, parser, storage, politeness, clock, max_workers=1)
    pipeline.process(urls)
    
    # Should only process unique URLs
    assert storage.count() == num_unique, \
        f'Expected {num_unique} unique pages, got {storage.count()}'
    
    # Should only fetch each URL once
    fetch_count = fetcher.get_fetch_count()
    # TODO: This will FAIL because Pipeline doesn't deduplicate
    assert fetch_count == num_unique, \
        f'Expected {num_unique} fetches, got {fetch_count} (duplicates were processed)'


def test_streaming_without_large_in_memory_list():
    '''Test that pipeline streams results incrementally.
    
    This test should FAIL initially because Pipeline.process() returns a list.
    '''
    # Setup: large number of URLs
    num_urls = 1000
    
    def large_url_generator():
        for i in range(num_urls):
            yield f'http://example.com/page{i}'
    
    html_bodies = {f'http://example.com/page{i}': f'<html><head><title>Page {i}</title></head></html>'
                   for i in range(num_urls)}
    
    clock = FakeClock()
    fetcher = FakeFetcher(html_bodies)
    parser = ParserRegistry()
    storage = InMemoryStorage()
    politeness = PolitenessPolicy()
    
    pipeline = Pipeline(fetcher, parser, storage, politeness, clock, max_workers=1)
    
    # Check that process() doesn't return a large list
    # TODO: Pipeline.process() should yield or return None, not build a list
    result = pipeline.process(large_url_generator())
    
    # This test checks if Pipeline returns a list (bad) or streams (good)
    # TODO: This will FAIL because Pipeline returns a list
    assert result is None or len(result) == 0, \
        'Pipeline.process() should not return a large in-memory list; it should stream to storage'
    
    # But all pages should be stored
    assert storage.count() == num_urls


def test_streaming_with_storage_counter():
    '''Test that pipeline stores incrementally, not all at once.
    
    This test should FAIL initially because Pipeline doesn't stream.
    '''
    # Setup: Use a custom storage that tracks when items are stored
    class CountingStorage(InMemoryStorage):
        def __init__(self):
            super().__init__()
            self.store_call_count = 0
        
        def store(self, page):
            self.store_call_count += 1
            super().store(page)
    
    num_urls = 100
    urls = [f'http://example.com/page{i}' for i in range(num_urls)]
    html_bodies = {url: f'<html><head><title>Page {i}</title></head></html>'
                   for i, url in enumerate(urls)}
    
    clock = FakeClock()
    fetcher = FakeFetcher(html_bodies)
    parser = ParserRegistry()
    storage = CountingStorage()
    politeness = PolitenessPolicy()
    
    pipeline = Pipeline(fetcher, parser, storage, politeness, clock, max_workers=1)
    
    # Process URLs
    result = pipeline.process(iter(urls))
    
    # Storage should have been called incrementally (once per URL)
    assert storage.store_call_count == num_urls, \
        'Pipeline should call storage.store() incrementally, not batch all at once'
    
    # TODO: To truly test streaming, we'd need to verify that results aren't
    # held in memory. The fact that process() returns a list is the problem.
    # This assertion will PASS even with current implementation, but the
    # memory usage test (result is None) above will FAIL.
