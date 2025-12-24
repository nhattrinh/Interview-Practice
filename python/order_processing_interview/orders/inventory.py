"""Inventory management."""


class Inventory:
    """Simple inventory management system."""
    
    def reserve(self, order_id: str) -> bool:
        """
        Reserve inventory for an order.
        
        Args:
            order_id: Order to reserve inventory for
            
        Returns:
            True if reservation successful, False otherwise
        """
        # Naive implementation - always succeeds
        # In a real system, this would check stock levels
        return True
