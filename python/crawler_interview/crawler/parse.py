'''HTML parsing and parser registry for content type routing.'''
from dataclasses import dataclass
from typing import Dict, Callable
import re


@dataclass
class ParsedPage:
    '''Represents a parsed web page.'''
    url: str
    title: str
    content_type: str


class HtmlParser:
    '''Basic HTML parser that extracts title from HTML content.'''
    
    def parse(self, html: str, url: str) -> ParsedPage:
        '''Parse HTML content and extract title.
        
        Args:
            html: HTML content as string
            url: URL of the page
            
        Returns:
            ParsedPage with extracted information
        '''
        # Naive title extraction using regex
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else 'No title'
        
        return ParsedPage(
            url=url,
            title=title,
            content_type='text/html'
        )


class ParserRegistry:
    '''Registry for managing parsers by content type.
    
    TODO: Implement plugin architecture to allow registering custom parsers.
    Currently always uses HtmlParser as a stub implementation.
    '''
    
    def __init__(self):
        '''Initialize the parser registry.'''
        self._parsers: Dict[str, Callable] = {}
        # For now, always use HtmlParser (stub implementation)
        self._default_parser = HtmlParser()
    
    def register(self, content_type: str, parser: Callable) -> None:
        '''Register a parser for a specific content type.
        
        TODO: Implement this method to support plugin architecture.
        
        Args:
            content_type: MIME type (e.g., 'application/json')
            parser: Parser callable that takes (content, url) and returns ParsedPage
        '''
        # TODO: Store parser in registry
        pass
    
    def parse(self, content: str, url: str, content_type: str = 'text/html') -> ParsedPage:
        '''Parse content using the appropriate parser for content type.
        
        TODO: Route to registered parser based on content_type.
        Currently always uses HtmlParser.
        
        Args:
            content: Content to parse
            url: URL of the content
            content_type: MIME type of the content
            
        Returns:
            ParsedPage with extracted information
        '''
        # TODO: Look up parser by content_type and use it
        # For now, always use default HTML parser
        return self._default_parser.parse(content, url)
