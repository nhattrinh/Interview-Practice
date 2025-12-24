"""Idempotency store to prevent duplicate processing."""

from typing import Set


class IdempotencyStore:
    """
    Tracks processed orders to prevent duplicate charges.
    
    TODO: Implement actual idempotency logic.
    Currently this is a stub that does nothing.
    
    Requirements:
    - Thread-safe operations
    - Record when an order has been processed
    - Check if an order has already been processed
    - Prevent race conditions (atomic check-and-set)
    """
    
    def __init__(self):
        """Initialize empty store."""
        self._processed: Set[str] = set()
    
    def is_processed(self, order_id: str) -> bool:
        """
        Check if an order has been processed.
        
        TODO: Implement thread-safe check
        
        Args:
            order_id: Order ID to check
            
        Returns:
            True if already processed, False otherwise
        """
        # Stub implementation - always returns False
        return False
    
    def mark_processed(self, order_id: str) -> bool:
        """
        Mark an order as processed.
        
        TODO: Implement atomic check-and-set
        
        Args:
            order_id: Order ID to mark as processed
            
        Returns:
            True if this call marked it (first time), False if already marked
        """
        # Stub implementation - doesn't actually store anything
        return True
