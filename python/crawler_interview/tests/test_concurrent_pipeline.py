'''Test concurrent pipeline performance.

This test verifies that concurrent processing (with max_workers > 1) completes
faster than sequential processing, measured in 'ticks' using FakeFetcher counters.
'''
import pytest
from crawler.clock import FakeClock
from crawler.fetch import FakeFetcher
from crawler.parse import ParserRegistry
from crawler.storage import InMemoryStorage
from crawler.politeness import PolitenessPolicy
from crawler.pipeline import Pipeline


def test_concurrent_pipeline_faster_than_sequential():
    '''Test that concurrent processing with max_workers=8 completes faster than sequential.
    
    This test should FAIL initially because Pipeline.process() is not yet concurrent.
    '''
    # Setup: 100 URLs with simulated latency
    num_urls = 100
    urls = [f'http://example.com/page{i}' for i in range(num_urls)]
    html_bodies = {url: f'<html><head><title>Page {i}</title></head></html>' 
                   for i, url in enumerate(urls)}
    
    # Simulate latency: each fetch "costs" 1 tick
    domain_latency = {'example.com': 1.0}
    
    # Test sequential pipeline (max_workers=1)
    clock_seq = FakeClock()
    fetcher_seq = FakeFetcher(html_bodies, domain_latency=domain_latency)
    parser_seq = ParserRegistry()
    storage_seq = InMemoryStorage()
    politeness_seq = PolitenessPolicy()
    
    pipeline_seq = Pipeline(
        fetcher_seq, parser_seq, storage_seq, politeness_seq, clock_seq, max_workers=1
    )
    
    pipeline_seq.process(urls)
    sequential_fetches = fetcher_seq.get_fetch_count()
    
    # Test concurrent pipeline (max_workers=8)
    clock_conc = FakeClock()
    fetcher_conc = FakeFetcher(html_bodies, domain_latency=domain_latency)
    parser_conc = ParserRegistry()
    storage_conc = InMemoryStorage()
    politeness_conc = PolitenessPolicy()
    
    pipeline_conc = Pipeline(
        fetcher_conc, parser_conc, storage_conc, politeness_conc, clock_conc, max_workers=8
    )
    
    pipeline_conc.process(urls)
    concurrent_fetches = fetcher_conc.get_fetch_count()
    
    # Both should process all URLs
    assert storage_seq.count() == num_urls
    assert storage_conc.count() == num_urls
    
    # TODO: With concurrency, we expect similar fetch counts but measured 'ticks' should differ
    # Since we're using counters not wall time, we need to track something that shows parallelism
    # For now, this assertion will FAIL because the implementation is sequential
    
    # This is a placeholder - in a real concurrent implementation, you'd measure
    # simulated time advancement or use fetch timestamps to prove parallelism
    # For this test to pass, the concurrent version should show evidence of parallel execution
    
    # EXPECTED TO FAIL: The current sequential implementation won't show any difference
    assert False, 'TODO: Implement concurrency and measure parallel execution improvement'
