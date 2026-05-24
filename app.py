"""
Flask Web Application — LU Decomposition (Doolittle Method)
============================================================

PIT Finals 2026 — Numerical Methods Online Calculator
Topic #8 from the project list.

Routes
------
/             — Main page (theory + worked examples + interactive calculator)
/api/solve    — POST endpoint; accepts JSON {matrix, vector, pivot} and
                returns a step-by-step solution.

Safety
------
User input is parsed via a strict whitelist-based parser (`parse_matrix_text`)
that rejects anything other than digits, decimal points, signs, whitespace,
commas, semicolons, and newlines. eval() is never used on user input.
"""

from flask import Flask, render_template, request, jsonify
import re
from lu_solver import (
    solve_system,
    matrix_to_latex,
    vector_to_latex,
    mat_mul,
)

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Safe input parsing
# ---------------------------------------------------------------------------

# Whitelist: digits, sign, decimal point, exponent, separators, whitespace
_NUMBER_PATTERN = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$")
_ALLOWED_CHARS = re.compile(r"^[\d\s,;.\-+eE\n\r\t]+$")


def parse_number(token: str) -> float:
    """Parse a single number token safely. Raises ValueError on failure."""
    token = token.strip()
    if not token:
        raise ValueError("Empty number.")
    if not _NUMBER_PATTERN.match(token):
        raise ValueError(f"Invalid number: {token!r}")
    return float(token)


def parse_matrix_text(text: str) -> list:
    """
    Parse a matrix from a textarea string.

    Accepts: rows separated by newlines OR semicolons; entries separated
    by commas, spaces, or tabs. Returns a list of lists of floats.
    """
    if text is None:
        raise ValueError("No matrix provided.")
    text = text.strip()
    if not text:
        raise ValueError("Matrix is empty.")
    if not _ALLOWED_CHARS.match(text):
        raise ValueError("Matrix contains disallowed characters.")

    # Normalise separators: semicolons act like newlines
    text = text.replace(";", "\n")
    rows = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Split on commas or any whitespace
        tokens = re.split(r"[,\s]+", line)
        row = [parse_number(t) for t in tokens if t]
        rows.append(row)

    if not rows:
        raise ValueError("No rows found.")
    width = len(rows[0])
    if any(len(r) != width for r in rows):
        raise ValueError("All rows must have the same number of columns.")
    return rows


def parse_vector_text(text: str) -> list:
    """Parse a vector — any of the row layouts accepted by parse_matrix_text."""
    if text is None:
        raise ValueError("No vector provided.")
    text = text.strip()
    if not text:
        raise ValueError("Vector is empty.")
    if not _ALLOWED_CHARS.match(text):
        raise ValueError("Vector contains disallowed characters.")

    text = text.replace(";", " ").replace("\n", " ")
    tokens = re.split(r"[,\s]+", text)
    return [parse_number(t) for t in tokens if t]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/solve", methods=["POST"])
def api_solve():
    """JSON endpoint. Body: { matrix: str, vector: str, pivot: bool }"""
    try:
        data = request.get_json(silent=True) or {}
        matrix_text = data.get("matrix", "")
        vector_text = data.get("vector", "")
        use_pivot = bool(data.get("pivot", False))

        A = parse_matrix_text(matrix_text)
        n = len(A)
        if any(len(row) != n for row in A):
            return jsonify({"ok": False, "error": "Matrix must be square."}), 400
        if n < 2 or n > 8:
            return jsonify({"ok": False, "error": "Matrix size must be 2×2 to 8×8."}), 400

        b = parse_vector_text(vector_text)
        if len(b) != n:
            return jsonify({
                "ok": False,
                "error": f"Vector length ({len(b)}) must match matrix size ({n}).",
            }), 400

        result = solve_system(A, b, use_pivoting=use_pivot)

        # Build LaTeX matrices for display
        latex = {
            "A": matrix_to_latex(A),
            "L": matrix_to_latex(result["L"]),
            "U": matrix_to_latex(result["U"]),
            "b": vector_to_latex(b),
            "y": vector_to_latex(result["y"]),
            "x": vector_to_latex(result["x"]),
            "LU": matrix_to_latex(mat_mul(result["L"], result["U"])),
        }
        if result["mode"] == "pivot":
            latex["P"] = matrix_to_latex(result["P"])
            latex["Pb"] = vector_to_latex(result["Pb"])

        return jsonify({
            "ok": True,
            "mode": result["mode"],
            "n": n,
            "latex": latex,
            "L": result["L"],
            "U": result["U"],
            "x": result["x"],
            "y": result["y"],
            "decomposition_steps": result.get("decomposition_steps", []),
            "forward_steps": result["forward_steps"],
            "backward_steps": result["backward_steps"],
            "swaps": result.get("swaps", []),
        })

    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:  # pragma: no cover — defensive
        return jsonify({"ok": False, "error": f"Unexpected error: {e}"}), 500


# Vercel entry point — they look for `app` at module level.
if __name__ == "__main__":
    app.run(debug=True, port=5000)
