"""Utility functions for environment variable parsing"""


def parse_bool(value: str) -> bool:
    """
    Parse a string value as a boolean.
    
    Args:
        value: String value to parse
        
    Returns:
        True if value is "true", "1", "yes" (case-insensitive), False otherwise
    """
    if not value:
        return False
    return value.lower() in ("true", "1", "yes")
