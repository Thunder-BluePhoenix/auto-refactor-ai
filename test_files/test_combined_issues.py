"""
Test file with functions that violate multiple rules simultaneously.
"""


def nightmare_function(a, b, c, d, e, f, g, h):
    """
    MULTIPLE VIOLATIONS:
    - Too many parameters: 8 params (WARN)
    - Too long: 50+ lines (WARN)
    - Deep nesting: 5 levels (WARN)

    This is an example of truly problematic code.
    """
    results = []

    for item_a in a:  # Level 1
        if item_a > 0:  # Level 2
            for item_b in b:  # Level 3
                if item_b > 0:  # Level 4
                    for item_c in c:  # Level 5
                        results.append(item_a + item_b + item_c)

    for item_d in d:
        results.append(item_d)

    for item_e in e:
        results.append(item_e)

    for item_f in f:
        results.append(item_f)

    for item_g in g:
        results.append(item_g)

    for item_h in h:
        results.append(item_h)

    total = sum(results)
    average = total / len(results) if results else 0
    maximum = max(results) if results else 0
    minimum = min(results) if results else 0

    final_result = {
        'total': total,
        'average': average,
        'max': maximum,
        'min': minimum,
        'count': len(results),
        'results': results
    }

    return final_result


def moderately_bad(x, y, z, a, b, c):
    """
    MULTIPLE VIOLATIONS (mild):
    - 6 parameters (INFO)
    - 35 lines (INFO)
    - 4 levels of nesting (INFO)
    """
    result = []

    for item in x:  # Level 1
        if item > 0:  # Level 2
            for subitem in y:  # Level 3
                if subitem > 0:  # Level 4
                    result.append(item + subitem)

    for item in z:
        result.append(item)

    for item in a:
        result.append(item)

    for item in b:
        result.append(item)

    for item in c:
        result.append(item)

    total = sum(result)
    average = total / len(result) if result else 0

    return {
        'total': total,
        'average': average,
        'data': result
    }


def params_and_length(a, b, c, d, e, f, g):
    """
    TWO VIOLATIONS:
    - 7 parameters (INFO)
    - 40 lines (INFO)
    - No nesting issues
    """
    result_1 = a + b
    result_2 = c + d
    result_3 = e + f
    result_4 = g

    combined_1 = result_1 + result_2
    combined_2 = result_3 + result_4

    final_sum = combined_1 + combined_2

    data = {
        'r1': result_1,
        'r2': result_2,
        'r3': result_3,
        'r4': result_4,
        'c1': combined_1,
        'c2': combined_2,
        'final': final_sum
    }

    metadata = {
        'processed': True,
        'param_count': 7,
        'timestamp': None
    }

    return {
        'data': data,
        'metadata': metadata,
        'success': True,
        'errors': []
    }


def length_and_nesting(data):
    """
    TWO VIOLATIONS:
    - 45 lines (WARN)
    - 5 levels of nesting (WARN)
    - Only 1 parameter (good)
    """
    results = []

    for level1 in data:  # Level 1
        if level1:  # Level 2
            for level2 in level1:  # Level 3
                if level2:  # Level 4
                    for level3 in level2:  # Level 5
                        results.append(level3)

    processed = [x * 2 for x in results]
    filtered = [x for x in processed if x > 0]

    total = sum(filtered)
    count = len(filtered)
    average = total / count if count else 0

    stats = {
        'total': total,
        'count': count,
        'average': average
    }

    metadata = {
        'processed': True,
        'original_count': len(results),
        'filtered_count': len(filtered)
    }

    return {
        'stats': stats,
        'metadata': metadata,
        'data': filtered
    }
