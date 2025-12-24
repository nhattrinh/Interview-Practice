"""Core data models for order processing."""

from dataclasses import dataclass
from typing import Literal


OrderStatus = Literal['pending', 'paid', 'failed']


@dataclass
class Order:
    """Represents a customer order."""
    order_id: str
    user_id: str
    amount_cents: int
    status: OrderStatus = 'pending'


@dataclass
class Receipt:
    """Tracks payment processing attempts."""
    order_id: str
    charged: bool
    attempt: int
