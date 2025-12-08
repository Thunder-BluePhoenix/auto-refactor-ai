"""Test file B for V8 duplicate detection.

Contains functions with IDENTICAL structure to test_duplicates_pair_a.py.
Only variable names differ - the logic is exactly the same.
"""


def check_value(value):
    """Check value validity."""
    if value is None:
        return False
    if not isinstance(value, dict):
        return False
    if len(value) == 0:
        return False
    return True


def compute_sum(numbers, multiplier):
    """Compute sum with multiplier."""
    if not numbers:
        return 0
    subtotal = 0
    for number in numbers:
        subtotal = subtotal + number
    result = subtotal * multiplier
    return result


def filter_items(entries, max_count):
    """Filter entries up to max_count."""
    output = []
    count = 0
    for entry in entries:
        if count >= max_count:
            break
        if entry is not None:
            output.append(entry)
            count = count + 1
    return output
