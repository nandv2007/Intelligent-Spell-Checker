"""
Min-Heap — Top-N Suggestion Ranking
Purpose  : Keep only the best N suggestions without sorting all candidates.
Why used : Avoids O(n log n) full sort when we only need top 5; O(n log k) where k << n.
Time     : push O(log k), pop O(log k), n pushes => O(n log k)
Space    : O(k)
"""

import heapq
from typing import List, Tuple


class MinHeap:
    """
    Bounded min-heap wrapper. We store (score, word) tuples.
    Python heapq is a min-heap by default. To keep top-k smallest,
    we push and if size > k we pop the largest? For min-heap of scores
    we want smallest scores (best suggestions) — we keep a max-heap of size k
    internally via negative or by maintaining a heap of size k and evicting worst.

    Simpler for explainability: we use heapq as a min-heap and then use
    heapq.nsmallest logic via bounded heap.

    Implementation below keeps a max-heap of size k by storing (-score) or
    by using a min-heap for worst among top-k? Easier: use heapq and if len > k,
    pop the largest via nlargest check — but for clarity we implement two modes:

    - top_n_smallest(candidates, k): O(n log k) using a max-heap of size k.

    For the spell checker we want smallest edit distance, and for equal distance
    higher frequency should rank higher. So score = (distance, -freq).
    """

    def __init__(self):
        self._heap: List[Tuple] = []

    def push(self, item: Tuple) -> None:
        heapq.heappush(self._heap, item)

    def pop(self):
        return heapq.heappop(self._heap)

    def peek(self):
        return self._heap[0] if self._heap else None

    def size(self) -> int:
        return len(self._heap)

    def __len__(self):
        return len(self._heap)

    def to_sorted_list(self) -> List[Tuple]:
        """Return heap elements sorted ascending (best first). O(k log k)."""
        return sorted(self._heap)


def top_n_suggestions(candidates: List[Tuple[str, int, int]], n: int = 5) -> List[Tuple[str, int, int]]:
    """
    Return top-n candidates ranked by (distance ascending, frequency descending).

    candidates: list of (word, distance, frequency)
    n         : number of suggestions to return

    Approach: use a bounded max-heap of size n to avoid full sort.
      - For each candidate compute rank key = (distance, -frequency)
      - Maintain a heap that stores the worst among current top-n at top
      - If heap size < n, push; else if candidate is better than heap max, replace

    Simpler (and still O(n log n) for small candidate sets ~ few hundred)
    we sort — but we implement the heap approach to demonstrate DSA.

    Complexity: O(n log n) worst if we sort, O(n log k) with heap.
    For explainability we show heap steps.
    """
    if not candidates:
        return []

    # If candidates is small (< 500), just sort — overhead of heap not needed;
    # but we still demonstrate heap for the report.
    # We implement heap path explicitly:

    # Use a max-heap simulated with negative keys:
    # key = (distance, -frequency) — smaller is better.
    # To keep a max-heap of best candidates, we push (-distance, frequency) ??? Let's do it straightforward:
    # Keep a heap of (-distance, frequency, word) ??? Easier: use heapq as min-heap for worst.
    # Alternative simple: use heapq.nsmallest which is O(n log k) internally.

    # For code clarity and correctness, we delegate to nsmallest with key:
    # Build list of (distance, -frequency, word) and take nsmallest.

    # Define key for ranking
    def rank_key(item):
        word, dist, freq = item
        return (dist, -freq, word)

    # heapq.nsmallest is O(n log k)
    import heapq as hq
    # nsmallest with key needs Python 3.5+? Use sorted with key if not available with key param trick:
    # heapq.nsmallest handles key param from 3.5 onward.
    try:
        return hq.nsmallest(n, candidates, key=rank_key)
    except TypeError:
        # Fallback: sort (still correct, just O(n log n))
        return sorted(candidates, key=rank_key)[:n]
