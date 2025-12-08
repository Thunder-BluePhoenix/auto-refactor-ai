"""Test file A for V8 duplicate detection.

Contains functions with IDENTICAL structure to test_duplicates_pair_b.py.
Only variable names differ - the logic is exactly the same.
"""


def validate_input(data):
    """Validate input data."""
    if data is None:
        return False
    if not isinstance(data, dict):
        return False
    if len(data) == 0:
        return False
    return True


def calculate_total(items, rate):
    """Calculate total with rate."""
    if not items:
        return 0
    subtotal = 0
    for item in items:
        subtotal = subtotal + item
    result = subtotal * rate
    return result


def process_data(records, limit):
    """Process records up to limit."""
    output = []
    count = 0
    for record in records:
        if count >= limit:
            break
        if record is not None:
            output.append(record)
            count = count + 1
    return output
