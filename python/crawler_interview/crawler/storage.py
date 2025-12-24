'''Storage backends for persisting crawled pages.'''
from abc import ABC, abstractmethod
from typing import List
from crawler.parse import ParsedPage


class StorageBackend(ABC):
    '''Abstract interface for storage backends.'''
    
    @abstractmethod
    def store(self, page: ParsedPage) -> None:
        '''Store a parsed page.
        
        Args:
            page: ParsedPage to store
        '''
        pass
    
    @abstractmethod
    def get_all(self) -> List[ParsedPage]:
        '''Retrieve all stored pages.
        
        Returns:
            List of all stored ParsedPage objects
        '''
        pass
    
    @abstractmethod
    def count(self) -> int:
        '''Get count of stored pages.
        
        Returns:
            Number of stored pages
        '''
        pass


class InMemoryStorage(StorageBackend):
    '''Simple in-memory storage backend.'''
    
    def __init__(self):
        '''Initialize in-memory storage.'''
        self._pages: List[ParsedPage] = []
    
    def store(self, page: ParsedPage) -> None:
        '''Store a parsed page in memory.
        
        Args:
            page: ParsedPage to store
        '''
        self._pages.append(page)
    
    def get_all(self) -> List[ParsedPage]:
        '''Retrieve all stored pages.
        
        Returns:
            List of all stored ParsedPage objects
        '''
        return self._pages.copy()
    
    def count(self) -> int:
        '''Get count of stored pages.
        
        Returns:
            Number of stored pages
        '''
        return len(self._pages)
