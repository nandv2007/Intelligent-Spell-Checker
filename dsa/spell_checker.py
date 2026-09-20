"""
Spell Checker Orchestrator — Brings all DSA layers together.
Architecture (as per proposal):
  Presentation Layer  -> Flask / UI  (app.py)
  Application Layer   -> SpellChecker (this file) + CheckResult
  Algorithm Layer     -> EditDistance, Similarity Scoring, Candidate Gen, Ranking
  Data Structure Layer-> HashSet, Trie, HashMap, MinHeap
  Dataset Layer       -> dictionary.txt, frequencies.json

Workflow implemented:
  Input -> Preprocess (normalize) -> Tokenize -> Lookup (HashSet O(1))
        -> Detect (flag misses) -> Candidates (Trie + DP, pruned) -> Rank (MinHeap) -> Output
"""

import re
import time
import json
import pathlib
from typing import List, Dict, Any, Tuple

from .hash_set import HashSet
from .hash_map import HashMap
from .trie import Trie
from .levenshtein import levenshtein_distance, damerau_levenshtein
from .min_heap import top_n_suggestions


# Token pattern: keep words with optional apostrophe (don't, it's), ignore pure punctuation
# We preserve original casing and punctuation for display, but lookup uses normalized form.
_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
# For display we also want to split keeping positions
_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\w\s]")


class SpellChecker:
    """
    Encapsulates all DSA components. Loads dictionary once at startup.
    Explainable line-by-line: each method corresponds to an FR-* requirement.
    """

    def __init__(self, dict_path: str = "data/dictionary.txt", freq_path: str = "data/frequencies.json"):
        # Data structures
        self.hash_set = HashSet()      # FR-04: membership check
        self.trie = Trie()             # FR-06: pruned candidate search
        self.freq_map = HashMap()      # FR-08: frequency-biased ranking

        self._load_dictionary(dict_path, freq_path)

    # ------------------------------------------------------------------
    # Dataset layer
    # ------------------------------------------------------------------
    def _load_dictionary(self, dict_path: str, freq_path: str) -> None:
        """
        Load dictionary into HashSet + Trie and frequencies into HashMap.
        Runs once at startup. Demonstrates NFR-04 scalability (36k words).
        """
        dict_file = pathlib.Path(dict_path)
        if not dict_file.exists():
            # Try alternative relative to project root
            dict_file = pathlib.Path(__file__).resolve().parent.parent / dict_path
        freq_file = pathlib.Path(freq_path)
        if not freq_file.exists():
            freq_file = pathlib.Path(__file__).resolve().parent.parent / freq_path

        # Load word list
        words = [w.strip().lower() for w in dict_file.read_text().splitlines() if w.strip()]
        for w in words:
            self.hash_set.add(w)
            self.trie.insert(w)

        # Load frequencies
        try:
            freq_data = json.loads(freq_file.read_text())
            for w, f in freq_data.items():
                # ensure lowercase
                self.freq_map.put(w.lower(), int(f))
        except Exception:
            # Fallback: assign uniform frequency
            for w in words:
                self.freq_map.put(w, 100)

    # ------------------------------------------------------------------
    # FR-02 / FR-03 : Tokenize + Normalize
    # ------------------------------------------------------------------
    def tokenize(self, text: str) -> List[Dict[str, Any]]:
        """
        Tokenize text into words while preserving positions for highlighting.
        Returns list of {raw, normalized, start, end, is_word}
        - FR-02: split into individual tokens
        - FR-03: case-fold + strip punctuation for lookup (normalized)
        """
        tokens = []
        if not text:
            return tokens

        # Use finditer to get positions; handles empty / punctuation-only gracefully (NFR-07)
        for m in _TOKEN_RE.finditer(text):
            raw = m.group(0)
            start, end = m.span()
            # Determine if this token is a word (alphabetic)
            is_word = bool(re.fullmatch(r"[A-Za-z]+(?:'[A-Za-z]+)?", raw))
            # Normalize: case-fold
            normalized = raw.lower() if is_word else raw
            # Additional: if word contains apostrophe, keep as-is lowercased
            tokens.append({
                "raw": raw,
                "normalized": normalized,
                "start": start,
                "end": end,
                "is_word": is_word
            })
        return tokens

    def normalize(self, word: str) -> str:
        """Normalize a single token (FR-03). Lowercase & strip surrounding punctuation."""
        # Since tokenization already stripped punctuation, just lower
        return word.lower().strip()

    # ------------------------------------------------------------------
    # FR-04 / FR-05 : Lookup + Flag
    # ------------------------------------------------------------------
    def is_correct(self, normalized_word: str) -> bool:
        """
        Check if normalized word is in dictionary.
        - Single letters 'a'/'i' are considered correct (common words of len 1)
        - Numbers / punctuation are not checked (NFR-07)
        Average O(1) via HashSet.
        """
        if len(normalized_word) == 1:
            return normalized_word in ("a", "i")
        if len(normalized_word) <= 1:
            return True  # ignore
        return self.hash_set.contains(normalized_word)

    # ------------------------------------------------------------------
    # FR-06 / FR-07 : Candidate Generation + Edit Distance
    # ------------------------------------------------------------------
    def generate_candidates(self, word: str, max_distance: int = 2) -> List[Tuple[str, int]]:
        """
        Generate candidate corrections within max_distance using Trie pruning.
        Returns list of (candidate, distance).
        This is the optimized path (Trie + DP) that avoids brute-force scan.
        """
        # For very short words (<=2) use distance 1 to avoid explosion;
        # for length 3 we allow 2 because transpositions like teh->the need it
        if len(word) <= 2:
            max_distance = min(max_distance, 1)
        # Trie search does DP pruning internally
        return self.trie.search_within_distance(word.lower(), max_distance)

    def compute_distance(self, a: str, b: str) -> int:
        """Wrapper for Levenshtein DP (FR-07). O(m*n)."""
        return levenshtein_distance(a.lower(), b.lower())

    # ------------------------------------------------------------------
    # FR-08 / FR-09 : Ranking
    # ------------------------------------------------------------------
    def rank_candidates(self, candidates: List[Tuple[str, int]], top_n: int = 5, original_word: str = "") -> List[Dict[str, Any]]:
        """
        Rank by (edit distance asc, frequency desc) and return top N.
        Uses Min-Heap O(n log k).
        Applies Damerau-Levenshtein refinement so transpositions (teh->the, recieve->receive)
        are correctly scored as distance 1. This keeps the demo intuitive.
        """
        if not candidates:
            return []

        enriched: List[Tuple[str, int, int]] = []
        for word, dist in candidates:
            # Refine distance with Damerau if original_word is known (handles adjacent swaps)
            if original_word:
                try:
                    d2 = damerau_levenshtein(original_word.lower(), word.lower())
                    # Use the better (smaller) of the two; Damerau never larger than Levenshtein
                    if d2 < dist:
                        dist = d2
                except Exception:
                    pass
            freq = self.freq_map.get(word, 1)
            enriched.append((word, dist, freq))

        top = top_n_suggestions(enriched, top_n)

        # Format for API: include score for explainability but UI shows only word
        result = []
        for word, dist, freq in top:
            result.append({"word": word, "distance": dist, "frequency": freq})
        return result

    # ------------------------------------------------------------------
    # Full pipeline — FR-11 Reporting
    # ------------------------------------------------------------------
    def check(self, text: str, top_n: int = 5, max_distance: int = 2) -> Dict[str, Any]:
        """
        End-to-end spell check pipeline.
        Returns structured result with per-token analysis and aggregate stats.

        Stats include (FR-11): total time, lookup time, candidates evaluated,
        candidate generation time, ranking time.
        """
        t0 = time.perf_counter()

        # NFR-07: handle malformed input gracefully
        if text is None:
            text = ""
        text = str(text)

        # Edge: empty or whitespace only
        if not text.strip():
            return {
                "original_text": text,
                "corrected_text": text,
                "tokens": [],
                "stats": {
                    "total_words": 0,
                    "misspelled": 0,
                    "total_time_ms": 0.0,
                    "lookup_time_ms": 0.0,
                    "candidate_time_ms": 0.0,
                    "ranking_time_ms": 0.0,
                    "candidates_evaluated": 0,
                    "dictionary_size": self.hash_set.size()
                }
            }

        tokens = self.tokenize(text)

        # Stats accumulators
        lookup_time = 0.0
        candidate_time = 0.0
        ranking_time = 0.0
        candidates_evaluated = 0

        analyzed = []
        misspelled_count = 0
        total_words = 0

        for idx, tok in enumerate(tokens):
            raw = tok["raw"]
            norm = tok["normalized"]
            is_word = tok["is_word"]

            if not is_word:
                # Punctuation / numbers — not checked, just pass through
                analyzed.append({
                    "index": idx,
                    "raw": raw,
                    "normalized": norm,
                    "is_word": False,
                    "is_correct": True,
                    "suggestions": [],
                    "candidate_count": 0
                })
                continue

            total_words += 1

            # Lookup timing
            ls = time.perf_counter()
            correct = self.is_correct(norm)
            lookup_time += (time.perf_counter() - ls) * 1000  # accumulate ms

            if correct:
                analyzed.append({
                    "index": idx,
                    "raw": raw,
                    "normalized": norm,
                    "is_word": True,
                    "is_correct": True,
                    "suggestions": [],
                    "candidate_count": 0
                })
            else:
                misspelled_count += 1

                # Candidate generation
                cs = time.perf_counter()
                candidates = self.generate_candidates(norm, max_distance)
                candidate_time += (time.perf_counter() - cs) * 1000
                candidates_evaluated += len(candidates)

                # Ranking (pass original word for Damerau refinement)
                rs = time.perf_counter()
                suggestions = self.rank_candidates(candidates, top_n, original_word=norm)
                ranking_time += (time.perf_counter() - rs) * 1000

                analyzed.append({
                    "index": idx,
                    "raw": raw,
                    "normalized": norm,
                    "is_word": True,
                    "is_correct": False,
                    "suggestions": suggestions,
                    "candidate_count": len(candidates)
                })

        # Build corrected text by applying top suggestion for preview
        # (FR-10: produce corrected output; UI will let user pick)
        corrected_parts = []
        last_end = 0
        for tok, analysis in zip(tokens, analyzed):
            # Append text between tokens (spaces)
            if tok["start"] > last_end:
                corrected_parts.append(text[last_end:tok["start"]])
            if analysis["is_word"] and not analysis["is_correct"] and analysis["suggestions"]:
                # Preserve original capitalization pattern
                sug = analysis["suggestions"][0]["word"]
                raw = analysis["raw"]
                # Simple case preservation: if original was Capitalized, capitalize suggestion
                if raw[0].isupper():
                    sug = sug.capitalize()
                elif raw.isupper():
                    sug = sug.upper()
                corrected_parts.append(sug)
            else:
                corrected_parts.append(tok["raw"])
            last_end = tok["end"]
        # trailing text
        if last_end < len(text):
            corrected_parts.append(text[last_end:])
        corrected_text = "".join(corrected_parts)

        total_time_ms = (time.perf_counter() - t0) * 1000

        return {
            "original_text": text,
            "corrected_text": corrected_text,
            "tokens": analyzed,
            "stats": {
                "total_words": total_words,
                "misspelled": misspelled_count,
                "total_time_ms": round(total_time_ms, 3),
                "lookup_time_ms": round(lookup_time, 3),
                "candidate_time_ms": round(candidate_time, 3),
                "ranking_time_ms": round(ranking_time, 3),
                "candidates_evaluated": candidates_evaluated,
                "dictionary_size": self.hash_set.size()
            }
        }

    def apply_corrections(self, text: str, selections: Dict[int, str]) -> str:
        """
        Apply user-selected corrections.
        selections: {token_index: chosen_word}
        Preserves original spacing and punctuation.
        """
        tokens = self.tokenize(text)
        result_parts = []
        last_end = 0
        for idx, tok in enumerate(tokens):
            if tok["start"] > last_end:
                result_parts.append(text[last_end:tok["start"]])
            if idx in selections and tok["is_word"]:
                chosen = selections[idx]
                # Preserve case
                raw = tok["raw"]
                if raw and raw[0].isupper():
                    chosen = chosen.capitalize()
                result_parts.append(chosen)
            else:
                result_parts.append(tok["raw"])
            last_end = tok["end"]
        if last_end < len(text):
            result_parts.append(text[last_end:])
        return "".join(result_parts)
