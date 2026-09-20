"""
Hash Map — Word Frequency Lookup
Purpose  : Store word → frequency for ranking (common words preferred).
Why used : O(1) average lookup lets ranking bias toward frequent words without scan.
Time     : get/put O(1) avg, space O(n)
"""

class HashMap:
    """Wrapper around Python dict — a hash map with chained buckets."""

    def __init__(self):
        self._map = {}

    def put(self, key: str, value: int) -> None:
        self._map[key] = value

    def get(self, key: str, default: int = 0) -> int:
        """Return frequency or default. O(1) avg."""
        return self._map.get(key, default)

    def contains(self, key: str) -> bool:
        return key in self._map

    def size(self) -> int:
        return len(self._map)

    def items(self):
        return self._map.items()
