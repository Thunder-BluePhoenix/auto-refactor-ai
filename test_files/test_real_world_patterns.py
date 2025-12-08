"""Test file for real-world code patterns.

This file contains realistic code patterns that developers often write
and that benefit from refactoring analysis.
"""


# ==============================================================================
# API HANDLER PATTERNS (commonly too long/nested)
# ==============================================================================


def handle_api_request(request, db_connection, cache, logger,
                       auth_service, rate_limiter):
    """Typical API handler with multiple concerns mixed together.
    
    Expected: WARN (6 params), INFO (40+ lines)
    """
    # Authentication
    logger.info(f"Received request: {request.method} {request.path}")

    if not auth_service.is_authenticated(request):
        logger.warning("Unauthenticated request")
        return {"error": "Unauthorized"}, 401

    # Rate limiting
    user_id = auth_service.get_user_id(request)
    if not rate_limiter.check_limit(user_id):
        logger.warning(f"Rate limit exceeded for user {user_id}")
        return {"error": "Too many requests"}, 429

    # Cache check
    cache_key = f"{request.method}:{request.path}"
    cached = cache.get(cache_key)
    if cached:
        logger.debug("Cache hit")
        return cached, 200

    # Database operation
    try:
        result = db_connection.execute(request.query)
        data = result.fetchall()
    except Exception as e:
        logger.error(f"Database error: {e}")
        return {"error": "Internal error"}, 500

    # Response formatting
    response = {
        "status": "success",
        "data": data,
        "count": len(data)
    }

    # Cache the result
    cache.set(cache_key, response, ttl=300)

    logger.info(f"Request completed: {len(data)} results")
    return response, 200


# ==============================================================================
# DATA PROCESSING PATTERNS
# ==============================================================================


def process_csv_file(file_path, delimiter, encoding, skip_header,
                     column_mapping, validation_rules, transform_functions,
                     error_handler):
    """CSV processor with too many configuration parameters.
    
    Expected: CRITICAL (8 params)
    """
    import csv

    results = []
    errors = []

    with open(file_path, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delimiter)

        if skip_header:
            next(reader)

        for row_num, row in enumerate(reader, start=1):
            try:
                # Apply column mapping
                mapped = {}
                for i, col_name in column_mapping.items():
                    if i < len(row):
                        mapped[col_name] = row[i]

                # Validate
                for field, rules in validation_rules.items():
                    value = mapped.get(field)
                    for rule in rules:
                        if not rule(value):
                            raise ValueError(f"Validation failed for {field}")

                # Transform
                for field, transform in transform_functions.items():
                    if field in mapped:
                        mapped[field] = transform(mapped[field])

                results.append(mapped)

            except Exception as e:
                error_handler(row_num, row, e)
                errors.append((row_num, str(e)))

    return results, errors


def calculate_statistics(numbers):
    """Statistical calculations with deep nesting.
    
    Expected: WARN (5 levels nesting), INFO (45+ lines)
    """
    if numbers:
        if len(numbers) > 0:
            # Calculate mean
            total = 0
            count = 0
            for num in numbers:
                if num is not None:
                    if isinstance(num, (int, float)):
                        total += num
                        count += 1

            if count > 0:
                mean = total / count

                # Calculate variance
                variance_sum = 0
                for num in numbers:
                    if num is not None:
                        if isinstance(num, (int, float)):
                            variance_sum += (num - mean) ** 2

                variance = variance_sum / count
                std_dev = variance ** 0.5

                # Find min/max
                min_val = None
                max_val = None
                for num in numbers:
                    if num is not None:
                        if isinstance(num, (int, float)):
                            if min_val is None or num < min_val:
                                min_val = num
                            if max_val is None or num > max_val:
                                max_val = num

                return {
                    'mean': mean,
                    'variance': variance,
                    'std_dev': std_dev,
                    'min': min_val,
                    'max': max_val,
                    'count': count
                }

    return None


# ==============================================================================
# VALIDATION PATTERNS (commonly deeply nested)
# ==============================================================================


def validate_form_data(form_data):
    """Form validation with excessive nesting.
    
    Expected: CRITICAL (7 levels nesting)
    """
    errors = []

    if form_data is not None:
        if isinstance(form_data, dict):
            if 'user' in form_data:
                user = form_data['user']
                if isinstance(user, dict):
                    if 'email' in user:
                        email = user['email']
                        if isinstance(email, str):
                            if '@' in email and '.' in email:
                                pass  # Valid
                            else:
                                errors.append("Invalid email format")
                        else:
                            errors.append("Email must be a string")
                    else:
                        errors.append("Email is required")
                else:
                    errors.append("User must be an object")
            else:
                errors.append("User is required")
        else:
            errors.append("Form data must be an object")
    else:
        errors.append("Form data is required")

    return len(errors) == 0, errors


# ==============================================================================
# REFACTORED EXAMPLES (for comparison)
# ==============================================================================


def validate_form_data_refactored(form_data):
    """Refactored version using guard clauses.
    
    Expected: No issues - demonstrates good patterns.
    """
    if form_data is None:
        return False, ["Form data is required"]

    if not isinstance(form_data, dict):
        return False, ["Form data must be an object"]

    if 'user' not in form_data:
        return False, ["User is required"]

    user = form_data['user']
    if not isinstance(user, dict):
        return False, ["User must be an object"]

    if 'email' not in user:
        return False, ["Email is required"]

    email = user['email']
    if not isinstance(email, str):
        return False, ["Email must be a string"]

    if '@' not in email or '.' not in email:
        return False, ["Invalid email format"]

    return True, []
