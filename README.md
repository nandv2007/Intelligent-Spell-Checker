# Intelligent Spell Checker — DSA Prototype

Pure Data Structures & Algorithms spell checker — no external APIs, no database.
Built for Phase 2 review: clean backend, professional UI, explainable code.

**Live demo:** deploy on Render (free) — see steps below.

## What it does
- Accepts a word or full sentence
- Tokenizes and normalizes (FR-02, FR-03)
- Checks each token against a **HashSet** — O(1) average lookup (FR-04, FR-05)
- Generates candidates via **Trie + DP pruning** — avoids scanning the full 36k dictionary (FR-06)
- Scores by **Levenshtein edit distance (DP)** — O(m·n) closeness metric (FR-07)
- Ranks with **Min-Heap** — O(n log k) top-N without full sort (FR-08, FR-09)
- Lets you click a suggestion to apply it and produces corrected text (FR-10)
- Shows timing and counts (FR-11) — just numbers, no jargon in the UI

## Data Structures (where in code)
| DSA | File | Purpose |
|-----|------|---------|
| HashSet | `dsa/hash_set.py` | Dictionary membership — O(1) avg |
| Trie | `dsa/trie.py` | Prefix-pruned candidate search — O(L), prunes by edit distance |
| DP / Levenshtein | `dsa/levenshtein.py` | Edit distance — O(m·n) |
| Min-Heap | `dsa/min_heap.py` | Top-N ranking — O(n log k) |
| HashMap | `dsa/hash_map.py` | Word frequency lookup — O(1) avg |

Architecture follows the proposal: Presentation → Application (`dsa/spell_checker.py`) → Algorithm → Data Structure → Dataset (`data/dictionary.txt`, `data/frequencies.json`).

## Project layout
```
app.py                  # Flask app (no DB)
dsa/
  hash_set.py
  hash_map.py
  trie.py
  levenshtein.py
  min_heap.py
  spell_checker.py      # orchestrator — Input → Normalize → Tokenize → Lookup → Detect → Candidates → Rank → Output
data/
  dictionary.txt        # 36,001 words
  frequencies.json      # word → frequency (for ranking)
templates/index.html    # single-page professional UI
requirements.txt
render.yaml
Procfile
```

## Run locally
```bash
pip install -r requirements.txt
python app.py
# open http://localhost:5000
```

## Deploy on Render (free)

### One-time setup (5 minutes)
1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial: Intelligent Spell Checker (DSA)"
   # create a new empty repo on github.com (no README), then:
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
   Replace `<your-username>` and `<repo-name>` with yours.

2. **Create the Render service**
   - Go to https://dashboard.render.com → **New +** → **Web Service**
   - Connect your GitHub and select the repo you just pushed
   - Render auto-detects `render.yaml` (or set manually):
     - **Environment:** Python 3
     - **Build command:** `pip install -r requirements.txt`
     - **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
     - **Plan:** Free
   - Click **Create Web Service**. First deploy finishes in ~2 minutes.

3. **Update**
   ```bash
   git add .
   git commit -m "Update"
   git push
   ```
   Render redeploys automatically.

### Notes
- No database or API keys required.
- Dictionary (≈ 36k words) is loaded into memory at startup (HashSet + Trie + HashMap).
- Health check: `GET /api/health` → `{ status, dictionary_size }`

## API
- `POST /api/check` → `{ text, top_n?, max_distance? }` → `{ original_text, corrected_text, tokens:[{raw, is_correct, suggestions:[{word,distance,frequency}], candidate_count}], stats:{total_words, misspelled, total_time_ms, lookup_time_ms, candidate_time_ms, ranking_time_ms, candidates_evaluated, dictionary_size} }`
- `POST /api/apply` → `{ text, selections: { tokenIndex: word } }` → `{ corrected_text }`
- `GET /api/health`

## How to explain in review (60 seconds)
1. **HashSet** answers “is this word valid?” in O(1).
2. **Trie** generates suggestions without scanning all 36k words — each branch keeps a DP row for the target; if `min(row) > maxDist`, the whole subtree is pruned.
3. **Levenshtein DP** scores closeness: `dp[i][j] = min(delete, insert, replace)`.
4. **Min-Heap** keeps the best 5 without sorting hundreds of candidates.
5. Walk through `dsa/spell_checker.py: check()` — it measures each stage so the stats strip is real data.

No DSA terms appear in the UI — only in code and this README.
