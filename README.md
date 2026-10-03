# Intelligent Spell Checker

> Precise. Quiet. Pure Data Structures & Algorithms — zero external APIs, zero database. Designed in a Creative Sunset Presentation Theme with Dual Interactive & Slide Deck views.

**Demo Link:** `https://spellchecker-2-oal4.onrender.com/` 

**Repository:** `https://github.com/nandv2007/Intelligent-Spell-Checker.git`

### Screenshots
#### Image:1
<img width="1342" height="760" alt="image" src="https://github.com/user-attachments/assets/2ade055d-9b10-4cf0-a84e-a2fd9fccbee9" />

#### Image:2
<img width="797" height="708" alt="image" src="https://github.com/user-attachments/assets/133498c2-c4a3-4af5-af9e-8c00da19e76c" />
<img width="797" height="295" alt="image" src="https://github.com/user-attachments/assets/f7f2310e-4d92-4b15-bdca-baee167d9595" />

---

### What it does
- **Creative Sunset Presentation Theme:** Warm aura glow framing, floating ivory presentation cards, and sunset-stepper accents inspired by modern creative slide decks.
- **Dual View Modes:**
  - **✨ Interactive Checker:** Full spelling verification workstation with live token stream, candidate pills, one-click correction, and real-time execution bar charts.
  - **📑 Slide Deck View:** An interactive 10-slide deck matching project viva & review presentations (Objectives, Methodology, Project Scope, Implementation Strategies, Mind Map, and Conclusions).
- **Accurate Detection & Normalization:** Preserves capitalization and punctuation boundaries.
- **Constant-Time Verification:** Queries a **HashSet** in $O(1)$ average time.
- **State-Pruned Candidate Generation:** Uses a **Prefix Trie + Dynamic Programming (DP)** pruning to search through a 36,001-word corpus in milliseconds without brute-force scans.
- **Damerau-Levenshtein Edit Distance:** $O(m \times n)$ scoring including transpositions.
- **Priority Ranking:** Uses a bounded **Min-Heap** to return top-N candidates scored by edit distance and weighted by corpus frequency.
- **One-Click Corrections:** Click any suggestion chip or "Apply all top suggestions" to replace misspellings instantly.

---

### Data Structures in Code

| DSA | File | Purpose | Time Complexity |
|-----|------|---------|-----------------|
| **HashSet** | `dsa/hash_set.py` | Dictionary membership verification | $O(1)$ average |
| **Trie** | `dsa/trie.py` | Prefix-pruned candidate search tree | $O(L)$ with DP pruning |
| **DP / Levenshtein** | `dsa/levenshtein.py` | Edit distance scoring | $O(m \cdot n)$ |
| **Min-Heap** | `dsa/min_heap.py` | Top-N candidate ranking | $O(n \log k)$ |
| **HashMap** | `dsa/hash_map.py` | Word frequency lookup | $O(1)$ average |

---

### How it works

**Workflow:**
`Input` → `Normalize & Tokenize` → `Lookup (HashSet)` → `Detect` → `Candidates (Trie + DP)` → `Rank (Min-Heap)` → `Corrected Output`

1. **Normalize & Tokenize** — Input is lowercased and split with regex. Handles `Hello, World!` → `hello` + `world`, ignores numbers/punctuation, handles empty input without crashing.
2. **Lookup (HashSet)** — Every token is checked in a hash set in **$O(1)$ average**. If found → marked correct.
3. **Candidate generation (Trie + DP pruning)** — Instead of comparing misspelled tokens to all 36,000 words (brute-force), the checker walks the Trie. For each node, it tracks a DP row for the target; if $\min(\text{row}) > \text{maxDist}$, the entire subtree is pruned.
4. **Scoring (Levenshtein + Damerau)** — Classic DP: `dp[i][j] = min(delete, insert, replace)`. Damerau accounts for adjacent character transpositions (e.g. `recieve` → `receive` is distance 1).
5. **Ranking (Min-Heap)** — Candidates are ranked by `(distance, -frequency)` using a min-heap, prioritizing higher English usage frequency when distances tie.
6. **Output & Export** — Live token visualizer, one-click suggestion application, and clipboard/download export.

---

### Project Layout
```
app.py                  # Flask application & JSON endpoints
dsa/
  hash_set.py           # O(1) hash set for dictionary membership
  hash_map.py           # O(1) frequency lookup
  trie.py               # Prefix Trie with DP branch pruning
  levenshtein.py        # Levenshtein & Damerau distance
  min_heap.py           # Priority queue for top-N ranking
  spell_checker.py      # Core orchestrator pipeline
data/
  dictionary.txt        # 36,001 curated English words
  frequencies.json      # Word frequencies for ranking
templates/
  index.html            # Single-page app in Creative Sunset Theme
requirements.txt        # Flask & gunicorn
render.yaml             # Render deployment config
Procfile                # Process file for cloud hosting
```

---

### Run Locally
```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000 in your browser
```

---

### Deployment on Render (Free)
1. Push to GitHub (`origin main`).
2. Go to [Render Dashboard](https://dashboard.render.com) → **New +** → **Web Service**.
3. Connect your repository — Render auto-detects `render.yaml`.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
