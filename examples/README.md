# Examples

This directory contains before/after examples of refactoring patterns detected by auto-refactor-ai.

## Before/After Examples

| Pattern | Description |
|---------|-------------|
| [long_function](before_after/long_function/) | Breaking down overly long functions |
| [too_many_params](before_after/too_many_params/) | Reducing parameter count with dataclasses |
| [deep_nesting](before_after/deep_nesting/) | Flattening deeply nested code |

## How to Use

Run auto-refactor-ai on the `before.py` files to see the issues:

```bash
auto-refactor-ai examples/before_after/long_function/before.py --explain
```

Compare with `after.py` to see the recommended refactoring.
