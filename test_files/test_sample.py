"""Sample file to test all analyzer rules."""


def good_function(x, y):
    """This is a good function - short, simple, no issues."""
    return x + y


def too_many_params(a, b, c, d, e, f, g):
    """Rule 2: This function has 7 parameters (max: 5)."""
    return a + b + c + d + e + f + g


def deeply_nested(data):
    """Rule 3: This function has deep nesting (> 3 levels)."""
    result = []
    for item in data:  # Level 1
        if item > 0:  # Level 2
            for i in range(item):  # Level 3
                if i % 2 == 0:  # Level 4
                    for j in range(i):  # Level 5
                        result.append(j)
    return result


def long_function_with_nesting(data, threshold, multiplier, offset, debug_mode, *args, **kwargs):
    """
    Rule 1: Long function (> 30 lines)
    Rule 2: Too many parameters (8 total)
    Rule 3: Deep nesting (> 3 levels)

    This function violates all three rules!
    """
    # Line 1
    results = []

    # Line 3
    if debug_mode:  # Level 1
        print("Starting processing...")

    # Line 7
    for item in data:  # Level 1
        # Line 9
        if item is not None:  # Level 2
            # Line 11
            if item > threshold:  # Level 3
                # Line 13
                processed = item * multiplier + offset
                # Line 15
                if processed > 1000:  # Level 4
                    # Line 17
                    processed = 1000
                    # Line 19
                    if debug_mode:  # Level 5
                        print("Capping value at 1000")
                # Line 22
                results.append(processed)
            # Line 24
            elif item < 0:
                # Line 26
                results.append(abs(item))
        # Line 28
        else:
            # Line 30
            results.append(0)

    # Line 33
    if args:
        # Line 35
        for arg in args:
            results.append(arg)

    # Line 39
    if kwargs:
        # Line 41
        for key, value in kwargs.items():
            # Line 43
            if isinstance(value, (int, float)):
                results.append(value)

    # Line 47
    total = sum(results)
    # Line 49
    average = total / len(results) if results else 0

    # Line 52
    return {
        'results': results,
        'total': total,
        'average': average,
        'count': len(results)
    }


def moderately_long_function():
    """Rule 1: This is 35 lines (slightly over the 30 line limit)."""
    print("Line 1")
    print("Line 2")
    print("Line 3")
    print("Line 4")
    print("Line 5")
    print("Line 6")
    print("Line 7")
    print("Line 8")
    print("Line 9")
    print("Line 10")
    print("Line 11")
    print("Line 12")
    print("Line 13")
    print("Line 14")
    print("Line 15")
    print("Line 16")
    print("Line 17")
    print("Line 18")
    print("Line 19")
    print("Line 20")
    print("Line 21")
    print("Line 22")
    print("Line 23")
    print("Line 24")
    print("Line 25")
    print("Line 26")
    print("Line 27")
    print("Line 28")
    print("Line 29")
    print("Line 30")
    return "Done"
