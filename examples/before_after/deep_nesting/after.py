# Deep Nesting Example - After

"""
Use early returns and extract helper functions to flatten nesting.
"""


def is_eligible_account(item: dict) -> bool:
    """Check if account is eligible for processing."""
    return (
        item.get('active') and
        item.get('type') == 'premium' and
        item.get('balance', 0) > 0
    )


def is_large_pending_transaction(transaction: dict) -> bool:
    """Check if transaction meets criteria."""
    return (
        transaction.get('status') == 'pending' and
        transaction.get('amount', 0) > 100
    )


def extract_transaction_info(transaction: dict, user_id: str) -> dict:
    """Extract relevant transaction info."""
    return {
        'id': transaction['id'],
        'amount': transaction['amount'],
        'user': user_id
    }


def process_data(data: list) -> list:
    """Process data with flattened, readable logic."""
    if not data:
        return []

    results = []

    for item in data:
        if not is_eligible_account(item):
            continue

        for transaction in item.get('transactions', []):
            if is_large_pending_transaction(transaction):
                results.append(
                    extract_transaction_info(transaction, item['user_id'])
                )

    return results
