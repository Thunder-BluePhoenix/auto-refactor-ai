"""Test file for project-level duplicate detection (V8).

This file contains intentional duplicates to test the project analyzer.
There's a companion file test_duplicates_b.py with similar functions.
"""


# ==============================================================================
# DUPLICATE FUNCTIONS (same in test_duplicates_b.py)
# ==============================================================================


def validate_email(email):
    """Validate email format - DUPLICATE with test_duplicates_b.py."""
    if email is None:
        return False
    if not isinstance(email, str):
        return False
    if '@' not in email:
        return False
    if '.' not in email:
        return False
    return True


def calculate_discount(price, percent):
    """Calculate discount amount - DUPLICATE with test_duplicates_b.py."""
    if price <= 0:
        return 0
    if percent <= 0:
        return 0
    if percent > 100:
        percent = 100
    discount = price * (percent / 100)
    return discount


def format_currency(amount, currency="USD"):
    """Format amount as currency - DUPLICATE with test_duplicates_b.py."""
    if amount is None:
        return "$0.00"
    if not isinstance(amount, (int, float)):
        return "$0.00"
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "EUR":
        return f"€{amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"


# ==============================================================================
# UNIQUE FUNCTIONS (only in this file)
# ==============================================================================


def process_order_a(order_id, items):
    """Process order - unique to this file."""
    total = 0
    for item in items:
        total += item.get('price', 0) * item.get('quantity', 1)
    return {
        'order_id': order_id,
        'total': total,
        'status': 'processed'
    }


def send_notification_a(user_id, message, channel="email"):
    """Send notification - unique to this file."""
    if channel == "email":
        return f"Email sent to {user_id}: {message}"
    elif channel == "sms":
        return f"SMS sent to {user_id}: {message}"
    else:
        return f"Notification to {user_id}: {message}"
