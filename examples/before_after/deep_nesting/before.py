# Deep Nesting Example - Before

"""
Deeply nested code is hard to follow and test.
"""


def process_data(data):
    results = []
    if data:
        for item in data:
            if item.get('active'):
                if item.get('type') == 'premium':
                    if item.get('balance') > 0:
                        for transaction in item.get('transactions', []):
                            if transaction.get('status') == 'pending':
                                if transaction.get('amount') > 100:
                                    # Finally do something!
                                    results.append({
                                        'id': transaction['id'],
                                        'amount': transaction['amount'],
                                        'user': item['user_id']
                                    })
    return results
