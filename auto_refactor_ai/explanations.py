"""Detailed explanations and refactoring guidance for code issues.

This module provides comprehensive explanations for each rule violation,
including why it matters, how to fix it, and examples of good vs bad code.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from .analyzer import Issue, Severity


@dataclass
class Explanation:
    """Detailed explanation for a code issue."""

    why_it_matters: str
    how_to_fix: List[str]
    good_example: str
    bad_example: str
    references: List[str]
    severity_note: Optional[str] = None


# Explanation templates for each rule
EXPLANATIONS: Dict[str, Explanation] = {
    "function-too-long": Explanation(
        why_it_matters="""
Long functions are harder to understand, test, and maintain. They often violate
the Single Responsibility Principle (SRP) by doing too many things. Studies show
that functions longer than 30 lines have significantly higher bug rates and take
longer to understand.

Key problems with long functions:
- Cognitive overload: Hard to keep entire function in working memory
- Hidden dependencies: More variables and state to track
- Testing difficulty: More code paths to test
- Reusability: Difficult to extract and reuse parts
- Debugging: More places for bugs to hide
""",
        how_to_fix=[
            "Extract cohesive blocks of code into separate functions",
            "Look for repeated code patterns and create helper functions",
            "Group related operations into their own functions",
            "Consider if the function is doing multiple things (violating SRP)",
            "Use descriptive function names that explain what each piece does",
        ],
        good_example="""
# GOOD: Short, focused functions with clear responsibilities
def process_user_registration(user_data):
    \"\"\"Process new user registration.\"\"\"
    validated_data = validate_user_data(user_data)
    user = create_user_account(validated_data)
    send_welcome_email(user)
    log_registration(user)
    return user

def validate_user_data(data):
    \"\"\"Validate user registration data.\"\"\"
    if not data.get('email'):
        raise ValueError("Email is required")
    if not data.get('password'):
        raise ValueError("Password is required")
    return data

def create_user_account(data):
    \"\"\"Create user account in database.\"\"\"
    return User.objects.create(**data)
""",
        bad_example="""
# BAD: Long function doing too many things
def process_user_registration(user_data):
    \"\"\"Process new user registration.\"\"\"
    # Validation (lines 3-15)
    if not user_data.get('email'):
        raise ValueError("Email is required")
    if not user_data.get('password'):
        raise ValueError("Password is required")
    if len(user_data['password']) < 8:
        raise ValueError("Password too short")
    # ... more validation ...

    # Database operations (lines 16-25)
    user = User(
        email=user_data['email'],
        password=hash_password(user_data['password']),
        # ... many more fields ...
    )
    user.save()

    # Email sending (lines 26-40)
    # ... email template loading ...
    # ... email sending ...

    # Logging (lines 41-50)
    # ... logging logic ...

    return user
""",
        references=[
            "Clean Code by Robert Martin - Chapter 3: Functions",
            "https://refactoring.guru/extract-method",
            "Single Responsibility Principle (SRP)",
        ],
    ),
    "too-many-parameters": Explanation(
        why_it_matters="""
Functions with too many parameters are difficult to use, test, and maintain.
Each parameter adds complexity and makes the function harder to understand.
More parameters mean more combinations to test and higher cognitive load.

Key problems:
- Hard to remember: Developers must recall parameter order
- Easy to make mistakes: Wrong order or missing parameters
- Testing explosion: More parameters = exponentially more test cases
- Poor encapsulation: Often indicates missing abstractions
- Refactoring difficulty: Changes affect many call sites
""",
        how_to_fix=[
            "Group related parameters into a configuration object or dataclass",
            "Use builder pattern for complex object construction",
            "Split function responsibilities - may indicate doing too much",
            "Use default values for optional parameters",
            "Consider if some parameters can be instance variables (OOP)",
        ],
        good_example="""
# GOOD: Parameters grouped into configuration object
from dataclasses import dataclass

@dataclass
class EmailConfig:
    \"\"\"Email sending configuration.\"\"\"
    to: str
    subject: str
    body: str
    from_address: str = "noreply@example.com"
    cc: List[str] = None
    bcc: List[str] = None

def send_email(config: EmailConfig):
    \"\"\"Send email with given configuration.\"\"\"
    # Implementation using config.to, config.subject, etc.
    pass

# Usage is clear and self-documenting
send_email(EmailConfig(
    to="user@example.com",
    subject="Welcome!",
    body="Thanks for signing up"
))
""",
        bad_example="""
# BAD: Too many parameters
def send_email(to, subject, body, from_address, cc, bcc,
               reply_to, priority, attachments, html_body):
    \"\"\"Send email with many parameters.\"\"\"
    # Which parameter is which? Easy to mix up!
    pass

# Usage is error-prone and hard to read
send_email(
    "user@example.com",           # to
    "Welcome!",                   # subject
    "Thanks for signing up",      # body
    "noreply@example.com",        # from
    None,                         # cc
    None,                         # bcc
    None,                         # reply_to
    "high",                       # priority
    [],                           # attachments
    "<h1>Welcome</h1>"            # html_body
)
""",
        references=[
            "Introduce Parameter Object - Martin Fowler",
            "https://refactoring.guru/introduce-parameter-object",
            "Builder Pattern - Gang of Four",
        ],
    ),
    "deep-nesting": Explanation(
        why_it_matters="""
Deep nesting makes code significantly harder to understand and maintain.
Each nesting level adds cognitive complexity. Code with deep nesting is
more likely to contain bugs and harder to test effectively.

Key problems:
- Cognitive complexity: Hard to track all conditions
- Arrow anti-pattern: Code drifts to the right
- Error-prone: Easy to miss edge cases
- Testing difficulty: Exponential test cases
- Debugging: Complex control flow to trace
""",
        how_to_fix=[
            "Use early returns (guard clauses) to reduce nesting",
            "Extract nested logic into separate functions",
            "Invert conditions to flatten structure",
            "Use polymorphism instead of nested if-else chains",
            "Consider using strategy pattern for complex conditionals",
        ],
        good_example="""
# GOOD: Guard clauses and early returns
def process_payment(order):
    \"\"\"Process payment for order.\"\"\"
    # Guard clauses at the top
    if not order:
        raise ValueError("Order is required")

    if not order.is_valid():
        return {"status": "invalid", "message": "Invalid order"}

    if order.total <= 0:
        return {"status": "invalid", "message": "Invalid amount"}

    # Main logic is not nested
    payment = charge_card(order.payment_method, order.total)

    if payment.success:
        order.mark_paid()
        send_confirmation(order)
        return {"status": "success"}

    return {"status": "failed", "message": payment.error}
""",
        bad_example="""
# BAD: Deep nesting
def process_payment(order):
    \"\"\"Process payment for order.\"\"\"
    if order:
        if order.is_valid():
            if order.total > 0:
                payment = charge_card(order.payment_method, order.total)
                if payment:
                    if payment.success:
                        order.mark_paid()
                        send_confirmation(order)
                        return {"status": "success"}
                    else:
                        return {"status": "failed", "message": payment.error}
                else:
                    return {"status": "failed", "message": "Payment failed"}
            else:
                return {"status": "invalid", "message": "Invalid amount"}
        else:
            return {"status": "invalid", "message": "Invalid order"}
    else:
        raise ValueError("Order is required")
""",
        references=[
            "Replace Nested Conditional with Guard Clauses",
            "https://refactoring.guru/replace-nested-conditional-with-guard-clauses",
            "Cyclomatic Complexity - Thomas McCabe",
        ],
    ),
}


def get_explanation(issue: Issue) -> Explanation:
    """Get detailed explanation for an issue.

    Args:
        issue: The code issue to explain

    Returns:
        Detailed explanation with examples and guidance
    """
    return EXPLANATIONS.get(issue.rule_name, _get_default_explanation(issue))


def _get_default_explanation(issue: Issue) -> Explanation:
    """Generate default explanation for unknown rules."""
    return Explanation(
        why_it_matters=f"This code pattern ({issue.rule_name}) may impact code quality.",
        how_to_fix=["Review the code and consider refactoring."],
        good_example="# No specific example available for this rule",
        bad_example="# No specific example available for this rule",
        references=["Consult code quality best practices"],
    )


def format_explanation(issue: Issue, explanation: Explanation, verbose: bool = True) -> str:
    """Format explanation as human-readable text.

    Args:
        issue: The code issue
        explanation: The explanation to format
        verbose: If True, include all details; if False, show summary

    Returns:
        Formatted explanation text
    """
    lines = []

    # Header
    lines.append(f"\n{'='*80}")
    lines.append(f"EXPLANATION: {issue.rule_name}")
    lines.append(f"File: {issue.file}:{issue.start_line}-{issue.end_line}")
    lines.append(f"Function: {issue.function_name}()")
    lines.append(f"Severity: {issue.severity.value}")
    lines.append(f"{'='*80}\n")

    # Issue message
    lines.append(f"Issue: {issue.message}\n")

    if verbose:
        # Why it matters
        lines.append("WHY THIS MATTERS:")
        lines.append("-" * 80)
        lines.append(explanation.why_it_matters.strip())
        lines.append("")

        # How to fix
        lines.append("HOW TO FIX:")
        lines.append("-" * 80)
        for i, step in enumerate(explanation.how_to_fix, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

        # Bad example
        lines.append("BAD EXAMPLE (Avoid this):")
        lines.append("-" * 80)
        lines.append(explanation.bad_example.strip())
        lines.append("")

        # Good example
        lines.append("GOOD EXAMPLE (Do this instead):")
        lines.append("-" * 80)
        lines.append(explanation.good_example.strip())
        lines.append("")

        # References
        if explanation.references:
            lines.append("FURTHER READING:")
            lines.append("-" * 80)
            for ref in explanation.references:
                lines.append(f"  • {ref}")
            lines.append("")
    else:
        # Summary mode
        lines.append("Quick fix suggestions:")
        for i, step in enumerate(explanation.how_to_fix[:3], 1):
            lines.append(f"  {i}. {step}")
        lines.append("")

    lines.append("="*80 + "\n")

    return "\n".join(lines)


def get_severity_guidance(severity: Severity) -> str:
    """Get guidance based on issue severity.

    Args:
        severity: The severity level

    Returns:
        Guidance text for the severity level
    """
    if severity == Severity.CRITICAL:
        return """
CRITICAL: This issue significantly impacts code quality and should be addressed
immediately. Critical issues often indicate fundamental design problems that make
code difficult to maintain, test, and debug.
"""
    elif severity == Severity.WARN:
        return """
WARNING: This issue moderately impacts code quality and should be addressed when
refactoring. Warning-level issues don't break the code but make it harder to work
with over time.
"""
    else:  # INFO
        return """
INFO: This is a minor quality concern. While not urgent, addressing it will
improve code maintainability. Consider fixing during regular maintenance.
"""
