"""
Test file focused on parameter-related issues (Rule 2).
"""


def few_params(x, y):
    """Good: Only 2 parameters."""
    return x + y


def exactly_five_params(a, b, c, d, e):
    """Borderline: Exactly 5 parameters (at the limit)."""
    return a + b + c + d + e


def six_params(a, b, c, d, e, f):
    """INFO severity: 6 parameters (slightly over 5)."""
    return a + b + c + d + e + f


def eight_params(a, b, c, d, e, f, g, h):
    """WARN severity: 8 parameters (1.6x over limit)."""
    return a + b + c + d + e + f + g + h


def twelve_params(a, b, c, d, e, f, g, h, i, j, k, l):
    """CRITICAL severity: 12 parameters (2.4x over limit)."""
    return a + b + c + d + e + f + g + h + i + j + k + l


def params_with_args(a, b, c, *args):
    """6 total: 3 regular + 1 *args = INFO severity."""
    return sum([a, b, c] + list(args))


def params_with_kwargs(a, b, c, **kwargs):
    """6 total: 3 regular + 1 **kwargs = INFO severity."""
    result = a + b + c
    for value in kwargs.values():
        result += value
    return result


def all_param_types(a, b, c, d, *args, e, f, **kwargs):
    """9 total: 4 regular + 1 *args + 2 kwonly + 1 **kwargs = WARN severity."""
    return sum([a, b, c, d, e, f] + list(args) + list(kwargs.values()))


def refactored_good_example(config):
    """
    Good refactor: Instead of many parameters, use a config object.
    This is the recommended approach when you have many related parameters.
    """
    return {
        'result': config.get('value', 0) * 2,
        'processed': True
    }
