"""
Intelligent Spell Checker — Flask Application
No database, no external APIs. Pure DSA backend.
Deployable on Render with gunicorn.
"""

import os
import time
from flask import Flask, request, jsonify, render_template

from dsa.spell_checker import SpellChecker

app = Flask(__name__, template_folder="templates", static_folder="static")

# ------------------------------------------------------------
# Global spell checker — loaded once at startup (fast subsequent requests)
# ------------------------------------------------------------
print("Loading dictionary and building DSA structures ...")
_load_start = time.perf_counter()
spell_checker = SpellChecker(
    dict_path="data/dictionary.txt",
    freq_path="data/frequencies.json"
)
print(f"Ready: {spell_checker.hash_set.size()} words loaded in {round((time.perf_counter()-_load_start)*1000,1)} ms "
      f"(HashSet, Trie, HashMap built)")

# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/check", methods=["POST"])
def api_check():
    """
    POST /api/check
    Body: { "text": "...", "top_n": 5, "max_distance": 2 }
    Returns: check result with tokens + stats
    """
    data = request.get_json(silent=True) or {}
    # Also accept form-encoded
    if not data and request.form:
        data = request.form.to_dict()

    text = data.get("text", "")
    # Clamp top_n and max_distance
    try:
        top_n = int(data.get("top_n", 5))
        top_n = max(1, min(top_n, 10))
    except Exception:
        top_n = 5

    try:
        max_distance = int(data.get("max_distance", 2))
        max_distance = max(1, min(max_distance, 3))
    except Exception:
        max_distance = 2

    # Empty check handled gracefully inside spell_checker (NFR-07)
    result = spell_checker.check(text, top_n=top_n, max_distance=max_distance)
    return jsonify(result)

@app.route("/api/apply", methods=["POST"])
def api_apply():
    """
    POST /api/apply
    Body: { "text": "...", "selections": { "2": "receive", ... } }
    Applies user-chosen suggestions and returns corrected text.
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    selections_raw = data.get("selections", {})
    # selections keys may be strings -> int
    selections = {}
    for k, v in selections_raw.items():
        try:
            selections[int(k)] = str(v)
        except Exception:
            continue
    corrected = spell_checker.apply_corrections(text, selections)
    return jsonify({"corrected_text": corrected})

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "dictionary_size": spell_checker.hash_set.size(),
        "trie_size": spell_checker.trie.size()
    })

@app.route("/api/dictionary/size")
def dict_size():
    return jsonify({"size": spell_checker.hash_set.size()})

# ------------------------------------------------------------
# Error handlers
# ------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal error"}), 500

# ------------------------------------------------------------
# Run
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # For local preview bind to 0.0.0.0
    app.run(host="0.0.0.0", port=port, debug=False)
