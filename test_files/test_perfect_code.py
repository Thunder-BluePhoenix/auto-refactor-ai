"""
Perfect code example - should have NO issues.
This file demonstrates well-written functions that pass all rules.
"""


def add(x, y):
    """Simple addition - short, clear, no issues."""
    return x + y


def calculate_average(numbers):
    """Calculate average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)


def validate_email(email):
    """Simple email validation."""
    if '@' not in email:
        return False

    parts = email.split('@')
    if len(parts) != 2:
        return False

    return bool(parts[0] and parts[1])


def format_user_data(user_id, name):
    """Format user data into a dictionary."""
    return {
        'id': user_id,
        'name': name,
        'formatted': f"{name} (ID: {user_id})"
    }


class Calculator:
    """Simple calculator class."""

    def __init__(self):
        self.result = 0

    def add(self, value):
        """Add value to result."""
        self.result += value
        return self.result

    def reset(self):
        """Reset calculator."""
        self.result = 0
