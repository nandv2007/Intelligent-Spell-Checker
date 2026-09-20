"""
Trie (Prefix Tree) — Prefix-Pruned Candidate Search
Purpose  : Avoid brute-force scan of entire dictionary when generating suggestions.
Why used : Prunes branches whose prefix is already too distant; reduces candidates
           from 36k full scans to a few hundred trie traversals.
Time     : insert O(L), exact search O(L) where L = word length
           approximate search O(nodes_visited * alphabet) but pruned by max distance.
Space    : O(total characters) nodes.
"""

from typing import List, Tuple, Dict


class TrieNode:
    """Single node in the Trie."""

    __slots__ = ("children", "is_end", "word")

    def __init__(self):
        # children: char -> TrieNode  (hash map of edges)
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end: bool = False
        # Store full word at terminal node so we can return it without backtracking.
        self.word: str = ""


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self._size = 0

    def insert(self, word: str) -> None:
        """Insert word into trie. O(L)."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        if not node.is_end:
            node.is_end = True
            node.word = word
            self._size += 1

    def search(self, word: str) -> bool:
        """Exact search. O(L)."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix: str) -> bool:
        """Prefix existence. O(L)."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def size(self) -> int:
        return self._size

    # -------------------------------------------------------------
    # Approximate search — Levenshtein automaton style
    # Collects all words within max_dist without scanning full dict.
    # -------------------------------------------------------------
    def search_within_distance(self, target: str, max_dist: int = 2) -> List[Tuple[str, int]]:
        """
        Return list of (word, distance) where edit distance <= max_dist.
        Uses DP row pruning: if the minimum value in the current DP row
        exceeds max_dist, the whole subtree is pruned.

        Algorithm:
          - Maintain a DP row for the current trie prefix vs target.
          - For each child, compute next row from previous row.
          - Recurse only if min(next_row) <= max_dist.

        This is the "optimized" approach vs brute-force comparison to all 36k words.
        """
        if not target:
            return []
        target = target.lower()
        results: List[Tuple[str, int]] = []

        # Initial row: distance from empty prefix to target[0..i]
        # e.g., target "hello" -> [0,1,2,3,4,5]
        initial_row = list(range(len(target) + 1))

        for char, child in self.root.children.items():
            self._search_recursive(child, char, target, initial_row, results, max_dist)

        return results

    def _search_recursive(
        self,
        node: TrieNode,
        char: str,
        target: str,
        previous_row: List[int],
        results: List[Tuple[str, int]],
        max_dist: int,
    ) -> None:
        """
        Recursive helper — computes DP row for this node and recurses.
        previous_row : DP row for parent prefix
        current_row  : DP row for current prefix (parent prefix + char)
        """
        columns = len(target) + 1
        current_row = [previous_row[0] + 1]

        for col in range(1, columns):
            insert_cost = current_row[col - 1] + 1      # insert char
            delete_cost = previous_row[col] + 1          # delete target[col-1]
            replace_cost = previous_row[col - 1] + (0 if target[col - 1] == char else 1)
            current_row.append(min(insert_cost, delete_cost, replace_cost))

        # If this node marks a word and its edit distance is within bound, collect it
        if node.is_end and current_row[-1] <= max_dist:
            results.append((node.word, current_row[-1]))

        # If any entry in current_row is <= max_dist, this prefix could still lead
        # to a valid word; otherwise prune the whole subtree.
        if min(current_row) <= max_dist:
            for next_char, child in node.children.items():
                self._search_recursive(child, next_char, target, current_row, results, max_dist)
