"""Sample file with long functions to test the analyzer."""


def short_function():
    """This is a short function that should not be flagged."""
    x = 1
    y = 2
    return x + y


def very_long_function(data):
    """This function is intentionally long to trigger the analyzer."""
    # Line 1
    result = []

    # Line 3
    for item in data:
        # Line 5
        if item > 0:
            # Line 7
            processed = item * 2
            # Line 9
            if processed > 100:
                # Line 11
                processed = 100
            # Line 13
            result.append(processed)
        # Line 15
        elif item < 0:
            # Line 17
            processed = abs(item)
            # Line 19
            result.append(processed)
        # Line 21
        else:
            # Line 23
            result.append(0)

    # Line 26
    total = sum(result)
    # Line 28
    average = total / len(result) if result else 0
    # Line 30
    maximum = max(result) if result else 0
    # Line 32
    minimum = min(result) if result else 0

    # Line 35
    stats = {
        'total': total,
        'average': average,
        'max': maximum,
        'min': minimum,
        'count': len(result)
    }

    # Line 44
    return stats


def another_long_function():
    """Another long function."""
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
    print("Line 31")
    print("Line 32")
    return "Done"


def medium_function():
    """This function is borderline."""
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    j = 10
    k = 11
    l = 12
    m = 13
    n = 14
    o = 15
    p = 16
    q = 17
    r = 18
    s = 19
    t = 20
    u = 21
    v = 22
    w = 23
    x = 24
    y = 25
    z = 26
    return a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + q + r + s + t + u + v + w + x + y + z
