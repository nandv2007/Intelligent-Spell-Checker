"""
Levenshtein (Edit Distance) — Dynamic Programming
Purpose  : Metric of closeness between two words (insert / delete / replace).
Why used : Provably correct closeness metric; DP guarantees optimal substructure.
Time     : O(m * n) where m, n are word lengths.
Space    : O(min(m,n)) with rolling array optimization.
"""

def levenshtein_distance(s: str, t: str) -> int:
    """
    Compute Levenshtein edit distance between s and t.
    Classic DP with two-row optimization.

    DP definition:
      dp[i][j] = min edits to convert s[:i] -> t[:j]
      dp[0][j] = j  (insert j chars)
      dp[i][0] = i  (delete i chars)
      dp[i][j] = min(
          dp[i-1][j] + 1,                         # delete
          dp[i][j-1] + 1,                         # insert
          dp[i-1][j-1] + (0 if s[i-1]==t[j-1] else 1)  # replace / keep
      )

    Explainability: walk through a 5x5 matrix in review; two rows suffice in code.
    """
    # Ensure s is the shorter string to minimise space (O(min(m,n)))
    if len(s) > len(t):
        s, t = t, s

    m, n = len(s), len(t)

    if m == 0:
        return n
    if n == 0:
        return m

    # previous row: dp for s[:0] vs t[:j]
    previous = list(range(m + 1))

    for j in range(1, n + 1):
        # current row: dp for s prefix vs t[:j]
        current = [j] + [0] * m
        t_char = t[j - 1]
        for i in range(1, m + 1):
            cost = 0 if s[i - 1] == t_char else 1
            current[i] = min(
                previous[i] + 1,       # deletion
                current[i - 1] + 1,    # insertion
                previous[i - 1] + cost # substitution
            )
        previous = current

    return previous[m]


def damerau_levenshtein(s: str, t: str) -> int:
    """
    Damerau-Levenshtein — extends Levenshtein with adjacent transposition (swap).
    This makes classic misspellings like 'recieve' -> 'receive' and 'teh' -> 'the'
    distance 1 instead of 2, so ranking + frequency correctly prefers 'receive'.
    Time O(m*n), Space O(m*n) for clarity (words are short, <15 chars).
    Used for final ranking only; Trie pruning still uses plain Levenshtein for speed.
    """
    m, n = len(s), len(t)
    if m == 0:
        return n
    if n == 0:
        return m

    # Full matrix for transposition check
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s[i - 1] == t[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )
            # Transposition: if s[i-2]==t[j-1] and s[i-1]==t[j-2], allow swap at cost 1
            if i > 1 and j > 1 and s[i - 1] == t[j - 2] and s[i - 2] == t[j - 1]:
                dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)
    return dp[m][n]


def levenshtein_matrix(s: str, t: str):
    """
    Full matrix version — useful for whiteboard explanation / debugging.
    Returns (distance, matrix). Not used in production (previous function is faster).
    """
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s[i - 1] == t[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[m][n], dp
