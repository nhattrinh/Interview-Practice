'''Test parser plugin architecture.

This test verifies that the ParserRegistry can register custom parsers
for different content types and route to the correct parser.
'''
import pytest
from crawler.parse import ParserRegistry, ParsedPage


class JsonParser:
    '''Example JSON parser plugin.'''
    
    def parse(self, content: str, url: str) -> ParsedPage:
        '''Parse JSON content.
        
        Args:
            content: JSON content as string
            url: URL of the content
            
        Returns:
            ParsedPage with extracted information
        '''
        # Naive JSON title extraction (look for "title" key)
        import json
        try:
            data = json.loads(content)
            title = data.get('title', 'No title')
        except (json.JSONDecodeError, AttributeError):
            title = 'Invalid JSON'
        
        return ParsedPage(
            url=url,
            title=title,
            content_type='application/json'
        )


def test_parser_registry_routes_by_content_type():
    '''Test that ParserRegistry routes to correct parser based on content_type.
    
    This test should FAIL initially because ParserRegistry.register() is not implemented.
    '''
    registry = ParserRegistry()
    
    # Register JSON parser
    json_parser = JsonParser()
    registry.register('application/json', json_parser)
    
    # Test HTML parsing (default)
    html_content = '<html><head><title>HTML Page</title></head></html>'
    html_result = registry.parse(html_content, 'http://example.com/page.html', 'text/html')
    assert html_result.title == 'HTML Page'
    assert html_result.content_type == 'text/html'
    
    # Test JSON parsing (plugin)
    json_content = '{"title": "JSON Page", "content": "data"}'
    json_result = registry.parse(json_content, 'http://example.com/data.json', 'application/json')
    
    # TODO: This will FAIL because ParserRegistry doesn't route to registered parsers
    assert json_result.title == 'JSON Page', \
        'ParserRegistry should route to JsonParser for application/json'
    assert json_result.content_type == 'application/json', \
        'ParserRegistry should use registered JsonParser'


def test_multiple_parser_plugins():
    '''Test registering multiple parser plugins.
    
    This test should FAIL initially because ParserRegistry.register() is not implemented.
    '''
    registry = ParserRegistry()
    
    # Register JSON parser
    json_parser = JsonParser()
    registry.register('application/json', json_parser)
    
    # Register another custom parser (e.g., XML)
    class XmlParser:
        def parse(self, content: str, url: str) -> ParsedPage:
            # Naive XML title extraction
            import re
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            title = title_match.group(1) if title_match else 'No title'
            return ParsedPage(url=url, title=title, content_type='application/xml')
    
    xml_parser = XmlParser()
    registry.register('application/xml', xml_parser)
    
    # Test routing to different parsers
    json_result = registry.parse('{"title": "JSON"}', 'http://example.com/data.json', 'application/json')
    xml_result = registry.parse('<root><title>XML</title></root>', 'http://example.com/data.xml', 'application/xml')
    
    # TODO: This will FAIL because routing is not implemented
    assert json_result.content_type == 'application/json'
    assert xml_result.content_type == 'application/xml'
    assert json_result.title == 'JSON'
    assert xml_result.title == 'XML'
