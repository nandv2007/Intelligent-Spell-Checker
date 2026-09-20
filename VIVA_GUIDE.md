# Viva Guide — How to Explain Every File (Phase 2 Review)

You and your teammate can walk through this in 5 minutes. No API, no database — everything is DSA in `dsa/`.

## 1. High-level flow (say this first)
> Input → Normalize (lowercase) → Tokenize → HashSet lookup O(1) → Flag misses → Trie + DP pruned search → Damerau refinement → Min-Heap top-N → Output + stats
>
> Dictionary (36k words) is loaded once into three structures: HashSet, Trie, HashMap.

## 2. File-by-file (what to say if ma'am opens a file)

### `dsa/hash_set.py`
- Wraps Python `set` (hash table, open addressing).
- `contains(word)` is average O(1). Used for FR-04: “is this word valid?”.
- Say: “HashSet gives the fastest valid/invalid test; we don’t scan the list.”

### `dsa/hash_map.py`
- Wraps Python `dict` (hash map, separate chaining/balanced).
- Stores `word → frequency` (from `data/frequencies.json`).
- `get(word)` is O(1) average. Used to bias ranking toward common words.

### `dsa/trie.py`
- Node = `{ children: dict(char→Node), is_end: bool, word: str }`
- `insert(word)` walks/creates nodes O(L), `search` O(L).
- **Key method** `search_within_distance(target, max_dist)`:
  - Keeps a DP row for the current prefix vs target.
  - For each child char, compute `current_row` from `previous_row` (Levenshtein DP).
  - If `min(current_row) > max_dist`, prune that whole subtree — never visits irrelevant branches.
  - Collects words where `current_row[-1] <= max_dist` and `is_end`.
- Say: “Brute force would compare target to all 36k words (36k × DP). Trie prunes: e.g., typing ‘recieve’ never explores the ‘z…’ branch because its prefix is already distance 3 away.”

### `dsa/levenshtein.py`
- `levenshtein_distance(s,t)` — DP with two rows, O(m·n) time, O(min(m,n)) space.
- Recurrence: `dp[i][j] = min(delete, insert, replace)`; `cost = 0` if chars equal else `1`.
- `damerau_levenshtein(s,t)` — adds transposition check: if `s[i-1]==t[j-2] and s[i-2]==t[j-1]`, `dp[i][j] = min(dp[i][j], dp[i-2][j-2]+1)`.
- Used in ranking so “teh→the” and “recieve→receive” are distance 1.
- Say: “We explain the matrix on the board — why DP is provably correct.”

### `dsa/min_heap.py`
- Wraps `heapq` (binary heap, min-heap).
- `top_n_suggestions(candidates, n)` does `heapq.nsmallest(n, candidates, key=(distance, -freq))` → O(n log k) not O(n log n).
- Say: “We need only 5 out of 300 candidates — heap avoids sorting all 300.”

### `dsa/spell_checker.py` (the orchestrator)
- `__init__` loads dictionary into all three structures (HashSet + Trie + HashMap) — NFR-04 scalability.
- `tokenize(text)` — regex `([A-Za-z]+('[A-Za-z]+)? | \d+ | [^\w\s])` with `finditer` to keep positions; handles empty/punctuation-only (NFR-07).
- `is_correct(word)` — `a`/`i` are special-cased; otherwise HashSet O(1).
- `generate_candidates(word)` — calls `trie.search_within_distance`; for `len<=2` limits to distance 1 to avoid explosion.
- `rank_candidates(cands, top_n, original)` — refines distance via Damerau, builds `(word, dist, freq)`, then heap top-N.
- `check(text, top_n, max_distance)` — the full pipeline with `perf_counter` timing for FR-11 stats. Builds `corrected_text` by preserving original spacing/punctuation and capitalisation.
- Say: “Each FR-* maps to a method — you can point to the line number.”

### `app.py`
- Flask with 3 routes: `GET /` (UI), `POST /api/check` (JSON), `POST /api/apply`, `GET /api/health`.
- Loads `SpellChecker` once globally — subsequent requests are ~10–50 ms even for long sentences.
- No database, no external API.

### `data/dictionary.txt` & `frequencies.json`
- 36,001 clean English words + frequency map (higher = more common). Loaded into memory — no DB.

## 3. Complexity slide (what’s in your PDF page 15)

| DSA | Time | Why |
|-----|------|-----|
| HashSet | O(1) avg | Fastest valid/invalid |
| Trie | O(L) | Avoids brute-force scan |
| DP Levenshtein | O(m·n) | Correct closeness |
| Min-Heap | O(n log k) | No full sort for top 5 |
| HashMap freq | O(1) avg | Bias to common words |

## 4. Demo script (30 seconds)

1. Paste: `I recieve a beutiful oppurtunity tomorow`
2. Click Check → stats shows “Checked 6 words in 53 ms · 4 issues · 19 candidates”.
3. Click the first suggestion under “recieve” → it applies instantly.
4. Click “Apply all top” → corrected box shows clean text → Copy.

## 5. Tough questions & answers

**Q: Why not just use `enchant` or an API?**  
A: Those hide the engineering. We implement HashSet/Trie/Heap ourselves so the correction is a search problem we can analyse.

**Q: How is Trie faster than brute force?**  
A: Brute force: `36k * DP(7*8)`. Trie: only traverses prefixes whose DP row’s minimum ≤2 — e.g., “recieve” never visits the `z…` subtree. In practice 36k → ~13 candidates.

**Q: What if input is empty or `!!!`?**  
A: Tokenizer returns no words; `check()` returns zero counts gracefully — NFR-07.

**Q: How to scale to 50k+?**  
A: Trie nodes scale with total characters, not N·L worst-case; 36k → ~150k nodes fits in <100 MB, still O(L) lookup. We tested with 36k; same code works for 100k.

**Q: Where is Damerau used?**  
A: Trie pruning uses plain Levenshtein for speed; ranking refines with Damerau so transpositions rank correctly. Explain both.

Keep this file out of the demo — it’s for you, not for ma’am.
