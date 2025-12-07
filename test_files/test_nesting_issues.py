"""
Test file focused on nesting-related issues (Rule 3).
"""


def no_nesting():
    """Good: No nesting at all."""
    x = 1
    y = 2
    return x + y


def single_level_nesting(items):
    """Good: Only 1 level of nesting."""
    result = []
    for item in items:
        result.append(item * 2)
    return result


def two_level_nesting(matrix):
    """Good: 2 levels of nesting (under limit of 3)."""
    result = []
    for row in matrix:
        for item in row:
            result.append(item)
    return result


def three_level_nesting(data):
    """Good: Exactly 3 levels (at the limit)."""
    result = []
    for category in data:
        for subcategory in category:
            for item in subcategory:
                result.append(item)
    return result


def four_level_nesting(data):
    """INFO severity: 4 levels of nesting."""
    result = []
    for a in data:
        for b in a:
            for c in b:
                for d in c:
                    result.append(d)
    return result


def five_level_nesting(data):
    """WARN severity: 5 levels of nesting (1.67x over limit)."""
    result = []
    for a in data:
        for b in a:
            for c in b:
                for d in c:
                    for e in d:
                        result.append(e)
    return result


def seven_level_nesting(data):
    """CRITICAL severity: 7 levels of nesting (2.33x over limit)."""
    result = []
    for a in data:
        for b in a:
            for c in b:
                for d in c:
                    for e in d:
                        for f in e:
                            for g in f:
                                result.append(g)
    return result


def mixed_nesting_if_for_while(data, threshold):
    """INFO severity: 4 levels with different control structures."""
    result = []
    for item in data:  # Level 1
        if item > threshold:  # Level 2
            counter = 0
            while counter < item:  # Level 3
                if counter % 2 == 0:  # Level 4
                    result.append(counter)
                counter += 1
    return result


def with_statement_nesting(filenames):
    """INFO severity: 4 levels including 'with' statements."""
    results = []
    for filename in filenames:  # Level 1
        with open(filename) as f:  # Level 2
            for line in f:  # Level 3
                if line.strip():  # Level 4
                    results.append(line)
    return results


def refactored_good_example(data):
    """
    Good refactor: Extracted nested logic into helper function.
    This reduces nesting and improves readability.
    """
    def process_item(item):
        """Helper function to process a single item."""
        return item * 2 if item > 0 else 0

    return [process_item(item) for sublist in data for item in sublist]


def early_return_pattern(value):
    """
    Good pattern: Use early returns to avoid nesting.
    This is called the 'guard clause' pattern.
    """
    if value is None:
        return None

    if value < 0:
        return 0

    if value > 100:
        return 100

    return value * 2
