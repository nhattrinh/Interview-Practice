'''Test bounded backpressure in the pipeline.

This test verifies that the pipeline implements a bounded queue between fetch
and parse stages, and that the queue never exceeds its size limit.
'''
import pytest
from crawler.clock import FakeClock
from crawler.fetch import FakeFetcher
from crawler.parse import ParserRegistry
from crawler.storage import InMemoryStorage
from crawler.politeness import PolitenessPolicy
from crawler.pipeline import Pipeline


def test_bounded_queue_never_exceeds_limit():
    '''Test that bounded queue size=5 never exceeds 5 items.
    
    This test should FAIL initially because Pipeline doesn't implement bounded queue.
    '''
    # Setup: 50 URLs
    num_urls = 50
    urls = [f'http://example.com/page{i}' for i in range(num_urls)]
    html_bodies = {url: f'<html><head><title>Page {i}</title></head></html>' 
                   for i, url in enumerate(urls)}
    
    clock = FakeClock()
    fetcher = FakeFetcher(html_bodies)
    parser = ParserRegistry()
    storage = InMemoryStorage()
    politeness = PolitenessPolicy()
    
    # TODO: Pipeline needs to accept queue_size parameter
    # For now, this will fail because the parameter doesn't exist
    try:
        pipeline = Pipeline(
            fetcher, parser, storage, politeness, clock,
            max_workers=4,
            queue_size=5  # TODO: This parameter doesn't exist yet
        )
        
        # TODO: Pipeline needs to expose max_queue_size metric/hook
        pipeline.process(urls)
        
        # Check that all URLs were processed
        assert storage.count() == num_urls
        
        # TODO: Get max queue size observed during processing
        # This requires Pipeline to expose a debug hook or metric
        max_queue_size_observed = pipeline.get_max_queue_size_observed()
        
        # Queue should never exceed the limit
        assert max_queue_size_observed <= 5, \
            f'Queue exceeded limit: {max_queue_size_observed} > 5'
        
    except TypeError:
        # Expected to fail: queue_size parameter doesn't exist
        pytest.fail('TODO: Implement queue_size parameter and bounded queue in Pipeline')


def test_bounded_queue_still_processes_all_urls():
    '''Test that bounded queue doesn't drop URLs.
    
    This test should FAIL initially because Pipeline doesn't implement bounded queue.
    '''
    # Setup: 100 URLs with small queue
    num_urls = 100
    urls = [f'http://example.com/page{i}' for i in range(num_urls)]
    html_bodies = {url: f'<html><head><title>Page {i}</title></head></html>' 
                   for i, url in enumerate(urls)}
    
    clock = FakeClock()
    fetcher = FakeFetcher(html_bodies)
    parser = ParserRegistry()
    storage = InMemoryStorage()
    politeness = PolitenessPolicy()
    
    # TODO: This will fail because queue_size parameter doesn't exist
    pytest.skip('TODO: Implement bounded queue with backpressure')
