"""Companion file for V8 duplicate detection testing.

This file contains intentional duplicates of functions in test_duplicates_a.py
to demonstrate the project-level duplicate detection feature.
"""


# ==============================================================================
# DUPLICATE FUNCTIONS (same structure as test_duplicates_a.py)
# ==============================================================================


def check_email_valid(email_addr):
    """Check email validity - DUPLICATE structure with test_duplicates_a.py."""
    if email_addr is None:
        return False
    if not isinstance(email_addr, str):
        return False
    if '@' not in email_addr:
        return False
    if '.' not in email_addr:
        return False
    return True


def compute_discount(base_price, discount_rate):
    """Compute discount - DUPLICATE structure with test_duplicates_a.py."""
    if base_price <= 0:
        return 0
    if discount_rate <= 0:
        return 0
    if discount_rate > 100:
        discount_rate = 100
    discount = base_price * (discount_rate / 100)
    return discount


def display_currency(value, currency_code="USD"):
    """Display value as currency - DUPLICATE structure with test_duplicates_a.py."""
    if value is None:
        return "$0.00"
    if not isinstance(value, (int, float)):
        return "$0.00"
    if currency_code == "USD":
        return f"${value:.2f}"
    elif currency_code == "EUR":
        return f"€{value:.2f}"
    else:
        return f"{value:.2f} {currency_code}"


# ==============================================================================
# UNIQUE FUNCTIONS (only in this file)
# ==============================================================================


def process_order_b(order_data):
    """Process order - unique to this file (different from test_duplicates_a)."""
    if not order_data:
        return None
    
    items = order_data.get('items', [])
    subtotal = sum(item['price'] for item in items)
    tax = subtotal * 0.08
    
    return {
        'subtotal': subtotal,
        'tax': tax,
        'total': subtotal + tax
    }


def send_alert(recipient, subject, body, priority="normal"):
    """Send alert - unique to this file."""
    if priority == "high":
        subject = f"[URGENT] {subject}"
    
    return {
        'to': recipient,
        'subject': subject,
        'body': body,
        'sent': True
    }
