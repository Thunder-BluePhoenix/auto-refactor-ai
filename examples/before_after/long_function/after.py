# Long Function Example - After

"""
Refactored into smaller, focused functions with single responsibilities.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OrderItem:
    price: float
    quantity: int
    taxable: bool = False


@dataclass
class ShippingInfo:
    cost: float = 5.99
    tracking: Optional[str] = None


def calculate_item_total(item: OrderItem) -> float:
    """Calculate total for a single item including tax."""
    total = item.price * item.quantity
    if item.taxable:
        total *= 1.08
    return total


def calculate_subtotal(items: List[OrderItem]) -> float:
    """Calculate subtotal for all items."""
    return sum(calculate_item_total(item) for item in items)


def apply_discount(subtotal: float, discount_code: Optional[str]) -> float:
    """Apply discount code and return discount amount."""
    discounts = {
        'SAVE10': 0.10,
        'SAVE20': 0.20,
    }
    if discount_code in discounts:
        return subtotal * discounts[discount_code]
    return 0.0


def calculate_shipping(subtotal: float, gift_wrap: bool = False) -> float:
    """Calculate shipping cost with free shipping over $100."""
    if subtotal > 100:
        cost = 0
    else:
        cost = 5.99
    if gift_wrap:
        cost += 3.99
    return cost


def process_order(order_id: str, items: List[OrderItem],
                  discount_code: Optional[str] = None,
                  gift_wrap: bool = False) -> dict:
    """Process an order with clear, testable steps."""
    subtotal = calculate_subtotal(items)
    discount = apply_discount(subtotal, discount_code)
    shipping = calculate_shipping(subtotal, gift_wrap)
    total = subtotal - discount + shipping

    return {
        'id': order_id,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total': total,
        'status': 'processed'
    }
