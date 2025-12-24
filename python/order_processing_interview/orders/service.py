"""Checkout service for order processing."""

from typing import Dict

from .models import Order
from .gateway import PaymentGateway
from .inventory import Inventory
from .queueing import InMemoryJobQueue, Job
from .idempotency import IdempotencyStore


class CheckoutService:
    """
    Service for processing customer checkouts.
    
    TODO: Move charge + reserve to background processing.
    Currently charges synchronously inline.
    """
    
    def __init__(
        self,
        gateway: PaymentGateway,
        inventory: Inventory,
        queue: InMemoryJobQueue,
        idempotency_store: IdempotencyStore
    ):
        """
        Initialize checkout service.
        
        Args:
            gateway: Payment gateway for charging
            inventory: Inventory system for reservations
            queue: Job queue for background processing
            idempotency_store: Store for preventing duplicate charges
        """
        self.gateway = gateway
        self.inventory = inventory
        self.queue = queue
        self.idempotency_store = idempotency_store
        self.orders: Dict[str, Order] = {}
    
    def checkout(self, order: Order) -> Order:
        """
        Process a checkout.
        
        TODO: Instead of charging inline, enqueue a background job and return
        order with status 'pending'. Background workers should later process
        the job and update order status to 'paid' or 'failed'.
        
        Args:
            order: Order to process
            
        Returns:
            Order with updated status
        """
        # Store order
        self.orders[order.order_id] = order
        
        # Currently charges synchronously - NOT the desired behavior
        # This should be changed to:
        # 1. Set order status to 'pending'
        # 2. Enqueue a job to the queue
        # 3. Return order immediately
        # 4. Let background workers charge and update status later
        try:
            receipt = self.gateway.charge(order.order_id, order.amount_cents)
            if receipt.charged:
                reserved = self.inventory.reserve(order.order_id)
                if reserved:
                    order.status = 'paid'
                else:
                    order.status = 'failed'
            else:
                order.status = 'failed'
        except Exception:
            order.status = 'failed'
        
        return order
    
    def get_order(self, order_id: str) -> Order:
        """
        Get an order by ID.
        
        Args:
            order_id: Order ID to retrieve
            
        Returns:
            Order if found
            
        Raises:
            KeyError: If order not found
        """
        return self.orders[order_id]
