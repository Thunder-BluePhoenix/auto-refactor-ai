"""Test file for V5-V7 features: AI suggestions and auto-refactor.

This file contains functions with various issues that are ideal for
demonstrating AI-powered refactoring suggestions.
"""


# ==============================================================================
# REFACTORING CANDIDATES - Good for AI suggestions
# ==============================================================================


def calculate_order_total(items, tax_rate, discount_percent, shipping_cost,
                          handling_fee, gift_wrap_cost, insurance_cost,
                          expedited_shipping):
    """Function with too many parameters - good refactoring candidate.
    
    Expected: AI should suggest using a dataclass or config object.
    Severity: CRITICAL (8 parameters, 2x over limit of 5)
    """
    subtotal = 0
    for item in items:
        subtotal += item['price'] * item['quantity']

    # Apply discount
    discount_amount = subtotal * (discount_percent / 100)
    subtotal -= discount_amount

    # Add tax
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    # Add fees
    total += shipping_cost
    total += handling_fee
    total += gift_wrap_cost
    total += insurance_cost

    if expedited_shipping:
        total += 15.00

    return total


def validate_user_data(user_dict):
    """Function with deep nesting - good refactoring candidate.
    
    Expected: AI should suggest guard clauses and early returns.
    Severity: WARN (5 levels of nesting)
    """
    if user_dict is not None:
        if 'email' in user_dict:
            if '@' in user_dict['email']:
                if 'password' in user_dict:
                    if len(user_dict['password']) >= 8:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


def process_data_pipeline(data):
    """Function that's too long - good refactoring candidate.
    
    Expected: AI should suggest extracting helper functions.
    Severity: INFO (35 lines, ~1.17x over limit of 30)
    """
    # Step 1: Validate input
    if data is None:
        return None

    if not isinstance(data, list):
        data = [data]

    # Step 2: Clean data
    cleaned = []
    for item in data:
        if item is not None:
            cleaned.append(str(item).strip())

    # Step 3: Transform data
    transformed = []
    for item in cleaned:
        transformed.append(item.upper())

    # Step 4: Filter data
    filtered = []
    for item in transformed:
        if len(item) > 0:
            filtered.append(item)

    # Step 5: Sort data
    sorted_data = sorted(filtered)

    # Step 6: Deduplicate
    seen = set()
    unique = []
    for item in sorted_data:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    # Step 7: Format output
    result = []
    for i, item in enumerate(unique):
        result.append(f"{i+1}. {item}")

    return result


# ==============================================================================
# COMPLEX REFACTORING SCENARIOS
# ==============================================================================


def analyze_sales_report(transactions, start_date, end_date, category_filter,
                         region_filter, min_amount, max_amount, include_returns,
                         group_by, sort_order):
    """Nightmare function: Too many params AND too long AND deep nesting.
    
    Expected: AI should suggest multiple refactoring strategies.
    Severity: CRITICAL (10 params), CRITICAL (70+ lines), WARN (5 nesting)
    """
    if transactions is None:
        return None

    results = []
    total_sales = 0
    total_returns = 0
    category_totals = {}
    region_totals = {}

    for transaction in transactions:
        if transaction is not None:
            trans_date = transaction.get('date')
            if trans_date is not None:
                if start_date <= trans_date <= end_date:
                    category = transaction.get('category')
                    if category_filter is None or category == category_filter:
                        region = transaction.get('region')
                        if region_filter is None or region == region_filter:
                            amount = transaction.get('amount', 0)
                            if min_amount <= amount <= max_amount:
                                is_return = transaction.get('is_return', False)
                                if include_returns or not is_return:
                                    if is_return:
                                        total_returns += amount
                                    else:
                                        total_sales += amount

                                    if category not in category_totals:
                                        category_totals[category] = 0
                                    category_totals[category] += amount

                                    if region not in region_totals:
                                        region_totals[region] = 0
                                    region_totals[region] += amount

                                    results.append({
                                        'date': trans_date,
                                        'category': category,
                                        'region': region,
                                        'amount': amount,
                                        'is_return': is_return
                                    })

    if group_by == 'category':
        grouped = category_totals
    elif group_by == 'region':
        grouped = region_totals
    else:
        grouped = None

    if sort_order == 'asc':
        results = sorted(results, key=lambda x: x['amount'])
    elif sort_order == 'desc':
        results = sorted(results, key=lambda x: x['amount'], reverse=True)

    return {
        'transactions': results,
        'total_sales': total_sales,
        'total_returns': total_returns,
        'net_sales': total_sales - total_returns,
        'grouped': grouped
    }


# ==============================================================================
# GOOD CODE EXAMPLES (for comparison)
# ==============================================================================


class OrderConfig:
    """Example of using a config object instead of many parameters."""
    def __init__(self, tax_rate=0.08, discount_percent=0, shipping_cost=5.99,
                 handling_fee=0, gift_wrap_cost=0, insurance_cost=0,
                 expedited_shipping=False):
        self.tax_rate = tax_rate
        self.discount_percent = discount_percent
        self.shipping_cost = shipping_cost
        self.handling_fee = handling_fee
        self.gift_wrap_cost = gift_wrap_cost
        self.insurance_cost = insurance_cost
        self.expedited_shipping = expedited_shipping


def calculate_order_total_refactored(items, config: OrderConfig):
    """Refactored version using config object.
    
    Expected: No issues - this is the GOOD example.
    """
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    subtotal *= (1 - config.discount_percent / 100)
    total = subtotal * (1 + config.tax_rate)
    total += config.shipping_cost + config.handling_fee
    total += config.gift_wrap_cost + config.insurance_cost
    if config.expedited_shipping:
        total += 15.00
    return total


def validate_user_data_refactored(user_dict):
    """Refactored version using guard clauses.
    
    Expected: No issues - this is the GOOD example.
    """
    if user_dict is None:
        return False
    if 'email' not in user_dict:
        return False
    if '@' not in user_dict['email']:
        return False
    if 'password' not in user_dict:
        return False
    if len(user_dict['password']) < 8:
        return False
    return True
