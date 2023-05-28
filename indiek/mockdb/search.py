import re


def build_search_query(string: str) -> re.Pattern:
    base_str = '('
    base_str += '|'.join(string.split())
    base_str += ')'
    return re.compile(base_str, flags=re.IGNORECASE)