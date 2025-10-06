def normalize_text(text):
    """Normalize text by stripping whitespace and converting to lowercase."""
    return text.strip().lower()


def calculate_similarity(text1, text2):
    """Calculate a simple similarity ratio between two strings."""
    import difflib
    return difflib.SequenceMatcher(None, text1, text2).ratio()


def load_json_file(filepath):
    """Load JSON data from a file."""
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data, filepath):
    """Save JSON data to a file."""
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def retry_on_exception(max_retries=3, exception=Exception):
    """Decorator to retry a function on specified exception."""
    def decorator(func):
        import time
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exception:
                    retries += 1
                    time.sleep(1)
            return func(*args, **kwargs)
        return wrapper
    return decorator
