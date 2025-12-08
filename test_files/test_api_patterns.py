"""Test file for API/web service patterns - common in production code."""


def fetch_user_data(user_id, api_key, base_url, timeout, retry_count, headers):
    """Function with too many parameters - API call pattern."""
    # This is a common anti-pattern in API code
    import requests
    
    for attempt in range(retry_count):
        try:
            response = requests.get(
                f"{base_url}/users/{user_id}",
                headers=headers,
                timeout=timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            if attempt == retry_count - 1:
                raise
    return None


def process_webhook(data):
    """Deeply nested webhook processing logic."""
    if data:
        if "event" in data:
            if data["event"] == "user.created":
                if "user" in data:
                    if "email" in data["user"]:
                        # Deep nesting - should use early returns
                        user = data["user"]
                        return {"status": "processed", "email": user["email"]}
    return {"status": "error"}


def validate_api_request(
    request_body,
    auth_token,
    ip_address,
    user_agent,
    content_type,
    accept_header,
    rate_limit_key,
):
    """Too many parameters - should use a Request dataclass."""
    errors = []
    
    if not request_body:
        errors.append("Missing request body")
    if not auth_token:
        errors.append("Missing auth token")
    if not ip_address:
        errors.append("Missing IP address")
        
    return len(errors) == 0, errors


def build_complex_query(
    table,
    columns,
    where_clause,
    order_by,
    limit,
    offset,
    joins,
    group_by,
    having,
):
    """Database query builder with too many parameters."""
    query_parts = [f"SELECT {', '.join(columns)} FROM {table}"]
    
    if joins:
        for join in joins:
            query_parts.append(f"JOIN {join}")
    
    if where_clause:
        query_parts.append(f"WHERE {where_clause}")
    
    if group_by:
        query_parts.append(f"GROUP BY {group_by}")
    
    if having:
        query_parts.append(f"HAVING {having}")
    
    if order_by:
        query_parts.append(f"ORDER BY {order_by}")
    
    if limit:
        query_parts.append(f"LIMIT {limit}")
    
    if offset:
        query_parts.append(f"OFFSET {offset}")
    
    return " ".join(query_parts)
