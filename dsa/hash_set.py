"""
Hash Set — Dictionary Membership Check
Purpose  : O(1) average-time valid / invalid test for a word.
Why used : Fastest possible membership test; avoids linear scan of 36k words.
Time     : add O(1) avg, contains O(1) avg, space O(n)
"""

class HashSet:
    """Thin wrapper around Python's built-in hash set so every operation is explicit."""

    def __init__(self):
        # Underlying hash table — Python set is a hash table with open addressing.
        self._table = set()

    def add(self, word: str) -> None:
        """Insert a word. Average O(1)."""
        self._table.add(word)

    def contains(self, word: str) -> bool:
        """Return True if word exists. Average O(1)."""
        return word in self._table

    # Alias used by spell checker for readability
    def has(self, word: str) -> bool:
        return self.contains(word)

    def size(self) -> int:
        return len(self._table)

    def __len__(self):
        return len(self._table)

    def __contains__(self, word):
        return word in self._table
