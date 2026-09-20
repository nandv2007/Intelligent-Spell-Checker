# Intelligent Spell Checker

> Precise. Quiet. Built only with data structures — no database, no external APIs.

**Demo Link:** `https://spellchecker-2-oal4.onrender.com/` 

**Repository:** `https://github.com/nandv2007/Intelligent-Spell-Checker.git`

### Screenshot
#### Image:1
<img width="1342" height="760" alt="image" src="https://github.com/user-attachments/assets/2ade055d-9b10-4cf0-a84e-a2fd9fccbee9" />

#### Image:2

<img width="797" height="708" alt="image" src="https://github.com/user-attachments/assets/133498c2-c4a3-4af5-af9e-8c00da19e76c" />
<img width="797" height="295" alt="image" src="https://github.com/user-attachments/assets/f7f2310e-4d92-4b15-bdca-baee167d9595" />


---

### How it works

**Workflow:**
Input → Normalize → Tokenize → Lookup (HashSet) → Detect → Candidates (Trie + DP) → Rank (Min-Heap) → Output

**Step-by-step:**

1.  **Normalize & Tokenize** — Input is lowercased and split with regex. Handles `Hello, World!` → `hello` + `world`, ignores numbers/punctuation, handles empty input without crashing.

2.  **Lookup (HashSet)** — Every token is checked in a hash set in **O(1) average**. If found → marked correct. Example: `hello` → correct, `recieve` → miss.

3.  **Candidate generation (Trie + DP pruning)** — Instead of comparing `recieve` to all 36,000 words (brute-force), we walk the Trie. For each node we keep a DP row for the target. If `min(row) > maxDist (2)`, the entire subtree is pruned. For `recieve`, the `z...` branch is never visited.

4.  **Scoring (Levenshtein + Damerau)** — Classic DP: `dp[i][j] = min(delete, insert, replace)` → **O(m×n)**. Damerau adds one check: if `s[i-1]==t[j-2]` and `s[i-2]==t[j-1]` → `dp[i][j] = min(dp[i][j], dp[i-2][j-2]+1)`. This makes `teh→the` and `recieve→receive` = 1 edit, not 2.

5.  **Ranking (Min-Heap)** — Candidates become `(word, distance, frequency)`. Rank key is `(distance, -frequency)`. A min-heap via `heapq.nsmallest` keeps only the best 5 → **O(n log k)** instead of sorting all 200+ candidates. Tie → more common word wins (e.g., `receive` (freq 9096) beats `relieve` (4011) when both distance 1).

6.  **Output** — Original spacing and capitalization are preserved. Click any chip to apply one word, or `Apply all top` to replace all. Stats are real: `Checked 6 words in 52 ms · 4 issues · 19 candidates` (lookup / candidate / ranking times).

**Example:** `recieve` → Trie finds 13 candidates within 2 edits → Damerau refines `receive` to 1 → Heap ranks `receive (1, 9096)` before `relieve (1, 4011)` → shown first.

**Layers:** Presentation (Flask/UI) → Application (`spell_checker.py`) → Algorithm (DP/ranking) → Data Structures (HashSet/Trie/Heap/Map) → Dataset (`dictionary.txt`)
