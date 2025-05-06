from collections.abc import Iterable
from typing import Any

def h_rule():
    print('-' * 80)

def quoted_listing(items: Iterable[Any]) -> str:
    return ', '.join(f"'{x}'" for x in items)
