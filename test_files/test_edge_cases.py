"""
Edge cases and special scenarios for the analyzer.
"""


# Empty function
def empty_function():
    """Should this be flagged? Currently not - it's only 2 lines."""
    pass


# Single line function
def one_liner(x, y): return x + y


# Function with only docstring
def only_docstring():
    """
    This function has a long docstring but minimal code.
    The docstring explains complex logic.
    But the actual implementation is short.
    """
    return True


# Lambda (not a FunctionDef, so won't be analyzed)
lambda_func = lambda x, y: x + y


# Nested function definitions
def outer_function():
    """Outer function is short."""
    def inner_function():
        """Inner function is also analyzed separately."""
        return 42
    return inner_function()


# Async function
async def async_function(x, y):
    """Async functions should be analyzed the same way."""
    result = x + y
    return result


# Generator function
def generator_function():
    """Generator with yield."""
    for i in range(10):
        yield i


# Function with decorators
def my_decorator(func):
    """Decorator function."""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@my_decorator
def decorated_function(x):
    """Function with decorator applied."""
    return x * 2


# Class methods
class MyClass:
    """Test class methods."""

    def __init__(self, a, b, c, d, e, f):
        """Constructor with 6 params (should be flagged as INFO)."""
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def instance_method(self):
        """Normal instance method."""
        return self.a + self.b

    @classmethod
    def class_method(cls, x, y):
        """Class method."""
        return x + y

    @staticmethod
    def static_method(x, y):
        """Static method."""
        return x + y

    @property
    def computed_property(self):
        """Property getter."""
        return self.a * 2


# Function with try/except (does try/except count as nesting?)
def function_with_exception_handling(data):
    """
    Exception handling test.
    Try/except blocks - do they count as nesting?
    Currently our visitor only tracks if/for/while/with.
    """
    result = []
    try:
        for item in data:  # Level 1
            if item > 0:  # Level 2
                result.append(item * 2)
    except Exception as e:
        return []
    return result


# Function with context managers
def function_with_context_manager(filename):
    """With statement is counted as nesting level."""
    results = []
    with open(filename) as f:  # Level 1
        for line in f:  # Level 2
            if line.strip():  # Level 3
                results.append(line)
    return results


# Unicode and special characters in names
def функция_с_unicode():
    """Function with unicode name."""
    return "Hello, мир!"


def function_with_special_chars():
    """Function with special chars in string literals (not name)."""
    return "✨ Special 😀 ✨"


# Very long parameter names (but only 3 params)
def function_with_very_long_parameter_names(
    extremely_long_parameter_name_for_configuration,
    another_incredibly_verbose_parameter_name,
    yet_another_unnecessarily_long_name
):
    """Only 3 params, should be fine."""
    return (extremely_long_parameter_name_for_configuration +
            another_incredibly_verbose_parameter_name +
            yet_another_unnecessarily_long_name)
