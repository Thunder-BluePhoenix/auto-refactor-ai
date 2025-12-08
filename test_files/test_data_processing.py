"""Test file with data processing patterns - ETL and analytics code."""

from dataclasses import dataclass
from typing import List, Dict, Any


def transform_data_pipeline(
    raw_data,
    filters,
    transformations,
    aggregations,
    output_format,
    validation_rules,
):
    """ETL pipeline with too many parameters."""
    # Apply filters
    filtered = [item for item in raw_data if all(f(item) for f in filters)]
    
    # Apply transformations
    transformed = filtered
    for transform in transformations:
        transformed = [transform(item) for item in transformed]
    
    # Apply aggregations
    result = {}
    for agg_name, agg_func in aggregations.items():
        result[agg_name] = agg_func(transformed)
    
    return result


def calculate_statistics(data):
    """Long function doing too much - should be split."""
    if not data:
        return {}
    
    # Calculate mean
    total = sum(data)
    count = len(data)
    mean = total / count
    
    # Calculate variance
    squared_diff_sum = 0
    for value in data:
        diff = value - mean
        squared_diff_sum += diff * diff
    variance = squared_diff_sum / count
    
    # Calculate standard deviation
    import math
    std_dev = math.sqrt(variance)
    
    # Calculate median
    sorted_data = sorted(data)
    mid = count // 2
    if count % 2 == 0:
        median = (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        median = sorted_data[mid]
    
    # Calculate mode
    frequency = {}
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    max_freq = max(frequency.values())
    mode = [k for k, v in frequency.items() if v == max_freq]
    
    # Calculate quartiles
    q1_idx = count // 4
    q3_idx = 3 * count // 4
    q1 = sorted_data[q1_idx]
    q3 = sorted_data[q3_idx]
    iqr = q3 - q1
    
    # Calculate min/max
    minimum = min(data)
    maximum = max(data)
    data_range = maximum - minimum
    
    return {
        "mean": mean,
        "variance": variance,
        "std_dev": std_dev,
        "median": median,
        "mode": mode,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "min": minimum,
        "max": maximum,
        "range": data_range,
        "count": count,
    }


def parse_nested_config(config):
    """Deeply nested config parsing."""
    result = {}
    
    if config:
        if "database" in config:
            if "connection" in config["database"]:
                if "host" in config["database"]["connection"]:
                    if "port" in config["database"]["connection"]:
                        result["db_host"] = config["database"]["connection"]["host"]
                        result["db_port"] = config["database"]["connection"]["port"]
    
    return result


def validate_record(record):
    """Another deeply nested validation function."""
    if record:
        if "id" in record:
            if record["id"] > 0:
                if "name" in record:
                    if len(record["name"]) > 0:
                        if "email" in record:
                            if "@" in record["email"]:
                                return True
    return False
