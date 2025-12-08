"""Test file for async and modern Python patterns.

Tests how the analyzer handles async/await, type hints, 
dataclasses, and other modern Python features.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ==============================================================================
# ASYNC FUNCTIONS
# ==============================================================================


async def fetch_all_data(urls, session, timeout, max_retries,
                         backoff_factor, headers):
    """Async function with too many parameters.
    
    Expected: WARN (6 params)
    """
    results = []

    for url in urls:
        for attempt in range(max_retries):
            try:
                async with session.get(url, timeout=timeout, headers=headers) as response:
                    data = await response.json()
                    results.append(data)
                    break
            except Exception:
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff_factor * (attempt + 1))
                else:
                    results.append(None)

    return results


async def process_queue_with_deep_nesting(queue, processor):
    """Async function with deep nesting.
    
    Expected: INFO (4 levels nesting)
    """
    while True:
        try:
            item = await queue.get()
            if item is not None:
                if item.get('type') == 'task':
                    if item.get('priority') == 'high':
                        await processor.process_urgent(item)
                    else:
                        await processor.process_normal(item)
                else:
                    await processor.skip(item)
                queue.task_done()
        except asyncio.CancelledError:
            break


# ==============================================================================
# TYPE-HINTED FUNCTIONS
# ==============================================================================


def merge_datasets(
    primary: List[Dict[str, Any]],
    secondary: List[Dict[str, Any]],
    merge_key: str,
    conflict_resolution: str,
    include_unmatched: bool,
    transform_func: Optional[callable]
) -> List[Dict[str, Any]]:
    """Type-hinted function with many parameters.
    
    Expected: WARN (6 params)
    """
    result = []
    secondary_map = {item[merge_key]: item for item in secondary if merge_key in item}

    for primary_item in primary:
        if merge_key in primary_item:
            key_value = primary_item[merge_key]
            if key_value in secondary_map:
                merged = {**primary_item}
                secondary_item = secondary_map[key_value]

                for k, v in secondary_item.items():
                    if k in merged:
                        if conflict_resolution == 'primary':
                            pass  # Keep primary value
                        elif conflict_resolution == 'secondary':
                            merged[k] = v
                        elif conflict_resolution == 'latest':
                            merged[k] = v if v is not None else merged[k]
                    else:
                        merged[k] = v

                if transform_func:
                    merged = transform_func(merged)

                result.append(merged)
                del secondary_map[key_value]
            elif include_unmatched:
                result.append(primary_item)

    if include_unmatched:
        result.extend(secondary_map.values())

    return result


# ==============================================================================
# DATACLASS METHODS
# ==============================================================================


@dataclass
class DataProcessor:
    """Dataclass with methods that have issues."""

    name: str
    config: Dict[str, Any]

    def process_with_too_many_params(self, data, filter_func, map_func,
                                      reduce_func, sort_key, reverse,
                                      limit) -> List[Any]:
        """Method with too many parameters.
        
        Expected: WARN (7 params excluding self)
        """
        result = data

        if filter_func:
            result = [x for x in result if filter_func(x)]

        if map_func:
            result = [map_func(x) for x in result]

        if reduce_func:
            from functools import reduce
            result = reduce(reduce_func, result)
        else:
            if sort_key:
                result = sorted(result, key=sort_key, reverse=reverse)

            if limit:
                result = result[:limit]

        return result


# ==============================================================================
# GENERATOR FUNCTIONS
# ==============================================================================


def paginated_fetch(api_client, endpoint, page_size, filters,
                    sort_by, include_metadata, max_pages):
    """Generator function with too many parameters.
    
    Expected: CRITICAL (7 params)
    """
    page = 1

    while page <= max_pages:
        params = {
            'page': page,
            'page_size': page_size,
            'sort_by': sort_by
        }

        if filters:
            params.update(filters)

        response = api_client.get(endpoint, params=params)

        if response.status_code != 200:
            break

        data = response.json()
        items = data.get('items', [])

        if not items:
            break

        for item in items:
            if include_metadata:
                item['_page'] = page
                item['_fetched_at'] = 'now'
            yield item

        if len(items) < page_size:
            break

        page += 1


# ==============================================================================
# CONTEXT MANAGERS
# ==============================================================================


class DatabaseConnection:
    """Class with context manager and long methods."""

    def __init__(self, host, port, database, user, password, ssl_enabled):
        """Init with many parameters.
        
        Expected: WARN (6 params excluding self)
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.ssl_enabled = ssl_enabled
        self.connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()


# ==============================================================================
# LAMBDA AND FUNCTIONAL PATTERNS
# ==============================================================================


def apply_pipeline(data, pipeline_config):
    """Apply a transformation pipeline with deep nesting.
    
    Expected: WARN (5 levels nesting)
    """
    result = data

    for step in pipeline_config:
        if step.get('enabled', True):
            step_type = step.get('type')
            if step_type:
                if step_type == 'filter':
                    condition = step.get('condition')
                    if condition:
                        if callable(condition):
                            result = [x for x in result if condition(x)]
                elif step_type == 'map':
                    func = step.get('function')
                    if func:
                        if callable(func):
                            result = [func(x) for x in result]
                elif step_type == 'sort':
                    key = step.get('key')
                    if key:
                        result = sorted(result, key=key)

    return result
