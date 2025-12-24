# Concurrent Crawler Interview Practice

A 60-minute interview exercise (10–15 min discussion, 40–45 min coding) focused on concurrent web crawling in Python 3.11.

## Project Structure

```
crawler_interview/
  README.md
  pyproject.toml
  crawler/
    __init__.py
    fetch.py        # FakeFetcher with simulated latency/failures
    parse.py        # ParsedPage, HtmlParser, ParserRegistry
    pipeline.py     # Main Pipeline orchestrator
    storage.py      # StorageBackend interface + InMemoryStorage
    politeness.py   # PolitenessPolicy for rate limiting
    clock.py        # FakeClock for deterministic time
  tests/
    test_concurrent_pipeline.py
    test_bounded_backpressure.py
    test_parser_plugins.py
    test_no_duplicates_streaming.py
```

## Current Baseline Implementation

The naive baseline includes:
- **FakeClock**: Deterministic time simulation via `now()` and `advance(seconds)`
- **FakeFetcher**: Simulates HTTP fetches with configurable per-domain failures/latency (no real sleep or network calls)
- **HtmlParser**: Basic title extraction from HTML
- **ParserRegistry**: Stub that always uses HtmlParser (TODO: plugin architecture)
- **InMemoryStorage**: Simple in-memory storage backend
- **PolitenessPolicy**: Stub that always allows requests (TODO: per-domain rate limiting)
- **Pipeline**: Sequential processing that loops through URLs and returns a list (TODO: streaming, concurrency, bounded queue)

## Interview Requirements (TODOs)

### 1. Concurrency
**Goal**: Fetch and parse concurrently using thread pool or asyncio.
- Must cap concurrency (e.g., `max_workers` parameter)
- Test: With `max_workers=8`, processing 100 URLs should complete in fewer 'ticks' than sequential baseline

### 2. Scaling & Streaming
**Goal**: Accept an iterable/generator of URLs (simulate millions) and stream results to storage.
- Pipeline should not hold all pages in memory
- Must process and store incrementally
- Test: Feed a generator; ensure pipeline yields/stores incrementally without building large in-memory lists

### 3. Backpressure
**Goal**: Introduce a bounded internal queue between fetch and parse stages.
- If queue is full, pipeline should slow down producers (deterministic in tests)
- Can block/yield until space is available
- Test: With queue size=5, never exceed 5 items; expose debug hook/metric to verify

### 4. OOP Plugin Architecture
**Goal**: ParserRegistry should allow registering parsers by content_type.
- Support multiple parser types (HtmlParser, JsonParser, etc.)
- Route to correct parser based on content type
- Test: Register JsonParser plugin and ensure URLs with '.json' use it

### 5. Correctness
**Goals**:
- Never process duplicate URLs
- Enforce per-domain politeness: max 2 requests per 10 seconds per domain
- Use FakeClock for deterministic testing (no real time)
- Test: Feed generator with duplicates; ensure storage contains unique URLs only

## Running Tests

```bash
# Install dependencies
pip install -e .

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_concurrent_pipeline.py -v
```

## Notes

- Uses stdlib + pytest only
- Single quotes for all Python strings
- No network calls - everything is simulated
- Tests fail initially - TODOs are not implemented in baseline
